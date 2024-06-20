import discord 
from discord import ui
from memorization_maker.inc.pakege import Add, Get, OwnerManager, Edit, Delete, Share, Genre

class SelectMission_1(discord.ui.Select):
    def __init__(self,title,missions: list,mode):
        self.title = title
        self.mode = mode
        options = []
        self.missions = missions
        for num,mission in enumerate(missions):
            options.append(discord.SelectOption(label=mission, value=str(num)))
        super().__init__(placeholder="問題を選択してください", options=options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectMiView(interaction,self.title,int(self.values[0]),self.mode).select_response()
            
class SelectMission_2(discord.ui.Select):
    def __init__(self,title,missions: list,mode):
        self.title = title
        self.mode = mode
        options = []
        self.missions = missions
        for num,mission in enumerate(missions):
            options.append(discord.SelectOption(label=mission, value=str(num)))
        super().__init__(placeholder="問題を選択してください", options=options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectMiView(interaction,self.title,int(self.values[0]),self.mode).select_response()
    
class SelectMission_3(discord.ui.Select):
    def __init__(self,title,missions: list,mode):
        self.title = title
        self.mode = mode
        options = []
        self.missions = missions
        for num,mission in enumerate(missions):
            options.append(discord.SelectOption(label=mission, value=str(num)))
        super().__init__(placeholder="問題を選択してください", options=options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectMiView(interaction,self.title,int(self.values[0]),self.mode).select_response()
    
class SelectMission_4(discord.ui.Select):
    def __init__(self,title,missions: list,mode):
        self.title = title
        options = []
        self.mode = mode
        self.missions = missions
        for num,mission in enumerate(missions):
            options.append(discord.SelectOption(label=mission, value=str(num)))
        super().__init__(placeholder="問題を選択してください", options=options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectMiView(interaction,self.title,int(self.values[0]),self.mode).select_response()
    
class SelectMissionView(discord.ui.View):
    def __init__(self,title,missions:list,mode):
        super().__init__()
        self.title = title
        missions_len = len(missions)
        self.missions = missions
        self.mode = mode
        #mode 0:問題を選択して削除
        self.options_1 = []
        self.options_2 = []
        self.options_3 = []
        self.options_4 = []
        self.options_list = [self.options_1, self.options_2, self.options_3, self.options_4]
        for j in range(4):
            start = j * 25
            end = start + 25
            if start < missions_len:
                for i in range(start, end):
                    if i >= missions_len:
                        break
                    self.options_list[j].append(discord.SelectOption(label=missions[i], value=str(i)))
                    
        self.add_item(SelectMission_1(self.title,self.options_1,self.mode))
        if missions_len > 25:
            self.add_item(SelectMission_2(self.title,self.options_2,self.mode))
        if missions_len > 50:
            self.add_item(SelectMission_3(self.title,self.options_3,self.mode))
        if missions_len > 75:
            self.add_item(SelectMission_4(self.title,self.options_4,self.mode))
                
class SelectMiView:
    def __init__(self,intracton:discord.Interaction,title,selectnumber,mode):
        self.intracton = intracton
        self.title = title
        self.selectnumber = selectnumber
        self.mode = mode
        
    async def select_response(self):
        if self.mode == 0:
            await Delete().delete_misson_select(str(self.intracton.user.id),self.title,self.selectnumber)