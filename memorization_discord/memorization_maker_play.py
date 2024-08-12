import discord
from memorization_maker.inc.package import Share,User,Get

class ChoicePlayMode(discord.ui.View):
    def __init__(self, sharecode:int):
        self.user = User()
        self.sharecode = sharecode
        self.share = Share()
        super().__init__()

    async def init_set(self,userid):
        await self.user.add_user_data_init(str(userid))
        await self.user.add_user_data(str(userid),self.sharecode)
        await self.user.user_data_try(str(userid),self.sharecode)
        
    @discord.ui.button(label="順番出題", style=discord.ButtonStyle.primary)
    async def choice_order(self, interaction: discord.Interaction, _:discord.ui.Button):
        await self.init_set(str(interaction.user.id))
        questions = await self.share.get_sharedata(self.sharecode)
        question_list = questions["questions"]
        await MemorizationPlay(interaction,self.sharecode,0,question_list,0,[]).main_start()
        
    @discord.ui.button(label="ランダム出題", style=discord.ButtonStyle.primary)
    async def choice_random(self, interaction: discord.Interaction, _:discord.ui.Button):
        await self.init_set(str(interaction.user.id))
        questions_user = await self.user.get_mission(str(interaction.user.id),self.sharecode)
        questions = await self.share.get_sharedata(self.sharecode)
        question_number_list = questions_user["questions_numberMemorizationSelectAnswer_list"]
        question_list = []
        for num in question_number_list:
            question_list.append(questions["questions"][num])
        await MemorizationPlay(interaction,self.sharecode,1,question_list,0,[]).main_start()
    
    @discord.ui.button(label="前回のミス問題出題", style=discord.ButtonStyle.primary)
    async def choice_mistake(self, interaction: discord.Interaction, _:discord.ui.Button):
        await self.init_set(str(interaction.user.id))
        question_list = []
        questions_user = await self.user.get_mission(str(interaction.user.id),self.sharecode)
        questions = await self.share.get_sharedata(self.sharecode)
        question_number_list = questions_user["miss_numbers"]
        for num in question_number_list:
            question_list.append(questions["questions"][num])
        await MemorizationPlay(interaction,self.sharecode,2,question_number_list,0,[]).main_start()

class MemorizationAnswer(discord.ui.View):
    def __init__(self,sharecode:int,playmode:int,question_list:list,score:int,miss_list:list,counts:int=0):
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
    async def answer(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(MemorizationAnswerModal(
                    self.sharecode,
                    self.playmode,
                    self.question_list,
                    self.score,
                    self.miss_list,
                    self.counts
                )
            )
        
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
            self.input = discord.ui.TextInput(label="答え", style=discord.TextStyle.short)
            self.add_item(self.input)
        elif self.question_list[self.counts]["mode"] == 2:
            self.inputs = []
            for num,_ in enumerate(self.question_list[self.counts]["answer"]):
                self.inputs.append(discord.ui.TextInput(label=f"{num+1}番目の回答", style=discord.TextStyle.short))
                self.add_item(self.inputs[num])
    
    async def on_submit(self, interaction: discord.Interaction):
        datas = await self.share.get_sharedata(self.sharecode)
        title = datas["title"]
        embed = discord.Embed(title=f"{self.counts+1}問目",color=0x00ff00)
        embed.add_field(name="問題",value=self.question_list[self.counts]["question"],inline=False)
        if self.question_list[self.counts]["mode"] == 0:
            ch = await self.gets.check_answer(title,self.counts,self.input.value)
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
            ch_an = 0
            for i,num in enumerate(self.inputs):
                ch = await self.gets.check_answer(title,self.counts,str(num.value),i)
                awnsers_ch.append(ch)
                embed.add_field(name="回答",value=self.question_list[self.counts]["answer"][i],inline=False)
                if ch:
                    view_ch = "正解"
                    self.score += 1
                else:
                    view_ch = "不正解"
                    ch_an = 1
                    
                embed.add_field(name="あなたの解答",value=num.value,inline=False)
                embed.add_field(name="結果",value=view_ch,inline=False)
            if ch_an:
                self.miss_list.append(self.counts)
        await interaction.response.edit_message(embed=embed,
                                                view=Contenu(
                                                    self.sharecode,
                                                    self.playmode,
                                                    self.question_list,
                                                    self.score,
                                                    self.miss_list,
                                                    self.counts
                                                    )
                                                )
        
class Contenu(discord.ui.View):
    def __init__(self,sharecode:int,playmode:int,question_list:list,score:int,miss_list:list,counts):
        self.sharecode = sharecode
        self.playmode = playmode
        self.question_list = question_list
        self.score = score
        self.miss_list = miss_list
        self.counts = counts
        super().__init__()
        
    @discord.ui.button(label="次の問題", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, _:discord.ui.Button):
        await MemorizationPlay(
            interaction,
            self.sharecode,
            self.playmode,
            self.question_list,
            self.score,
            self.miss_list,
            self.counts+1
            ).main_start()

class MemorizationSelectAnswer(discord.ui.View):
    def __init__(self,sharecode:int,playmode:int,question_list:list,score:int,miss_list:list,counts:int=0):
        self.sharecode = sharecode
        self.playmode = playmode
        self.question_list = question_list
        self.score = score
        self.miss_list = miss_list
        self.counts = counts
        self.user = User()
        self.gets = Get()
        self.share = Share()
        super().__init__()

    async def check_choice(self,num,interaction:discord.Interaction):
        select = self.question_list[self.counts]["select"]
        data = await self.share.get_sharedata(self.sharecode)
        title = data["title"]
        ch = await self.gets.check_answer(title,self.counts,select[num])
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
        await interaction.response.edit_message(embed=embed,
                                                     view=Contenu(
                                                         self.sharecode,
                                                         self.playmode,
                                                         self.question_list,
                                                         self.score,
                                                         self.miss_list,
                                                         self.counts
                                                         )
                                                     )
    
    @discord.ui.button(label="選択肢①", style=discord.ButtonStyle.green)
    async def choice1(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.check_choice(1,interaction)
    @discord.ui.button(label="選択肢②", style=discord.ButtonStyle.green)
    async def choice2(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.check_choice(2,interaction)
    @discord.ui.button(label="選択肢③", style=discord.ButtonStyle.green)
    async def choice3(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.check_choice(3,interaction)
    @discord.ui.button(label="選択肢④", style=discord.ButtonStyle.green)
    async def choice4(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self.check_choice(4,interaction)

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
        print("-----------------")
        print(self.counts)
        print(len(self.question_list))
        print("-----------------")
        if self.counts >= len(self.question_list):
            await self.user.user_data_miss(str(self.interaction.user.id),self.sharecode,self.miss_list)
            await self.user.user_data_score(str(self.interaction.user.id),self.sharecode,self.score)
            await self.user.user_data_shuffle(str(self.interaction.user.id),self.sharecode)
            embed = discord.Embed(title="終了",color=0x00ff00)
            embed.add_field(name="スコア",value=f"{self.score}/{len(self.question_list)}",inline=False)
            embed.add_field(name="間違った問題",value="",inline=False)
            if len(self.miss_list) > 0 and len(self.miss_list) < 20:
                for miss_num in self.miss_list:
                    embed.add_field(name=f"{miss_num+1}問目:{self.question_list[miss_num]['question']}",value=self.question_list[miss_num]["answer"],inline=False)
                return await self.interaction.response.edit_message(embed=embed,view=None)
            elif len(self.miss_list) > 20:
                return await self.interaction.response.edit_message(embed=embed,view=MemorizationMissView(self.sharecode,self.miss_list))
        if len(self.question_list) == 0:
            return await self.interaction.response.edit_message(content="問題がありません",view=None,embed=None)
        embed = discord.Embed(title="問題",color=0x00ff00)
        question = self.question_list[self.counts]["question"]
        embed.add_field(name="問題",value=question,inline=False)
        if self.question_list[self.counts]["mode"] == 0 or self.question_list[self.counts]["mode"] == 2:
            await self.interaction.response.edit_message(embed=embed,
                                                         view=MemorizationAnswer(
                                                             self.sharecode,
                                                             self.playmode,
                                                             self.question_list,
                                                             self.score,
                                                             self.miss_list,
                                                             self.counts
                                                             )
                                                         )
        elif self.question_list[self.counts]["mode"] == 1:
            select = self.question_list[self.counts]["select"]
            for num,selects in enumerate(select):
                embed.add_field(name=f"選択肢{num+1}",value=selects,inline=False)
            await self.interaction.response.edit_message(embed=embed,
                                                         view=MemorizationSelectAnswer(
                                                             self.sharecode,
                                                             self.playmode,
                                                             self.question_list,
                                                             self.score,
                                                             self.miss_list,
                                                             self.counts
                                                             )
                                                         )
            
class MemorizationMissView(discord.ui.View):
    def __init__(self,sharecode:list,miss_number_list:list,page:int = 0):
        self.sharecode = sharecode
        self.page = page
        self.user = User()
        self.gets = Get()
        self.miss_number_list = miss_number_list
        self.miss_list = []
        #miss_number_listを20個ずつに分ける
        for i in range(0, len(self.miss_number_list), 20):
            self.miss_list.append(self.miss_number_list[i:i + 20])
        super().__init__()
        
    async def page_show_embed(self):
        embed = discord.Embed(title=f"間違った問題 : {self.page+1}ページ目",color=0x00ff00)
        for num,miss_num in enumerate(self.miss_list[self.page]):
            datas = await self.share.get_sharedata(self.sharecode)
            if datas["questions"][miss_num]["mode"] == 0:
                embed.add_field(name=f"{num+1}問目",value=f"問題:{datas['questions'][miss_num]['question']}\n解答:{datas['questions'][miss_num]['answer']}",inline=False)
            elif datas["questions"][miss_num]["mode"] == 1:
                question = datas["questions"][miss_num]["question"]
                anwer = datas['questions'][miss_num]['select'][datas['questions'][miss_num]['answer']]
                select = datas['questions'][miss_num]['select']
                embed.add_field(name=f"{num+1}問目",value=f"問題:{question}\n解答:{anwer}\n選択肢:{select}",inline=False)
            elif datas["questions"][miss_num]["mode"] == 2:
                answer = ""
                for i,ans in enumerate(datas["questions"][miss_num]["answer"]):
                    answer += f"{i+1}番目の解答:{ans}\n"
                embed.add_field(name=f"{num+1}問目",value=f"問題:{datas['questions'][miss_num]['question']}\n{answer}",inline=False)
        return embed

    @discord.ui.button(label="左ページ", style=discord.ButtonStyle.primary)
    async def left(self, interaction: discord.Interaction, _:discord.ui.Button):
        if not self.page == 0:
            self.page -= 1
        embed = await self.page_show_embed()
        await interaction.response.edit_message(embed=embed,view=MemorizationMissView(self.sharecode,self.miss_number_list,self.page))
    @discord.ui.button(label="右ページ", style=discord.ButtonStyle.primary)
    async def right(self, interaction: discord.Interaction, _:discord.ui.Button):
        if not self.page == len(self.miss_list) - 1:
            self.page += 1
        embed = await self.page_show_embed()
        await interaction.response.edit_message(embed=embed,view=MemorizationMissView(self.sharecode,self.miss_number_list,self.page))