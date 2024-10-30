import memorization_maker.src.Read_and_Write as Read_and_Write
import memorization_maker.src.share as share
import memorization_maker.src.genre as genre

class Vocabulary:
    def __init__(self) -> None:
        self.rw = Read_and_Write.Read_and_Write()
        self.share = share.Share()
        self.genre = genre.Genre()

    async def make_vocabulary(self,user_id:str,title:str,start_number:int,end_unmber:int):
        num_id = str(user_id)
        self.base_data:dict = await self.rw.load_base()
        shrecode = await self.share.make_sharecode(2)
        self.base_data["vocabularies"].setdefault(shrecode,{"title":title,"start":start_number,"end":end_unmber})
        await self.genre.make_genre(num_id,"vocabulary")
        await self.genre.add_genre(num_id,"vocabulary",shrecode)
        await self.rw.write_base(self.base_data)
        return shrecode

    async def get_vocabulary(self,_sharecode:int):
        self.base_data:dict = await self.rw.load_base()
        sharecode = str(_sharecode)
        return self.base_data["vocabularies"][sharecode]
    
    async def del_vocabulary(self,_sharecode:int):
        self.base_data:dict = await self.rw.load_base()
        sharecode = str(_sharecode)
        del self.base_data["vocabularies"][sharecode]
        await self.rw.write_base(self.base_data)
        return True
    
    async def edit_vocabulary(self,_sharecode:int,start_number:int,end_unmber:int):
        self.base_data:dict = await self.rw.load_base()
        sharecode = str(_sharecode)
        self.base_data["vocabularies"][sharecode]["start"] = start_number
        self.base_data["vocabularies"][sharecode]["end"] = end_unmber
        await self.rw.write_base(self.base_data)
        return True        