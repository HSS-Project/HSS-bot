import discord
from discord.ext import commands
from discord import app_commands


class bot_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register", description="学校へのアクセス権を追加します。")
    async def register(self, interaction:discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="アクセスする",style=discord.ButtonStyle.url, url="https://hss.aknet.tech/application/6392922062414939136"))
        await interaction.response.send_message(embed=discord.Embed(title="登録", description="下のボタンから、Botを学校に追加してください。"), view=view, ephemeral=True)

    @app_commands.command(name="dashboard",description="ダッシュボードにアクセスします。")
    async def dashboard(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="アクセスする",style=discord.ButtonStyle.url, url="https://hss.aknet.tech/dashboard"))
        await interaction.response.send_message(embed=discord.Embed(title="ダッシュボード！", description=""), view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(bot_(bot))