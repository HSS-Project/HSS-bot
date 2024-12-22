from discord.ext import commands
from discord import app_commands
import discord
import memorization_discord.memorization_maker_add as maker_add
import memorization_discord.select_title as select_title
from memorization_maker.genre import Genre
from memorization_maker.base_question_add import Add
from memorization_maker.base_question_get import Get
from memorization_maker.memorization_vocabulary import Vocabulary
from memorization_maker.share import Share

class MemorizationCog(commands.Cog):
    def __init__(self,bot):
        self.bot:discord.Client = bot
        self.adds = Add()
        self.genres = Genre()
        self.shares = Share()
        self.get = Get()

    memorization = app_commands.Group(name="memorization", description="暗記メーカ")

    @memorization.command(name="add", description="問題を追加します。")
    async def add(self, interaction:discord.Interaction):
        await interaction.response.send_modal(maker_add.TitleModal())
    
    @memorization.command(name="add_excel", description="エクセルファイルから問題を追加します。")
    async def add_excel(self, interaction:discord.Interaction,excel:discord.Attachment,title:str):
        _sharecode = await self.shares.make_sharecode()
        await self.adds.init_add(str(interaction.user.id),title,_sharecode)
        await self.adds.add_misson_in_Excel(_sharecode,excel)
        await self.genres.add_genre(str(interaction.user.id),"default",_sharecode)
        await interaction.response.send_message("追加しました。", ephemeral=True)
    
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
        await interaction.response.send_message(embed=embed, view=select_title.SelectGenre(genre_list,3,0),ephemeral=True)
    
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
        if ctx.author.id == 705264675138568192:
            self.vocabulary = Vocabulary()
            if end_number - start_number > 100:return await ctx.send("100問までです。")
            await self.vocabulary.make_vocabulary(str(ctx.author.id), title, start_number, end_number, mode)
            await ctx.send(f"追加しました")
        else:
            await ctx.send("403 Forbidden")

async def setup(bot):
    await bot.add_cog(MemorizationCog(bot))