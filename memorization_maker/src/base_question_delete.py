import Read_and_Write
import owner_manager
import share

class Delete:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.owner = owner_manager.OwnerManager()
        self.share = share.Share()
        self.base_data:dict = {"memorization":{}}
        
    
    async def delete_title(self,_id:str,title:str):
        user_id = str(_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(user_id,title)
        if not await self.owner.ower_check(user_id,title):return False
        del self.base_data["memorization"][sharecode]
        await self.rw.write_base(self.base_data)
        return False
    
    async def delete_misson_select(self,_id:str,title:str,select_len_number:int):
        user_id = str(_id)
        self.base_data:dict = await self.rw.load_base()
        if not await self.owner.ower_check(user_id,title):return False
        sharecode = await self.share.get_sharecode(user_id,title)
        del self.base_data["memorization"][sharecode]["questions"][select_len_number]
        await self.rw.write_base(self.base_data)
        return False