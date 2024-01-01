from time import sleep
import aria2p


class AriaHelper():
    global aria2, yt_dict
    yt_dict = {}
    #yt_dict = {}

    ''' <class> to initiate aria2 before we can deploy it onto Telegram '''

    def __init__(self):
        global aria2
        link = 'https://linuxmint.com/torrents/lmde-5-cinnamon-64bit.iso.torrent'
        aria2 = aria2p.API(
            aria2p.Client(
                host="http://localhost",
                port=6800,
                secret=""
            )
        )
        dire = '/home/mvsr/Mini-Project/Downloads/'
        aria2.add_uris([link], {'dir': dire})
        sleep(2)
        downloads = aria2.get_downloads()
        aria2.remove(downloads, force=True, files=True, clean=True)
        print("Successfully initialized Aria API...")
        # os.system("pkill -9 rclone")
        # os.system("rclone mount \"Google Drive Harvest:\" GDrive &")

    def clearQueues(self):
        ''' Function to clear all the downloads '''
        aria2.remove_all(force=True)
    # list downloads

    async def getEtaDownloads(self):
        """
        Function to get the list of ETAs for the downloads
        """
        return [download.eta_string() for download in aria2.get_downloads()]

    async def getNames(self):
        ''' Function to get the Names of the ongoing downloads '''
        return [idown.name for idown in aria2.get_downloads()]

    async def AddDownload(self, link: str):
        ''' Function to add the specific URL to the download lists '''
        self.link = link
        aria2.add(self.link)

    async def AddTorrent(self, link):
        ''' Function to add torrent URIs to the Aria queue'''
        self.link = link
        aria2.add_magnet(self.link)

    #
    async def getDownloadsOnGid(self, gid: str):
        ''' Return the class entity of the download object using GID '''
        self.gid = gid
        return aria2.get_download(self.gid)

    async def getLiveDownloads(self, gidList: list) -> list:
        ''' [D] Returns a list of the live downloads'''
        self.gidList = gidList
        return aria2.get_downloads(gidList)

    # Returns download speed of the ongoing downloads
    async def getSpeed(self, gid: str) -> str:
        ''' Returns download speed of the ongoing downloads'''
        self.gid = gid
        return aria2.get_download(gid).download_speed_string(human_readable=True)

    async def getProgress(self, gid: str) -> str:
        ''' Returns the progress of the ongoing downloads with percentage '''
        self.gid = gid
        return aria2.get_download(gid).progress_string(2)

    async def getSize(self, gid: str):
        ''' Returns the size of the particular download when GID is passed'''
        self.gid = gid
        return aria2.get_download(gid).total_length_string(human_readable=True)

    # cancel Download based on GID
    async def cancelDownload(self, gid: str) -> bool:
        ''' Delete downloads based on GID '''
        self.gid = gid
        p = aria2.get_download(gid)
        aria2.remove([p], force=True, files=True)

    # returns name based on GID
    async def getNameBasedOnGID(self, gid: str):
        ''' returns the name of the download based on GID'''
        self.gid = gid
        try:
            p = aria2.get_download(gid)
            return p.name
        except:
            print(await self.listOfGids())

    # returns a list of downloads with their GID values
    async def listOfGids(self) -> list:
        ''' Returns the list of the downlaods with its GID Values '''
        l = []
        for idown in aria2.get_downloads():
            l.append(idown.gid)
        return l

    async def cleanUp(self) -> bool:
        ''' Purges up, i.e, Cleans up zombies'''
        aria2.purge()

    async def completedDownloads(self) -> set:
        ''' Returns out the list of completed download names '''
        p = await self.getNames()
        await self.cleanUp()
        q = await self.getNames()
        return list(set(p) - set(q))


    async def getStatusOfAllDownloads(self) -> list:
        ''' Returns a json datatype consisting the information of live downloads '''
        gid_list = self.listOfGids()
        dataset = []
        for i in await gid_list:
            k = aria2.get_download(i)
            data = {
                'Name': k.name,
                'Speed': k.download_speed_string(human_readable=True),
                'GID': k.gid,
                'Status': "Downloading...",
                'Progress': k.progress_string(2),
                'totalSize': k.total_length_string(human_readable=True),
                'TimeRemaining': k.eta_string()
            }
            dataset.append(data)
        return dataset
