import memorization_maker.src.Read_and_Write as Read_and_Write
import memorization_maker.src.share as share

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
        sharecode = await self.share.make_sharecode(1)
        self.user_data["genre"][num_id].setdefault(genre_title,{"sharecodes":[],"share":sharecode})
        await self.rw.write_user(self.user_data)
        return True
    
    async def delete_genre(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        if genre_title == "defult":return False
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
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        self.user_data["genre"][num_id][genre_title]["sharecodes"].append(sharecode)
        await self.rw.write_user(self.user_data)
        return True
    
    async def remove_genre(self,user_id:str,genre_title:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        self.user_data["genre"][num_id][genre_title]["sharecodes"].remove(sharecode)
        await self.rw.write_user(self.user_data)
        return True
    
    async def move_genre(self,user_id:str,genre_title:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():return False
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
        for genre in self.user_data["genre"][num_id].keys():
            if sharecode in self.user_data["genre"][num_id][genre]["sharecodes"]:
                return genre
        return False
    
    async def get_genres_name(self,user_id:str) -> list:
        num_id = str(user_id)
        self.user_data: dict = await self.rw.load_user()
        gnres_list = []
        for genre in self.user_data["genre"][num_id].keys():
            gnres_list.append(genre)
        return gnres_list
    
    async def get_genres_list_sharecodes(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        return self.user_data["genre"][num_id][genre_title]["sharecodes"]
    
    async def get_genres_to_sharecode_list(self,sharecode:int):
        self.user_data:dict = await self.rw.load_user()
        for user_id in self.user_data.keys():
            for genre in self.user_data[user_id]["genre"].keys():
                if sharecode in self.user_data[user_id]["genre"][genre]["sharecodes"]:
                    return genre
        return False
    
    async def get_genres_sharecode(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        return self.user_data["genre"][num_id][genre_title]["share"]
    
    async def genres_in_titles(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        sharecode = self.user_data["genre"][num_id][genre_title]["sharecodes"]
        titles = []
        for sharecode in sharecode:
            datas = await self.share.get_sharedata(sharecode)
            title = datas["title"]
            titles.append(title)
        return titles
    
    async def share_genere_set(self,user_id:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        #sharecodeからgenrutitleを取得
        genre_title = await self.search_genre(user_id,sharecode)
        if not genre_title:return False
        self.user_data["genre"][num_id][genre_title] = await self.get_genres_to_sharecode_list(sharecode)
        return True
    
    async def len_genre(self,user_id:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        return len(self.user_data["genre"][num_id].keys())