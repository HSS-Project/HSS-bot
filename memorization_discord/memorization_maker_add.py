import discord
from memorization_maker.genre import Genre
from memorization_maker.share import Share
from memorization_maker.base_question_add import Add
from memorization_maker.base_question_get import Get
from memorization_maker.owner_manager import OwnerManager
import random

class TitleModal(discord.ui.Modal,title="タイトル追加"):
    def __init__(self):
        super().__init__()
        self.title_input = discord.ui.TextInput(label="タイトル", style=discord.TextStyle.short)
        self.add_item(self.title_input)
    async def on_submit(self, interaction: discord.Interaction):
        from memorization_discord.memorization_control import MemorizationControlView
        genre = Genre()
        share = Share()
        adds = Add()
        title = str(self.title_input.value)
        if not title:return await interaction.response.send_message("タイトルが入力されていません",ephemeral=True)
        await genre.make_genre(str(interaction.user.id),"default")
        sharecode = await share.make_sharecode()
        await adds.init_add(str(interaction.user.id),title,sharecode)
        await genre.add_genre(str(interaction.user.id),"default",sharecode)
        genre_list = await genre.get_genres_name(str(interaction.user.id))
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        data_title = f"{title}_{sharecode}"
        await interaction.response.send_message(content="",embed=embed,view=MemorizationControlView(data_title,genre_list),ephemeral=True)

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
        from memorization_discord.memorization_control import MemorizationControlView
        add = Add()
        share = Share()
        genre = Genre()
        question = str(self.inputs[0].value)
        answer = str(self.inputs[1].value)
        sharecode = await share.get_sharecode(self.title)
        await add.add_misson(sharecode,question,answer)
        await interaction.response.edit_message(view=MemorizationControlView(self.title,await genre.get_genres_name(str(interaction.user.id))))

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
        await interaction.response.send_message(embed=embed,view=MemorizationAddChangeSelectMode(self.title,question),ephemeral=True)

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
        data = await self.get.get_misson(self.title)
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
        self.genre = Genre()
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
        from memorization_discord.memorization_control import MemorizationControlView
        #選択肢が同じものがあった場合はエラー
        if self.mode == 0:
            select_list = []
            for input_item in self.inputs:
                select_list.append(str(input_item.value))
            if len(select_list) != len(set(select_list)):return await interaction.response.send_message("選択肢が重複しています",ephemeral=True)
        select_list = []
        for input_item in self.inputs:
            select_list.append(str(input_item.value))
        if self.mode == 0:
            embed = discord.Embed(title="選択肢", color=0x00ff00)
            embed.add_field(name="問題", value=self.question)
            for i in range(4):
                embed.add_field(name=f"選択肢:{chr(9312 + i)}", value=self.inputs[i].value,inline=False)
            return await interaction.response.edit_message(embed=embed,view=MemorizationAddChoiceAnswer(self.title,self.question,select_list))
        elif self.mode == 1:
            select_list_number = self.question_select_list_number
            random.shuffle(select_list_number)
            randam_select = []
            random_number = random.randint(0,3)
            for i in range(4):
                data = await self.get.get_misson_select(self.title,select_list_number[i])
                select = data["select"]
                random.shuffle(select)
                randam_select.append(select[0])
            randam_select[random_number] = str(self.inputs[0].value)
            answer = randam_select.index(str(self.inputs[0].value))
            sharecode = await self.share.get_sharecode(self.title)
            await self.add.add_misson_select(sharecode,self.question,answer,randam_select)
            embed = discord.Embed(title="問題追加", color=0x00ff00)
            genre_list = await self.genre.get_genres_name(str(interaction.user.id))
            await interaction.response.edit_message(content="",embed=embed,view=MemorizationControlView(self.title,genre_list))

class MemorizationAddChoiceAnswer(discord.ui.View):
    def __init__(self,title,question,select):
        super().__init__()
        self.title = title
        self.question = question
        self.select = select
        self.add = Add()
        self.share = Share()
        self.genre = Genre()

    async def choice(self,interaction:discord.Interaction,anwernumber:int):
        from memorization_discord.memorization_control import MemorizationControlView
        sharecode = await self.share.get_sharecode(self.title)
        await self.add.add_misson_select(sharecode,self.question,anwernumber,self.select)
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        genre_list = await self.genre.get_genres_name(str(interaction.user.id))
        await interaction.response.edit_message(embed=embed,view=MemorizationControlView(self.title,genre_list))

    @discord.ui.button(label="選択肢①", style=discord.ButtonStyle.green)
    async def choice1(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.choice(interaction,0)
    
    @discord.ui.button(label="選択肢②", style=discord.ButtonStyle.green)
    async def choice2(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.choice(interaction,1)
    
    @discord.ui.button(label="選択肢③", style=discord.ButtonStyle.green)
    async def choice3(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.choice(interaction,2)
    
    @discord.ui.button(label="選択肢④", style=discord.ButtonStyle.green)
    async def choice4(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.choice(interaction,3)
    
class MemorizationAddTextModal(discord.ui.Modal, title="文章問題追加"):
    def __init__(self, titles):
        self.title = titles
        self.genre = Genre()
        super().__init__()
        self.inputs = [discord.ui.TextInput(label="文章を入力してください", style=discord.TextStyle.long)]
        for input_item in self.inputs:
            self.add_item(input_item)
        
    async def on_submit(self, interaction: discord.Interaction):
        add = Add()
        share = Share()
        question = str(self.inputs[0].value)
        sharecode = await share.get_sharecode(self.title)
        ch = await add.add_misson_text(sharecode,question)
        if ch is False:return await interaction.response.send_message("問題の追加に失敗しました",ephemeral=True)
        await interaction.response.send_message("追加しました",ephemeral=True)
    
class MemorizationMakeGenre(discord.ui.Modal, title="ジャンル作成"):
    def __init__(self):
        self.genre_input = discord.ui.TextInput(label="ジャンル", style=discord.TextStyle.short)
        super().__init__()
        self.add_item(self.genre_input)
    async def on_submit(self, interaction: discord.Interaction):
        from memorization_discord.memorization_control import MemorizationControlView
        genre_title = str(self.genre_input.value)
        genre = Genre()
        await genre.make_genre(str(interaction.user.id),genre_title)
        genre_list = await genre.get_genres_name(str(interaction.user.id))
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=MemorizationControlView(str(interaction.user.id),genre_list))

class OwnerAddModal(discord.ui.Modal, title="オーナー追加"):
    def __init__(self, title):
        self.title = title
        self.genre = Genre()
        self.share = Share()
        self.owner_input = discord.ui.TextInput(label="ユーザー名またはユーザーIDを入力してください", style=discord.TextStyle.short)
        super().__init__()
        self.add_item(self.owner_input)
    async def on_submit(self, interaction: discord.Interaction):
        owner = OwnerManager()
        data = int(self.owner_input.value) if self.owner_input.value.isdigit() else str(self.owner_input.value)
        #型判別 int or str
        ownerid_list = await owner.owner_list(str(interaction.user.id),self.title)
        guild = interaction.guild
        if isinstance(data,int):
            try:
                member = guild.get_member(data)
            except:
                return await interaction.response.send_message("存在しないユーザーIDです",ephemeral=True)
            if str(data) in ownerid_list:return await interaction.response.send_message("既に追加されています",ephemeral=True)
            await owner.owner_add(str(interaction.user.id),self.title,str(data))
            #問題の共有コードを追加
            sharecode = await self.share.get_sharecode(self.title)
            await self.genre.add_genre(str(self.owner_input.value),"default",int(sharecode))
        elif isinstance(data,str):
            try:
                member = discord.utils.find(lambda m: m.name == str(data), guild.members)
                userid = str(member.id)
            except:
                return await interaction.response.send_message("存在しないユーザー名です",ephemeral=True)
            if userid in ownerid_list:return await interaction.response.send_message("既に追加されています",ephemeral=True)
            await owner.owner_add(str(interaction.user.id),self.title,str(userid))
            sharecode = await self.share.get_sharecode(self.title)
            await self.genre.add_genre(userid,"default",int(sharecode))
        await interaction.response.send_message(content=f"追加しました",ephemeral=True)

class OwnerDeleteSelect(discord.ui.Select):
    def __init__(self, title, owner_id_list, owner_name):
        options = [
            discord.SelectOption(label=name, value=str(owner_id))
            for owner_id, name in zip(owner_id_list, owner_name)
        ]
        super().__init__(placeholder="削除する管理者を選択してください", min_values=1, max_values=1, options=options)
        self.title = title

    async def callback(self, interaction: discord.Interaction):
        owner = OwnerManager()
        await owner.owmer_remove(str(interaction.user.id),self.title,self.values[0])
        await interaction.response.edit_message(content="削除しました",view=None)