import discord
from discord import ui
from memorization_maker import MemorizationSystem as MS, CardData
from discord import app_commands
from discord.ext import commands


class MakerSelect(discord.ui.Select):
    def __init__(self, selectlist: list[str], title: str, question: str, count: int, ms: MS, miss_anwer_indexs: list[int]):
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
        self.miss_anwer_indexs = miss_anwer_indexs
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
            self.miss_anwer_indexs.append(self.count)
        embed = discord.Embed(title="回答結果",color=0x00ff00 if result else discord.Color.red())
        embed.add_field(name="問題",value=f"{self.question}",inline=False)
        embed.add_field(name="あなたの回答",value=f"{answer}",inline=False)
        embed.add_field(name="正誤",value=f"あなたの回答は「{ch}」です",inline=False)
        embed.add_field(name="解答",value=f"正解は「{await self.ms.get_answer(str(interaction.user.id),self.title,self.question)}」です",inline=False)
        await interaction.response.edit_message(embed=embed,view=MakerAmwerButtonContenu(self.title,self.question,self.count, self.ms, self.miss_anwer_indexs))


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

    def __init__(self, title: str, question: str, counts: int, ms: MS, miss_anwer_indexs: list[int]):
        super().__init__()
        self.title = title
        self.question = question
        self.counts = counts
        self.input = ui.TextInput(label=question, style=discord.TextStyle.short)
        self.ms = ms
        self.miss_anwer_indexs = miss_anwer_indexs
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
            self.miss_anwer_indexs.append(self.counts)
        embed = discord.Embed(title="回答結果",color=0x00ff00 if result else discord.Color.red())
        embed.add_field(name="問題", value=f"{self.question}", inline=False)
        embed.add_field(name="あなたの回答", value=f"{answer}", inline=False)
        embed.add_field(name="正誤", value=f"あなたの回答は「{ch}」です", inline=False)
        embed.add_field(name="解答", value=f"正解は「{await self.ms.get_answer(str(interaction.user.id), self.title, self.question)}」です", inline=False)
        await interaction.response.edit_message(embed=embed, view=MakerAmwerButtonContenu(self.title, self.question, self.counts, self.ms, self.miss_anwer_indexs))

class MakerAmwerButtonContenu(discord.ui.View):
    def __init__(self, title: str, question: str, count: int, ms: MS, miss_anwer_indexs: list[int]):
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
        self.miss_anwer_indexs = miss_anwer_indexs
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
        memorizationPlayMain = MemorizationPlayMain(self.title, lists, self.count, self.ms, self.miss_anwer_indexs)
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

    def __init__(self, title: str, question: str, mode: int, counts: int, ms: MS, miss_anwer_indexs,select: list[str] | None = None):
        super().__init__()
        self.title = title
        self.question = question
        self.mode = mode
        self.select = select
        self.counts = counts
        self.ms = ms
        self.miss_anwer_indexs = miss_anwer_indexs

    @discord.ui.button(label="回答する", style=discord.ButtonStyle.primary)
    async def callback(self, interaction: discord.Interaction, _: discord.ui.Button):
        if self.mode == 0:
            await interaction.response.send_modal(MakerAnswer(self.title, self.question, self.counts, self.ms, self.miss_anwer_indexs))
        elif self.mode == 1:
            assert self.select is not None
            view = discord.ui.View()
            view.add_item(MakerSelect(self.select, self.title, self.question, self.counts, self.ms, self.miss_anwer_indexs))
            await interaction.response.edit_message(view=view)


class MemorizationQuestionSelect(discord.ui.Select):
    """
    A custom select menu for selecting a memorization mission in the Memorization Discord UI.
    """

    def __init__(self, lists: list[str], ms: MS,mode:int):
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
        self.mode = mode
        super().__init__(placeholder="タイトルを選択してください", min_values=1, max_values=1, options=[discord.SelectOption(label=i) for i in lists])

    async def callback(self, interaction: discord.Interaction):
        """
        The callback method called when an option is selected.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's interaction with the select menu.

        Returns:
            None
        """
        if self.mode == 0:
            title = self.values[0]
            miss_anwer_indexs = []
            lists = await self.ms.get_mission(str(interaction.user.id), title)
            if not lists:
                return await interaction.response.send_message("エラー: データが見つかりませんでした。", ephemeral=True)
            memorizationPlayMain = MemorizationPlayMain(title, lists, 0, self.ms,miss_anwer_indexs)
            await memorizationPlayMain.main_start(interaction)
        elif self.mode == 1:
            title = self.values[0]
            dicts = await self.ms.get_user_status(str(interaction.user.id), title)
            if not dicts:
                return await interaction.response.send_message("エラー: データが見つかりませんでした。", ephemeral=True)
            score = dicts["score"]
            count = dicts["count"]
            embed = discord.Embed(title=f"{count}回挑戦", color=0x00ff00)
            embed.add_field(name="結果", value=f"問題: [{title}]のスコアは{score}点です")
            await interaction.response.edit_message(embed=embed)

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

    def __init__(self, title: str, lists: CardData, counts: int, ms: MS, miss_anwer_indexs: list[int]):
        self.title = title
        self.lists = lists["questions"]
        self.counts = counts
        self.ms = ms
        self.miss_anwer_indexs = miss_anwer_indexs
        

    async def main_start(self, interaction: discord.Interaction):
        """
        Starts the main process of the game.

        Args:
            interaction (discord.Interaction): The interaction object for Discord.
        """
        if self.counts == len(self.lists):
            dicts = await self.ms.get_user_status(str(interaction.user.id), self.title)
            if not dicts:
                return await interaction.response.send_message("エラー：ユーザーデータの取得に失敗しました。")
            score = dicts["score"] 
            count = dicts["count"]
            embed = discord.Embed(title=f"{count}回目の挑戦終了",color=0x00ff00)
            embed.add_field(name="結果",value=f"問題: [{self.title}]のスコアは{score}点です")
            embed.add_field(name="不正解問題",value=f"{len(self.miss_anwer_indexs)}問",inline=False)
            for i in self.miss_anwer_indexs:
                question = self.lists[i]["question"]
                anwer = await self.ms.get_answer(str(interaction.user.id), self.title, question)
                embed.add_field(name=f"問題: {question}",value=f"解答: {anwer}",inline=False)                
            await interaction.response.send_message(embed=embed,ephemeral=True)
            await self.ms.randam_mission_select(str(interaction.user.id), self.title)
            mission_lists = await self.ms.get_mission_selectmode_list(str(interaction.user.id), self.title)
            for i in mission_lists:
                await self.ms.select_question_randam(str(interaction.user.id), self.title, i)
            return
        if self.counts == 0:
            await self.ms.add_user_status(str(interaction.user.id), self.title)
            await self.ms.edit_user_status(str(interaction.user.id), self.title, 1, 0)
        mode = self.lists[self.counts]["mode"]
        question = self.lists[self.counts]["question"]
        embed = discord.Embed(title=f"{self.counts+1}問目",color=0x00ff00)
        embed.add_field(name="問題",value=f"{question}",inline=False)
        if mode == 0:
            view = MakerAnwerButton(self.title,question,mode,self.counts, self.ms,self.miss_anwer_indexs)
            await interaction.response.send_message(embed=embed, view=view,ephemeral=True)
        elif mode == 1:
            x = self.lists[self.counts]
            assert "select" in x
            select = x["select"]
            view = MakerAnwerButton(self.title, question, mode, self.counts, self.ms, self.miss_anwer_indexs,select)
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
        view.add_item(MemorizationQuestionSelect(title, self.ms,0))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command()
    async def get_score(self, interaction:discord.Interaction):
        """スコアを取得するコマンド"""
        title = await self.ms.get_mission_title(str(interaction.user.id))
        if not title:
            return await interaction.response.send_message("ユーザーデータが見つかりませんでした。", ephemeral=True)
        embed = discord.Embed(title="問題を選択してください",color=0x00ff00)
        view = discord.ui.View()
        view.add_item(MemorizationQuestionSelect(title, self.ms,1))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(MakerComanndsCog(bot))
    print("[SystemLog] memorization_maker_view loaded")