from discord.ext import commands
from discord import app_commands
import discord
import memorization_discord.memorization_maker_add as maker_add
import memorization_discord.select_title as select_title
from memorization_maker.inc.pakege import Genre,Get

class MemorizationCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.genre = Genre()
        self.get = Get()
    memorization = app_commands.Group(name="memorization", description="暗記メーカ")
    
    @memorization.command(name="add", description="問題を追加します。")
    async def add(self, interaction:discord.Interaction):
        await interaction.response.send_modal(maker_add.TitleModal())
        
    @memorization.command(name="edit", description="問題を編集します。")
    async def edit(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genre.get_genres_name(str(interaction.user.id))
        titles = await self.get.get_titles(str(interaction.user.id))
        await interaction.response.send_message(embed=embed, view=select_title.SelectTitleView(genre_list,titles,0))

    @memorization.command(name="play", description="問題を解きます。")
    async def play(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genre.get_genres_name(str(interaction.user.id))
        titles = await self.get.get_titles(str(interaction.user.id))
        await interaction.response.send_message(embed=embed, view=select_title.SelectTitleView(genre_list,titles,1))
        
    @memorization.command(name="misson_sharecode", description="問題を共有します。")
    async def share(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genre.get_genres_name(str(interaction.user.id))
        titles = await self.get.get_titles(str(interaction.user.id))
        await interaction.response.send_message(embed=embed, view=select_title.SelectTitleView(genre_list,titles,2))
        
    @memorization.command(name="genre_sharecode", description="ジャンルを共有します。")
    async def share2(self, interaction:discord.Interaction):
        embed = discord.Embed(title="選択してください",description="")
        genre_list = await self.genre.get_genres_name(str(interaction.user.id))
        view = discord.ui.View()
        view.add_item(select_title.SelectGenre(genre_list,2))
        await interaction.response.send_message(embed=embed, view=select_title.SelectGenre(genre_list,2))