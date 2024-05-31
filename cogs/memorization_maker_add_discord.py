import discord
from discord import ui
import memorization_maker
from discord import app_commands
from discord.ext import commands
import openpyxl
import io


class TitleAddModal(ui.Modal, title="タイトル追加"):
    """
    A class representing a view for adding a title in the Memorization Maker Discord bot system.
    """
    def __init__(self):
        super().__init__()
        self.title_input = ui.TextInput(label="タイトル", style=discord.TextStyle.short)
        self.add_item(self.title_input)

    async def on_submit(self, interaction: discord.Interaction):
        memmorization = memorization_maker.MemorizationSystem()
        titles = await memmorization.get_mission_title(str(interaction.user.id))
        content = ""
        if titles and isinstance(titles, list) and str(self.title_input.value) in titles:content = "編集モード"
        title = str(self.title_input.value)        
        embed = discord.Embed(title="問題追加", description=f"現在の選択問題設定個数:4", color=0x00ff00)
        await interaction.response.send_message(content=content,embed=embed, ephemeral=True, view=MemorizationControlView(title))

class MemorizationAddModal(ui.Modal,title="問題追加"):
    """
    A class representing the user interface for adding a memorization mission in a Discord bot.

    Attributes:
        title (str): The title of the memorization mission.
        inputs (list): A list of ui.TextInput objects representing the input fields for the question and answer.

    Methods:
        __init__(self, title): Initializes the MemorizationAddDiscordUi object.
        on_submit(self, interaction): Handles the event when the user submits the form.

    """
    def __init__(self, titles):
        super().__init__()
        self.title = titles
        self.inputs =[
            ui.TextInput(label="問題",style=discord.TextStyle.long),
            ui.TextInput(label="答え",style=discord.TextStyle.short)
        ]
        for input_item in self.inputs:
            self.add_item(input_item)

    async def on_submit(self, interaction: discord.Interaction):
        memorization = memorization_maker.MemorizationSystem()
        getcode = await memorization.sharecode_true(str(interaction.user.id),self.title)
        if not getcode:
            random_number = await memorization.make_sharecode()
        else:
            random_number = getcode
        question, answer = [str(input_item) for input_item in self.inputs]
        ch = await memorization.add_mission(str(interaction.user.id), self.title,random_number, 0, question,answer)
        if not ch:return await interaction.response.send_message("追加失敗", ephemeral=True)
        await interaction.response.edit_message(view=MemorizationControlView(self.title))


class EditCountSelect(discord.ui.Select):
    def __init__(self, title):
        self.title = title
        super().__init__(placeholder="選択数を選択してください",
                         min_values=1,
                         max_values=1,
                         options=[discord.SelectOption(label=str(i), value=str(i)) for i in range(1, 6)])
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="問題追加", description=f"現在の選択問題設定個数:{int(self.values[0])}", color=0x00ff00)
        await interaction.response.edit_message(embed=embed, view=MemorizationControlView(self.title, int(self.values[0])))


class TitleSetModal(ui.Modal,title="タイトル設定"):
    """
    A class representing a modal for selecting a title in the Memorization Add Discord UI.

    Attributes:
    - title (str): The title of the modal.
    - base_count (int): The base count value.
    - inputs (list): A list of input items.

    Methods:
    - __init__(self, title, base_count=4): Initializes the MemorizationAddDiscordUiSelectTitle object.
    - on_submit(self, interaction: discord.Interaction): Handles the submit event of the modal.
    """
    def __init__(self, title, base_count=4):
        super().__init__()
        self.title = title
        self.base_count = base_count
        self.inputs = [
            ui.TextInput(label="問題", style=discord.TextStyle.long),
        ]
        for input_item in self.inputs:
            self.add_item(input_item)

    async def on_submit(self, interaction: discord.Interaction):
        question = str(self.inputs[0])  # 最初の入力は問題です
        embed = discord.Embed(title="問題", description=f"{question}", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=MemorizationAddView(self.title, self.base_count, 1,question))

class QuestionAddModal(ui.Modal, title="選択問題追加"):
    """
    A class representing a modal for selecting questions in the Memorization Add Discord UI.

    Args:
        title (str): The title of the modal.
        base_count (int): The base count of the questions.
        question (str): The question to be displayed.

    Attributes:
        title (str): The title of the modal.
        base_count (int): The base count of the questions.
        question (str): The question to be displayed.
        inputs (list): A list of TextInput objects representing the choices.
    """

    def __init__(self, title, base_count, question):
        super().__init__()
        self.title = title
        self.base_count = base_count
        self.question = question
        self.inputs = [ui.TextInput(label=f"選択肢:{i+1}", style=discord.TextStyle.short) for i in range(self.base_count)]
        for input_item in self.inputs:
            self.add_item(input_item)
    async def on_submit(self, interaction: discord.Interaction):
        select = [str(input_item) for input_item in self.inputs[0:]]
        embed = discord.Embed(title="選択問題", color=0x00ff00)
        for sen, value in enumerate(select, start=1):
            embed.add_field(name=f"選択肢:{sen}", value=value, inline=False)
        await interaction.response.edit_message(embed=embed, view=MemorizationAddView(self.title, self.base_count, 2, self.question, select))


class AnsewrEditSelect(discord.ui.Select):
    """
    A custom select menu for editing the answer in the Memorization Add Discord UI.

    Args:
        title (str): The title of the select menu.
        lists (list): The list of questions.
        selected_index (int): The index of the selected question.
    
    Attributes:
        title (str): The title of the select menu.
        lists (list): The list of questions.
        selected_index (int): The index of the selected question.
    
    Methods:
        callback(interaction: discord.Interaction) -> None: The callback method that is called when the select menu is interacted with.

    """
    def __init__(self,title,lists,selected_index):
        self.title = title
        self.lists = lists
        self.selected_index = selected_index
        placeholder = "答えを選択してください"
        min_values = 1
        max_values = 1
        options = []
        self.index = len(self.lists[selected_index]["select"])
        for raw in range(self.index):
            num = str(raw+1)
            options.append(discord.SelectOption(label=num))
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)

    async def callback(self, interaction: discord.Interaction):
        memorization = memorization_maker.MemorizationSystem()
        await memorization.edit_misson(str(interaction.user.id), self.title,self.selected_index, 1, self.values[0])
        embed = discord.Embed(title="問題追加", description=f"現在の選択問題設定個数:{self.index}", color=0x00ff00)
        await interaction.response.edit_message(embed=embed, view=MemorizationControlView(self.title,self.index))

class AnswerAddSelect(discord.ui.Select):
    """
    A custom UI select component for selecting answers in the Memorization Maker Discord bot.

    Args:
        title (str): The title of the question.
        base_count (int): The base count for generating options.
        question (str): The question to be displayed.
        select (list): The list of answer choices.

    Attributes:
        title (str): The title of the question.
        base_count (int): The base count for generating options.
        question (str): The question to be displayed.
        select (list): The list of answer choices.
        answer (str): The selected answer.

    """

    def __init__(self, title, base_count, question, select):
        options = []
        for i in range(base_count):
            i += 1
            a = str(i)
            option = discord.SelectOption(label=str(a))
            options.append(option)

        super().__init__(placeholder="答えを選択してください", min_values=1, max_values=1, options=options)
        self.title = title
        self.base_count = base_count
        self.question = question
        self.select = select

    async def callback(self, interaction: discord.Interaction):
        self.answer = self.values[0]
        embed = discord.Embed(title="選択問題", color=0x00ff00)
        for sen, value in enumerate(self.select, start=1):
            embed.add_field(name=f"選択肢{sen}", value=value, inline=False)
        embed.add_field(name="答え", value=self.answer, inline=False)
        memorizationmaker = memorization_maker.MemorizationSystem()
        getcode = await memorizationmaker.sharecode_true(str(interaction.user.id),self.title)
        if getcode:
            random_number = getcode
        else:
            random_number = await memorizationmaker.make_sharecode()
        await memorizationmaker.add_mission(str(interaction.user.id), self.title, random_number,1, self.question, self.answer, self.select)
        await interaction.response.edit_message(embed=embed, view=MemorizationAddView(self.title, self.base_count, 3, self.question, self.select))


class MemorizationAddView(discord.ui.View):
    """
    A custom UI select button for the Memorization Maker Discord bot.

    Args:
        title (str): The title of the select button.
        base_count (int): The base count for the select button.
        mode (int): The mode of the select button.
        question (str, optional): The question for the select button. Defaults to None.
        select (str, optional): The select option for the select button. Defaults to None.
    """

    def __init__(self, title, base_count, mode, question=None, select=None):
        super().__init__()
        self.title = title
        self.base_count = base_count
        self.question = question
        self.select = select
        self.mode = mode
        
    async def swithcing(self, interaction: discord.Interaction, button, mode):
        if mode == 0:
            await interaction.response.send_modal(TitleSetModal(self.title))
        elif mode == 1:
            await interaction.response.send_modal(QuestionAddModal(self.title, self.base_count, self.question))
        elif mode == 2:
            view = discord.ui.View()
            view.add_item(AnswerAddSelect(self.title, self.base_count, self.question, self.select))
            await interaction.response.edit_message(view=view)
        elif mode == 3:
            embed = discord.Embed(title="問題追加", description=f"現在の選択問題設定個数:{self.base_count}", color=0x00ff00)
            await interaction.response.edit_message(embed=embed, view=MemorizationControlView(self.title, self.base_count))
    
    
    @discord.ui.button(label="続行", style=discord.ButtonStyle.blurple)
    async def continue_(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.swithcing(interaction, button, self.mode)

class QuestionEditSelect(discord.ui.Select):
    """
    A custom select menu for selecting a memorization mission in the Memorization Discord UI.
    """
    def __init__(self, lists):
        placeholder = "タイトルを選択してください"
        min_values = 1
        max_values = 1
        self.lists = lists
        options_1 = [discord.SelectOption(label=item) for item in self.lists[:25]]
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options_1)
        for i in range(25, len(self.lists), 25):
            for item in self.lists[i:i+25]:
                option = discord.SelectOption(label=item)
                self.add_option(option)

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method called when an option is selected.
        """
        title = self.values[0]
        await interaction.response.edit_message(content="編集モード",view=MemorizationControlView(title))


class MemorizationDeleteSelect(discord.ui.Select):
    """
    A custom select menu for deleting a memorization mission in Discord.

    Attributes:
    - lists (list): The list of options for the select menu.
    - title (str): The title of the mission to be deleted.
    - count (int): The count of the mission to be deleted.

    Methods:
    - callback(interaction): The callback method called when an option is selected.
    """

    def __init__(self, lists, title,count):
        self.title = title
        placeholder = "問題を選択してください"
        min_values = 1
        max_values = 1
        lists = lists["questions"]
        self.lists = lists
        self.count = count
        options=[discord.SelectOption(label=item["question"], value=str(index)) for index, item in enumerate(lists)]
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)
        for i in range(25, len(self.lists), 25):
            for item in self.lists[i:i+25]:
                option = discord.SelectOption(label=item)
                super().add_option(option)

    async def callback(self, interaction: discord.Interaction):
        selected_index = int(self.values[0])
        selected_question = self.lists[selected_index]["question"]
        memorization = memorization_maker.MemorizationSystem()
        await memorization.del_mission(str(interaction.user.id), self.title, selected_question)
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        await interaction.response.edit_message(embed=embed, view=MemorizationControlView(self.title,self.count))

class MemorizationShareSelect(discord.ui.Select):
    """
    A custom select component for selecting a title for memorization sharing.
    
    Attributes:
    - lists: title select
    """
    def __init__(self, lists):
        self.lists = lists
        placeholder = "タイトルを選択してください"
        min_values = 1
        max_values = 1
        options = [discord.SelectOption(label=i) for i in lists[:25]]
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)
        for i in range(25, len(self.lists), 25):
            for item in self.lists[i:i+25]:
                option = discord.SelectOption(label=item)
                super().add_option(option)

    async def callback(self, interaction: discord.Interaction):
        memorization = memorization_maker.MemorizationSystem()
        number = await memorization.get_sharecode(str(interaction.user.id),self.values[0])
        await interaction.response.edit_message(content=f"共有コード:{number}")

class MemorizationTitleDeleteSelect(discord.ui.Select):
    """
    A custom Discord UI select component for deleting a memorization mission.

    Args:
        list (list): The list of options for the select component.

    Attributes:
        lists (list): The list of options for the select component.

    """

    def __init__(self, title_list):
        placeholder = "問題を選択してください"
        min_values = 1
        max_values = 1
        self.title_lists = title_list
        options = [discord.SelectOption(label=i) for i in self.title_lists[:25]]
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)
        for i in range(25, len(self.title_lists), 25):
            for item in self.title_lists[i:i+25]:
                option = discord.SelectOption(label=item)
                super().add_option(option)

    async def callback(self, interaction: discord.Interaction):
        memorization = memorization_maker.MemorizationSystem()
        await memorization.del_mission_title(str(interaction.user.id), self.values[0])
        await interaction.response.edit_message(content="削除完了", view=None)

class MemorizationEditSelect(discord.ui.Select):
    """
    A custom select menu for selecting a question in the Memorization Edit Discord UI.

    Attributes:
    - lists (list): The list of questions to be displayed in the select menu.
    - title (str): The title of the select menu.
    - count (int): The count of the select menu.

    Methods:
    - __init__(self, lists, title): Initializes the MemorizationEditDiscordSelect object.
    - callback(self, interaction): The callback method that is called when a selection is made.
    """

    def __init__(self, lists, title,count):
        self.title = title
        self.lists = lists
        placeholder = "問題を選択してください"
        min_values = 1
        max_values = 1
        lists = lists["questions"]
        self.lists = lists
        self.count = count
        options=[discord.SelectOption(label=item["question"], value=str(index)) for index, item in enumerate(lists)]
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)
        for i in range(25, len(self.lists), 25):
            index = 0
            for item in self.lists[i:i+25]:
                option = discord.SelectOption(label=item, value=str(index))
                super().add_option(option)
                index+=1

    async def callback(self, interaction: discord.Interaction):
        selected_index = int(self.values[0])
        mode = self.lists[selected_index]["mode"]
        view = discord.ui.View()
        embed = discord.Embed(title="編集機能", color=0x00ff00)
        embed.add_field(name="選択した問題", value=self.lists[selected_index]["question"], inline=False)
        embed.add_field(name="選択した答え", value=self.lists[selected_index]["answer"], inline=False)
        if mode == 1:
            for i in self.lists[selected_index]["select"]:
                embed.add_field(name="選択肢", value=i, inline=False)
        view.add_item(EditModeSelect(self.title, selected_index, self.lists, mode,self.count))
        await interaction.response.edit_message(embed=embed,view=view)

class EditModeSelect(discord.ui.Select):
    """
    A custom select menu for selecting the mode in the Memorization Edit Discord.

    Args:
        title (str): The title of the select menu.
        selected_index (int): The index of the selected option.
        lists (list): The list of options for the select menu.
        mode (int): The mode of the select menu.
        count (int): The count of the select menu.

    Attributes:
        title (str): The title of the select menu.
        selected_index (int): The index of the selected option.
        lists (list): The list of options for the select menu.
        count (int): The count of the select menu.

    Methods:
        callback(interaction: discord.Interaction): The callback method for handling user interaction.

    """

    def __init__(self, title, selected_index, lists, mode,count):
        self.title = title
        self.selected_index = selected_index
        self.lists = lists
        self.count = count
        self.mode = mode
        if mode == 0:
            super().__init__(placeholder="選択してください",
                             min_values=1,
                             max_values=1,
                             options=[
                                    discord.SelectOption(label="問題", value="0"),
                                    discord.SelectOption(label="答え", value="1")
                                ]
                            )
        elif mode == 1:
            super().__init__(placeholder="選択してください",
                             min_values=1,
                             max_values=1,
                             options=[
                                    discord.SelectOption(label="問題", value="0"),
                                    discord.SelectOption(label="答え", value="1"),
                                    discord.SelectOption(label="選択肢", value="2")
                                ]
                            )
    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View()
        if self.values[0] == "0":
            await interaction.response.send_modal(MemorizationEditModal(self.title, self.selected_index, self.lists,0, self.count))
            return
        elif self.values[0] == "1":
            if self.mode == 1:
                view.add_item(AnsewrEditSelect(self.title, self.lists, self.selected_index))
                await interaction.response.edit_message(view=view)
                return
            else:
                await interaction.response.send_modal(MemorizationEditModal(self.title, self.selected_index, self.lists, 1, self.count))
        elif self.values[0] == "2":
            view.add_item(ChoiceEditSelect(self.title, self.selected_index, self.lists,self.count))
            await interaction.response.edit_message(view=view)


class ChoiceEditSelect(discord.ui.Select):
    """
    A custom select menu for selecting a question in the memorization edit Discord interaction.

    Attributes:
        title (str): The title of the select menu.
        selected_index (int): The index of the selected question.
        lists (list): The list of questions to choose from.
        count (int): The count of the select menu.

    Methods:
        callback(interaction: discord.Interaction): The callback method called when the select menu is interacted with.
    """

    def __init__(self, title, selected_index, lists,count):
        self.title = title
        self.selected_index = selected_index
        self.lists = lists
        self.count = count
        lists = self.lists[self.selected_index]["select"]
        placeholder = "選択してください"
        min_values = 1
        max_values = 1
        options = []
        for i in range(len(lists)):
            options.append(discord.SelectOption(label=lists[int(i)], value=str(i)))
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)
        for i in range(25, len(lists), 25):
            for item in lists[i:i+25]:
                option = discord.SelectOption(label=item)
                super().add_option(option)

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method called when the select menu is interacted with.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.
        """
        number = int(self.values[0])
        await interaction.response.send_modal(
            MemorizationEditModal(
                self.title, self.selected_index, self.lists, 2, self.count,number
            )
        )


class MemorizationEditModal(ui.Modal, title="問題編集"):
    """
    A modal for editing a memorization task in Discord.

    Args:
        title (str): The title of the modal.
        selected_index (int): The index of the selected task.
        lists (list): The list of tasks.
        mode (int): The mode of the modal.
        count (int): The count of the modal.
        selected_number (int, optional): The selected number. Defaults to None.
    """
    def __init__(self, title, selected_index, lists, mode, count,selected_number=None):
        self.title = title
        self.selected_index = selected_index
        self.lists = lists
        self.mode = mode
        self.count = count
        self.selected_number = selected_number
        super().__init__()
        if self.mode == 0:
            self.input = ui.TextInput(label="問題", style=discord.TextStyle.long)
        elif self.mode == 1:
            self.input = ui.TextInput(label="答え", style=discord.TextStyle.short)
        elif self.mode == 2:
            self.input = ui.TextInput(label="選択肢", style=discord.TextStyle.short)
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        value = str(self.input)

        memorization = memorization_maker.MemorizationSystem()
        if self.mode <= 1:
            await memorization.edit_misson(str(interaction.user.id), self.title, self.selected_index, self.mode, value)
        elif self.mode == 2:
            await memorization.edit_misson(str(interaction.user.id), self.title, self.selected_index, self.mode, value, self.selected_number)
        embed = discord.Embed(title="問題追加", description=f"現在の選択問題設定個数:{self.count}", color=0x00ff00)
        await interaction.response.edit_message(embed=embed, view=MemorizationControlView(self.title,self.count))


class MemorizationControlView(discord.ui.View):
    """
    Discord UI button for adding memorization questions.

    Args:
        title (str): The title of the memorization question.
        base_count (int, optional): The base count for the question. Defaults to 4.
    """
    def __init__(self,title,base_count=4):
        super().__init__()
        self.base_count = base_count
        self.title = title
        self.memorization = memorization_maker.MemorizationSystem()
        self.view = discord.ui.View()

    @discord.ui.button(label="問題を追加", style=discord.ButtonStyle.blurple)
    async def add(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(MemorizationAddModal(self.title))
        
    @discord.ui.button(label="選択問題を追加", style=discord.ButtonStyle.green)
    async def select_add(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(TitleSetModal(self.title,self.base_count))

    @discord.ui.button(label="選択数変更", style=discord.ButtonStyle.gray)
    async def count(self, interaction: discord.Interaction, _:discord.ui.Button):
        self.view.add_item(EditCountSelect(self.title))
        embed = discord.Embed(title="選択数変更", description=f"現在の選択問題設定個数:{self.base_count}", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=self.view)

    @discord.ui.button(label="問題を削除", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        lists = await self.memorization.get_mission(str(interaction.user.id),self.title)
        if lists is False:return await interaction.response.send_message("問題がありません",ephemeral=True)
        self.view.add_item(MemorizationDeleteSelect(lists, self.title,self.base_count))
        embed = discord.Embed(title="削除する問題を選択してください。", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=self.view)

    @discord.ui.button(label="問題編集", style=discord.ButtonStyle.red)
    async def edit(self, interaction: discord.Interaction, _:discord.ui.Button):
        lists = await self.memorization.get_mission(str(interaction.user.id),self.title)
        if lists is False:return await interaction.response.send_message("問題がありません",ephemeral=True)
        self.view.add_item(MemorizationEditSelect(lists, self.title,self.base_count))
        embed = discord.Embed(title="編集する問題を選択してください", color=0x00ff00)
        await interaction.response.edit_message(embed=embed,view=self.view)

    @discord.ui.button(label="終了", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, _:discord.ui.Button):
        sharecode = await self.memorization.get_sharecode(str(interaction.user.id),self.title)
        await interaction.response.edit_message(content=f"終了\nこの問題の共有コード:{sharecode}",embed=None,view=None)


class MemorizationCog(commands.Cog):
    def __init__(self, bot):
        """
        Initializes an instance of the class.

        Parameters:
        - bot: The Discord bot object.

        Returns:
        - None
        """
        self.bot = bot
        self.memorization = memorization_maker.MemorizationSystem()

    @app_commands.command()
    async def memorization_add(self, interaction: discord.Interaction):
        """
        メモリゼーションを追加するコマンドです。
        """
        if await self.memorization.checkuser_in_HSS(interaction) is False:return
        await interaction.response.send_modal(TitleAddModal())

    @app_commands.command()
    async def memorization_edit(self, interaction: discord.Interaction):
        """
        メモリゼーションの問題を編集するコマンドです。
        """
        if await self.memorization.checkuser_in_HSS(interaction) is False:return
        lists = await self.memorization.get_mission_title(str(interaction.user.id))
        if len(lists) == 0:return await interaction.response.send_message("問題がありません",ephemeral=True)
        view = discord.ui.View()
        view.add_item(QuestionEditSelect(lists))
        await interaction.response.send_message("編集する問題を選択してください", view=view, ephemeral=True)

    @app_commands.command()
    async def sharecode_copy(self, interaction: discord.Interaction,code:int):
        """
        共有コードから問題をコピーするコマンドです。
        """
        if await self.memorization.checkuser_in_HSS(interaction) is False:return
        await interaction.response.defer(thinking=True)
        ch = await self.memorization.sharecode_question_copy(str(interaction.user.id),code)
        await interaction.followup.send(f"{code}の問題をコピーしました" if ch else "コピー失敗")

    @app_commands.command()
    async def memorization_add_excel(self, interaction: discord.Interaction,file: discord.Attachment,title:str):
        """
        Exselファイルから問題を追加するコマンドです。
        """
        if await self.memorization.checkuser_in_HSS(interaction) is False:return
        await interaction.response.defer(thinking=True)
        file_bytes = await file.read()
        file_like_object = io.BytesIO(file_bytes)
        workbook = openpyxl.load_workbook(file_like_object)
        number = await self.memorization.make_sharecode()
        ch = await self.memorization.add_mission_Excel(str(interaction.user.id),title,number,workbook)
        await interaction.followup.send("追加完了" if ch else "追加失敗")

    @app_commands.command()
    async def memorization_sharecode(self, interaction:discord.Interaction):
        """
        共有コードを取得するコマンドです。
        """
        if await self.memorization.checkuser_in_HSS(interaction) is False:return
        lists = await self.memorization.get_mission_title(str(interaction.user.id))
        if len(lists) == 0:return await interaction.response.send_message("問題がありません",ephemeral=True)
        view = discord.ui.View()
        view.add_item(MemorizationShareSelect(lists))
        await interaction.response.send_message("共有コードを取得する問題を選択してください", view=view, ephemeral=True)

    @app_commands.command()
    async def delete_title(self,interaction:discord.Interaction):
        """
        タイトルを削除するコマンドです。
        """
        if await self.memorization.checkuser_in_HSS(interaction) is False:return
        lists = await self.memorization.get_mission_title(str(interaction.user.id))
        if len(lists) == 0:return await interaction.response.send_message("問題がありません",ephemeral=True)
        view = discord.ui.View()
        view.add_item(MemorizationTitleDeleteSelect(lists))
        await interaction.response.send_message("削除するタイトルを選択してください",view=view,ephemeral=True)

async def setup(bot):
    await bot.add_cog(MemorizationCog(bot))