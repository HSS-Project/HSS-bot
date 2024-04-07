from HSS import NewSchool as School
from HSS import User
import json

import discord
from discord.ext import commands, tasks
from discord import app_commands

import datetime
import aiohttp

with open("token.json", "r", encoding="utf-8") as f:
    token = json.load(f)
    token = token["HSSAPI_TOKEN"]

class SchoolSelect(discord.ui.Select):
    def __init__(self,id:int,modes:int):
        options = []
        self.mode = modes
        user = User(token=token)
        schools:list = user.get_permission_discordUserID(id)
        names = []
        options = []
        print(schools)
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
    def __init__(self,schoolid:int,modes:int):
        self.schoolid = schoolid
        school = School(token=token,schoolid=schoolid)
        get_classes:list = school.get_classes()
        self.mode = modes
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
        lists:list = [self.mode,self.schoolid, self.grade, self.values[0]]
        await interaction.response.send_modal(TimeModal(lists))

class TimeModal(discord.ui.Modal):
    def __init__(self,lists:list):
        super().__init__(timeout=None)
        self.lists = lists
        self.input = discord.ui.TextInput(placeholder="時間を入力してください(HH:MM)", min_length=5, max_length=5)
        self.add_item(self.input)
    
    async def on_submit(self, interaction:discord.Interaction):
        time = self.input.value
        try:
            time = datetime.datetime.strptime(time, "%H:%M")
        except:
            await interaction.response.send_message("時間の形式が間違っています")
            return
        
        if self.lists[0] == 0:
            webhook = await interaction.channel.create_webhook(name="Timed Notification Webhook")
            webhook_url = webhook.url
            await Timed_NotificationsAdd.add(self.lists[1], self.lists[2], self.lists[3], webhook_url, time)
            await interaction.response.send_message("通知を登録しました")
        elif self.lists[0] == 1:
            webhooks = await interaction.channel.webhooks()
            webhook_url = webhooks[0].url if webhooks else None
            if webhook_url:
                index = await Timed_NotificationsAdd.get_index(self.lists[1], self.lists[2], self.lists[3], webhook_url)
                await Timed_NotificationsAdd.remove(index)
                await interaction.response.send_message("通知を削除しました")
            else:
                await interaction.response.send_message("Webhookが見つかりません")

class Timed_NotificationsAdd:
    def __init__(self):
        self.data:dict = {}
            # "send_data":[
            #     {
            #         "school_id":0,
            #         "grade":0,
            #         "class":0,
            #         "webhool_url":0,
            #         "time":"00;00"
            #     }
            # ]}

    def load(self):
        with open("send_data.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save(self):
        with open("send_data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    async def add(self,school_id,grade,class_,webhook_url,time):
        self.data["send_data"].append({
            "school_id":school_id,
            "grade":grade,
            "class":class_,
            "webhook_url":webhook_url,
            "time":time
        })
        self.save()
        return True

    async def remove(self,index:int):
        del self.data["send_data"][index]
        self.save()
        return True

    async def get(self):
        return self.data["send_data"]
    
    async def get_index(self,school_id:int,grade:int,class_:int,webhook_url:int):
        for i in range(len(self.data["send_data"])):
            if self.data["send_data"][i]["school_id"] == school_id and self.data["send_data"][i]["grade"] == grade and self.data["send_data"][i]["class"] == class_ and self.data["send_data"][i]["webhook_url"] == webhook_url:
                return i
            
        return None
    
    async def get_data(self,index:int):
        return self.data["send_data"][index]
    
    async def get_data_index(self,school_id:int,grade:int,class_:int):
        index = await self.get_index(school_id,grade,class_)
        return self.data["send_data"][index]    
    

class Timed_Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Timed_NotificationsAdd = Timed_NotificationsAdd()
        self.Timed_NotificationsAdd.load()
        self.send.start()
    
    @app_commands.command()
    async def add(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(SchoolSelect(interaction.user.id, 0))
        await interaction.response.send_message("学校を選択してください", view=view)

    @app_commands.command()
    async def remove(self,interection:discord.Interaction):
        view = discord.ui.View()
        view.add_item(SchoolSelect(interection.user.id, 1))
        await interection.response.send_message("学校を選択してください", view=view)
        
        
    @tasks.loop(seconds=60)
    async def send(self):
        now = datetime.datetime.now()
        listsweekdays = ["mon","tue","wed","thu","fri","sat","sun"]
        for data in await self.Timed_NotificationsAdd.get():
            time = datetime.datetime.strptime(data["time"], "%H:%M")
            if time.hour == now.hour and time.minute == now.minute:
                school = School(token=token, schoolid=data["school_id"])
                index = await school.search_class(school, data["grade"], data["class"])
                weekday = listsweekdays[now.weekday()]
                timeline = school.get_timeline(index, weekday)
                default_timeline = school.get_default_timeline(index, weekday)
                homework = school.get_homework(index, weekday)
                event = school.get_event(index, weekday)
                if timeline == []:
                    timeline = default_timeline
                async with aiohttp.ClientSession() as session:
                    webhook = discord.Webhook.from_url(data["webhook_url"], adapter=session)
                embed = discord.Embed(title=f"{school.get_data()['details']['name']} {data['grade']}年{data['class']}組", description=f"{weekday} {now.hour}:{now.minute}の通知です", color=0x00ff00)
                for i in range(len(timeline)):
                    embed.add_field(name=f"{i+1}時間目:{timeline[i]['name']}",value=f"場所:{timeline[i]['place']}",inline=False) 
                await webhook.send(embed=embed)    
                
async def setup(bot: commands.Bot):
    await bot.add_cog(Timed_Notifications(bot))