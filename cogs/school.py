import discord
from discord.ext import commands
from discord import app_commands


from HSS import NewSchool as School
from HSS import User
import requests
import json
import os

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
        try:
            self.class_index = self.school.search_class(int(grade), int(_class))
        except Exception as e:
            print(e)
            self.add_item(discord.ui.Button(style=discord.ButtonStyle.red, label="エラーが発生しました"))
            return

    async def make_embed(self, grade:int, _class:int, res,modes:int):
        embed = discord.Embed(title=f"{grade}-{_class}の{self.date}の{"標準"if modes == 0 else "今週"}の時間割", description="")
        for n in range(len(res)):
            embed.add_field(name=f"{n+1}時間目", value=f'教科:{res[n]["name"]}\n 場所:{"指定なし" if res[n]["place"] == "初期値" else res[n]["place"]}\n イベントか:{"はい" if res[n]["IsEvent"] else "いいえ"}', inline=False)
        return embed
    
    @discord.ui.button(style=discord.ButtonStyle.green, label="標準時間割")
    async def default_timeline(self, interaction:discord.Interaction, button:discord.ui.Button):
        res = self.school.get_default_timeline(self.class_index, self.date)
        embed = await self.make_embed(self.grade, self._class, res,0)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(style=discord.ButtonStyle.green, label="今週の時間割")
    async def timeline(self, interaction:discord.Interaction, button:discord.ui.Button):
        res = self.school.get_timeline(self.class_index, self.date)
        embed = await self.make_embed(self.grade, self._class, res,1)
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
        options = []
        self.mode = mode
        school = School(token=token,schoolid=schoolid)
        self.get_list:list = school.get_classes()
        for grade in self.get_list.keys():
            options.append(discord.SelectOption(label=f"{grade}年生", value=grade))
                
        super().__init__(placeholder="学年を選択してください", options=options)
                    
    async def callback(self, interaction:discord.Interaction):
        self.values[0] = str(self.values[0])
        class_list = self.get_list[self.values[0]]
        view = discord.ui.View()
        view.add_item(ClassSelect(self.schoolid, self.values[0], self.mode,class_list))
        await interaction.response.edit_message(content="クラスを選択してください", view=view)
        
class ClassSelect(discord.ui.Select):
    def __init__(self, schoolid:int, grade:int,mode:int,class_list:list):
        self.mode = mode
        self.schoolid = schoolid
        self.grade = grade
        options = []
        class_list = class_list
        for _class in class_list:
            options.append(discord.SelectOption(label=f"{_class}組", value=_class))
        super().__init__(placeholder="クラスを選択してください", options=options)
    
    async def callback(self, interaction:discord.Interaction):
        view = discord.ui.View()
        if self.mode < 4:
            view.add_item(DayOfWeekSelect(self.schoolid, self.grade, self.values[0], self.mode))
            return await interaction.response.edit_message(content="曜日を選択してください", view=view)
        elif self.mode == 4:
            return await interaction.response.edit_message(content="宿題を選択してください", view=HomeworkView(self.schoolid, self.grade, self.values[0]))

class DayOfWeekSelect(discord.ui.Select):
    def __init__(self,schoolid:int, grade:int, _class:int, mode:int):
        self.schoolid = schoolid    
        self.grade = grade
        self._class = _class
        self.mode = mode
        self.school = School(token=token, schoolid=self.schoolid)
        
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
    
    async def callback(self, interaction:discord.Interaction):
        search_class_index = self.school.search_class(int(self.grade),int(self._class))
        if self.mode == 0:            
            await interaction.response.edit_message(content="どちらの時間割を取得しますか", view=gettimelineselect(self.schoolid, self.grade, self._class, self.values[0]))
        elif self.mode == 1:        
            gettimeline = self.school.get_timeline(search_class_index, self.values[0])
            timelineindex = self.school.default_timelineindex(search_class_index)
            if len(gettimeline) < timelineindex:
                await interaction.response.send_modal(send(self.schoolid, self.grade, self._class, self.values[0], 0))
            else:
                view = discord.ui.View()
                view.add_item(EditSendSelect(self.schoolid, self.grade, self._class, self.values[0]))
                await interaction.response.edit_message(content="編集する時間を選択してください", view=view)
        elif self.mode == 2:
            try:
                event = self.school.get_event(search_class_index, self.values[0])
                await interaction.response.edit_message(embed=discord.Embed(
                    title=f"{self.values[0]}のイベント",
                    description=""
                ).add_field(name="場所", value={event['place']}
                ).add_field(name="開始時間/終了時間(終日続くか)", 
                            value=f"{event['timeData']['startTime']}～{event['timeData']['end']}（{'終日' if event['timeData']['isEndofDay'] else '時間内のみ'}）"))
            except TypeError as e:
                await interaction.response.edit_message(content="エラー\n内容はないようです")
        elif self.mode == 3:
            try:
                homework = self.school.get_homework(search_class_index)
            except Exception as e:
                print(e)
                return await interaction.response.edit_message(content="エラー\n内容はないようです")
            lens = len(homework)
            embed = discord.Embed(title=f"{self.values[0]}の宿題")
            for n in range(lens):
                embed.add_field(name=f"{n+1}番目の宿題", value=f"教科:{homework[n]['name']}\nとっても大きくてやるのに時間がかかるものか:{homework[n]['istooBig']}\nページ情報:\nはじまり{homework[n]['start']}\nおわり{homework[n]['end']}\n補足:{homework[n]['comment']}")
            await interaction.response.edit_message(embed=embed)

class EditSendSelect(discord.ui.Select):
    def __init__(self, schoolid:int, grade:int, _class:int, date:str):
        self.schoolid = schoolid
        self.grade:int = int(grade)
        self._class:int = int(_class)
        self.date = date
        self.school = School(token=token, schoolid=self.schoolid)
        options = []
        number:int = self.school.search_class(self.grade, self._class)
        defulttimelineindex = self.school.default_timelineindex(number)
        for i in range(defulttimelineindex):
            i = str(i+1)
            options.append(discord.SelectOption(label=f"{i}時間目", value=i))
        super().__init__(placeholder="編集する時間を選択してください", options=options)
    
    async def callback(self, interaction:discord.Interaction):
        self.values[0] = int(self.values[0])-1
        await interaction.response.send_modal(send(self.schoolid, self.grade, self._class, self.date, 1,self.values[0]))
            
class send(discord.ui.Modal):
    def __init__(self, schoolid:int, grade:int, _class:int, date:str, mode:int,editmode:int=None):
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
        self.editmode = editmode

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
        if (self.isevent.value not in ["True", "False"]):
            embed = discord.Embed(
                title="hss - エラー", description="エラーが発生しました。", color=discord.Color.orange()
            ).add_field(name="エラー内容", value="イベントかどうかはTrueかFalseで指定してください。")
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        school = School(token=token, schoolid=self.schoolid)
        if self.mode == 0 and self.editmode == None:
            try:
                school.patch_timeline(grade=self.grade, _class=self._class, date=self.date, name=self.name.value, isEvent=self.isevent.value, place=self.place.value)
                embed = discord.Embed(title="hss - 設定完了" , description="設定が正常に完了しました。", color=discord.Color.green()
                ).add_field(name="教科名", value=self.name.value).add_field(name="イベントか", value=f"{'はい' if bool(self.isevent.value) else 'いいえ'}").add_field(name="場所", value=self.place.value)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                embed = discord.Embed(title="hss - エラー", description="エラーが発生しました。", color=discord.Color.red()).add_field(name="エラー内容", value=e)
                await interaction.response.send_message(embed=embed, ephemeral=True)
        elif self.mode == 1 and self.editmode != None:
            try:
                self.editmode = int(self.editmode)
                school.patch_timeline(grade=self.grade, _class=self._class, date=self.date, name=self.name.value, isEvent=self.isevent.value, place=self.place.value, state="update",index=self.editmode)
                embed = discord.Embed(title="hss - 設定完了" , description="設定が正常に完了しました。", color=discord.Color.green()
                ).add_field(name="教科名", value=self.name.value).add_field(name="イベントか", value=f"{'はい' if bool(self.isevent.value) else 'いいえ'}").add_field(name="場所", value=self.place.value)
                await interaction.response.send_message(content=None,embed=embed, ephemeral=True)
            except Exception as e:
                embed = discord.Embed(title="hss - エラー", description="エラーが発生しました。", color=discord.Color.red()).add_field(name="エラー内容", value=e)
                await interaction.response.send_message(embed=embed, ephemeral=True)

class HomeworkView(discord.ui.View):
    def __init__(self,schoolid:int,grade:int,_class:int):
        self.schoolid = schoolid
        self.grade = grade
        self._class = _class
        self.view = discord.ui.View()
        super().__init__()
        
    @discord.ui.button(style=discord.ButtonStyle.green, label="宿題追加")
    async def add_homework(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.send_modal(HomeworkAddModal(self.schoolid, self.grade, self._class,0))
    
    @discord.ui.button(style=discord.ButtonStyle.green, label="宿題削除")
    async def delete_homework(self, interaction:discord.Interaction, button:discord.ui.Button):
        self.view.add_item(SelectHomeWork(self.schoolid, self.grade, self._class, 1))
        await interaction.response.edit_message(content="削除する宿題を選択してください", view=self.view)
        
    
    @discord.ui.button(style=discord.ButtonStyle.green, label="宿題編集")
    async def edit_homework(self, interaction:discord.Interaction, button:discord.ui.Button):
        self.view.add_item(SelectHomeWork(self.schoolid, self.grade, self._class, 0))
        await interaction.response.edit_message(content="編集する宿題を選択してください", view=self.view)
    
class HomeworkAddModal(discord.ui.Modal):
    def __init__(self, schoolid:int,grade:int,_class:int,modechange:int,homwork=None):
        self.school = School(token=token, schoolid=schoolid)
        self.grade = grade
        self._class = _class
        self.modechange = modechange
        self.homework = homwork
        super().__init__(title="宿題追加", timeout=None)
        if modechange == 0:
            self.name = discord.ui.TextInput(label="名前", placeholder="レポート名", required=True)
            self.page_start = discord.ui.TextInput(label="開始ページ", placeholder="1", required=True)
            self.page_end = discord.ui.TextInput(label="終了ページ", placeholder="1", required=True)
            self.istooBig = discord.ui.TextInput(label="大きいか", placeholder="True / False", required=True)
            self.comment = discord.ui.TextInput(label="補足", placeholder="補足", required=False)
        elif modechange == 1:            
            self.name = discord.ui.TextInput(label="名前", placeholder=f"{self.homework['name']}", required=False)
            self.page_start = discord.ui.TextInput(label="開始ページ", placeholder=f"{self.homework['page']['start']}", required=False)
            self.page_end = discord.ui.TextInput(label="終了ページ", placeholder=f"{self.homework['page']['end']}", required=False)
            self.istooBig = discord.ui.TextInput(label="大きいか", placeholder=self.homework['istooBig'], required=False)
            self.comment = discord.ui.TextInput(label="補足", placeholder="補足", required=False)
        self.add_item(self.name)
        self.add_item(self.comment)
        self.add_item(self.page_start)
        self.add_item(self.page_end)
        self.add_item(self.istooBig)
    
    async def on_submit(self, interaction:discord.Interaction):
        if self.istooBig.value not in ["True", "False"]:
            return await interaction.response.send_message("エラーが発生しました", ephemeral=True)
        if self.modechange == 0:            
            self.school.patch_homework(grade=int(self.grade),_class=int(self._class),date="mon",name=str(self.name.value),comment=self.comment.value,start=self.page_start.value,end=self.page_end.value,istooBig=bool(self.istooBig.value))
        elif self.modechange == 1:
            homeworkindex = self.school.get_homework(self.school.search_class(self.grade, self._class)).index(self.homework)
            self.school.patch_homework(grade=self.grade,_class=self._class,date="mon",name=self.name.value,comment=self.comment.value,start=self.page_start.value,end=self.page_end.value,istooBig=bool(self.istooBig.value),state="update",index=homeworkindex)
        await interaction.response.send_message("宿題を追加しました", ephemeral=True)

class SelectHomeWork(discord.ui.Select):
    def __init__(self,schoolid:int,grade:int,_class:int,modes:int):
        self.school = School(token=token, schoolid=schoolid)
        self.schoolid = schoolid
        self.grade = int(grade)
        self._class = int(_class)
        self.modes = modes
        self.number = self.school.search_class(int(self.grade), int(self._class))
        self.homework = self.school.get_homework(self.number)
        options = [discord.SelectOption(label=f"{self.homework[n]['name']}", value=n) for n in range(len(self.homework))]
        super().__init__(placeholder="宿題を選択してください", options=options)
        
    async def callback(self, interaction:discord.Interaction):
        self.values[0] = int(self.values[0])
        homework = self.homework[self.values[0]]
        if self.modes == 0:
            await interaction.response.send_modal(HomeworkAddModal(self.schoolid, self.grade, self._class, 1, homework))
        elif self.modes == 1:
            self.school.patch_homework(grade=self.grade,_class=self._class,date="mon",name="aa",comment="aa",start=1,end=1,istooBig=False,state="remove",index=self.values[0])
            await interaction.response.edit_message(content="削除しました")

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user = User(token=token)
    
    school = app_commands.Group(name="school", description="school updateやremoveの場合は、indexを指定してください。そのindexで上書きをします。 api")

    async def check_schools(self,interaction:discord.Interaction):
        user = User(token=token)
        try:
            schools:list = user.get_permission_discordUserID(str(interaction.user.id))
        except Exception as e:
            schools = []
            print(e)
        if len(schools) == 0:
            await interaction.response.send_message("学校が登録されていません", ephemeral=True)
            return 0
        elif len(schools) == 1:
            return 1
        else:
            return 2

    @school.command(name="get_timeline", description="school/get_timeline")
    async def get_timeline(self, interaction:discord.Interaction):
        """時間割を取得します。"""
        view = discord.ui.View()
        schools = await self.check_schools(interaction)
        if schools == 0:return
        elif schools == 1:
            schoolslist = self.user.get_permission_discordUserID(interaction.user.id) 
            view.add_item(GradeSelect(schoolslist[0], 0))
            return await interaction.response.send_message("学年を選択してください", view=view, ephemeral=True)
        else:
            view.add_item(SchoolSelect(0, interaction.user.id))
            return await interaction.response.send_message("学校を選択してください", view=view, ephemeral=True)

    @school.command(name="patch", description="school/patch")
    async def school_patch(self, interaction:discord.Interaction):
        """時間割を設定します。"""
        view = discord.ui.View()
        schools = await self.check_schools(interaction)
        if schools == 0:return
        elif schools == 1:
            schoolslist = self.user.get_permission_discordUserID(interaction.user.id) 
            view.add_item(GradeSelect(schoolslist[0], 1))
            return await interaction.response.send_message("学年を選択してください", view=view, ephemeral=True)
        else:
            view.add_item(SchoolSelect(1, interaction.user.id))
            await interaction.response.send_message("学校を選択してください", view=view, ephemeral=True)
            
    @school.command(name="get_event", description="school/get_event)")
    async def get_event(self, interaction:discord.Interaction):
        """イベントを取得します。"""
        view = discord.ui.View()

        schools = await self.check_schools(interaction)
        if schools == 0:return
        elif schools == 1:
            schoolslist = self.user.get_permission_discordUserID(interaction.user.id) 
            view.add_item(GradeSelect(schoolslist[0], 2))
            await interaction.response.send_message("学年を選択してください", view=view, ephemeral=True)
        else:
            view.add_item(SchoolSelect(2, interaction.user.id))
            await interaction.response.send_message("学校を選択してください", view=view, ephemeral=True)
        
    @school.command(name="get_homework", description="school/get_homework")
    async def get_homework(self, interaction:discord.Interaction):
        """宿題を取得します。"""
        view = discord.ui.View()
        schools = await self.check_schools(interaction)
        if schools == 0:return
        elif schools == 1:
            schoolslist = self.user.get_permission_discordUserID(interaction.user.id) 
            view.add_item(GradeSelect(schoolslist[0], 3))
            return await interaction.response.send_message("学年を選択してください", view=view, ephemeral=True)
        else:
            view.add_item(SchoolSelect(3, interaction.user.id))
            await interaction.response.send_message("学校を選択してください", view=view, ephemeral=True)
    
    @school.command(name="patch_homework", description="school/patch_homework")
    async def patch_homework(self, interaction:discord.Interaction):
        """宿題を設定します。"""
        view = discord.ui.View()
        schools = await self.check_schools(interaction)
        if schools == 0:return
        elif schools == 1:
            schoolslist = self.user.get_permission_discordUserID(interaction.user.id) 
            view.add_item(GradeSelect(schoolslist[0], 4))
            return await interaction.response.send_message("学年を選択してください", view=view, ephemeral=True)
        else:
            view.add_item(SchoolSelect(4, interaction.user.id))
            await interaction.response.send_message("学校を選択してください", view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(CommandsCog(bot))