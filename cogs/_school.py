import discord
from discord.ext import commands
from discord import app_commands


from HSS.HSS import School
import requests
import json
import os
import json

class SchoolSelect(discord.ui.Select):
    def __init__(self,school_dict:dict):
        options = []
        for id, name in school_dict.items():
            options.append(discord.SelectOption(label=id, value=name))
        
        super().__init__(placeholder="学校を選択してください", options=options)
    
    async def callback(self, interaction:discord.Interaction):
        pass
        
class GradeAndClassSelect(discord.ui.Select):
    def __init__(self):
        school = School(token="token",schoolid="schoolid")
        school_data:list = school.get_data()
        options = []
        for data in school_data:
            gradename = data["grade"]
            classname = data["class"]
            options.append(discord.SelectOption(label=f"{gradename}-{classname}"))
        
        super().__init__(placeholder="学年とクラスを選択してください", options=options)
        
    async def callback(self, interaction:discord.Interaction):
        anser = self.values[0]
        gradename, classname = anser.split("-")
        pass
        
class send(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="時間割設定",
            timeout=None
            )
        self.value = None

        self.name = discord.ui.TextInput(
            label="教科名",
            placeholder="",
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
            placeholder="教室",
            required=False,
            style=discord.TextStyle.short
        )
        self.add_item(self.name)
        self.add_item(self.isevent)
        self.add_item(self.place)
        
    async def callback(self, interaction:discord.Interaction):
        pass


#HSS.pyで学校名取得するの作ってない。気合でもってくるか　ok
# get_data()でbody.data.details.nameやね ※get_dataのreturnがbody.dataらしいので、details.nameだけでいいっぽい
#tokenってアプリケーションはどうなるん　token設定どうやる？ token.jsonにぶちこむ？　そう。　School(token=token)毎回するのだるいからなんかglobalで良い説　... だな！　とりま　かくぞおお
#基本的にはユーザーと変わらないはず？　とくにせっていしてない！ アプリケーションのトークン一個だけおいとくって感じか　たぶんいいとおも school id指定...:)) まあ後にやるってことでとりあえずこれで行くか！
class patch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    school = app_commands.Group(name="school", description="school api")

    @school.command(name="patch", description="school/patch")
    @app_commands.choices(date=[
        app_commands.Choice(name="月曜日", value="mon"),
        app_commands.Choice(name="火曜日", value="tue"),
        app_commands.Choice(name="水曜日", value="wed"),
        app_commands.Choice(name="木曜日", value="thu"),
        app_commands.Choice(name="金曜日", value="fri"),
        app_commands.Choice(name="土曜日", value="sat"),
        app_commands.Choice(name="日曜日", value="sun")
    ]
    )
    async def school_patch(self,id,interaction:discord.Interaction, date: app_commands.Choice[str], grade:int, class_number:int, time:int):
        await interaction.response.defer()
        school = School(token="token", schoolid="6392060546862023680")
        
        req = school.patch_timeline(day=date.value, grade=grade, _class=class_number, date=date, )
        if req != 200:
            await interaction.followup.send("error")
        else:
            await interaction.followup.send("success")
    
    @school.command(name="get", description="school/get")
    async def school_get(self, interaction:discord.Interaction, id):
        school = School(token="token", schoolid=id)
        res = school.get_data()
        await interaction.response.send_message(res)
    
    @school.command(name="get_timeline", description="school/get_timeline")
    @app_commands.choices(date=[
        app_commands.Choice(name="月曜日", value="mon"),
        app_commands.Choice(name="火曜日", value="tue"),
        app_commands.Choice(name="水曜日", value="wed"),
        app_commands.Choice(name="木曜日", value="thu"),
        app_commands.Choice(name="金曜日", value="fri"),
        app_commands.Choice(name="土曜日", value="sat"),
        app_commands.Choice(name="日曜日", value="sun")
    ]
    )
    async def get_timeline(self, interaction:discord.Interaction, grade, _class, date:app_commands.Choice[str]):
        school = School(token="token", schoolid="6392060546862023680")
        class_ = school.search_class(grade, _class)
        res = school.get_timeline(class_, date.value)
        embed = discord.Embed(title=f"{grade}-{_class}、{date.name}の時間割", description="")
        a = len(res)
        n = len(res) - a
        for d in res:
            if n >= len(res):
                embed.add_field(name=f"{n+1}時間目", value=f"教科:{d[n]["name"]}\n 場所:{"指定なし" if d[n]["place"] == "初期値" else d[n]["place"]}\n イベントか:{"はい" if d[n]["IsEvent"] else "いいえ"}", inline=False)
                n +=1
        await interaction.response.send_message(embed=embed)
    @school.command(name="get_defaulttimeline", description="school/get_timeline")
    @app_commands.choices(date=[
        app_commands.Choice(name="月曜日", value="mon"),
        app_commands.Choice(name="火曜日", value="tue"),
        app_commands.Choice(name="水曜日", value="wed"),
        app_commands.Choice(name="木曜日", value="thu"),
        app_commands.Choice(name="金曜日", value="fri"),
        app_commands.Choice(name="土曜日", value="sat"),
        app_commands.Choice(name="日曜日", value="sun")
    ]
    )
    async def get_defaulttimeline(self, interaction:discord.Interaction, grade, _class, date:app_commands.Choice[str]):
        school = School(token="token", schoolid="6392060546862023680")
        class_ = school.search_class(grade, _class)
        res = school.get_timeline(class_, date.value)
        embed = discord.Embed(title=f"{grade}-{_class}、{date.name}の時間割", description="")
        a = len(res)
        n = len(res) - a
        for d in res:
            if n >= len(res):
                embed.add_field(name=f"{n+1}時間目", value=f"教科:{d[n]["name"]}\n 場所:{"指定なし" if d[n]["place"] == "初期値" else d[n]["place"]}\n イベントか:{"はい" if d[n]["IsEvent"] else "いいえ"}", inline=False)
                n +=1
        await interaction.response.send_message(embed=embed)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(patch(bot))