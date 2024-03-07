import discord
from discord import ui
from memorization_maker import MemorizationSystem as MS, ProblemData
from discord import app_commands
from discord.ext import commands


class MakerSelect(discord.ui.Select):
    def __init__(self, selectlist: list[str], title: str, question: str, count: int, ms: MS):
        """
        Initializes a MakerSelect object.

        Args:
        - selectlist (list): A list of options for the select dropdown.
        - title (str): The title of the question.
        - question (str): The question to be displayed.
        - count (int): The count of the question.

        Returns:
        - None
        """
        self.ms = ms
        self.title = title  
        self.question = question
        self.count = count
        super().__init__(placeholder="選択してください。", min_values=1, max_values=1, options=[discord.SelectOption(label=selectlist[i]) for i in range(len(selectlist))])

    async def callback(self, interaction: discord.Interaction):
        """
        Callback function for the select dropdown.

        Args:
        - interaction (discord.Interaction): The interaction object.

        Returns:
        - None
        """
        answer = self.values[0]
        result = await self.ms.check_answer(str(interaction.user.id), self.title,self.question,answer,1)
        if result:
            await self.ms.edit_user_status(str(interaction.user.id),self.title,0,1)
            ch = "正解"
        else:
            ch = "不正解"
        embed = discord.Embed(title="回答結果",color=0x00ff00)
        embed.add_field(name="あなたの回答",value=f"{answer}",inline=False)
        embed.add_field(name="正誤",value=f"あなたの回答は{ch}です",inline=False)
        await interaction.response.edit_message(embed=embed,view=MakerAmwerButtonContenu(self.title,self.question,self.count, self.ms))


class MakerAnswer(ui.Modal,title="回答"):
    """
    A class representing the modal for answering a question in the memorization maker system.

    Args:
    - title (str): The title of the modal.
    - question (str): The question to be answered.
    - counts (int): The number of counts.

    Attributes:
    - title (str): The title of the modal.
    - question (str): The question to be answered.
    - counts (int): The number of counts.
    - input (ui.TextInput): The input field for the answer.

    Methods:
    - on_submit(interaction: discord.Interaction): Handles the submission of the answer.
    """

    def __init__(self, title: str, question: str, counts: int, ms: MS):
        super().__init__()
        self.title = title
        self.question = question
        self.counts = counts
        self.input = ui.TextInput(label=question, style=discord.TextStyle.short)
        self.ms = ms
        self.add_item(self.input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        Handles the submission of the answer.

        Args:
        - interaction (discord.Interaction): The interaction object representing the user's interaction.

        Returns:
        - None
        """
        answer = str(self.input.value)
        result = await self.ms.check_answer(str(interaction.user.id), self.title, self.question, answer, 0)
        if result:
            await self.ms.edit_user_status(str(interaction.user.id), self.title, 0, 1)
            ch = "正解"
        else:
            ch = "不正解"
        embed = discord.Embed(title="回答結果", color=0x00ff00)
        embed.add_field(name="あなたの回答", value=f"{answer}", inline=False)
        embed.add_field(name="正誤", value=f"あなたの回答は{ch}です", inline=False)
        await interaction.response.edit_message(embed=embed, view=MakerAmwerButtonContenu(self.title, self.question, self.counts, self.ms))

class MakerAmwerButtonContenu(discord.ui.View):
    def __init__(self, title: str, question: str, count: int, ms: MS):
        """
        コンストラクタ

        :param title: タイトル
        :param question: 質問
        :param count: カウント
        """
        self.title = title
        self.question = question
        self.count = count
        self.ms = ms
        super().__init__()

    @discord.ui.button(label="次に進む", style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction, _: discord.ui.Button):
        """
        ボタンのコールバック関数

        :param interaction: インタラクション
        :param button: ボタン
        """
        self.count += 1
        lists = await self.ms.get_mission(str(interaction.user.id), self.title)
        if not lists:
            return await interaction.response.send_message("エラー: データが見つかりませんでした。", ephemeral=True)
        memorizationPlayMain = MemorizationPlayMain(self.title, lists, self.count, self.ms)
        await memorizationPlayMain.main_start(interaction)

class MakerAnwerButton(discord.ui.View):
    """
    A custom button class for answering questions in the memorization maker view.

    Attributes:
        title (str): The title of the question.
        question (str): The content of the question.
        mode (int): The mode of the view.
        counts (int): The number of counts.
        select (Optional): The optional select parameter.

    Methods:
        callback(interaction: discord.Interaction, button: discord.ui.Button) -> None:
            The callback method for handling button interactions.
    """

    def __init__(self, title: str, question: str, mode: int, counts: int, ms: MS, select: list[str] | None = None):
        super().__init__()
        self.title = title
        self.question = question
        self.mode = mode
        self.select = select
        self.counts = counts
        self.ms = ms

    @discord.ui.button(label="回答する", style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self.mode == 0:
            await interaction.response.send_modal(MakerAnswer(self.title, self.question, self.counts, self.ms))
        elif self.mode == 1:
            assert self.select is not None
            view = discord.ui.View()
            view.add_item(MakerSelect(self.select, self.title, self.question, self.counts, self.ms))
            await interaction.response.edit_message(view=view)


class MemorizationQuestionSelect(discord.ui.Select):
    """
    A custom select menu for selecting a memorization mission in the Memorization Discord UI.
    """

    def __init__(self, lists: list[str], ms: MS):
        """
        Initializes the Memorization_question_Discord_Select object.

        Args:
            lists (list): The list of options to be displayed in the select menu.
            mode (str): The mode of the memorization mission.

        Returns:
            None
        """
        self.lists = lists
        self.ms = ms
        super().__init__(placeholder="タイトルを選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label=i) for i in lists])

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method called when an option is selected.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.

        Returns:
            None
        """
        title = self.values[0]
        lists = await self.ms.get_mission(str(interaction.user.id), title)
        if not lists:
            return await interaction.response.send_message("エラー: データが見つかりませんでした。", ephemeral=True)
        memorizationPlayMain = MemorizationPlayMain(title, lists, 0, self.ms)
        await memorizationPlayMain.main_start(interaction)


class MemorizationPlayMain:
    """
    Represents a class for playing the memorization game.

    Attributes:
        title (str): The title of the game.
        lists (dict): The lists of content for the game.
        counts (int): The number of times the game has been played.
        interaction (discord.Interaction): The interaction object for Discord.

    Methods:
        main_start(interaction: discord.Interaction): Starts the main process of the game.
    """

    def __init__(self, title: str, lists: list[ProblemData], counts: int, ms: MS):
        self.title = title
        self.lists = lists
        self.counts = counts
        self.ms = ms

    async def main_start(self, interaction: discord.Interaction):
        """
        Starts the main process of the game.

        Args:
            interaction (discord.Interaction): The interaction object for Discord.
        """
        self.lists = self.lists["questions"]
        if self.counts == len(self.lists):
            dicts = await self.ms.get_user_status(str(interaction.user.id), self.title)
            if not dicts:
                return await interaction.response.send_message("エラー：ユーザーデータの取得に失敗しました。")
            score = dicts["score"] 
            count = dicts["count"]
            embed = discord.Embed(title=f"{count}回目の挑戦終了",color=0x00ff00)
            embed.add_field(name="結果",value=f"問題: [{self.title}]のスコアは{score}点です")
            return await interaction.response.send_message(embed=embed,ephemeral=True)
        if self.counts == 0:
            await self.ms.add_user_status(str(interaction.user.id), self.title)
            await self.ms.edit_user_status(str(interaction.user.id), self.title, 1, 0)
        mode = self.lists[self.counts]["mode"]
        question = self.lists[self.counts]["question"]
        embed = discord.Embed(title=f"{self.counts+1}問目",color=0x00ff00)
        embed.add_field(name="問題",value=f"{question}",inline=False)
        if mode == 0:
            view = MakerAnwerButton(self.title,question,mode,self.counts, self.ms)
            await interaction.response.send_message(embed=embed, view=view,ephemeral=True)
        elif mode == 1:
            x = self.lists[self.counts]
            assert "select" in x
            select = x["select"]
            view = MakerAnwerButton(self.title, question, mode, self.counts, self.ms, select)
            await interaction.response.send_message(embed=embed, view=view,ephemeral=True)


class MakerComanndsCog(commands.Cog):
    """コグクラス: メモリゼーションメーカーのコマンドを管理するクラス"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ms = MS()

    @app_commands.command()
    async def memorization_maker_view(self, interaction:discord.Interaction):
        """問題を表示するコマンド"""
        title = await self.ms.get_mission_title(str(interaction.user.id))
        if not title:
            return await interaction.response.send_message("ユーザーデータが見つかりませんでした。", ephemeral=True)
        embed = discord.Embed(title="問題を選択してください",color=0x00ff00)
        view = discord.ui.View()
        view.add_item(MemorizationQuestionSelect(title, self.ms))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


    @app_commands.command()
    async def anki_help(self, interaction:discord.Interaction):
        """ヘルプコマンド"""
        embed = discord.Embed(title="暗記機能help ver0.0.1 Beta",color=0x00ff00)
        embed.add_field(name="memorization_maker_view",value="問題回答スタート",inline=False)
        embed.add_field(name="memorization_add",value="問題追加",inline=False)
        embed.add_field(name="memorization_edit",value="問題編集",inline=False)
        embed.add_field(name="delete_title",value="問題削除",inline=False)
        embed.add_field(name="memorization_add_excel",value="エクセルから問題を追加 (Aに問題 Bに答え)",inline=False)
        embed.add_field(name="memorization_sharecode",value="問題を共有するための共有コードを取得します。",inline=False)
        embed.add_field(name="sharecode_copy",value="共有コードから問題を取得し、保存します。",inline=False)
        await interaction.response.send_message(embed=embed,ephemeral=True)
async def setup(bot):
    await bot.add_cog(MakerComanndsCog(bot))
    print("[SystemLog] memorization_maker_view loaded")