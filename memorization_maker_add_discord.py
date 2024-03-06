import discord
from discord import ui
import memorization_maker
from discord import app_commands
from discord.ext import commands
import openpyxl
import os
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
        """
        Event handler for when the submit button is clicked.

        Parameters:
        - interaction (discord.Interaction): The interaction object representing the user's interaction with the view.

        Returns:
        - None
        """
        title = str(self.title_input.value)        
        embed = discord.Embed(title="問題追加", description=f"現在の選択問題設定個数:4", color=0x00ff00)
        await interaction.response.send_message(embed=embed, ephemeral=True, view=MemorizationControlView(title))

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
        """
        Handles the event when the user submits the form.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the bot.

        Returns:
            None

        """
        memorization = memorization_maker.MemorizationSystem()
        getcode = await memorization.sharecode_true(str(interaction.user.id),self.title)
        if not getcode:
            random_number = await memorization.make_sharecode()
        else:
            random_number = getcode
        question, answer = [str(input_item) for input_item in self.inputs]
        ch = await memorization.add_mission(str(interaction.user.id), self.title,random_number, 0, question,answer)
        if ch:
            await interaction.response.edit_message(view=MemorizationControlView(self.title))
        else:
            await interaction.response.send_message("追加失敗", ephemeral=True)

class EditCountSelect(discord.ui.Select):
    """
    A custom select menu for editing the count of selected items in the Memorization Add Discord UI.

    Args:
        title (str): The title of the select menu.

    Attributes:
        title (str): The title of the select menu.

    Methods:
        callback(interaction: discord.Interaction) -> None: The callback method that is called when the select menu is interacted with.

    """

    def __init__(self, title):
        self.title = title
        super().__init__(placeholder="選択数を選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label=str(i), value=str(i)) for i in range(1, 6)])

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method that is called when the select menu is interacted with.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.

        Returns:
            None

        """
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
        await interaction.response.send_message(embed=embed,ephemeral=True, view=MemorizationAddView(self.title, self.base_count, 1,question))

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
        a = 1
        for input_item in self.inputs:
            a += 1
            self.add_item(input_item)
        
    async def on_submit(self, interaction: discord.Interaction):
        select = [str(input_item) for input_item in self.inputs[0:]]
        embed = discord.Embed(title="選択問題", color=0x00ff00)
        a = 1
        for value in select:
            embed.add_field(name=f"選択肢:{a}", value=value, inline=False)
            a += 1
        await interaction.response.edit_message(embed=embed, view=MemorizationAddView(self.title, self.base_count, 2, self.question, select))

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
        """
        コンストラクタメソッドです。

        :param title: タイトル
        :type title: str
        :param base_count: ベースの数
        :type base_count: int
        :param question: 質問
        :type question: str
        :param select: 選択肢
        :type select: str
        """
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
            """
            Callback function for handling interaction with a selection question.

            Parameters:
            - interaction (discord.Interaction): The interaction object representing the user's interaction.

            Returns:
            - None
            """
            self.answer = self.values[0]
            embed = discord.Embed(title="選択問題", color=0x00ff00)
            a = 1
            for value in self.select:
                embed.add_field(name=f"選択肢{a}", value=value, inline=False)
                a += 1
            embed.add_field(name="答え", value=self.answer, inline=False)
            memorizationmaker = memorization_maker.MemorizationSystem()
            getcode = await memorizationmaker.sharecode_true(str(interaction.user.id),self.title)
            if not getcode:
                random_number = await memorizationmaker.make_sharecode()
            else:
                random_number = getcode
            await memorizationmaker.add_mission(str(interaction.user.id), self.title, random_number,1, self.question, self.answer, self.select)
            await interaction.response.edit_message(embed=embed, view=None)


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
        """
        Switches the mode of the select button and sends the appropriate modal.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button object.
            mode (int): The mode of the select button.
        """
        if mode == 0:
            await interaction.response.send_modal(TitleSetModal(self.title))
        elif mode == 1:
            await interaction.response.send_modal(QuestionAddModal(self.title, self.base_count, self.question))
        elif mode == 2:
            view = discord.ui.View()
            view.add_item(AnswerAddSelect(self.title, self.base_count, self.question, self.select))
            await interaction.response.edit_message(view=view)
    
    
    @discord.ui.button(label="続行", style=discord.ButtonStyle.blurple)
    async def continue_(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Continues the select button interaction.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button object.
        """
        await self.swithcing(interaction, button, self.mode)

class QuestionEditSelect(discord.ui.Select):
    """
    A custom select menu for selecting a memorization mission in the Memorization Discord UI.
    """
    def __init__(self, lists):
        """
        Initializes the Memorization_questionDiscordSelect object.
        """
        placeholder = "タイトルを選択してください"
        min_values = 1
        max_values = 1
        self.lists = lists
        options_1 = [discord.SelectOption(label=item) for item in self.lists[:25]]
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options_1)
        for i in range(25, len(self.lists), 25):
            for item in self.lists[i:i+25]:
                option = discord.SelectOption(label=item)
                super().add_option(option)

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

    Methods:
    - callback(interaction): The callback method called when an option is selected.
    """

    def __init__(self, lists, title):
        """
        Initializes the MemorizationDelete_DiscordSelect object.

        Parameters:
        - lists (list): The list of options for the select menu.
        - title (str): The title of the mission to be deleted.
        """
        self.title = title
        placeholder = "問題を選択してください"
        min_values = 1
        max_values = 1
        lists = lists["questions"]
        self.lists = lists
        options=[discord.SelectOption(label=item["question"], value=str(index)) for index, item in enumerate(lists)]
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)
        for i in range(25, len(self.lists), 25):
            for item in self.lists[i:i+25]:
                option = discord.SelectOption(label=item)
                super().add_option(option)

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method called when an option is selected.

        Parameters:
        - interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.
        """
        selected_index = int(self.values[0])
        selected_question = self.lists[selected_index]["question"]
        memorization = memorization_maker.MemorizationSystem()
        await memorization.del_mission(str(interaction.user.id), self.title, selected_question)
        embed = discord.Embed(title="問題追加", color=0x00ff00)
        await interaction.response.edit_message(embed=embed, view=MemorizationControlView(self.title))

class MemorizationShareSelect(discord.ui.Select):
    """
    A custom select component for selecting a title for memorization sharing.
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
        """
        Callback method called when the select component is interacted with.

        Parameters:
        - interaction (discord.Interaction): The interaction object representing the user's interaction.
        """
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

    def __init__(self, list):
        
        placeholder = "問題を選択してください"
        min_values = 1
        max_values = 1
        lists = lists["questions"]
        self.lists = list
        options=[discord.SelectOption(label=item["question"], value=str(index)) for index, item in enumerate(lists)]
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)
        for i in range(25, len(self.lists), 25):
            for item in self.lists[i:i+25]:
                option = discord.SelectOption(label=item)
                super().add_option(option)

    async def callback(self, interaction: discord.Interaction):
        """
        Callback method called when the select component is interacted with.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the select component.

        """
        memorization = memorization_maker.MemorizationSystem()
        await memorization.del_mission_title(str(interaction.user.id), self.values[0])
        await interaction.response.edit_message(content="削除完了", view=None)

class MemorizationEditSelect(discord.ui.Select):
    """
    A custom select menu for selecting a question in the Memorization Edit Discord UI.

    Attributes:
    - lists (list): The list of questions to be displayed in the select menu.
    - title (str): The title of the select menu.

    Methods:
    - __init__(self, lists, title): Initializes the MemorizationEditDiscordSelect object.
    - callback(self, interaction): The callback method that is called when a selection is made.
    """

    def __init__(self, lists, title):
        """
        Initializes the MemorizationEditDiscordSelect object.

        Parameters:
        - lists (list): The list of questions to be displayed in the select menu.
        - title (str): The title of the select menu.
        """
        self.title = title
        self.lists = lists
        placeholder = "問題を選択してください"
        min_values = 1
        max_values = 1
        lists = lists["questions"]
        self.lists = lists
        options=[discord.SelectOption(label=item["question"], value=str(index)) for index, item in enumerate(lists)]
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, options=options)
        for i in range(25, len(self.lists), 25):
            for item in self.lists[i:i+25]:
                option = discord.SelectOption(label=item)
                super().add_option(option)

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method that is called when a selection is made.

        Parameters:
        - interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.
        """
        selected_index = int(self.values[0])
        mode = self.lists[selected_index]["mode"]
        view = discord.ui.View()
        view.add_item(EditModeSelect(self.title, selected_index, self.lists, mode))
        await interaction.response.edit_message(view=view)

class EditModeSelect(discord.ui.Select):
    """
    A custom select menu for selecting the mode in the Memorization Edit Discord.

    Args:
        title (str): The title of the select menu.
        selected_index (int): The index of the selected option.
        lists (list): The list of options for the select menu.
        mode (int): The mode of the select menu.

    Attributes:
        title (str): The title of the select menu.
        selected_index (int): The index of the selected option.
        lists (list): The list of options for the select menu.

    Methods:
        callback(interaction: discord.Interaction): The callback method for handling user interaction.

    """

    def __init__(self, title, selected_index, lists, mode):
        self.title = title
        self.selected_index = selected_index
        self.lists = lists
        if mode == 0:
            super().__init__(placeholder="選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label="問題", value="0"), discord.SelectOption(label="答え", value="1")])
        elif mode == 1:
            super().__init__(placeholder="選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label="問題", value="0"), discord.SelectOption(label="答え", value="1"), discord.SelectOption(label="選択肢", value="2")])

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method for handling user interaction.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.

        Returns:
            None

        """
        if self.values[0] == "0":
            await interaction.response.send_modal(MemorizationEditModal(self.title, self.selected_index, self.lists, 0))
        elif self.values[0] == "1":
            await interaction.response.send_modal(MemorizationEditModal(self.title, self.selected_index, self.lists, 1))
        elif self.values[0] == "2":
            view = discord.ui.View()
            view.add_item(ChoiceEditSelect(self.title, self.selected_index, self.lists))
            await interaction.response.edit_message(view=view)


class ChoiceEditSelect(discord.ui.Select):
    """
    A custom select menu for selecting a question in the memorization edit Discord interaction.

    Attributes:
        title (str): The title of the select menu.
        selected_index (int): The index of the selected question.
        lists (list): The list of questions to choose from.

    Methods:
        callback(interaction: discord.Interaction): The callback method called when the select menu is interacted with.
    """

    def __init__(self, title, selected_index, lists):
        """
        Initializes a MemorizationEditDiscordSelectMenu instance.

        Args:
            title (str): The title of the select menu.
            selected_index (int): The index of the selected question.
            lists (list): The list of questions to choose from.
        """
        self.title = title
        self.selected_index = selected_index
        self.lists = lists
        lists = self.lists[self.selected_index]["select"]
        placeholder = "選択してください"
        min_values = 1
        max_values = 1
        options = [discord.SelectOption(label=i) for i in lists[:25]]
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
                self.title, self.selected_index, self.lists, 2, number
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
        selected_number (int, optional): The selected number. Defaults to None.
    """

    def __init__(self, title, selected_index, lists, mode, selected_number=None):
        self.title = title
        self.selected_index = selected_index
        self.lists = lists
        self.mode = mode
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
        if self.mode == 1:
            try:
                values = int(value)
            except:
                await interaction.response.edit_message(content="選択肢は数字を入力してください", view=None)
                return
        if self.mode <= 1:
            await memorization.edit_misson(str(interaction.user.id), self.title, self.selected_index, self.mode, value)
        elif self.mode == 2:
            await memorization.edit_misson(str(interaction.user.id), self.title, self.selected_index, self.mode, value, self.selected_number)
        await interaction.response.edit_message(content="編集完了", view=None)

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

    @discord.ui.button(label="問題を追加", style=discord.ButtonStyle.blurple)
    async def add(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(MemorizationAddModal(self.title))
        
    @discord.ui.button(label="選択問題を追加", style=discord.ButtonStyle.green)
    async def select_add(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(TitleSetModal(self.title,self.base_count))

    @discord.ui.button(label="選択数変更", style=discord.ButtonStyle.gray)
    async def count(self, interaction: discord.Interaction, _:discord.ui.Button):
        view = discord.ui.View()
        view.add_item(EditCountSelect(self.title))
        await interaction.response.edit_message(view=view)

    @discord.ui.button(label="問題を削除", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        memorization = memorization_maker.MemorizationSystem()
        lists = await memorization.get_mission(str(interaction.user.id),self.title)
        if lists:
            view = discord.ui.View()
            view.add_item(MemorizationDeleteSelect(lists, self.title))
            embed = discord.Embed(title="削除する問題を選択してください。", color=0x00ff00)
            await interaction.response.send_message(embed=embed,view=view,ephemeral=True)
        else:
            await interaction.response.send_message("問題がありません",ephemeral=True)

    @discord.ui.button(label="問題編集", style=discord.ButtonStyle.red)
    async def edit(self, interaction: discord.Interaction, _:discord.ui.Button):
        memorization = memorization_maker.MemorizationSystem()
        lists = await memorization.get_mission(str(interaction.user.id),self.title)
        if lists:
            view = discord.ui.View()
            view.add_item(MemorizationEditSelect(lists, self.title))
            await interaction.response.send_message("編集する問題を選択してください",view=view,ephemeral=True)
        else:
            await interaction.response.send_message("問題がありません",ephemeral=True)

    @discord.ui.button(label="終了", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, _:discord.ui.Button):
        memorization = memorization_maker.MemorizationSystem()
        sharecode = await memorization.get_sharecode(str(interaction.user.id),self.title)
        await interaction.response.edit_message(content=f"終了\nこの問題の共有コード:{sharecode}",view=None)
        
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
        await interaction.response.send_modal(TitleAddModal())

    @app_commands.command()
    async def memorization_edit(self, interaction: discord.Interaction):
        """
        メモリゼーションの問題を編集するコマンドです。
        """
        lists = await self.memorization.get_mission_title(str(interaction.user.id))
        view = discord.ui.View()
        view.add_item(QuestionEditSelect(lists))
        await interaction.response.send_message("編集する問題を選択してください", view=view, ephemeral=True)


    @app_commands.command()
    async def sharecode_copy(self, interaction: discord.Interaction,code:int):
        """
        共有コードから問題をコピーするコマンドです。
        """
        ch = await self.memorization.sharecode_question_copy(str(interaction.user.id),code)
        if ch:
            await interaction.response.send_message("コピー完了", ephemeral=True)
        else:
            await interaction.response.send_message("コピー失敗", ephemeral=True)

    @app_commands.command()
    async def memorization_add_excel(self, interaction: discord.Interaction,file: discord.Attachment,title:str):
        """
        Exselファイルから問題を追加するコマンドです。
        """
        if not file:
            await interaction.response.send_message("ファイルがありません", ephemeral=True)
            return
        file_bytes = await file.read()
        file_like_object = io.BytesIO(file_bytes)
        workbook = openpyxl.load_workbook(file_like_object)
        id = str(interaction.user.id)
        number = await self.memorization.make_sharecode()
        await interaction.response.defer(thinking=True)
        ch = await self.memorization.add_mission_into_Excel(id,title,number,workbook)
        workbook.close()
        if ch:
            await interaction.followup.send("追加完了", ephemeral=True)
        else:
            await interaction.followup.send("追加失敗", ephemeral=True)

    @app_commands.command()
    async def memorization_sharecode(self, interaction:discord.Interaction):
        """
        共有コードを取得するコマンドです。
        """
        lists = await self.memorization.get_mission_title(str(interaction.user.id))
        view = discord.ui.View()
        view.add_item(MemorizationShareSelect(lists))
        await interaction.response.send_message("共有コードを取得する問題を選択してください", view=view, ephemeral=True)

    @app_commands.command()
    async def delete_title(self,intearction:discord.Interaction):
        """
        タイトルを削除するコマンドです。
        """
        lists = await self.memorization.get_mission_title(str(intearction.user.id))
        view = discord.ui.View()
        view.add_item(MemorizationTitleDeleteSelect(lists))
        await intearction.response.send_message("削除するタイトルを選択してください",view=view,ephemeral=True)

async def setup(bot):
    await bot.add_cog(MemorizationCog(bot))
    print("[SystemLog] memorization_maker_add_discord loaded")