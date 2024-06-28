import discord
from discord.ext import commands
from discord import app_commands
import json

class WhichHelp(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Schedule", value="schedule"),
            discord.SelectOption(label="Memorization", value="memorization")
        ]
        super().__init__(placeholder="選択してください", options=options, row=1, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        with open("help.json", "r") as f:
            HelpData = json.load(f)
        select = self.values[0]
        embed = discord.Embed(title=select,color=0x00ff00)
        for key, value in HelpData[select].items():
            embed.add_field(name=key, value=value,inline=False)
        view = discord.ui.View()
        view.add_item(WhichHelp())
        await interaction.response.edit_message(embed=embed, view=view)
    
class bot_(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="register", description="学校へのアクセス権を追加します。")
    async def register(self, interaction:discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="アクセスする",style=discord.ButtonStyle.url, url="https://hss.aknet.tech/application/6424788515065693184"))
        await interaction.response.send_message(embed=discord.Embed(title="登録", description="下のボタンから、Botを学校に追加してください。"), view=view, ephemeral=True)

    @app_commands.command(name="dashboard",description="ダッシュボードにアクセスします。")
    async def dashboard(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="アクセスする",style=discord.ButtonStyle.url, url="https://hss.aknet.tech/dashboard"))
        await interaction.response.send_message(embed=discord.Embed(title="ダッシュボード！", description=""), view=view, ephemeral=True)
        
    @app_commands.command(name="help", description="ヘルプを表示します。")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Help",color=0x00ff00)
        view = discord.ui.View()
        view.add_item(WhichHelp())
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(bot_(bot))
