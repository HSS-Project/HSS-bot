from discord.ext import commands
from discord import app_commands
import discord
import json
import importlib.util
import random
import memorization_discord.memorization_maker_add as maker_add
import memorization_discord.select_title as select_title
from memorization_maker.genre import Genre
from memorization_maker.base_question_add import Add
from memorization_maker.base_question_get import Get
from memorization_maker.memorization_vocabulary import Vocabulary
from memorization_maker.share import Share

class MemorizationCog(commands.Cog):
    OWNER_ID = 705264675138568192

    def __init__(self,bot):
        self.bot:discord.Client = bot
        self.adds = Add()
        self.genres = Genre()
        self.shares = Share()
        self.get = Get()

    def _load_gemini_api_key(self):
        try:
            with open("token.json", "r", encoding="utf-8") as file:
                token_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

        return token_data.get("GEMINI_API_KEY") or token_data.get("GEMINI_KEY") or token_data.get("GENAI_API_KEY")

    memorization = app_commands.Group(name="memorization", description="暗記メーカ")

    @memorization.command(name="add", description="問題を追加します。")
    async def add(self, interaction:discord.Interaction):
        await interaction.response.send_modal(maker_add.TitleModal())
    
    @memorization.command(name="add_excel", description="エクセルファイルから問題を追加します。")
    async def add_excel(self, interaction:discord.Interaction,excel:discord.Attachment,title:str):
        # 拡張子のバリデーション
        if not (excel.filename.lower().endswith(".xlsx") or excel.filename.lower().endswith(".xlsm")):
            return await interaction.response.send_message(
                "エクセルファイル (.xlsx または .xlsm) を添付してください。.xls などの旧形式やその他のファイル形式には対応していません。", 
                ephemeral=True
            )

        _sharecode = await self.shares.make_sharecode()
        if _sharecode is None:
            return await interaction.response.send_message("共有コードの生成に失敗しました。", ephemeral=True)
        
        if not await self.adds.init_add(str(interaction.user.id), title, _sharecode):
            return await interaction.response.send_message("タイトルの初期化に失敗しました。", ephemeral=True)
        
        try:
            success = await self.adds.add_misson_in_Excel(_sharecode, excel)
            if not success:
                raise ValueError("エクセルファイルの解析に失敗しました。問題が足りないか、シートのフォーマットが正しくない可能性があります。(※問題は最低5件以上必要です)")
        except Exception as e:
            # ロールバック処理: 作成された共有コードをデータベースから削除する
            base_data = await self.adds.rw.load_base()
            if _sharecode in base_data.get("memorization", {}):
                del base_data["memorization"][_sharecode]
                await self.adds.rw.write_base(base_data)
            
            # エラー内容に応じた分かりやすいメッセージ
            error_name = type(e).__name__
            if error_name == "BadZipFile":
                error_msg = "エクセルファイルの読み込み中にエラーが発生しました: ファイルが破損しているか、対応していない形式（例: 旧式の.xlsファイルなど）の可能性があります。.xlsx 形式であることを確認してください。"
            else:
                error_msg = f"エクセルファイルの処理中にエラーが発生しました: {e}"
            
            return await interaction.response.send_message(error_msg, ephemeral=True)
            
        await self.genres.add_genre(str(interaction.user.id),"default",_sharecode)
        await interaction.response.send_message("追加しました。", ephemeral=True)

    @commands.command(name="add_pdf", description="PDFファイルから問題を追加します。タイトルの後に任意でAIへの指令を追加できます。")
    async def add_pdf(self, ctx, title: str, *ai_instruction: str):
        if ctx.author.id != self.OWNER_ID:
            return await ctx.send("403 Forbidden")

        pdf_attachment = next((attachment for attachment in ctx.message.attachments if attachment.filename.lower().endswith(".pdf")), None)
        if pdf_attachment is None:
            return await ctx.send("PDFファイルを添付してください。")

        api_key = self._load_gemini_api_key()
        if not api_key:
            return await ctx.send("token.json に GEMINI_API_KEY を追加してください。")

        # 必要なランタイム依存をチェック
        if importlib.util.find_spec("google.genai") is None or importlib.util.find_spec("pypdf") is None:
            return await ctx.send("依存ライブラリが不足しています。まずリポジトリのルートで次を実行してください:\n```\npip install -r requirements.txt\n```")
        desired_count = None
        ai_instruction_text = None
        if ai_instruction:
            first = ai_instruction[0]
            try:
                desired_count = int(first)
                rest = ai_instruction[1:]
            except Exception:
                rest = ai_instruction
            ai_instruction_text = " ".join(rest).strip() if rest else None

        # 問題数: 指定がなければ 40〜60 の範囲でランダムに決定、指定があれば最大100で上限
        if desired_count is None:
            max_q = random.randint(40, 60)
        else:
            max_q = max(1, min(desired_count, 100))
        async with ctx.typing():
            questions = await self.adds.generate_questions_from_pdf(pdf_attachment, api_key, max_questions=max_q, force_mode=1, ai_instruction=ai_instruction_text)
        if not questions:
            return await ctx.send("PDFから問題を生成できませんでした。")

        _sharecode = await self.shares.make_sharecode()
        if _sharecode is None:
            return await ctx.send("共有コードの生成に失敗しました。")
        if not await self.adds.init_add(str(ctx.author.id), title, _sharecode):
            return await ctx.send("タイトルの作成に失敗しました。")

        if not await self.adds.add_generated_questions(_sharecode, questions):
            return await ctx.send("問題の保存に失敗しました。")

        await self.genres.add_genre(str(ctx.author.id), "default", _sharecode)
        await ctx.send(f"追加しました。{len(questions)}問を生成しました。")
    
    @memorization.command(name="edit", description="問題を編集します。")
    async def edit(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genres.get_genres_name(str(interaction.user.id))
        titles = await self.genres.genres_in_titles(str(interaction.user.id),"default")
        await interaction.response.send_message(embed=embed, view=select_title.SelectTitleView(genre_list,titles,0),ephemeral=True)

    @memorization.command(name="play", description="問題を解きます。")
    async def play(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genres.get_genres_name(str(interaction.user.id))
        titles = await self.genres.genres_in_titles(str(interaction.user.id),"default")
        await interaction.response.send_message(embed=embed, view=select_title.SelectTitleView(genre_list,titles,1),ephemeral=True)

    @memorization.command(name="sheet", description="問題の暗記シートを生成します。")
    async def sheet(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genres.get_genres_name(str(interaction.user.id))
        titles = await self.genres.genres_in_titles(str(interaction.user.id),"default")
        await interaction.response.send_message(embed=embed, view=select_title.SelectTitleView(genre_list,titles,5))
        
    @memorization.command(name="misson_sharecode", description="問題を共有します。")
    async def share(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genres.get_genres_name(str(interaction.user.id))
        titles = await self.genres.genres_in_titles(str(interaction.user.id),"default")
        await interaction.response.send_message(embed=embed, view=select_title.SelectTitleView(genre_list,titles,2),ephemeral=True)
        
    @memorization.command(name="genre_sharecode", description="ジャンルを共有します。")
    async def share2(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genres.get_genres_name(str(interaction.user.id))
        view = discord.ui.View()
        view.add_item(select_title.SelectGenre(genre_list,2,2))
        await interaction.response.send_message(embed=embed, view=view,ephemeral=True)
    
    @memorization.command(name="misson_set", description="共有コードから問題を追加します。")
    async def misson(self, interaction:discord.Interaction,sharecode:int,genre:str="default"):
        await self.genres.make_genre(str(interaction.user.id),genre)
        ch = await self.genres.add_genre(str(interaction.user.id),genre,sharecode)
        if ch:await interaction.response.send_message("追加しました。", ephemeral=True)
        else:await interaction.response.send_message("追加に失敗しました。", ephemeral=True)
    
    @memorization.command(name="genre_set", description="共有コードからジャンルを追加します。")
    async def genre(self, interaction:discord.Interaction,sharecode:int):
        await self.genres.make_genre(str(interaction.user.id),"default")
        if await self.genres.len_genre(str(interaction.user.id)) >= 25:return await interaction.response.send_message("ジャンルは25個までです。どれか削除してください", ephemeral=True)
        ch = await self.genres.share_genere_set(str(interaction.user.id),sharecode)
        if ch:await interaction.response.send_message("追加しました。", ephemeral=True)
        else:await interaction.response.send_message("追加に失敗しました。", ephemeral=True)

    @memorization.command(name="genre_delete", description="ジャンルを削除します。")
    async def delete2(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genres.get_genres_name(str(interaction.user.id))
        view = discord.ui.View()
        view.add_item(select_title.SelectGenre(genre_list,3,0))
        await interaction.response.send_message(embed=embed, view=view,ephemeral=True)
    
    @memorization.command(name="all_misson_delete",description="問題を完全削除します")
    async def all_delete(self,interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genres.get_genres_name(str(interaction.user.id))
        titles = await self.genres.genres_in_titles(str(interaction.user.id),"default")
        await interaction.response.send_message(embed=embed, view=select_title.SelectTitleView(genre_list,titles,4),ephemeral=True)
        
    @memorization.command(name="misson_delete", description="個人の問題リストから問題を削除します。")
    async def delete(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genres.get_genres_name(str(interaction.user.id))
        titles = await self.genres.genres_in_titles(str(interaction.user.id),"default")
        await interaction.response.send_message(embed=embed, view=select_title.SelectTitleView(genre_list,titles,3),ephemeral=True)

    @commands.command(name="add_vo", description="問題を追加します。")
    async def add_vocabulary(self, ctx, title: str, start_number: int, end_number: int, mode:int = 0):
        if ctx.author.id == self.OWNER_ID:
            self.vocabulary = Vocabulary()
            if end_number - start_number > 100:return await ctx.send("100問までです。")
            await self.vocabulary.make_vocabulary(str(ctx.author.id), title, start_number, end_number, mode)
            await ctx.send(f"追加しました")
        else:
            await ctx.send("403 Forbidden")

    @commands.command(name="gemini", description="Geminiに質問します。")
    async def ask_gemini(self, ctx, *, prompt: str):
        if ctx.author.id != self.OWNER_ID:
            return await ctx.send("403 Forbidden")

        api_key = self._load_gemini_api_key()
        if not api_key:
            return await ctx.send("GEMINI_API_KEY を追加してください。")
        from google import genai
        
        async with ctx.typing():
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=prompt
                )
                
                text = response.text
                if len(text) > 2000:
                    for i in range(0, len(text), 2000):
                        await ctx.send(text[i:i+2000])
                else:
                    await ctx.send(text)
            except Exception as e:
                await ctx.send(f"エラーが発生しました: {e}")

async def setup(bot):
    await bot.add_cog(MemorizationCog(bot))