import memorization_maker.src.Read_and_Write as Read_and_Write
import memorization_maker.src.share as share
import memorization_maker.src.base_question_add as base_question_add
class Edit:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.share = share.Share()
        self.textre = base_question_add.Add()
        self.base_data:dict = {"memorization":{}}
        
    async def edit_misson(self,title:str,quetion:str,answer:str,select_len_number:int):
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["question"] = quetion
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["answer"] = answer
        await self.rw.write_base(self.base_data)
        return False
    
    async def edit_misson_select(self,title:str,quetion:str,answer:str,select:list,select_len_number:int):
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)        
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["question"] = quetion
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["answer"] = select.index(answer)+1
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["select"] = select
        await self.rw.write_base(self.base_data)
        return False
    
    async def edit_misson_text(self,title:str,raw_text,select_len_number:int):
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)        
        text, answers = await self.textre.replace_parentheses(raw_text)
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["question"] = text
        self.base_data["memorization"][sharecode]["questions"][select_len_number]["answer"] = answers
        await self.rw.write_base(self.base_data)
        return False