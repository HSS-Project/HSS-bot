import discord
from memorization_maker.inc.pakege import Add, Get, OwnerManager, Share, Genre
import random
from select_mission import SelectMissionView
from cogs.memorization_discord.select_title import SelectGenre

class TitleModal(discord.ui.Modal,title="タイトル追加"):
    def __init__(self):
        self.title_input = discord.ui.TextInput(label="タイトル", style=discord.TextStyle.short)
        self.add_item(self.title_input)
        
    async def callback(self, interaction: discord.Interaction):
        genre = Genre()
        title = str(self.title_input.value)
        if not title:return await interaction.response.send_message("タイトルが入力されていません",ephemeral=True)
        await genre.add_genre(str(interaction.user.id),"defult",title)
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        await interaction.response.send_message(content="",embed=embed,view=MemorizationControlView(title),ephemeral=True)

class MemorizationAddModal(discord.ui.Modal,title="問題追加"):
    def __init__(self, titles):
        super().__init__()
        self.title = titles
        self.inputs =[
            discord.ui.TextInput(label="問題",style=discord.TextStyle.long),
            discord.ui.TextInput(label="答え",style=discord.TextStyle.short)
        ]
        for input_item in self.inputs:
            self.add_item(input_item)

    async def on_submit(self, interaction: discord.Interaction):
        add = Add()
        share = Share()
        question = str(self.inputs[0].value)
        answer = str(self.inputs[1].value)
        sharecode = await share.get_sharecode(str(interaction.user.id),self.title)
        if not sharecode:sharecode = await share.make_sharecode()
        await add.add_misson(str(interaction.user.id),self.title,sharecode,question,answer)
        await interaction.response.edit_message(view=MemorizationAddModal(self.title))

class TitleSetModal(discord.ui.Modal,title="問題"):
    def __init__(self, title, base_count=4):
        super().__init__()
        self.title = title
        self.base_count = base_count
        self.inputs = [
            discord.ui.TextInput(label="問題", style=discord.TextStyle.long),
        ]
        for input_item in self.inputs:
            self.add_item(input_item)

    async def on_submit(self, interaction: discord.Interaction):
        question = str(self.inputs[0])  # 最初の入力は問題です
        embed = discord.Embed(title="問題", description=f"{question}", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=MemorizationAddChangeSelectMode(self.title,question))

class MemorizationAddChangeSelectMode(discord.ui.View):
    def __init__(self, title,question):
        super().__init__()
        self.get = Get()
        self.title = title
        self.question = question
        
    @discord.ui.button(label="選択肢を追加", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(MemorizationAddSlect(self.title,self.question,0))

    @discord.ui.button(label="選択肢自動追加", style=discord.ButtonStyle.red)
    async def auto_add(self, interaction: discord.Interaction, _: discord.ui.Button):
        data = await self.get.get_misson(str(interaction.user.id),self.title)
        if data is False:return await interaction.response.send_message("問題がないためこの機能は使えません",ephemeral=True)
        question_select_list_number = []
        for i, question in enumerate(data["questions"]):
            if question["mode"] == 1:
                question_select_list_number.append(i)
        if not question_select_list_number:return await interaction.response.send_message("選択肢の問題がありません",ephemeral=True)
        await interaction.response.send_modal(MemorizationAddSlect(self.title,self.question,1,question_select_list_number))
        
class MemorizationAddSlect(discord.ui.Modal,title="選択肢追加"):
    def __init__(self, title, question,mode,question_select_list_number=None):
        super().__init__()
        self.title = title
        self.question = question
        self.inputs =[]
        self.mode = mode
        self.get = Get()
        self.add = Add()
        self.share = Share()
        self.question_select_list_number = question_select_list_number
        if self.mode == 0:
            self.inputs = [
                discord.ui.TextInput(label="選択肢:①", style=discord.TextStyle.short),
                discord.ui.TextInput(label="選択肢:②", style=discord.TextStyle.short),
                discord.ui.TextInput(label="選択肢:③", style=discord.TextStyle.short),
                discord.ui.TextInput(label="選択肢:④", style=discord.TextStyle.short),
            ]
        elif mode == 1:
            self.inputs = [
                discord.ui.TextInput(label="答え", style=discord.TextStyle.short),
            ]
        for input_item in self.inputs:
            self.add_item(input_item)
    async def on_submit(self, interaction: discord.Interaction):
        if self.mode == 0:
            embed = discord.Embed(title="選択肢", color=0x00ff00)
            embed.add_field(name="問題", value=self.question)
            embed.add_field(name="選択肢①", value=self.inputs[0].value)
            embed.add_field(name="選択肢②", value=self.inputs[1].value)
            embed.add_field(name="選択肢③", value=self.inputs[2].value)
            embed.add_field(name="選択肢④", value=self.inputs[3].value)
            await interaction.response.edit_message(embed=embed,view=MemorizationAddChoiceAnswer(self.title,self.question,self.inputs))
            return
        elif self.mode == 1:
            select_list_number = self.question_select_list_number
            random.shuffle(select_list_number)
            randam_select = []
            random_number = random.randint(0,3)
            for i in range(4):
                data = await self.get.get_misson_select(str(interaction.user.id),self.title,select_list_number[i])
                select = data["select"]
                random.shuffle(select)
                randam_select.append(select[0])
            randam_select[random_number] = str(self.inputs[0].value)
            answer = randam_select.index(str(self.inputs[0].value)) + 1
            sharecode = await self.share.get_sharecode(str(interaction.user.id),self.title)
            if not sharecode:
                sharecode = await self.share.make_sharecode()
            await self.add.add_misson_select(str(interaction.user.id),self.title,sharecode,self.question,answer,randam_select)
            embed = discord.Embed(title="問題追加", color=0x00ff00)
            await interaction.response.edit_message(content="",embed=embed,view=MemorizationControlView(self.title))

class MemorizationAddChoiceAnswer(discord.ui.View):
    def __init__(self,title,question,select):
        super().__init__()
        self.title = title
        self.question = question
        self.select = select
        self.add = Add()
        self.share = Share()

    async def choice(self,interaction:discord.Interaction,anwernumber:int):
        sharecode = await self.share.get_sharecode(str(interaction.user.id),self.title)
        if not sharecode:sharecode = await self.share.make_sharecode()
        await self.add.add_misson_select(str(interaction.user.id),self.title,sharecode,self.question,anwernumber,self.select)
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=MemorizationControlView(self.title))

    @discord.ui.button(label="選択肢①", style=discord.ButtonStyle.green)
    async def choice1(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.choice(interaction,1)
    
    @discord.ui.button(label="選択肢②", style=discord.ButtonStyle.green)
    async def choice2(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.choice(interaction,2)
    
    @discord.ui.button(label="選択肢③", style=discord.ButtonStyle.green)
    async def choice3(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.choice(interaction,3)
    
    @discord.ui.button(label="選択肢④", style=discord.ButtonStyle.green)
    async def choice4(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.choice(interaction,4)
    
class MemorizationAddTextModal(discord.ui.Modal, title="文章問題追加"):
    def __init__(self, titles):
        self.title = titles
        super().__init__()
        self.inputs = [discord.ui.TextInput(label="文章を入力してください", style=discord.TextStyle.long)]
        for input_item in self.inputs:
            self.add_item(input_item)
        
    async def on_submit(self, interaction: discord.Interaction):
        add = Add()
        share = Share()
        question = str(self.inputs[0].value)
        sharecode = await share.get_sharecode(str(interaction.user.id),self.title)
        if not sharecode:
            sharecode = await share.make_sharecode()
        ch = await add.add_misson_text(str(interaction.user.id),self.title,sharecode,question)
        if ch:
            return await interaction.response.edit_message(content="",view=MemorizationControlView(self.title))
        return await interaction.response.edit_message(content="追加に失敗しました。答えの最大個数は5つまでです。確認してください",view=MemorizationControlView(self.title))

class MemorizationMakeGenre(discord.ui.Modal, title="ジャンル作成"):
    def __init__(self):
        self.genre_input = discord.ui.TextInput(label="ジャンル", style=discord.TextStyle.short)
        super().__init__()
        self.add_item(self.genre_input)
        
    async def on_submit(self, interaction: discord.Interaction):
        genre = str(self.genre_input.value)
        genre = Genre()
        await genre.make_genre(str(interaction.user.id),genre)
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=MemorizationControlView(str(interaction.user.id),genre))

class OwnerAddModal(discord.ui.Modal, title="オーナー追加"):
    def __init__(self, title):
        self.title = title
        self.owner_input = discord.ui.TextInput(label="discord idを入力してください", style=discord.TextStyle.short)
        super().__init__()
        self.add_item(self.owner_input)
    async def on_submit(self, interaction: discord.Interaction):
        owner = OwnerManager()
        await owner.owner_add(str(interaction.user.id),self.title,str(self.owner_input.value))
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=MemorizationControlView(self.title))

class OwnerDeleteSelect(discord.ui.Select, title="オーナー削除"):
    def __init__(self, intraction:discord.Interaction,title,owners:list,usernames:list):
        self.title = title
        self.get = Get()
        self.options = []
        for owner in owners:
            if owner != str(intraction.user.id):
                self.options.append(discord.SelectOption(label=usernames,value=owner))
        super().__init__(placeholder="オーナーを選択してください", options=self.options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        owner = OwnerManager()
        await owner.owmer_remove(str(interaction.user.id),self.title,self.values[0])
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=MemorizationControlView(self.title))
        
class MemorizationControlView(discord.ui.View):
    def __init__(self,title,genres:list):
        self.bot = discord.Client()
        super().__init__()
        self.title = title
        self.view = discord.ui.View()
        self.share = Share()
        self.add_item(SelectGenre(genres,0))

    @discord.ui.button(label="問題追加", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(MemorizationAddModal(self.title))
        
    @discord.ui.button(label="選択問題追加", style=discord.ButtonStyle.green)
    async def select_add(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(TitleSetModal(self.title))

    @discord.ui.button(label="文章問題追加", style=discord.ButtonStyle.green)
    async def text_add(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(MemorizationAddTextModal(self.title))

    @discord.ui.button(label="問題編集", style=discord.ButtonStyle.green)
    async def edit(self, interaction: discord.Interaction, _:discord.ui.Button):
        data = await self.share.get_sharedata(str(interaction.user.id),self.title)
        missions = data["questions"]
        embed = discord.Embed(title="問題編集", color=0x00ff00)
        await interaction.response.send_message(embed=embed,view=SelectMissionView(self.title,missions,1))

    @discord.ui.button(label="問題削除", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        data = await self.share.get_sharedata(str(interaction.user.id),self.title)        
        missions = data["questions"]
        embed = discord.Embed(title="問題削除", color=0x00ff00)
        await interaction.response.send_message(embed=embed,view=SelectMissionView(missions))

    @discord.ui.button(label="ジャンル作成", style=discord.ButtonStyle.blurple)
    async def genre(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(MemorizationMakeGenre())
        

    @discord.ui.button(label="オーナー追加", style=discord.ButtonStyle.red)
    async def owner(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(OwnerAddModal(self.title))
        
    @discord.ui.button(label="オーナー削除", style=discord.ButtonStyle.red)
    async def owner_delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        onewr = OwnerManager()
        owners = await onewr.owner_list(str(interaction.user.id),self.title)
        view = discord.ui.View()
        username = []
        for owner in owners:
            user = await self.bot.fetch_user(owner)
            username.append(user.name)
        view.add_item(OwnerDeleteSelect(interaction,self.title,owners,username))
        embed = discord.Embed(title="削除するユーザーを選択してください", color=0x00ff00)
        await interaction.response.send_message(embeds=embed,view=view)

    @discord.ui.button(label="終了", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, _:discord.ui.Button):
        sharecode = await self.share.get_sharecode(str(interaction.user.id),self.title)
        await interaction.response.edit_message(content=f"終了\nこの問題の共有コード:{sharecode}",embed=None,view=None)