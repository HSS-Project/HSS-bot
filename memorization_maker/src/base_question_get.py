import Read_and_Write
import owner_manager
import share

class Get:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.owner = owner_manager.OwnerManager()
        self.share = share.Share()
        self.base_data:dict = {"memorization":{}}
                               
    async def get_titles(self,user_id:str):
        num_id = str(user_id)
        self.base_data:dict = await self.rw.load_base()
        #全てのタイトルのownerにuser_idが含まれているlistを返す
        lists = []
        for title in self.base_data["memorization"].keys():
            if num_id in self.base_data["memorization"][title]["onwer"]:
                lists.append(title)        
                
        return lists

    async def get_misson_select(self,user_id:str,title:str,select_len_number:int):
        num_id = str(user_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(user_id,title)
        if not await self.owner.owner_check(num_id,title):return False
        return self.base_data["memorization"][sharecode]["questions"][select_len_number]

    async def get_misson(self,user_id:str,title:str):
        num_id = str(user_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(user_id,title)
        if not await self.owner.owner_check(num_id,title):return False
        return self.base_data["memorization"][sharecode]
    
    async def check_answer(self,user_id:str,title:str,select_len_number:int,answer:str,text_question_number:int = None):
        num_id = str(user_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(user_id,title)
        if not await self.owner.owner_check(num_id,title):return False
        data = self.base_data["memorization"][sharecode]["questions"][select_len_number]
        mode = data["mode"]
        if mode == 0:
            return data["answer"] == answer
        elif mode == 1:
            return data[int(data["answer"])-1] == answer
        elif mode == 2:
            return answer == data["answer"][text_question_number]
        
    async def len_misson(self,user_id:str,title:str):
        num_id = str(user_id)
        self.base_data:dict = await self.rw.load_base()
        sharecode = await self.share.get_sharecode(user_id,title)
        if not await self.owner.owner_check(num_id,title):return False
        return len(self.base_data["memorization"][sharecode]["questions"])