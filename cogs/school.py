import discord
from discord.ext import commands
from discord import app_commands


from HSS import NewSchool as School
from HSS import User
import requests
import json
import os
import json

with open("token.json", 'r', encoding='utf-8') as file:
    t = json.load(file)
    token = t["HSSAPI_TOKEN"]
    
class gettimelineselect(discord.ui.View):
    def __init__(self, school_id,grade:int, _class:int, date):
        super().__init__(timeout=None)
        self.school_id = school_id
        self.grade:int = int(grade)
        self._class:int = int(_class)
        self.date = date
        self.school = School(token=token, schoolid=self.school_id)
        self.class_index = self.school.search_class(int(grade), int(_class))

    @discord.ui.button(style=discord.ButtonStyle.green, label="標準時間割")
    async def default_timeline(self, interaction:discord.Interaction, button:discord.ui.Button):
        res = self.school.get_default_timeline(self.class_index, self.date)
        embed = discord.Embed(title=f"{self.grade}-{self._class}の{self.date}の標準時間割", description="")
        for n in range(len(res)):
            embed.add_field(name=f"{n+1}時間目", value=f'教科:{res[n]["name"]}\n 場所:{"指定なし" if res[n]["place"] == "初期値" else res[n]["place"]}\n イベントか:{"はい" if res[n]["IsEvent"] else "いいえ"}', inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(style=discord.ButtonStyle.green, label="今週の時間割")
    async def timeline(self, interaction:discord.Interaction, button:discord.ui.Button):
        res = self.school.get_timeline(self.class_index, self.date)
        embed = discord.Embed(title=f"{self.grade}-{self._class}の{self.date}の時間割", description="")
        for n in range(len(res)):
            embed.add_field(name=f"{n+1}時間目", value=f'教科:{res[n]["name"]}\n 場所:{"指定なし" if res[n]["place"] == "初期値" else res[n]["place"]}\n イベントか:{"はい" if res[n]["IsEvent"] else "いいえ"}', inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SchoolSelect(discord.ui.Select):
    def __init__(self,mode:int,id:int):
        self.mode = mode
        options = []
        user = User(token=token)
        schools:list = user.get_permission_discordUserID(id)
        names = []
        options = []
        for school_id in schools:
            school = School(token=token, schoolid=school_id)
            data = school.get_data()            
            name = data["details"]["name"]
            names.append(name)
        for name,id in zip(names, schools):
            options.append(discord.SelectOption(label=name, value=id))
        super().__init__(placeholder="学校を選択してください", options=options)
    
    async def callback(self, interaction:discord.Interaction):
        view = discord.ui.View()
        view.add_item(GradeSelect(self.values[0], self.mode))
        await interaction.response.edit_message(content="学年を選択してください", view=view)
        
class GradeSelect(discord.ui.Select):
    def __init__(self,schoolid:int,mode:int):
        self.schoolid = schoolid
        self.mode = mode
        school = School(token=token,schoolid=schoolid)
        get_classes:list = school.get_classes()
        options = []
        for grade in get_classes:
            for key in grade.keys():
                options.append(discord.SelectOption(label=f"{key}年", value=key))
                
        super().__init__(placeholder="学年を選択してください", options=options)
                    
    async def callback(self, interaction:discord.Interaction):
        view = discord.ui.View()
        view.add_item(ClassSelect(self.schoolid, self.values[0], self.mode))
        await interaction.response.edit_message(content="クラスを選択してください", view=view)
        
    
class ClassSelect(discord.ui.Select):
    def __init__(self, schoolid:int, grade:int,mode:int):
        school = School(token=token,schoolid=schoolid)
        self.mode = mode
        self.schoolid = schoolid
        self.grade = grade
        get_classes:list = school.get_classes()
        options = []
        for grade_ in get_classes:
            for key in grade_.keys():
                if key == grade:
                    for class_ in grade_[key]:
                        options.append(discord.SelectOption(label=f"{class_}組", value=class_))
        super().__init__(placeholder="クラスを選択してください", options=options)
    
    async def callback(self, interaction:discord.Interaction):
        view = discord.ui.View()
        view.add_item(DayOfWeekSelect(self.schoolid, self.grade, self.values[0], self.mode))
        await interaction.response.edit_message(content="曜日を選択してください", view=view)

class DayOfWeekSelect(discord.ui.Select):
    def __init__(self,schoolid:int, grade:int, _class:int, mode:int):
        self.schoolid = schoolid    
        self.grade = grade
        self._class = _class
        self.mode = mode
        options = [
            discord.SelectOption(label="月曜日", value="mon"),
            discord.SelectOption(label="火曜日", value="tue"),
            discord.SelectOption(label="水曜日", value="wed"),
            discord.SelectOption(label="木曜日", value="thu"),
            discord.SelectOption(label="金曜日", value="fri"),
            discord.SelectOption(label="土曜日", value="sat"),
            discord.SelectOption(label="日曜日", value="sun")
        ]
        super().__init__(placeholder="曜日を選択してください", options=options)
        self.school = School(token=token, schoolid=self.schoolid)
    
    async def callback(self, interaction:discord.Interaction):
        if self.mode == 0:            
            print("gettimelineselect")
            print(self.schoolid, self.grade, self._class, self.values[0])
            await interaction.response.edit_message(content="どちらの時間割を取得しますか", view=gettimelineselect(self.schoolid, self.grade, self._class, self.values[0]))
        elif self.mode == 1:
            await interaction.response.send_modal(send(self.schoolid, self.grade, self._class, self.values[0], self.mode))
        elif self.mode == 2:
            try:
                _class = self.school.search_class(int(self.grade),int(self._class))
                event = self.school.get_event(_class, self.values[0])
                await interaction.response.edit_message(embed=discord.Embed(
                    title=f"{self.values[0]}のイベント",
                    description=""
                ).add_field(name="場所", value={event['place']}
                ).add_field(name="開始時間/終了時間(終日続くか)", 
                            value=f"{event['timeData']['startTime']}～{event['timeData']['end']}（{'終日' if event['timeData']['isEndofDay'] else '時間内のみ'}）"))
            except TypeError as e:
                await interaction.response.edit_message(content="内容はないようです")
        elif self.mode == 3:
            _class = self.school.search_class(int(self.grade),int(self._class))
            homework = self.school.get_homework(_class, self.values[0])
            lens = len(homework)
            embed = discord.Embed(title=f"{self.values[0]}の宿題")
            await interaction.response.edit_message(content=homework)


class send(discord.ui.Modal):
    def __init__(self, schoolid:int, grade:int, _class:int, date:str, mode:int):
        super().__init__(
            title="時間割設定",
            timeout=None
            )
        self.value = None
        self.schoolid = schoolid
        self.grade = grade
        self._class = _class
        self.date = date
        self.mode = mode

        self.name = discord.ui.TextInput(
            label="名前",
            placeholder="国語",
            style=discord.TextStyle.short,
            required=True
        )
        self.isevent = discord.ui.TextInput(
            label="イベントかどうか",
            placeholder="True / Falseのどちらか",
            style=discord.TextStyle.short,
            required=True,
            default="False"
        )
        self.place = discord.ui.TextInput(
            label="場所",
            placeholder="ばしょめ",
            required=True,
            default="教室",
            style=discord.TextStyle.short
        )
        self.add_item(self.name)
        self.add_item(self.isevent)
        self.add_item(self.place)
        
    async def on_submit(self, interaction:discord.Interaction):
        self.stop()
        print(self.isevent.value)
        print(type(self.isevent.value))
        if (self.isevent.value not in ["True", "False"]):
            embed = discord.Embed(
                title="hss - エラー", description="エラーが発生しました。", color=discord.Color.orange()
            ).add_field(name="エラー内容", value="イベントかどうかはTrueかFalseで指定してください。")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        school = School(token=token, schoolid=self.schoolid)
        if self.mode == 1:
            #try:
            req = school.patch_timeline(grade=self.grade, _class=self._class, date=self.date, name=self.name.value, isEvent=self.isevent.value, place=self.place.value)
            embed = discord.Embed(title="hss - 設定完了" , description="設定が正常に完了しました。", color=discord.Color.green()
            ).add_field(name="教科名", value=self.name.value).add_field(name="イベントか", value=f"{'はい' if bool(self.isevent.value) else 'いいえ'}").add_field(name="場所", value=self.place.value)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            #except Exception as e:
                # embed = discord.Embed(title="hss - エラー", description="エラーが発生しました。", color=discord.Color.red()).add_field(name="エラー内容", value=e)
                # await interaction.response.send_message(embed=embed, ephemeral=True)

#学校選択→学年選択→クラス選択できた。　「技術的には可能だけど僕知らない　○-○だったら25クラスまでしかできないからマンモス学校死ぬ」
#学年とクラスいっしょは無理だった？　まあいっか(　これどんな感じで渡されるんですk
# get_data()でbody.data.details.nameやね ※get_dataのreturnがbody.dataらしいので、details.nameだけでいいっぽい
#tokenってアプリケーションはどうなるん　token設定どうやる？ token.jsonにぶちこむ？　そう。　School(token=token)毎回するのだるいからなんかglobalで良い説　... だな！　とりま　かくぞおお
#基本的にはユーザーと変わらないはず？　とくにせっていしてない！ アプリケーションのトークン一個だけおいとくって感じか　たぶんいいとおも school id指定...:)) まあ後にやるってことでとりあえずこれで行くか！
class patch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    school = app_commands.Group(name="school", description="school api")

    @school.command(name="get_timeline", description="school/get_timeline")
    async def get_timeline(self, interaction:discord.Interaction):
        """時間割を取得します。"""
        view = discord.ui.View()
        view.add_item(SchoolSelect(0, interaction.user.id))
        await interaction.response.send_message("学校を選択してください", view=view, ephemeral=True)

    @school.command(name="patch", description="school/patch")
    async def school_patch(self, interaction:discord.Interaction):
        """時間割を設定します。"""
        view = discord.ui.View()
        view.add_item(SchoolSelect(1, interaction.user.id))
        await interaction.response.send_message("学校を選択してください", view=view, ephemeral=True)
            
    @school.command(name="get_event", description="school/get_event)")
    async def get_event(self, interaction:discord.Interaction):
        """イベントを取得します。"""
        view = discord.ui.View()
        view.add_item(SchoolSelect(2, interaction.user.id))
        await interaction.response.send_message("学校を選択してください", view=view, ephemeral=True)
        
    @school.command(name="get_homework", description="school/get_homework")
    async def get_homework(self, interaction:discord.Interaction):
        """宿題を取得します。"""
        view = discord.ui.View()
        view.add_item(SchoolSelect(3,interaction.user.id))
        await interaction.response.send_message("学校を選択してください", view=view, ephemeral=True)
    
async def setup(bot: commands.Bot):
    await bot.add_cog(patch(bot))
