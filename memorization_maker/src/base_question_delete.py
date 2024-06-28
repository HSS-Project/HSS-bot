import memorization_maker.src.Read_and_Write as Read_and_Write
from memorization_maker.src.share import Share
from memorization_maker.src.genre import Genre
class Delete:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.share = Share()
        self.base_data:dict = {"memorization":{}}
        
    
    async def delete_title(self,_id:str,title:str):
        user_id = str(_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(user_id,title)
        del self.base_data["memorization"][sharecode]
        await self.rw.write_base(self.base_data)
        return False
    
    async def delete_misson_select(self,_id:str,title:str,select_len_number:int):
        user_id = str(_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(user_id,title)
        genre = Genre()
        genre_title = await genre.search_genre(user_id,sharecode)
        await genre.remove_genre(user_id,genre_title,sharecode)
        del self.base_data["memorization"][sharecode]["questions"][select_len_number]
        await self.rw.write_base(self.base_data)
        return False