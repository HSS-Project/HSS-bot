from HSS import NewSchool as School
from HSS import User
import json

import discord
from discord.ext import commands, tasks
from discord import app_commands

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
        self.class_ = self.values[0]


class HourTimeSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for i in range(24):
            options.append(discord.SelectOption(label=f"{i}時", value=i))
        super().__init__(placeholder="時間を選択してください", options=options)
    
    async def callback(self, interaction:discord.Interaction):
        view = discord.ui.View()
        view.add_item(MinuteTimeSelect(self.values[0]))
        await interaction.response.edit_message(content="分を選択してください", view=view)

class MinuteTimeSelect(discord.ui.Select):
    def __init__(self,hour:int):
        options = []
        for i in range(15):
            options.append(discord.SelectOption(label=f"{i}分", value=i))
        super().__init__(placeholder="分を選択してください", options=options)
        for i in range(15,30,15):
            options = discord.SelectOption(label=f"{i}分", value=i)
            self.add_option(options)

        for i in range(15,45,30):
            options = discord.SelectOption(label=f"{i}分", value=i)
            self.add_option(options)

        for i in range(15,60,45):
            options = discord.SelectOption(label=f"{i}分", value=i)
            self.add_option(options)


    async def callback(self, interaction:discord.Interaction):
        await interaction.response.edit_message(content="時間を設定しました", view=None)
    
            

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

    async def add(self,school_id,grade,class_,channel_id,time):
        self.data["send_data"].append({
            "school_id":school_id,
            "grade":grade,
            "class":class_,
            "webhook_url":channel_id,
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
    
    async def get_index(self,school_id:int,grade:int,class_:int):
        for i in range(len(self.data["send_data"])):
            if self.data["send_data"][i]["school_id"] == school_id and self.data["send_data"][i]["grade"] == grade and self.data["send_data"][i]["class"] == class_:
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
        self.add = Timed_NotificationsAdd()
        self.add.load()
    
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