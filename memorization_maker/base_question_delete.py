import memorization_maker.Read_and_Write as Read_and_Write
from memorization_maker.share import Share
from memorization_maker.genre import Genre
from memorization_maker.owner_manager import OwnerManager

class Delete:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.share = Share()
        self.genre = Genre()
        self.ower = OwnerManager()
        self.base_data:dict = {"memorization":{}}
        self.user_data:dict = {"genre":{}}

    
    async def all_delete_title(self,_id:str,title:str):
        user_id = str(_id)
        if not await self.ower.owner_check(user_id,title):
            return False
        self.base_data:dict = await self.rw.load_base()
        self.user_data:dict = await self.rw.load_user()
        sharecode = await self.share.get_sharecode(title)
        del self.base_data["memorization"][sharecode]
        #ジャンルから削除
        for num_id in self.user_data["genre"].keys():
            for genre in self.user_data["genre"][num_id].keys():
                if int(sharecode) in self.user_data["genre"][num_id][genre]["sharecodes"]:
                    self.user_data["genre"][num_id][genre]["sharecodes"].remove(int(sharecode))
        await self.rw.write_base(self.base_data)
        await self.rw.write_user(self.user_data)
        return True
    
    async def delete_misson_select(self,title:str,select_len_number:int):
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        question_list:list = self.base_data["memorization"][sharecode]["questions"]
        question_list.pop(select_len_number)
        await self.rw.write_base(self.base_data)
        return True