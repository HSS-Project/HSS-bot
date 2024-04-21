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
    """
    Select School 
    
    Args:
        id (int): Discord User ID
        modes (int): 0: Add, 1: Remove
    
    Returns:
        None
    """
    def __init__(self,id:int,modes:int):
        options = []
        self.mode = modes
        user = User(token=token)
        schools:list = user.get_permission_discordUserID(id)
        names = []
        options = []
        for school_id in schools:
            try:
                school = School(token=token, schoolid=school_id)
                data = school.get_data()            
                name = data["details"]["name"]
                names.append(name)
            except Exception as e:
                print(e)
                name = "取得失敗"
                names.append(name)
        for name,id in zip(names, schools):
            options.append(discord.SelectOption(label=name, value=id))
        super().__init__(placeholder="学校を選択してください", options=options)
    
    async def callback(self, interaction:discord.Interaction):
        if self.values[0] == "取得失敗":
            await interaction.response.send_message("取得失敗しました", ephemeral=True)
            return
        view = discord.ui.View()
        view.add_item(GradeSelect(self.values[0], self.mode))
        await interaction.response.edit_message(content="学年を選択してください", view=view)

class GradeSelect(discord.ui.Select):
    """
    Select Grade
    
    Args:
        schoolid (int): School ID
        modes (int): 0: Add, 1: Remove
        
    Returns:
        None
    """
    def __init__(self,schoolid:int,modes:int):
        self.schoolid = schoolid
        school = School(token=token,schoolid=schoolid)
        options = []
        try:
            get_classes:list = school.get_classes()
        except Exception as e:
            print(e)
            options.append(discord.SelectOption(label="取得失敗", value="取得失敗"))
            super().__init__(placeholder="学年を選択してください", options=options)
            return
        self.mode = modes
        for grade in get_classes:
            for key in grade.keys():
                options.append(discord.SelectOption(label=f"{key}年", value=key))
                
        super().__init__(placeholder="学年を選択してください", options=options)
                    
    async def callback(self, interaction:discord.Interaction):
        if self.values[0] == "取得失敗":
            await interaction.response.send_message("取得失敗しました", ephemeral=True)
            return
        view = discord.ui.View()
        view.add_item(ClassSelect(self.schoolid, self.values[0], self.mode))
        await interaction.response.edit_message(content="クラスを選択してください", view=view)

class ClassSelect(discord.ui.Select):
    """
    Select Class
    
    Args:
        schoolid (int): School ID
        grade (int): Grade
        mode (int): 0: Add, 1: Remove
        
    Returns:
        None
    """
    def __init__(self, schoolid:int, grade:int,mode:int):
        school = School(token=token,schoolid=schoolid)
        self.mode = mode
        self.schoolid = schoolid
        self.grade = grade
        options = []
        try:
            get_classes:list = school.get_classes()
        except Exception as e:
            print(e)
            options.append(discord.SelectOption(label="取得失敗", value="取得失敗"))
            super().__init__(placeholder="クラスを選択してください", options=options)
            return
        for grade_ in get_classes:
            for key in grade_.keys():
                if key == grade:
                    for class_ in grade_[key]:
                        options.append(discord.SelectOption(label=f"{class_}組", value=class_))
        super().__init__(placeholder="クラスを選択してください", options=options)
    
    async def callback(self, interaction:discord.Interaction):
        lists:list = [self.mode,self.schoolid, self.grade, self.values[0]]
        self.timed_notifications_add = Timed_NotificationsAdd()
        if self.mode == 0:
            await interaction.response.send_modal(TimeModal(lists))
        elif self.mode == 1:
            view = discord.ui.View()
            view.add_item(RemoveSelect(lists))
            if self.timed_notifications_add.get_lists(lists[1],lists[2],lists[3]) == []:
                await interaction.response.send_message("通知が登録されていません",ephemeral=True)
                return
            
            await interaction.response.edit_message(content="削除する通知を選択してください", view=view)
        
class RemoveSelect(discord.ui.Select):
    """
    Select Remove
    
    Args:
        lists (list): [mode, schoolid, grade, class]
        
    Returns:
        None
    """
    def __init__(self,lists:list):
        self.timed_notifications_add = Timed_NotificationsAdd()
        options = []
        self.lists = lists
        try:
            selectlists = self.timed_notifications_add.get_lists(lists[1],lists[2],lists[3])
        except Exception as e:
            print(e)
            options.append(discord.SelectOption(label="取得失敗", value="取得失敗"))
            super().__init__(placeholder="削除する通知を選択してください", options=options)
            return
        for data in selectlists:
            options.append(discord.SelectOption(label=f"{data['time']}", value=f"{data['time']}"))
            
        super().__init__(placeholder="削除する通知を選択してください", options=options, min_values=1, max_values=1)
        
    async def callback(self, interaction:discord.Interaction):
        if self.values[0] == "取得失敗":
            await interaction.response.send_message("取得失敗しました", ephemeral=True)
            return
        time = self.values[0]
        index = self.timed_notifications_add.get_index_2(self.lists[1], self.lists[2], self.lists[3],time)
        data = await self.timed_notifications_add.get_data(index)
        webhook = await interaction.channel.webhooks()
        for i in webhook:
            if i.url == data["webhook_url"]:
                webhook = i
                break
        await webhook.delete()
        await self.timed_notifications_add.remove(index)
        await interaction.response.send_message("通知を削除しました")
        
class TimeModal(discord.ui.Modal,title="送信時間指定"):
    """
    Time Modal
    
    Args:
        lists (list): [mode, schoolid, grade, class]
    
    Returns:
        None
    """
    def __init__(self,lists:list):
        super().__init__(timeout=None)
        self.lists = lists
        self.input = discord.ui.TextInput(label="時間を入力してください",style=discord.TextStyle.short,placeholder="HH:MM", min_length=5, max_length=5)
        self.add_item(self.input)
    
    async def on_submit(self, interaction:discord.Interaction):
        timed_notifications_add = Timed_NotificationsAdd()
        time = self.input.value
        try:
            temp_time = datetime.datetime.strptime(time, "%H:%M")
        except:
            await interaction.response.send_message("時間の形式が間違っています")
            return
        try:
            webhook = await interaction.channel.create_webhook(name="HSS スケジュール通知")
            webhook_url = webhook.url
        except Exception as e:
            print(e)
            await interaction.response.send_message("Webhookの作成に失敗しました")
            return
        
        try:
            await timed_notifications_add.add(self.lists[1], self.lists[2], self.lists[3], webhook_url, time)
        except Exception as e:
            print(e)
            await interaction.response.send_message("通知の登録に失敗しました")
            return
        await interaction.response.send_message("通知を登録しました")

class Timed_NotificationsAdd:
    """
    Timed Notifications Add
    """
    def __init__(self):
        self.data:dict = {}
        self.load()

    def load(self):
        """
        Load send_data.json
        
        Args:
            None
        
        Returns:
            None
        """ 
        with open("send_data.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save(self):
        """
        Save send_data.json
        
        Args:
            None
        
        Returns:
            None
        """
        with open("send_data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    async def add(self,school_id,grade,class_,webhook_url,time):
        """
        Add Send Data
        
        Args:
            school_id (int): School ID
            grade (int): Grade
            class_ (int): Class
            webhook_url (str): Webhook URL
            time (str): Time
        
        Returns:
            True
        """
        self.load()
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
        """
        Remove Send Data
        
        Args:
            index (int): Index

        Returns:
            True
        """
        self.load()
        del self.data["send_data"][index]
        self.save()
        return True

    async def get(self):
        """
        Get Send Data
        
        Args:
            None
        
        Returns:
            self.data["send_data"]
        """
        self.load()
        return self.data["send_data"]
    
    def get_index(self,school_id:int,grade:int,class_:int,webhook_url:str):
        """
        Get Index
        
        Args:
            school_id (int): School ID
            grade (int): Grade
            class_ (int): Class
            webhook_url (str): Webhook URL
        
        Returns:
            i (int): Index
        """
        self.load()
        for i in range(len(self.data["send_data"])):
            if self.data["send_data"][i]["school_id"] == school_id and self.data["send_data"][i]["grade"] == grade and self.data["send_data"][i]["class"] == class_ and self.data["send_data"][i]["webhook_url"] == webhook_url:
                return i
            
        return None
    
    def get_index_2(self,school_id:int,grade:int,class_:int,time:str):
        """
        Get Index
        
        Args:   
            school_id (int): School ID
            grade (int): Grade
            class_ (int): Class
            time (str): Time
        Returns:
            i (int): Index
        """
        self.load()
        for i in range(len(self.data["send_data"])):
            if self.data["send_data"][i]["school_id"] == school_id and self.data["send_data"][i]["grade"] == grade and self.data["send_data"][i]["class"] == class_ and self.data["send_data"][i]["time"] == time:
                return i

    
    def get_lists(self,school_id:int,grade:int,class_:int):
        """
        Get Lists
        
        Args:
            school_id (int): School ID
            grade (int): Grade
            class_ (int): Class 
        
        Returns:    
            lists (list): Lists
        """
        self.load()
        lists = []
        for data in self.data["send_data"]:
            if data["school_id"] == school_id and data["grade"] == grade and data["class"] == class_:
                lists.append(data)
        return lists
    
    async def get_data(self,index:int):
        """
        get Data
        
        Args:
            index (int): Index
        Returns:
            self.data["send_data"][index]
        """
        self.load()
        return self.data["send_data"][index]
    
    async def get_data_index(self,school_id:int,grade:int,class_:int):
        """ 
        Get Data Index
        Args:
            school_id (int): School ID
            grade (int): Grade
            class_ (int): Class
        Returns:
            self.data["send_data"][index]
        """
        self.load()
        index = await self.get_index(school_id,grade,class_)
        return self.data["send_data"][index]    
    

class Timed_Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.Timed_NotificationsAdd = Timed_NotificationsAdd()
        self.Timed_NotificationsAdd.load()
        self.send.start()
    
    @app_commands.command()
    async def time_notifications_add(self, interaction: discord.Interaction):
        """指定した時間にwebhookを使用して明日の日程を送信する機能の設定です"""
        view = discord.ui.View()
        view.add_item(SchoolSelect(interaction.user.id, 0))
        await interaction.response.send_message("学校を選択してください", view=view,ephemeral=True)

    @app_commands.command()
    async def time_notifications_remove(self,interection:discord.Interaction):
        """指定した時間にwebhookを使用して明日の日程を送信する機能の削除です"""
        view = discord.ui.View()
        view.add_item(SchoolSelect(interection.user.id, 1))
        await interection.response.send_message("学校を選択してください", view=view,ephemeral=True)
        
        
    @tasks.loop(seconds=60)
    async def send(self):
        try:
            now = datetime.datetime.now()
            listsweekdays = ["mon","tue","wed","thu","fri","sat","sun"]
            for data in await self.Timed_NotificationsAdd.get():
                time = datetime.datetime.strptime(data["time"], "%H:%M")
                if time.hour == now.hour and time.minute == now.minute:
                    school = School(token=token, schoolid=data["school_id"])
                    print(data)
                    print(data["grade"], data["class"])
                    grade:int = int(data["grade"])
                    class_:int = int(data["class"])
                    index = school.search_class(grade=grade, classname=class_)
                    print(index)
                    if now.weekday() == 6:
                        weekday = listsweekdays[0]
                    else:
                        weekday = listsweekdays[now.weekday()+1]
                    timeline = school.get_timeline(index, weekday)
                    default_timeline = school.get_default_timeline(index, weekday)
                    homework = school.get_homework(index)
                    # event = school.get_event(index, weekday)
                    if timeline == []:
                        timeline = default_timeline
                    embed = discord.Embed(title=f"{school.get_data()['details']['name']} {data['grade']}年{data['class']}組", description=f"{weekday} 明日の日程です", color=0x00ff00)
                    for i in range(len(timeline)):
                        if timeline[i]['place'] == "初期値":
                            place = "未設定"
                        else:
                            place = timeline[i]['place']
                        embed.add_field(name=f"{i+1}時間目:{timeline[i]['name']}",value=place,inline=False) 
                    embed.add_field(name="〜〜宿題〜〜",value="",inline=False)
                    for i in range(len(homework)):
                        embed.add_field(name=f"ーーー{homework[i]['name']}ーーーー",value="",inline=False)
                        embed.add_field(name="時間かかるか",value="はい" if homework[i]['istooBig'] == True else "いいえ",inline=False)
                        embed.add_field(name="ページ",value=f"{homework[i]['page']['start']}〜{homework[i]['page']['end']}",inline=False)
                        embed.add_field(name="コメント",value=homework[i]['page']['comment'],inline=False)
                    try:
                        async with aiohttp.ClientSession() as session:
                            webhook = discord.Webhook.from_url(data["webhook_url"], session=session)
                            await webhook.send(embed=embed)    
                    except Exception as e:
                        print("送信失敗",data,e)
        except Exception as e:
            print(e)
                
async def setup(bot: commands.Bot):
    await bot.add_cog(Timed_Notifications(bot))