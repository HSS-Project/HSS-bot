import discord
from memorization_maker.inc.pakege import Add, Get, OwnerManager, Share, Genre
import random
import memorization_discord.select_mission as select_mission
import memorization_discord.select_title as select_title

class TitleModal(discord.ui.Modal,title="タイトル追加"):
    def __init__(self):
        super().__init__()
        self.title_input = discord.ui.TextInput(label="タイトル", style=discord.TextStyle.short)
        self.add_item(self.title_input)
        
    async def on_submit(self, interaction: discord.Interaction):
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
        print(self.title)
        print(self.question)
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
        genre_list = await self.genre.get_genres_name(str(interaction.user.id))
        ch = await add.add_misson_text(sharecode,question)
        if ch is False:return await interaction.response.send_message("問題の追加に失敗しました",ephemeral=True)
        return await interaction.response.edit_message(content="",view=MemorizationControlView(self.title,genre_list))
    
class MemorizationMakeGenre(discord.ui.Modal, title="ジャンル作成"):
    def __init__(self):
        self.genre_input = discord.ui.TextInput(label="ジャンル", style=discord.TextStyle.short)
        super().__init__()
        self.add_item(self.genre_input)
    async def on_submit(self, interaction: discord.Interaction):
        genre_title = str(self.genre_input.value)
        genre = Genre()
        genre_list = await genre.get_genres_name(str(interaction.user.id))
        await genre.make_genre(str(interaction.user.id),genre_title)
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=MemorizationControlView(str(interaction.user.id),genre_list))

class OwnerAddModal(discord.ui.Modal, title="オーナー追加"):
    def __init__(self, title):
        self.title = title
        self.genre = Genre()
        self.owner_input = discord.ui.TextInput(label="ユーザー名またはユーザーIDを入力してください", style=discord.TextStyle.short)
        super().__init__()
        self.add_item(self.owner_input)
    async def on_submit(self, interaction: discord.Interaction):
        owner = OwnerManager()
        data = self.owner_input.value
        #型判別 int or str
        if isinstance(data,int):
            await owner.owner_add(str(interaction.user.id),self.title,str(data))
        elif isinstance(data,str):
            
            await owner.owner_add(str(interaction.user.id),self.title,str(data))
            
        await owner.owner_add(str(interaction.user.id),self.title,str(self.owner_input.value))
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        genre_list = await self.genre.get_genres_name(str(interaction.user.id))
        await interaction.response.edit_message(embed=embed,view=MemorizationControlView(self.title,genre_list))

class OwnerDeleteSelect(discord.ui.Select):
    def __init__(self, intraction:discord.Interaction,title,owners:list,usernames:list):
        self.title = title
        self.get = Get()
        self.genre = Genre()
        self.options = []
        for owner in owners:
            if owner != str(intraction.user.id):
                self.options.append(discord.SelectOption(label=usernames,value=owner))
        super().__init__(placeholder="オーナーを選択してください", options=self.options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        owner = OwnerManager()
        await owner.owmer_remove(str(interaction.user.id),self.title,self.values[0])
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        genre_list = await self.genre.get_genres_name(str(interaction.user.id))
        await interaction.response.edit_message(embed=embed,view=MemorizationControlView(self.title,genre_list))
        
class MemorizationControlView_sub(discord.ui.View):
    def __init__(self,title:str,genres:list):
        super().__init__()
        self.title = title
        self.view = discord.ui.View()
        self.share = Share()
        self.select_mission = select_mission
        self.select_title = select_title
        self.genre_list = genres
    
    @discord.ui.button(label="ジャンル削除", style=discord.ButtonStyle.red)
    async def genre_delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        pass
    @discord.ui.button(label="オーナー追加", style=discord.ButtonStyle.green)
    async def owner_add(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(OwnerAddModal(self.title))
    
    @discord.ui.button(label="オーナー削除", style=discord.ButtonStyle.red)
    async def owner_delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        owner = OwnerManager()
        data = await owner.get_owner(self.title)
        usernames = []
        for owner in data:
            usernames.append(owner["username"])
        await interaction.response.send_message(embed=discord.Embed(title="選択してください",description=""),view=OwnerDeleteSelect(interaction,self.title,data,usernames),ephemeral=True)
    
    @discord.ui.button(label="終了", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, _:discord.ui.Button):
        sharecode = await self.share.get_sharecode(self.title)
        await interaction.response.edit_message(content=f"終了\nこの問題の共有コード:{sharecode}",embed=None,view=None)
    
class MemorizationControlView(discord.ui.View):
    def __init__(self,title:str,genres:list):
        super().__init__()
        self.title = title
        self.view = discord.ui.View()
        self.share = Share()
        self.select_mission = select_mission
        self.select_title = select_title
        self.genre_list = genres
        self.add_item(self.select_title.SelectGenre(genres,0,0,title))

    @discord.ui.button(label="問題追加", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(MemorizationAddModal(self.title))
        
    @discord.ui.button(label="選択問題追加", style=discord.ButtonStyle.green)
    async def select_add(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(TitleSetModal(self.title))

    @discord.ui.button(label="文章問題追加", style=discord.ButtonStyle.green)
    async def text_add(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(MemorizationAddTextModal(self.title))

    @discord.ui.button(label="問題編集", style=discord.ButtonStyle.grey)
    async def edit(self, interaction: discord.Interaction, _:discord.ui.Button):
        sharecode = await self.share.get_sharecode(self.title)
        data = await self.share.get_sharedata(sharecode)
        missions_question:list = []
        missions = data["questions"]
        for mission in missions:
            missions_question.append(mission["question"])
        embed = discord.Embed(title="問題編集", color=0x00ff00)
        await interaction.response.send_message(embed=embed,view=self.select_mission.SelectMissionView(self.title,missions_question,1), ephemeral=True)

    @discord.ui.button(label="問題削除", style=discord.ButtonStyle.grey)
    async def delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        sharecode = await self.share.get_sharecode(self.title)
        data = await self.share.get_sharedata(sharecode)
        missions_question:list = []
        missions = data["questions"]
        for mission in missions:
            missions_question.append(mission["question"])
        embed = discord.Embed(title="問題削除", color=0x00ff00)
        await interaction.response.send_message(embed=embed,view=self.select_mission.SelectMissionView(self.title,missions_question,0), ephemeral=True)

    @discord.ui.button(label="ジャンル作成", style=discord.ButtonStyle.blurple)
    async def genre(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(MemorizationMakeGenre())

    @discord.ui.button(label="終了", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, _:discord.ui.Button):
        sharecode = await self.share.get_sharecode(self.title)
        await interaction.response.edit_message(content=f"終了\nこの問題の共有コード:{sharecode}",embed=None,view=None)

