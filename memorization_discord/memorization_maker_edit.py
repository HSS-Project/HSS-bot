import discord
from memorization_maker.inc.pakege import Edit,Get

class EditModeSelect(discord.ui.Select):
    def __init__(self, title,select_number,mode):
        self.title = title
        self.select_number = select_number
        self.mode = mode
        options = []
        if self.mode == 0 or self.mode == 1:
            options = [
                discord.SelectOption(label="問題編集", value="add"),
                discord.SelectOption(label="回答編集", value="edit"),
            ]
        elif self.mode == 1:
            options.append(discord.SelectOption(label="選択肢編集", value="select"))
        elif self.mode == 2:
            options = [
                discord.SelectOption(label="問題編集", value="text"),
            ]
        super().__init__(placeholder="編集モードを選択してください", options=options, row=1, min_values=1, max_values=1)
            
    async def callback(self, interaction: discord.Interaction):
        datas = await Get().get_misson(self.title)
        question = datas["questions"][self.select_number]["question"]
        if self.values[0] == "add" :
            await interaction.response.send_modal(EditmModal(self.title,self.select_number,0))
        elif self.values[0] == "edit":
            if datas["questions"][self.select_number]["mode"] == 0:
                await interaction.response.send_modal(EditmModal(self.title,self.select_number,1))
            elif datas["questions"][self.select_number]["mode"] == 1:
                await interaction.response.send_message(view=EditSelectMenuView(self.title,self.select_number,datas["questions"][self.select_number]["select"],question,0))
        elif self.values[0] == "select":
            await interaction.response.send_message(view=EditSelectMenuView(self.title,self.select_number,datas["questions"][self.select_number]["select"],question,1))
        elif self.values[0] == "text":
            await interaction.response.send_modal(EditmModal(self.title,self.select_number,2))

class EditModeSelectView(discord.ui.View):
    def __init__(self,title,select_number,mode):
        super().__init__()
        self.add_item(EditModeSelect(title,select_number,mode,))

class EditSelectMenu(discord.ui.Select):
    def __init__(self,title,slect_number,options:list,question,chanege):
        self.title = title
        self.select_number = slect_number
        self.options = options
        self.question = question
        self.chanege = chanege
        for num,option in enumerate(options):
            options.append(discord.SelectOption(label=option, value=str(num+1)))
        super().__init__(placeholder="選択肢を選択してください", options=options, row=1, min_values=1, max_values=1)
        
    async def callback(self, interaction: discord.Interaction):
        if self.chanege == 0:
            answer = int(self.values[0])
            await Edit().edit_misson(self.title,self.question,answer,self.select_number)
            await interaction.response.send_message("編集しました。", ephemeral=True)
        elif self.chanege == 1:
            select_num = int(self.values[0])
            await interaction.response.send_modal(EditmModal(self.title,self.select_number,3,select_num))
        
class EditSelectMenuView(discord.ui.View):
    def __init__(self,title,select_number,options,mode,chanege):
        super().__init__()
        self.add_item(EditSelectMenu(title,select_number,options,mode,chanege))

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
        datas = await Get().get_misson(self.title)
        if self.mode == 0:
            question = str(self.input.value)
            answer = datas["questions"][self.select_number]["answer"]
            await Edit().edit_misson(self.title,question,answer,self.select_number)
        elif self.mode == 1:
            question = datas["questions"][self.select_number]["question"]
            answer = str(self.input.value)
            await Edit().edit_misson(self.title,question,answer,self.select_number)
        elif self.mode == 2:
            await Edit().edit_misson_text(self.title,self.input.value)
        elif self.mode == 3:
            select = datas["questions"][self.select_number]["select"]
            select[self.edit_number] = self.input.value
            await Edit().edit_misson_select(self.title,question,select,self.select_number)
        await interaction.response.send_message("編集しました。", ephemeral=True)