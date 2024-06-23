import Read_and_Write
import owner_manager
import random
import share
class Edit:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.owner = owner_manager.OwnerManager()
        self.share = share.Share()
        self.base_data:dict = {"memorization":{}}
        
    async def edit_misson(self,_id:str,title:str,quetion:str,answer:str,select_len_number:int):
        user_id = str(_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(user_id,title)
        if not await self.owner.owner_check(user_id,title):return False
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["question"] = quetion
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["answer"] = answer
        await self.rw.write_base(self.base_data)
        return False
    
    async def edit_misson_select(self,_id:str,title:str,quetion:str,answer:str,select:list,select_len_number:int):
        user_id = str(_id)
        self.base_data:dict = await self.rw.load_base()
        if not await self.owner.owner_check(user_id,title):return False
        sharecode = await self.share.get_sharecode(user_id,title)        
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["question"] = quetion
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["answer"] = select.index(answer)+1
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["select"] = select
        await self.rw.write_base(self.base_data)
        return False