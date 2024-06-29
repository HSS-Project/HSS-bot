import memorization_maker.src.Read_and_Write as Read_and_Write
import memorization_maker.src.share as share

class Get:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.share = share.Share()
        self.base_data:dict = {"memorization":{}}
       
    async def get_titles(self,user_id:str):
        num_id = str(user_id)
        self.base_data:dict = await self.rw.load_base()
        #全てのタイトルのownerにuser_idが含まれているlistを返す
        lists = []
        for share in self.base_data["memorization"].keys():
            if num_id in self.base_data["memorization"][share]["onwer"]:
                lists.append(self.base_data["memorization"][share]["title"])                
        return lists

    async def get_misson_select(self,title:str,select_len_number:int):
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        return self.base_data["memorization"][sharecode]["questions"][select_len_number]

    async def get_misson(self,title:str):
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        return self.base_data["memorization"][sharecode]
    
    async def check_answer(self,title:str,select_len_number:int,answer:str,text_question_number:int = None):
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        data = self.base_data["memorization"][sharecode]["questions"][select_len_number]
        mode = data["mode"]
        if mode == 0:
            return data["answer"] == answer
        elif mode == 1:
            return data[int(data["answer"])-1] == answer
        elif mode == 2:
            return answer == data["answer"][text_question_number]
        
    async def len_misson(self,title:str):
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(title)
        return len(self.base_data["memorization"][sharecode]["questions"])