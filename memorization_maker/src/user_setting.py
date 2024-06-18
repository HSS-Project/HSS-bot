import owner_manager
import random
import Read_and_Write
import share

class User:
    def __init__(self):
        self.owner = owner_manager.OwnerManager()
        self.rw = Read_and_Write.Read_and_Write()
        self.share = share.Share()
        self.base_data:dict = {"memorization":{}}
        self.user_data = {}
        # self.user_data:dict = {
        #     "Userdata":{
        #         "ID":{
        #             "sharecode":{
        #                 "title":"title",
        #                 "randam":"bool",
        #                 "questions_number_list":"int",
        #                 "miss_number":"list",
        #                 "try_number":"int",
        #                 "score":"int"
        #             }
        #         }
        #     }
        # }
    
    async def add_user_data_init(self,user_id):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        self.user_data.setdefault(num_id,{})
        await self.rw.write_user(self.user_data)
        return True
    
    async def add_user_data(self,user_id:str,_sharecode:str):
        num_id = str(user_id)
        sharecode = str(_sharecode)
        self.user_data = await self.rw.load_user()
        missondata = await self.share.get_sharedata(sharecode)
        #listを1 2 3 ・・・と番号を振る
        questions_number_list = [i for i in range(len(missondata["questions"]))]
        self.user_data[num_id].setdefault(sharecode,{
            "title":missondata["title"],
            "randam":False,
            "questions_number_list":questions_number_list,
            "miss_numbers":[],
            "try_number":0,
            "score":0
        })
        await self.rw.write_user(self.user_data)
        return True
    
    async def randam_Trerue(self,user_id,sharecode):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        self.user_data[num_id][sharecode]["randam"] = True
        await self.rw.write_user(self.user_data)
        return True
    
    async def randam_False(self,user_id,sharecode):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        self.user_data[num_id][sharecode]["randam"] = False
        await self.rw.write_user(self.user_data)
        return True

    async def get_user_data(self,user_id):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        return self.user_data[num_id]
    
    async def get_missons_title(self,user_id):
        num_id = str(user_id)
        self.user_data = await self.rw.load_user()
        titles = []
        #ユーザーが持っているsharecodeの中にあるtitleを取得
        for sharecode in self.user_data[num_id].keys():
            titles.append(self.user_data[num_id][sharecode]["title"])
        return titles