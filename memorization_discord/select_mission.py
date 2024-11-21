import discord
from memorization_maker.base_question_get import Get
from memorization_maker.base_question_delete import Delete
from memorization_discord.memorization_maker_edit import EditModeSelectView

class SelectMission_1(discord.ui.Select):
    def __init__(self,title,missions: list,mode):
        self.title = title
        self.mode = mode
        self.missions = missions
        super().__init__(placeholder="問題を選択してください", options=missions,min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        if str(self.values[0]) == "None":
            return await interaction.response.edit_message(content="キャンセルしました。",embed=None, view=None)
        await SelectView(interaction,self.title,int(self.values[0]),self.mode).select_response()
            
class SelectMission_2(discord.ui.Select):
    def __init__(self,title,missions: list,mode):
        self.title = title
        self.mode = mode
        self.missions = missions
        super().__init__(placeholder="問題を選択してください", options=missions,min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectView(interaction,self.title,int(self.values[0]+25),self.mode).select_response()
    
class SelectMission_3(discord.ui.Select):
    def __init__(self,title,missions: list,mode):
        self.title = title
        self.mode = mode
        self.missions = missions
        super().__init__(placeholder="問題を選択してください", options=missions,min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectView(interaction,self.title,int(self.values[0])+50,self.mode).select_response()
    
class SelectMission_4(discord.ui.Select):
    def __init__(self,title,missions: list,mode):
        self.title = title
        self.mode = mode
        self.missions = missions
        super().__init__(placeholder="問題を選択してください", options=missions,min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectView(interaction,self.title,int(self.values[0])+75,self.mode).select_response()
    
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
        if self.mode == 0:
            self.options_list[0].append(discord.SelectOption(label="None", value="None"))
        self.add_item(SelectMission_1(self.title,self.options_list[0],self.mode))
        if missions_len > 25:
            self.add_item(SelectMission_2(self.title,self.options_list[1],self.mode))
        if missions_len > 50:
            self.add_item(SelectMission_3(self.title,self.options_list[2],self.mode))
        if missions_len > 75:
            self.add_item(SelectMission_4(self.title,self.options_list[3],self.mode))
                
class SelectView:
    def __init__(self,interaction:discord.Interaction,title,selectnumber,mode):
        self.interaction:discord.Interaction = interaction
        self.title = title
        self.selectnumber = selectnumber
        self.mode = mode
        
    async def select_response(self):
        
        if self.mode == 0:
            await Delete().delete_misson_select(self.title,self.selectnumber)
            await self.interaction.response.edit_message(content="削除しました。",embed=None, view=None)
        if self.mode == 1:
            datas = await Get().get_misson(self.title)
            missonmode = datas["questions"][self.selectnumber]["mode"]
            embed = discord.Embed(title="選択してください",description="")
            embed.add_field(name="問題",value=f"```\n{datas['questions'][self.selectnumber]['question']}\n```",inline=False)
            if missonmode == 0:
                embed.add_field(name="回答",value=f"```\n{datas['questions'][self.selectnumber]['answer']}\n```",inline=False)
            elif missonmode == 1:
                selects = datas["questions"][self.selectnumber]["select"]
                for num,select in enumerate(selects):
                    embed.add_field(name=f"選択肢{num+1}",value=f"```\n{select}\n```",inline=False)
                embed.add_field(name="回答",value=f"```\n{datas['questions'][self.selectnumber]['answer']}\n```",inline=False)
            elif missonmode == 2:
                embed.add_field(name="回答",value=f"```\n{datas['questions'][self.selectnumber]['answer']}\n```",inline=False)
            await self.interaction.response.edit_message(embed=embed, view=EditModeSelectView(self.title,self.selectnumber,missonmode))