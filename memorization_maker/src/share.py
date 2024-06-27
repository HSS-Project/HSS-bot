import Read_and_Write
import owner_manager
import random

class Share:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.owner = owner_manager.OwnerManager()
        self.base_data:dict = {"memorization":{}}
        self.user_data:dict = {}

    async def make_sharecode(self,modes:int = 0):
        #全てのtitleのsharecodeと被っていないことを確認する　被っていたら再生成
        self.base_data:dict = await self.rw.load_base()
        self.user_data:dict = await self.rw.load_user()
        if modes == 0:
            while True:
                sharecode = random.randint(000000,999999)
                for sharecodes in self.base_data["memorization"]:
                    if sharecode == self.base_data["memorization"][sharecodes]["sharecode"]:
                        continue
                return sharecode
        elif modes == 1:
            while True:
                sharecode = random.randint(0000,9999)
                for sharecodes in self.user_data["genre"]:
                    if sharecode == self.user_data["genre"][sharecodes]["share"]:
                        continue
                return sharecode
        
    async def get_sharecode(self,user_id:str,title:str):
        self.base_data:dict = await self.rw.load_base()
        if not await self.owner.owner_check(user_id,title):return False
        for sharecode in self.base_data["memorization"]:
            if self.base_data["memorization"][sharecode]["title"] == title:
                return sharecode
        return False

    async def get_sharedata(self,sharecode:int):
        self.base_data:dict = await self.rw.load_base()
        return self.base_data["memorization"][sharecode]
    
    async def get_genre_sharecode(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if not await self.owner.owner_check(num_id,genre_title):return False
        return self.user_data["genre"][num_id][genre_title]["share"]