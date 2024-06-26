import discord
from memorization_maker.inc.pakege import Get,Genre,Share,User

class ChoicePlayMode(discord.ui.View):
    def __init__(self, sharecode:int):
        self.user = User()
        self.sharecode = sharecode
        super().__init__()

    async def init_set(self):
        await self.user.add_user_data_init()
        await self.user.add_user_data(self.sharecode)        

    @discord.ui.button(label="順番出題", style=discord.ButtonStyle.primary)
    async def choice_order(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.init_set()
        await MemorizationPlay(interaction,self.sharecode,0).main_start()
        
    @discord.ui.button(label="ランダム出題", style=discord.ButtonStyle.primary)
    async def choice_random(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.init_set()
        await MemorizationPlay(interaction,self.sharecode,1).main_start()
    
    @discord.ui.button(label="前回のミス問題出題", style=discord.ButtonStyle.primary)
    async def choice_mistake(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.init_set()
        await MemorizationPlay(interaction,self.sharecode,2).main_start()
    

class MemorizationPlay:
    def __init__(self, interaction:discord.Interaction,sharecode:int,playmode:int,question_list:list,counts:int=0):
        self.interaction = interaction
        self.sharecode = sharecode
        self.playmode = playmode
        self.counts = counts
        self.user = User()
        self.gets = Get()
    
    async def main_start(self):
        question_list = []
        questions = await self.gets.get_misson(self.sharecode)
        if self.playmode == 0:
            question_list = questions["questions"]
        elif self.playmode == 1:
            questions_user = await self.user.get_mission(str(self.interaction.user.id),self.sharecode)
            question_number_list = questions_user["questions_number_list"]
            #ランダム出題
            #questions["questions"]の順番がquestion_number_listに入っている
            for num in question_number_list:
                question_list.append(questions["questions"][num])
        elif self.playmode == 2:
            questions_user = await self.user.get_mission(str(self.interaction.user.id),self.sharecode)
            question_number_list = questions_user["miss_numbers"]
            #前回のミス問題出題
            for num in question_number_list:
                question_list.append(questions["questions"][num])
            
                        
        