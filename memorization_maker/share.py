import memorization_maker.Read_and_Write as Read_and_Write
import random

class Share:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.base_data:dict = {"memorization":{}}
        self.user_data:dict = {}

    async def make_sharecode(self,modes:int = 0):
        #全てのtitleのsharecodeと被っていないことを確認する　被っていたら再生成
        self.base_data:dict = await self.rw.load_base()
        self.user_data:dict = await self.rw.load_user()
        if modes == 0:
            while True:
                sharecode = random.randint(100000,999999)
                for sharecodes in self.base_data["memorization"].keys():
                    if sharecode == sharecodes:continue
                return sharecode
        elif modes == 1:
            while True:
                sharecode = random.randint(1000,9999)
                for numid in self.user_data["genre"].keys():
                    for genre in self.user_data["genre"][numid].keys():
                        for sharecodes in self.user_data["genre"][numid][genre]["sharecodes"]:
                            if sharecode == sharecodes:continue
                return sharecode
        
    async def get_sharecode(self,title:str):
        self.base_data:dict = await self.rw.load_base()
        for sharecode in self.base_data["memorization"]:
            if self.base_data["memorization"][sharecode]["title"] == title:
                return sharecode
        return False

    async def get_sharedata(self,_sharecode:str):
        self.base_data:dict = await self.rw.load_base()
        sharecode = str(_sharecode)
        return self.base_data["memorization"][sharecode]
    
    async def get_genre_sharecode(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        return self.user_data["genre"][num_id][genre_title]["share"]