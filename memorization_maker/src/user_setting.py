import random
import memorization_maker.src.Read_and_Write as Read_and_Write
import memorization_maker.src.share as share
#これ全部ミスってるかも
class User:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.share = share.Share()
        self.base_data:dict = {"memorization":{}}
        self.user_data:dict = {"Userdata":{}}
    
    async def add_user_data_init(self,user_id):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        userdata:dict = self.user_data["Userdata"]
        userdata.setdefault(num_id,{})
        await self.rw.write_user(self.user_data)
        return True
    
    async def add_user_data(self,user_id:str,_sharecode:str):
        num_id = str(user_id)
        sharecode = str(_sharecode)
        self.user_data = await self.rw.load_user()
        missondata = await self.share.get_sharedata(sharecode)
        #listを1 2 3 ・・・と番号を振る
        questions_number_list:list = [i for i in range(len(missondata["questions"]))]
        #listをシャッフル
        random.shuffle(questions_number_list)
        self.user_data["Userdata"][num_id].setdefault(sharecode,{
            "title":missondata["title"],
            "questions_number_list":questions_number_list,
            "miss_numbers":[],
            "try_number":0,
            "score":0
        })
        await self.rw.write_user(self.user_data)
        return True
    
    async def get_mission(self,user_id:str,sharecode:str):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        return self.user_data["Userdata"][num_id][sharecode]
    
    async def user_data_shuffle(self,user_id:str,sharecode:str):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        questions_number_list:list = self.user_data["Userdata"][num_id][sharecode]["questions_number_list"]
        random.shuffle(questions_number_list)
        self.user_data["Userdata"][num_id][sharecode]["questions_number_list"] = questions_number_list
        await self.rw.write_user(self.user_data)
        return True
    
    async def get_mission_number(self,user_id:str,sharecode:str):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        return self.user_data["Userdata"][num_id][sharecode]["questions_number_list"]
    
    async def user_data_miss(self,user_id:str,sharecode:str,miss_number_list:list):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        self.user_data["Userdata"][num_id][sharecode]["miss_numbers"] = miss_number_list
        await self.rw.write_user(self.user_data)
        return True
    
    async def user_data_try(self,user_id:str,sharecode:str):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        self.user_data["Userdata"][num_id][sharecode]["try_number"] += 1
        await self.rw.write_user(self.user_data)
        return True

    async def user_data_score(self,user_id:str,sharecode:str, score:int):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        self.user_data["Userdata"][num_id][sharecode]["score"] = score
        await self.rw.write_user(self.user_data)
        return True
    
    async def get_user_data(self,user_id):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        return self.user_data["Userdata"][num_id]
    
    async def get_missons_title(self,user_id):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        titles = []
        #ユーザーが持っているsharecodeの中にあるtitleを取得
        for sharecode in self.user_data["Userdata"][num_id].keys():
            titles.append(self.user_data["Userdata"][num_id][sharecode]["title"])
        return titles