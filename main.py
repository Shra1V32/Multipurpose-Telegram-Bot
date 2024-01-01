#!/usr/bin/env python3
from telethon import TelegramClient, events
from telethon.errors.rpcerrorlist import (
    MessageIdInvalidError,
    MessageEmptyError,
    MessageNotModifiedError,
)
from constants import API_ID, API_HASH, BOT_TOKEN
import os
import time
from subprocess import check_output, PIPE
import aria_helper
import asyncio
import upload_gdrive
from threading import Thread
from PIL import Image
from pdf2image import convert_from_path
import requests
import random
import yt_handler
import logging


################## Constants ##################
# A dictionary to reply based on certain patterns
data = {"hello": "Hello there! How are you doing?", "Greet me": "Good Morning"}

global messageIdBasedOnUID, completed_downloads, completedUploads, streak, calledPDFCommand, calledImg2PDF, photo_list
messageIdBasedOnUID = dict()
image2PDFUsers = {}
completedUploads = set()
numOfDownloads = 0
calledPDFCommand, calledImg2PDF, photo_list = False, False, []
authorizedUsers = [658048451]

commands = {
    "/dl": {
        "description": "This command allows you to download & upload a file directly to your Google Drive"
    },
    "/convert": {
        "description": "Send this command whenever you've sent all your images & to convert"
    },
    "/ytdl": {
        "description": "This command helps you to download any YouTube Video within seconds by uploading them to your GDrive"
    },
    "/img2pdf": {
        "description": "This command helps you convert your album of images to a single PDF"
    },
    "/pdf2img": {
        "description": "This command helps you convert your PDF to an album of images"
    },
    "/cancel": {
        "description": "To cancel your Download, Give a an argument its GID to delete"
    },
    "/cancelall": {
        "description": "To cancel all the downloads & uploads which are live"
    },
}

calledDownloadHandler = False


################ - ######################


# define custom class
class EmptyQueueInfo(Exception):
    pass

logging.basicConfig(filename=f'session-{str(time.time()).split(".")[0]}.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')
# Start up client
CREDS_REQ = False
assert API_ID, "Telegram API ID can't be left empty"
assert API_HASH, "Telegram API Hash can't be left empty"
assert BOT_TOKEN, "Telegram Bot Token can't be left empty"
client = TelegramClient("AdvancedTelegramBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
client.start()
os.system("bash ./aria.sh")
########### Creating objects ##########
upload = upload_gdrive.getUploads()
p = Thread(target=upload.cronUpdateGDriveToken)
p.start()


aria_helper = aria_helper.AriaHelper()
aria_helper.clearQueues()

youtubeHandler = yt_handler.YTDL()
########################################


async def genQuote() -> tuple:
    """To generate quotes from zenquotes API"""
    p = requests.get("https://zenquotes.io/api/quotes", timeout=5)
    req = p.json()
    p = req[random.randint(0, len(req) - 1)]
    author = p["a"]
    quote = p["q"]
    return (quote, author)


async def QueueHandler(dataset: list):
    """One of the core tasks
    Handles which download needs to be entered
    updates the `queue_info` whenever called.
    """
    try:
        global queue_info, message, calledDownloadHandler, ytlist
        sum = 0
        ytlist = []
        for i in dataset:
            req = dataset[sum]
            try:
                download_name = req["Name"]
                progress_str = req["Progress"]
                eta_str = req["TimeRemaining"]
                if eta_str == "-":
                    eta_str = "NA"
                if progress_str != "100.00%" and download_name != "":
                    if ".youtube." not in download_name:
                        queue_info += f"\nName: `{download_name}`\nTime Remaining: `{eta_str}`\nSpeed: `{req['Speed']}`\nStatus: {req['Status']}\nSize: `{req['totalSize']}`\nProgress: `{progress_str}`\nGID: `{req['GID']}`\n"
                    elif ".youtube.audio" not in download_name:
                        queue_info += f"\nName: `[YouTube] {download_name.split('.youtube.video')[0]}`\nTime Remaining: `{eta_str}`\nSpeed: `{req['Speed']}`\nStatus: {req['Status']}\nSize: `{req['totalSize']}`\nProgress: `{progress_str}`\nGID: `{req['GID']}`\n"
            except KeyError:
                queue_info += f"\n{req['Status']}\n"
            finally:
                sum += 1
        if queue_info == "":
            logging.info("Empty Queue Info detected")
            await asyncio.gather(
                *[
                    client.delete_messages(user, message)
                    for user, message in messageIdBasedOnUID.items()
                ]
            )
            calledDownloadHandler = False

    except MessageNotModifiedError:
        logging.info("QueueHandler: Received Exception: MessageNotModified")
        return 0


async def parallel_update(user, message):
    global messageIdBasedOnUID, queue_info
    message = await client.edit_message(user, message, queue_info)
    messageIdBasedOnUID[user] = message.id


async def sendDownloadCompletedMessage(user, names):
    await client.send_message(
        user,
        f"Successfully Downloaded: `{await upload.getFilenameBasedOnGid(names)}`\nGDrive URL: [Click Here]({upload_gdrive.urlForCompletedDownloads[names]})",
    )


async def run_command(cmd):
    epoch = time.time()
    process = await asyncio.create_subprocess_shell(
        f"{cmd} | tee {epoch}.cmd", stderr=PIPE, stdout=PIPE
    )
    await asyncio.sleep(0.2)
    fd = open(f"{epoch}.cmd", "r")
    k = await client.send_message(user, "Gaining output...")
    while 1 != 0:
        buf_str = fd.readline()
        await client.edit_message(k, buf_str)
        await asyncio.sleep(2)


async def DownloadHandler():
    """Download Handler to handle the downloads & chat tasks"""
    global user, messageIdBasedOnUID, calledDownloadHandler, numOfDownloads, message, queue_info, gids, i, completed_downloads, download_name, data, completedUploads
    while numOfDownloads > 0:
        queue_info = ""
        data = (
            await aria_helper.getStatusOfAllDownloads()
            + await upload.getStatusOfAllDownloads()
            + await youtubeHandler.getStatusOfAllDownloads()
        )
        # print(data)
        completedUploads = set(await upload.getCompletedUploads())
        completedDownloads = await aria_helper.completedDownloads()
        downDiff = len(data) - numOfDownloads
        if downDiff > 0:
            try:
                await asyncio.gather(
                    *[
                        client.delete_messages(user, int(message - 2))
                        for user, message in messageIdBasedOnUID.items()
                    ]
                )

            except BaseException:
                logging.warn(f"Exception Received: {messageIdBasedOnUID.items()}")
        for names in completedDownloads:
            if "[METADATA]" not in names:
                await upload.addUpload(names)
                # await asyncio.sleep(2)
            else:
                print(f"Ignored: '{names}'")
        numOfDownloads = len(data)
        for names in completedUploads:
            try:
                await asyncio.gather(
                    *[
                        sendDownloadCompletedMessage(user, names)
                        for user, _ in messageIdBasedOnUID.items()
                    ]
                )
            except KeyError:
                await client.send_message(
                    user,
                    f"Successfully deleted: `{await upload.getFilenameBasedOnGid(names)}`",
                )
        if len(completedUploads) != 0:
            await upload.cleanUp()
        try:
            await QueueHandler(data)
            # await QueueHandler(upload_data)
        except (IndexError, EmptyQueueInfo, TypeError):
            pass
        try:
            await asyncio.gather(
                *[
                    parallel_update(int(user), message)
                    for user, message in messageIdBasedOnUID.items()
                ]
            )
        except MessageIdInvalidError:
            logging.info("DownloadHandler: Exception received: MessageIdInvalidError")
            try:
                if numOfDownloads != 0:
                    for user in messageIdBasedOnUID:
                        message = await client.send_message(user, queue_info)
                        messageIdBasedOnUID[user] = message.id
            except (MessageIdInvalidError, ValueError):
                continue
        except MessageEmptyError:
            logging.info("DownloadHandler: Exception received: MessageEmptyError")
            if queue_info == "":
                continue
        except MessageNotModifiedError:
            logging.info("DownloadHandler: Exception received: MessageNotModifiedError")
            continue
        await asyncio.sleep(3)
    else:
        calledDownloadHandler = False
        messageIdBasedOnUID.clear()
        return 0


async def Pdf2ImgHandler(user, messageId):
    global calledPDFCommand
    calledPDFCommand = False
    epoch_time = time.time()
    msg_pdf2img = await client.send_message(user, "`Downloading PDF File...`")
    filename = f"Downloads/{epoch_time}.file"
    await asyncio.create_subprocess_shell(
        f"mkdir -p Downloads/{epoch_time}/", shell=True
    )
    data = await client.download_media(messageId, file=filename)
    if b"PDF document" in check_output(f"file {filename}", shell=True):
        images = convert_from_path(f"Downloads/{epoch_time}.file")
        await client.edit_message(
            msg_pdf2img,
            f"`Found a total of {len(images)} Images in the PDF\n\nConverting PDF file to Images...`",
        )
        for i in range(len(images)):
            images[i].save(
                f"Downloads/{epoch_time}/" + str(epoch_time) + str(i) + ".jpg", "JPEG"
            )
        files = check_output(f"ls Downloads/{epoch_time}/*", shell=True)
        files = files.decode().split()
        if len(files) < 30:
            await client.edit_message(msg_pdf2img, "`Uploading photos...`")
            await client.send_file(user, files)
            await client.delete_messages(user, msg_pdf2img)
        else:
            k = await asyncio.create_subprocess_shell(
                f"7z a Downloads/{epoch_time}.zip ./Downloads/{epoch_time}/*",
                shell=True,
            )
            await k.communicate()
            file = await client.upload_file(f"Downloads/{epoch_time}.zip")
            await client.send_file(user, file)
            await client.delete_messages(user, msg_pdf2img)
            await asyncio.create_subprocess_shell(
                f"rm Downloads/{epoch_time}/ && rm {filename}", shell=True
            )
    else:
        await client.edit_message(
            msg_pdf2img, "File is corrupted / Not a valid PDF File."
        )
    return 0

    # Iterate over all pages in the PDF


async def img2PdfHandler(event, k):
    # Download the photo
    await event.download_media(file=f"Downloads/{k}")


async def Voice2TextHandler(event, voicemsgid):
    epoch_time = time.time()
    voice2txt_msg = await client.send_message(
        event.chat_id, "Analyzing audio file . . ."
    )
    data = await client.download_media(voicemsgid, file=f"Downloads/{epoch_time}.data")
    p = await asyncio.create_subprocess_shell(
        f"vosk-transcriber -i Downloads/{epoch_time}.data -o Downloads/{epoch_time}.srt",
        shell=True,
        stderr=PIPE,
        stdout=PIPE,
    )
    await p.communicate()
    with open(f"Downloads/{epoch_time}.srt", "r") as outfile:
        outdata = outfile.read()
    await client.edit_message(voice2txt_msg, f"**Voice2Text:** {outdata}")


async def convert(phl: list, msg, awaitMessageUser):
    """For converting images to PDF"""
    global calledImg2PDF, photo_list
    len_phl = len(phl)
    await client.delete_messages(awaitMessageUser, image2PDFUsers[awaitMessageUser])
    for i in range(len_phl):
        phl[i] = await asyncio.to_thread(Image.open, ("Downloads/" + str(phl[i])))
    pdf_file = f"{str(time.time())}.pdf"
    await client.edit_message(
        msg, f"`Received Images: {len_phl}\n\nMerging jpg file to a PDF...`"
    )
    try:
        phl[0].save(
            pdf_file, "PDF", resolution=100.0, save_all=True, append_images=phl[1:]
        )
        await client.edit_message(msg, "`Sucessfully converted Images to PDF`")
    except BaseException:
        await client.edit_message(msg, "`An Error Occured!`")
        return 0
    await client.edit_message(msg, "`Uploading file...`")
    await client.send_file(user, pdf_file)
    await client.delete_messages(user, msg)
    os.system(f"rm {pdf_file} &")
    photo_list = []
    calledImg2PDF = False


@client.on(events.NewMessage)
async def handler(event):
    """Event handler whenever a message is sent
    This block will get executed whenever a user sends a message
    """
    content = event.raw_text
    if event.message.text and content[0] == "/":
        global numOfDownloads, calledDownloadHandler, user, message, data, yt_title, yt_filename, yt_urls, yt, calledPDFCommand, calledImg2PDF, photo_list, users, messageIdBasedOnUID
        user = event.chat_id
        logging.debug(f"User ID/Chat ID: {user}")
        content = event.raw_text
        try:
            prefix = content.split(" ")[0]  # Prefix contains command calls
            # response contains whatever the argument you call it
            response = content.split(" ")[1]
        except BaseException:
            response = None
        if prefix == "/dl" and response is not None:
            if "magnet:?" not in response:
                # Add url to the downloads list
                await aria_helper.AddDownload(response)
            else:
                await aria_helper.AddTorrent(response)
            print(numOfDownloads)
            if not calledDownloadHandler:
                print("Called Download Handler")
                calledDownloadHandler = True
                message = await client.send_message(user, "Downloading...")
                messageIdBasedOnUID[user] = message.id
                await asyncio.sleep(2)
                numOfDownloads = len(await aria_helper.getNames())
                await DownloadHandler()
            else:
                try:
                    tmp = await client.send_message(user, queue_info)
                    messageIdBasedOnUID[user] = tmp.id
                except NameError:
                    pass
        elif (
            prefix == "/cancel" and response is not None
        ):  # To cancel the download based on GID
            if response in await aria_helper.listOfGids():
                delete_msg = await event.reply(f"Deleting {response}")
                deleted_name = await aria_helper.getNameBasedOnGID(response)
                await aria_helper.cancelDownload(response)
                if response not in await aria_helper.listOfGids():
                    await client.edit_message(
                        delete_msg, f"Successfully deleted `{deleted_name}`"
                    )
            elif response in await upload.getListOfGids():
                await upload.cancelUpload(response)
            else:
                await event.reply(f"Current GIDs: {gids}")
                await event.reply("No Download found with the specific GID")
        elif prefix == "/cancelall":
            if numOfDownloads != 0:
                aria_helper.clearQueues()
                await event.reply("Successfully cancelled all the downloads.")
            else:
                msgstr = ""
                msgstr += "No active downloads"
                msgstr += "\n\n**Help:** "
                msgstr += commands["/cancelall"]["description"]
                await client.send_message(user, msgstr)
        elif prefix == "/ytdl" and response is not None:
            if not calledDownloadHandler:
                print("Called Download Handler")
                calledDownloadHandler = True
                numOfDownloads += 1
                message = await client.send_message(user, "Downloading...")
                messageIdBasedOnUID[user] = message.id
                await youtubeHandler.downloadYT(response)
                await asyncio.sleep(3)
                await DownloadHandler()
                # asyncio.to_thread(youtubeHandler.downloadYT(response))
                # popa.start()
            else:
                await yt_handler.YTDL().downloadYT(response)
                numOfDownloads += 1
                await asyncio.sleep(2)
        elif prefix == "/start":
            await event.reply("Bot is up & Running...")
        elif prefix == "/pdf2img":
            if not event.is_reply:
                await client.send_message(
                    user,
                    "No file has been tagged to, Please tag to a file that you want to convert",
                )
            else:
                msgid = await client.get_messages(
                    user, ids=await event.get_reply_message()
                )
                await Pdf2ImgHandler(user, msgid)
                return 0
        elif prefix == "/img2pdf":
            calledImg2PDF = True
            awaitMsg = await client.send_message(
                user, "Awaiting for the album to be be sent"
            )
            image2PDFUsers[user] = awaitMsg
        elif prefix == "/quote":
            q_msg = await event.reply("Fetching quote from server...")
            data = await genQuote()
            quote = data[0]
            author = data[1]
            await client.edit_message(q_msg, f"__{quote}__\n\t\t~ {author}")
        elif prefix == "/clone" and response is not None:
            fileId = await upload.getFileId(response)
            if fileId is not False:
                msg_clone = await client.send_message(user, f"Cloning `{fileId}`")
                cloneResponse = await upload.cloneFile(fileId)
                if cloneResponse is not False:
                    try:
                        await client.edit_message(
                            msg_clone,
                            f"**Successfully Cloned**\n**File:** `{cloneResponse[1]}`\n**GDrive URL:** [Click Here](https://drive.google.com/file/d/{cloneResponse[0]}/view)",
                        )
                    except BaseException:
                        print(f"Error Found: {cloneResponse}")
                else:
                    await client.send_message(user, "Error occured while cloning!")
            else:
                await client.send_message(user, "Invalid URL sent!")
            # await client.download_media(user, file=f"Downloads/{}")
        elif prefix == "/convert":
            if calledImg2PDF:
                msgimg2pdf = await client.send_message(
                    user, "Converting images to PDF File..."
                )
                calledImg2PDF = False
                await convert(photo_list, msgimg2pdf, user)
            else:
                msgstr = "This command depends upon `/img2pdf`"
                msgstr += "\n\n**Help:** "
                msgstr += commands[prefix]["description"]
                await client.send_message(user, msgstr)
        elif prefix == "/run":
            if user in authorizedUsers:
                response = content.split("/run ")
                await client.send_message(user, f"**$ {response[1]}**")
                if response[1] != "":
                    await run_command(response[1])
                    return 0
                else:
                    await client.send_message(user, "No argument given")
            else:
                await client.send_message(
                    user, "You are not authorized to use this command."
                )
        elif prefix == "/ping":
            msg = await event.reply("`Pinging...`")
            k = await asyncio.create_subprocess_shell(
                "ping -c 1 8.8.4.4 | tail -n1", shell=True, stderr=PIPE, stdout=PIPE
            )
            out, err = await k.communicate()
            if out:
                out = "`Pong!\n`" + str(f"`{out.decode()}`")
                await client.edit_message(msg, out)
            if err:
                await client.edit_message(msg, err.decode())
            return 0
        elif prefix == "/help":
            help_str = "There are the available commands: \n\n"
            for command, description in commands.items():
                help_str += f"{command}: {description['description']}\n\n"
            await client.send_message(user, help_str)
        elif prefix == "/voice2text":
            if not event.is_reply:
                await client.send_message(
                    user,
                    "No file has been tagged to, Please tag to a file that you want to convert",
                )
            else:
                msgid = await client.get_messages(
                    user, ids=await event.get_reply_message()
                )
                await Voice2TextHandler(event, msgid)
                return 0
        else:
            msgstr = f"`{prefix}`: No argument given\n\n**Help:** "
            msgstr += commands[prefix]["description"]
            await event.reply(msgstr)

    elif event.message.photo and calledImg2PDF:
        k = str(time.time())
        photo_list.append(k)
        await img2PdfHandler(event, k)
    else:
        calledImg2PDF = False


client.run_until_disconnected()
