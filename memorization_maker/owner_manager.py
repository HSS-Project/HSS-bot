import memorization_maker.Read_and_Write as Read_and_Write
import memorization_maker.share as share

class OwnerManager:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.share = share.Share()
        self.base_data:dict = {"memorization":{}}

    async def owner_check(self, user_id:str,title:str):
        num_id = str(user_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        if title in self.base_data["memorization"].keys():
            if num_id in self.base_data["memorization"][sharecode]["onwer"]:
                return True
            else:
                return False
        else:
            return False
        
    async def owner_add(self,user_id:str,title:str,_target_id:str):
        num_id = str(user_id)
        if await self.owner_check(num_id,title):return False
        target_id = str(_target_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        self.base_data["memorization"][sharecode]["onwer"].append(target_id)
        await self.rw.write_base(self.base_data)
        return True
    
    async def owmer_remove(self,user_id:str,title:str,_target_id:str):
        num_id = str(user_id)
        if await self.owner_check(num_id,title):return False
        target_id = str(_target_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        self.base_data["memorization"][sharecode]["onwer"].remove(target_id)
        await self.rw.write_base(self.base_data)
        return True
    
    async def owner_list(self,user_id:str,title:str):
        num_id = str(user_id)
        if await self.owner_check(num_id,title):return False
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        return self.base_data["memorization"][sharecode]["onwer"]