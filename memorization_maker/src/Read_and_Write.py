import json

class Read_and_Write:
    def __init__(self):
        self.basefile = "memorization_base_v2.json"
        self.userfile = "memorization_user_v2.json"
        

    async def load_data(self,filename):
        with open(filename, "r") as f:
            return json.load(f)
        
    async def write_data(self,filename,data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
            
    
    async def load_base(self) -> dict:
        data = await self.load_data(self.basefile)
        return data
    
    async def load_user(self) -> dict:
        data= await self.load_data(self.userfile)
        return data
    
    async def write_base(self,data:dict):
        await self.write_data(self.basefile,data)
        
    async def write_user(self,data:dict):
        await self.write_data(self.userfile, data)