import discord
from memorization_maker.inc.pakege import Edit,Get

class EditModeSelect(discord.ui.Select):
    def __init__(self, title,select_number,mode):
        self.title = title
        self.select_number = select_number
        self.mode = mode
        options = []
        if self.mode == 0:
            options = [
                discord.SelectOption(label="問題編集", value="add"),
                discord.SelectOption(label="回答編集", value="edit"),
            ]
        elif self.mode == 1:
            options = [
                discord.SelectOption(label="問題編集", value="text"),
            ]
        elif self.mode == 2:
                options.append(discord.SelectOption(label="選択肢編集", value="select"))
                
        super().__init__(placeholder="編集モードを選択してください", options=options, row=1, min_values=1, max_values=1)
            
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "add" :
            await interaction.response.send_modal(EditmModal(self.title,self.select_number,0))
        elif self.values[0] == "edit":
            datas = await Get().get_misson(str(interaction.user.id),self.title)
            if datas["questions"][self.select_number]["mode"] == 0:
                await interaction.response.send_modal(EditmModal(self.title,self.select_number,1))
            elif datas["questions"][self.select_number]["mode"] == 2:
                await interaction.response.send_message(view=EditSelectMenuView(self.title,self.select_number,datas["questions"][self.select_number]["answer"],1))
        elif self.values[0] == "select":
            pass
        elif self.values[0] == "text":
            await interaction.response.send_modal(EditmModal(self.title,self.select_number,self.mode))

class EditModeSelectView(discord.ui.View):
    def __init__(self,title,select_number,mode):
        super().__init__()
        self.add_item(EditModeSelect(title,select_number,mode,))

class EditSelectMenu(discord.ui.Select):
    def __init__(self,title,slect_number,mode,options:list,chanege):
        self.title = title
        self.select_number = slect_number
        for num,option in enumerate(options):
            options.append(discord.SelectOption(label=option, value=str(num)))
        super().__init__(placeholder="選択肢を選択してください", options=options, row=1, min_values=1, max_values=1)
        
    async def callback(self, interaction: discord.Interaction):
        # await interaction.response.send_modal(EditmModal(self.title,self.select_number,3,int(self.values[0])))
        pass

class EditSelectMenuView(discord.ui.View):
    def __init__(self,title,select_number,options,mode):
        super().__init__()
        self.add_item(EditSelectMenu(title,select_number,options,mode))

class EditmModal(discord.ui.Modal,title="編集"):
    def __init__(self,title,select_number,mode,edit_number = None):
        super().__init__()
        self.title = title
        self.select_number = select_number
        self.mode = mode
        self.edit_number = edit_number
        self.input = discord.ui.TextInput(placeholder="入力してください", style=discord.TextStyle.long)
        self.add_item(self.input)
        
    async def on_submit(self, interaction: discord.Interaction):
        datas = await Get().get_misson(str(interaction.user.id),self.title)
        if self.mode == 0:
            question = str(self.input.value)
            answer = datas["questions"][self.select_number]["answer"]
            await Edit().edit_misson(str(interaction.user.id),self.title,question,answer,self.select_number)
        elif self.mode == 1:
            question = datas["questions"][self.select_number]["question"]
            answer = str(self.input.value)
            # await Edit().edit_misson(str(interaction.user.id),self.title,question,answer,self.select_number)
            pass
        elif self.mode == 2:
            # question = datas["questions"][self.select_number]["question"]
            # answer = datas["questions"][self.select_number]["answer"]
            # text_question_number = int(self.input.value)
            # await Edit().edit_misson(str(interaction.user.id),self.title,question,answer,self.select_number,text_question_number)
            pass
        await interaction.response.send_message("編集しました。", ephemeral=True)