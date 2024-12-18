import memorization_maker.Read_and_Write as Read_and_Write
import memorization_maker.share as share

class Genre:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.share = share.Share()
        self.base_data:dict = {"memorization":{}}
        self.user_data:dict = {}

    async def make_genre(self,user_id:str,_genre_title):
        num_id = str(user_id)
        genre_title = str(_genre_title)
        self.user_data:dict = await self.rw.load_user()
        if "genre" not in self.user_data:
            self.user_data["genre"] = {}
        def_number = await self.share.make_sharecode(1)
        self.user_data["genre"].setdefault(num_id,{"default":{"sharecodes":[],"share":def_number}})
        voca_number = await self.share.make_sharecode(1)
        self.user_data["genre"][num_id].setdefault("vocabulary",{"sharecodes":[],"share":voca_number})
        sharecode = await self.share.make_sharecode(1)
        self.user_data["genre"][num_id].setdefault(genre_title,{"sharecodes":[],"share":sharecode})
        await self.rw.write_user(self.user_data)
        return True
    
    async def delete_genre(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():await self.make_genre(user_id,"default")
        if genre_title == "defult":await self.make_genre(user_id,"default")
        #デフォルトに移動 もし100個以上ある場合はエラー
        for sharecode in self.user_data["genre"][num_id][genre_title]["sharecodes"]:
            if len(self.user_data["genre"][num_id]["default"]["sharecodes"]) >= 100:return False
            self.user_data["genre"][num_id]["default"]["sharecodes"].append(sharecode)
        del self.user_data["genre"][num_id][genre_title]
        await self.rw.write_user(self.user_data)
        return True
        
    async def add_genre(self,user_id:str,genre_title:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if num_id not in self.user_data.keys():await self.make_genre(user_id,"default")
        if genre_title not in self.user_data["genre"][num_id].keys():await self.make_genre(user_id,genre_title)
        if sharecode in self.user_data["genre"][num_id][genre_title]["sharecodes"]:return False
        genre_title_list = await self.get_genres_name(user_id)
        if len(genre_title_list) >= 100:return False
        for genre in genre_title_list:
            sharecode_list = await self.get_genres_list_sharecodes(user_id,genre)
            if sharecode in sharecode_list:return False
        if len(str(sharecode)) != 6:return False
        self.user_data["genre"][num_id][genre_title]["sharecodes"].append(sharecode)
        await self.rw.write_user(self.user_data)
        return True
    
    async def remove_genre(self,user_id:str,genre_title:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():await self.make_genre(user_id,"default")
        self.user_data["genre"][num_id][genre_title]["sharecodes"].remove(int(sharecode))
        await self.rw.write_user(self.user_data)
        return True
    
    async def move_genre(self,user_id:str,genre_title:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():await self.make_genre(user_id,"default")
        _sharecode = int(sharecode)
        before_genre = await self.search_genre(user_id,_sharecode)
        if not before_genre:return False
        self.user_data["genre"][num_id][before_genre]["sharecodes"].remove(_sharecode)
        self.user_data["genre"][num_id][genre_title]["sharecodes"].append(_sharecode)
        await self.rw.write_user(self.user_data)
        return True
    
    async def search_genre(self,user_id:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if num_id not in self.user_data.keys():
            await self.make_genre(user_id,"default")
            await self.rw.write_user(self.user_data)
        for genre in self.user_data["genre"][num_id].keys():
            for __sharecode in self.user_data["genre"][num_id][genre]["sharecodes"]:
                if sharecode == __sharecode:
                    return genre
        return False
    
    async def get_genres_name(self,user_id:str) -> list:
        num_id = str(user_id)
        self.user_data: dict = await self.rw.load_user()
        if num_id not in self.user_data.keys():await self.make_genre(user_id,"default")
        gnres_list = []
        for genre in self.user_data["genre"][num_id].keys():
            gnres_list.append(genre)
        return gnres_list
    
    async def get_genres_list_sharecodes(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():await self.make_genre(user_id,"default")
        return self.user_data["genre"][num_id][genre_title]["sharecodes"]
    
    async def genres_in_titles(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():await self.make_genre(user_id,"default")
        sharecode = self.user_data["genre"][num_id][genre_title]["sharecodes"]
        titles = []
        for sharecode in sharecode:
            datas = await self.share.get_sharedata(sharecode)
            title = datas["title"]
            titles.append(title)
        return titles
    
    async def get_genres_sharecode(self,genre_sharecode:int):
        self.user_data:dict = await self.rw.load_user()
        for num_id in self.user_data["genre"].keys():
            for genrename in self.user_data["genre"][num_id].keys():
                if genre_sharecode == self.user_data["genre"][num_id][genrename]["share"]:
                    return self.user_data["genre"][num_id][genrename],num_id,genrename
        return False,False,False
    
    async def get_genres_sharecode_title(self,userid:str,genre_title:str):
        self.user_data:dict = await self.rw.load_user()
        num_id = str(userid)
        genre_title = str(genre_title)
        for genrename in self.user_data["genre"][num_id].keys():
            if genre_title == genrename:
                return self.user_data["genre"][num_id][genrename]["share"]
        return False
    
    async def share_genere_set(self,user_id:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        genre_title,number,name = await self.get_genres_sharecode(sharecode)
        if not genre_title or not number or not name:return False
        if user_id == number:return False
        make_name = f"{name}_share_{sharecode}_{number}"
        await self.make_genre(num_id,make_name)
        for sharecode in genre_title["sharecodes"]:
            await self.add_genre(num_id,make_name,sharecode)      
        return True
    
    async def len_genre(self,user_id:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        return len(self.user_data["genre"][num_id].keys())