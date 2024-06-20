import Read_and_Write
import owner_manager
import share

class Genre:
    def __init__(self):
        self.rw = Read_and_Write.Read_and_Write()
        self.owner = owner_manager.OwnerManager()
        self.share = share.Share()
        
        self.base_data:dict = {"memorization":{}}
        self.user_data:dict = {}
        
    async def make_genre(self,user_id:str,genre_title):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if not await self.owner.owner_check(num_id,genre_title):return False
        def_number = await self.share.make_sharecode()
        self.user_data["genre"].setdefault(num_id,{"defult":{"sharecodes":[],"share":def_number}})
        sharecode = await self.share.make_sharecode()
        self.user_data["genre"][num_id].setdefault(genre_title,{genre_title:{"sharecodes":[],"share":sharecode}})
        await self.rw.write_user(self.user_data)
    
    async def delete_genre(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if not await self.owner.owner_check(num_id,genre_title):return False
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        del self.user_data["genre"][num_id][genre_title]
        await self.rw.write_user(self.user_data)
        
    async def add_genre(self,user_id:str,genre_title:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if not await self.owner.owner_check(num_id,genre_title):return False
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        self.user_data["genre"][num_id][genre_title]["sharecodes"].append(sharecode)
        await self.rw.write_user(self.user_data)
    
    async def remove_genre(self,user_id:str,genre_title:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if not await self.owner.owner_check(num_id,genre_title):return False
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        self.user_data["genre"][num_id][genre_title]["sharecodes"].remove(sharecode)
        await self.rw.write_user(self.user_data)
    
    async def move_genre(self,user_id:str,genre_title:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if not await self.owner.owner_check(num_id,genre_title):return False
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        self.user_data["genre"][num_id][genre_title]["sharecodes"].remove(sharecode)
        self.user_data["genre"][num_id]["defult"]["sharecodes"].append(sharecode)
        await self.rw.write_user(self.user_data)
    
    async def search_genre(self,user_id:str,sharecode:int):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        for genre in self.user_data["genre"][num_id].keys():
            if sharecode in self.user_data["genre"][num_id][genre]["sharecodes"]:
                return genre
        return False
    
    async def get_genres_name(self,user_id:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        gnres_list = []
        for genre in self.user_data["genre"][num_id].keys():
            gnres_list.append(genre)
        return gnres_list
    
    async def get_genres_list_sharecodes(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        return self.user_data["genre"][num_id][genre_title]["sharecodes"]
    
    async def get_genres_sharecode(self,user_id:str,genre_title:str):
        num_id = str(user_id)
        self.user_data:dict = await self.rw.load_user()
        if genre_title not in self.user_data["genre"][num_id].keys():return False
        return self.user_data["genre"][num_id][genre_title]["share"]