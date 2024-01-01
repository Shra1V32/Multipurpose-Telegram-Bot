from yt_dlp import YoutubeDL
import upload_gdrive
import asyncio
from threading import Thread, Lock
import time

lock = Lock()


class YTDL:
    def __init__(self) -> None:
        global gidBasedOnVID, statusBasedOnGID, gidsWithCompletedDownloads
        gidBasedOnVID = {}
        statusBasedOnGID = {}
        gidsWithCompletedDownloads = []
        self.data_dict = dict()

    def download_status(self, d):
        with lock:
            self.data_dict = d
            if d is not None:
                if self.data_dict["status"] == "downloading":
                    self.vid = self.data_dict["info_dict"]["id"]
                    try:
                        self.gid = gidBasedOnVID[self.vid]
                    except KeyError:
                        self.gid = gidBasedOnVID[
                            self.vid
                        ] = upload_gdrive.getUploads().genRandomStringSync()
                    self.data = {
                        "Name": (self.data_dict["info_dict"]["_filename"]),
                        "Speed": (self.data_dict["_speed_str"]),
                        "GID": f"{gidBasedOnVID[self.vid]}",
                        "Status": "Downloading",
                        "Progress": (self.data_dict["_percent_str"]),
                        "totalSize": (self.data_dict["_total_bytes_str"]),
                        "TimeRemaining": (self.data_dict["_eta_str"]),
                    }
                    statusBasedOnGID[self.gid] = self.data
                elif self.data_dict["status"] == "finished":
                    self.data = {
                        "Status": f"`Merging Audio & video for {self.data_dict['info_dict']['_filename']}...`"
                    }
                    self.vid = self.data_dict["info_dict"]["id"]
                    self.gid = gidBasedOnVID[self.vid]
                    statusBasedOnGID[self.gid] = self.data

    async def getCompletedDownloads(self) -> list[str]:
        self.completedDownloads = []
        # await asyncio.sleep(0.2)
        print(f"yt-dlp: Thread status: {self.p.is_alive()}")
        for self.compgid in gidsWithCompletedDownloads:
            self.completedDownloads.append(statusBasedOnGID[self.compgid]["Name"])
            del statusBasedOnGID[self.compgid]
            gidsWithCompletedDownloads.clear()
        return self.completedDownloads

    async def getStatusOfAllDownloads(self):
        return [downData for downData in statusBasedOnGID.values()]

    def checkStatus(self, thread_obj):
        self.thread_obj = thread_obj
        time.sleep(3)
        print(f"Waiting for Status {self.data_dict['info_dict']['id']}")
        while 1 != 0:
            if self.thread_obj.is_alive() == False:
                break
            time.sleep(1)
        self.thread_upload = Thread(
            target=asyncio.run(
                upload_gdrive.getUploads.addUpload(
                    (self.data_dict["info_dict"]["_filename"])
                )
            )
        )
        self.thread_upload.start()
        print(f'{self.data_dict["info_dict"]["id"]} completed.')
        self.derive_gid = gidBasedOnVID[self.data_dict["info_dict"]["id"]]
        # gidsWithCompletedDownloads.append(
        #     self.derive_gid
        # )
        del statusBasedOnGID[self.derive_gid]
        print(f'{self.data_dict["info_dict"]["id"]}: Added upload')

    async def downloadYT(self, link: str):
        self.link = link
        self.ydl_opts = {
            "quiet": True,
            "progress_hooks": [self.download_status],
            "noprogress": True,
            "no_warnings": True,
            "cookiefile": "cookies.txt",
        }
        self.p = Thread(target=YoutubeDL(self.ydl_opts).download, args=([self.link]))
        self.q = Thread(target=self.checkStatus, args=[self.p])
        self.p.start()
        self.q.start()
        # self.gid = await upload_gdrive.getUploads().genRandomString()


if __name__ == "__main__":

    async def main():
        # url = input("Enter the url: ")
        await YTDL().downloadYT("https://www.youtube.com/watch?v=cFS7-CHCaiw")

    asyncio.run(main())
