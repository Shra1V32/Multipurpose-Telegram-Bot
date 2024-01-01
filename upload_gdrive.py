#!/usr/bin/env python3
import os
import sys
import time
from subprocess import check_output, Popen, PIPE
import update_token
import random
import json
import asyncio
import requests
from constants import GDRIVE_APIKEY
from signal import SIGKILL

S = 16


class InvalidCredentials(Exception):
    pass


class TokenError(Exception):
    pass


global urlForCompletedDownloads, gidsWithCompletedDownloads


class getUploads:
    def __init__(self) -> None:
        global gidsWithFilename, gidsWithCompletedDownloads, urlForCompletedDownloads
        gidsWithFilename = {}
        gidsWithCompletedDownloads = []
        urlForCompletedDownloads = {}

    @classmethod
    async def genRandomString(cls):
        return "".join(random.choice('1234567890abcdef') for _ in range(16))

    
    @classmethod
    def genRandomStringSync(cls):
        return "".join([random.choice("1234567890abcdef") for _ in range(16)])

    
    @classmethod
    async def addUpload(cls, filename: str):
        cls.filename = filename
        cls.epoch_time = str(time.time())
        cls.curl_filename = f"{cls.epoch_time}.curl"
        await asyncio.create_subprocess_shell(
            f"./upload_gdrive.sh '{cls.filename}' > '{cls.curl_filename}' 2>&1", shell=True
        )
        await asyncio.sleep(1)
        with open(cls.curl_filename, "r") as progressFile:
            if "{" not in progressFile.readlines()[-1]:
                cls.data = {
                    "curl_filename": cls.curl_filename,
                    "filename": cls.filename,
                }
                gidsWithFilename[await cls.genRandomString()] = cls.data
            else:
                print(progressFile.readlines())

    async def getFilenameBasedOnGid(self, gid: str) -> str:
        self.gid = gid
        return gidsWithFilename[self.gid]["filename"]

    async def getListOfGids(self):
        return [i.split(":")[0] for i in gidsWithFilename]

    async def getFileId(self, url):
        self.url = url
        if "uc?id" not in self.url:
            try:
                self.fileId = self.url.split("/")[5]
            except:
                return False
            if self.fileId != "":
                return self.fileId
            else:
                return False
        else:
            try:
                self.fileId = self.url.split("id=")[1].split("&")[0]
            except:
                return False
            return self.fileId

    async def cloneFile(self, fileId: str):
        self.fileId = fileId

        headers = {
            "Authorization": f'Bearer {open("gdrivetoken","r").read()}',
            "Accept": "application/json",
        }

        params = {
            "supportsAllDrives": "true",
            "supportsTeamDrives": "true",
            "key": GDRIVE_APIKEY,
        }

        json_data = {}

        response = requests.post(
            f"https://www.googleapis.com/drive/v3/files/{self.fileId}/copy",
            params=params,
            headers=headers,
            json=json_data,
        )
        if response.status_code == 200:
            self.id = response.json()["id"]
            self.name = response.json()["name"]
            return (self.id, self.name)
        else:
            return False

    async def getStatusBasedOnGid(self, gid, filename) -> dict:
        self.gid = gid
        self.filename = filename
        with open(self.filename, "r") as prgfile:
            self.progress = prgfile.readlines()[-1]
            if "{" not in self.progress:
                self.progress = self.progress.split()
                if self.progress[0] != "100":
                    self.data = {
                        "Name": (gidsWithFilename[self.gid]["filename"]),
                        "Speed": ("".join(self.progress[-1]) + "/s"),
                        "GID": f"{self.gid}",
                        "Status": "Uploading...",
                        "Progress": (self.progress[0] + "%"),
                        "totalSize": (self.progress[1]),
                        "TimeRemaining": (self.progress[-2]),
                    }
                    print(self.data)
                    return self.data
            else:
                try:
                    k = json.loads(self.progress)
                    if k["error"]["message"] == "Invalid Credentials":
                        raise TokenError
                except TokenError:
                    print("Auth Token Expired")
                except KeyError:
                    filename = gidsWithFilename[self.gid]
                    Popen([f"rm '{filename['curl_filename']}'"], shell=True)
                    Popen([f"rm '{filename['filename']}'"], shell=True)
                    gidsWithCompletedDownloads.append(self.gid)
                    urlForCompletedDownloads[
                        self.gid
                    ] = f"https://drive.google.com/file/d/{k['id']}/view"

    async def getStatusOfAllDownloads(self):
        uploadStatuses = []
        for self.gid, self.filename in gidsWithFilename.items():
            self.filename = self.filename["curl_filename"]
            uploadStatuses.append(
                await self.getStatusBasedOnGid(self.gid, self.filename)
            )
        return uploadStatuses

    async def getCompletedUploads(self) -> list:
        return gidsWithCompletedDownloads

    async def cleanUp(self):
        k = gidsWithCompletedDownloads
        for i in k:
            del gidsWithFilename[i]
        gidsWithCompletedDownloads.clear()

    async def cancelUpload(self, gid: str):
        self.gid = gid
        self.filename = await self.getFilenameBasedOnGid(self.gid)
        self.filename = self.filename.replace("]", "\]").replace("[", "\[")
        self.output = (
            check_output(
                f"ps -aux | grep '{self.filename}' | grep -v 'upload_gdrive.sh'",
                shell=True,
            )
            .decode()
            .split()
        )
        self.pid = self.output[1]
        print(self.output)
        os.kill(int(self.pid), SIGKILL)
        gidsWithCompletedDownloads.append(self.gid)

    def cronUpdateGDriveToken(self):
        while 1 != 0:
            update_token.genToken()
            time.sleep(3400)


if __name__ == "__main__":
    k = getUploads()
    asyncio.run(k.addUpload(sys.argv[1]))
