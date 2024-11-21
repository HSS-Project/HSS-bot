import memorization_maker.Read_and_Write as Read_and_Write
from memorization_maker.share import Share
from memorization_maker.genre import Genre

class Delete:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.share = Share()
        self.base_data:dict = {"memorization":{}}

    
    async def delete_title(self,_id:str,title:str):
        user_id = str(_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        genre = Genre()
        genre_title = await genre.search_genre(user_id,sharecode)
        await genre.remove_genre(user_id,genre_title,sharecode)
        del self.base_data["memorization"][sharecode]
        await self.rw.write_base(self.base_data)
        return True
    
    async def delete_misson_select(self,title:str,select_len_number:int):
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        question_list:list = self.base_data["memorization"][sharecode]["questions"]
        question_list.pop(select_len_number)
        await self.rw.write_base(self.base_data)
        return True