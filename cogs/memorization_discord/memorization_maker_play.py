import discord
from memorization_maker.inc.pakege import Get,Genre,Share,User

class ChoicePlayMode(discord.ui.View):
    def __init__(self, sharecode:int):
        self.user = User()
        self.sharecode = sharecode
        self.gets = Get()
        self.user = User()
        super().__init__()

    async def init_set(self):
        await self.user.add_user_data_init()
        await self.user.add_user_data(self.sharecode)
        await self.user.user_data_try(self.sharecode)
        
    @discord.ui.button(label="順番出題", style=discord.ButtonStyle.primary)
    async def choice_order(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.init_set()
        questions = await self.gets.get_misson(self.sharecode)
        question_list = questions["questions"]
        await MemorizationPlay(interaction,self.sharecode,0,question_list,0,[]).main_start()
        
    @discord.ui.button(label="ランダム出題", style=discord.ButtonStyle.primary)
    async def choice_random(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.init_set()
        questions_user = await self.user.get_mission(str(interaction.user.id),self.sharecode)
        questions = await self.gets.get_misson(self.sharecode)
        question_number_list = questions_user["questions_number_list"]
        question_list = []
        for num in question_number_list:
            question_list.append(questions["questions"][num])
        await MemorizationPlay(interaction,self.sharecode,1,question_list,0,[]).main_start()
    
    @discord.ui.button(label="前回のミス問題出題", style=discord.ButtonStyle.primary)
    async def choice_mistake(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.init_set()
        question_list = []
        questions_user = await self.user.get_mission(str(interaction.user.id),self.sharecode)
        questions = await self.gets.get_misson(self.sharecode)
        question_number_list = questions_user["miss_numbers"]
        for num in question_number_list:
            question_list.append(questions["questions"][num])
        await MemorizationPlay(interaction,self.sharecode,2,question_number_list,0,[]).main_start()

class MemorizationAnswer(discord.ui.View):
    def __init__(self, interaction:discord.Interaction,sharecode:int,playmode:int,question_list:list,score:int,miss_list:list,counts:int=0):
        self.interaction = interaction
        self.sharecode = sharecode
        self.playmode = playmode
        self.question_list = question_list
        self.score = score
        self.miss_list = miss_list
        self.counts = counts
        self.user = User()
        self.gets = Get()
        super().__init__()
        
    @discord.ui.button(label="回答する", style=discord.ButtonStyle.primary)
    async def answer(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(MemorizationAnswerModal(self.sharecode,self.playmode,self.question_list,self.score,self.miss_list,self.counts))
        
class MemorizationAnswerModal(discord.ui.Modal,title="問題回答"):
    def __init__(self,sharecode:int,playmode:int,question_list:list,score:int,miss_list:list,counts):
        self.sharecode = sharecode
        self.playmode = playmode
        self.question_list = question_list
        self.score = score
        self.miss_list = miss_list
        self.counts = counts
        self.gets = Get()
        self.share = Share()
        super().__init__()
        if self.question_list[self.counts]["mode"] == 0:
            self.input = discord.ui.TextInput(placeholder="答え", style=discord.TextStyle.short)
            self.add_item(self.input)
        elif self.question_list[self.counts]["mode"] == 2:
            self.inputs = []
            for num,_ in enumerate(self.question_list[self.counts]["answer"]):
                self.inputs.append(discord.ui.TextInput(placeholder=f"{num+1}番目の回答", style=discord.TextStyle.short))
                self.add_item(self.inputs[num])
    
    async def on_submit(self, interaction: discord.Interaction):
        datas = await self.gets.get_misson(self.sharecode)
        embed = discord.Embed(title=f"{self.counts+1}問目",color=0x00ff00)
        embed.add_field(name="問題",value=self.question_list[self.counts]["question"],inline=False)
        if self.question_list[self.counts]["mode"] == 0:
            ch = await self.gets.check_answer(str(interaction.user.id),self.sharecode,self.counts,self.input.value)
            embed.add_field(name="回答",value=self.question_list[self.counts]["answer"],inline=False)
            embed.add_field(name="あなたの解答",value=self.input.value,inline=False)
            if ch:
                view_ch = "正解"
                self.score += 1
            else:
                view_ch = "不正解"
                self.miss_list.append(self.counts)
            embed.add_field(name="結果",value=view_ch,inline=False)
        elif self.question_list[self.counts]["mode"] == 2:
            awnsers_ch = []
            for i,num in enumerate(self.inputs):
                datas = await self.share.get_sharedata(self.sharecode)
                title = datas["title"]
                ch = await self.gets.check_answer(str(interaction.user.id),title,self.counts,str(i.value),num)
                awnsers_ch.append(ch)
                embed.add_field(name="回答",value=self.question_list[self.counts]["answer"][num],inline=False)
                if ch:
                    view_ch = "正解"
                    self.score += 1
                else:
                    view_ch = "不正解"
                    self.miss_list.append(self.counts)
                embed.add_field(name="あなたの解答",value=i.value,inline=False)
                embed.add_field(name="結果",value=view_ch,inline=False)
        await interaction.response.edit_message(embed=embed,view=Contenu(interaction,self.sharecode,self.playmode,self.question_list,self.score,self.miss_list,self.counts+1))
        
class Contenu(discord.ui.View):
    def __init__(self, interaction:discord.Interaction,sharecode:int,playmode:int,question_list:list,score:int,miss_list:list,counts):
        self.interaction = interaction
        self.sharecode = sharecode
        self.playmode = playmode
        self.question_list = question_list
        self.score = score
        self.miss_list = miss_list
        self.counts = counts
        super().__init__()
        
    @discord.ui.button(label="次の問題", style=discord.ButtonStyle.primary)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        await MemorizationPlay(interaction,self.sharecode,self.playmode,self.question_list,self.score,self.miss_list,self.counts+1).main_start()

class MemorizationSelectAnswer(discord.ui.View):
    def __init__(self, interaction:discord.Interaction,sharecode:int,playmode:int,question_list:list,score:int,miss_list:list,counts:int=0):
        self.interaction = interaction
        self.sharecode = sharecode
        self.playmode = playmode
        self.question_list = question_list
        self.score = score
        self.miss_list = miss_list
        self.counts = counts
        self.user = User()
        self.gets = Get()
        super().__init__()

    async def check_choice(self,num):
        select = self.question_list[self.counts]["select"]
        title = await self.gets.get_misson(str(self.interaction.user.id),self.sharecode)["title"]
        ch = await self.gets.check_answer(str(self.interaction.user.id),title,self.counts,select[num-1])
        embed = discord.Embed(title=f"{self.counts+1}問目",color=0x00ff00)
        embed.add_field(name="問題",value=self.question_list[self.counts]["question"],inline=False)
        embed.add_field(name="回答",value=self.question_list[self.counts]["answer"],inline=False)
        embed.add_field(name="あなたの解答",value=select[num-1],inline=False)
        if ch:
            view_ch = "正解"
            self.score += 1
        else:
            view_ch = "不正解"
            self.miss_list.append(self.counts)
        embed.add_field(name="結果",value=view_ch,inline=False)
        await self.interaction.response.edit_message(embed=embed,view=Contenu(self.interaction,self.sharecode,self.playmode,self.question_list,self.score,self.miss_list,self.counts+1))
    
    @discord.ui.button(label="選択肢①", style=discord.ButtonStyle.green)
    async def choice1(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.check_choice(1)
    @discord.ui.button(label="選択肢②", style=discord.ButtonStyle.green)
    async def choice2(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.check_choice(2)
    @discord.ui.button(label="選択肢③", style=discord.ButtonStyle.green)
    async def choice3(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.check_choice(3)
    @discord.ui.button(label="選択肢④", style=discord.ButtonStyle.green)
    async def choice4(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.check_choice(4)

class MemorizationPlay:
    def __init__(self, interaction:discord.Interaction,sharecode:int,playmode:int,question_list:list,score:int,miss_list:list,counts:int=0):
        self.interaction = interaction
        self.sharecode = sharecode
        self.playmode = playmode
        self.question_list = question_list
        self.score = score
        self.miss_list = miss_list
        self.counts = counts
        self.user = User()
        self.gets = Get()
    
    async def main_start(self):
        if self.counts == len(self.question_list):
            await self.user.user_data_miss(str(self.interaction.user.id),self.sharecode,self.miss_list)
            await self.user.user_data_score(str(self.interaction.user.id),self.sharecode,self.score)
            await self.user.user_data_shuffle(str(self.interaction.user.id),self.sharecode)
            embed = discord.Embed(title="終了",color=0x00ff00)
            embed.add_field(name="スコア",value=f"{self.score}/{len(self.question_list)}",inline=False)
            embed.add_field(name="間違った問題",value="",inline=False)
            if len(self.miss_list) > 0 and len(self.miss_list) < 20:
                for miss_num in self.miss_list:
                    embed.add_field(name=f"{miss_num+1}問目:{self.question_list[miss_num]['question']}",value=self.question_list[miss_num]["anwer"],inline=False)
            return await self.interaction.response.edit_message(embed=embed,view=None)
        embed = discord.Embed(title="問題",color=0x00ff00)
        question = self.question_list[self.counts]["question"]
        embed.add_field(name="問題",value=question,inline=False)
        if self.question_list[self.counts]["mode"] == 0 or self.question_list[self.counts]["mode"] == 2:
            await self.interaction.response.send_message(embed=embed,view=MemorizationAnswer(self.interaction,self.sharecode,self.playmode,self.question_list,self.score,self.miss_list,self.counts))
        elif self.question_list[self.counts]["mode"] == 1:
            select = self.question_list[self.counts]["select"]
            for num,selects in enumerate(select):
                embed.add_field(name=f"選択肢{num+1}",value=selects,inline=False)
            await self.interaction.response.send_message(embed=embed,view=MemorizationSelectAnswer(self.interaction,self.sharecode,self.playmode,self.question_list,self.score,self.miss_list,self.counts))
            
class MemorizationMissView(discord.ui.view):
    def __init__(self,sharecode:list,page):
        self.sharecode = sharecode
        self.page = page
        super().__init__()
        
    @discord.ui.button(label="左", style=discord.ButtonStyle.primary)
    async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass
    
    @discord.ui.button(label="右", style=discord.ButtonStyle.primary)
    async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
        pass