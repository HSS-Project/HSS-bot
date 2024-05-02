import discord
from discord.ext import commands
from discord import app_commands

from HSS.HSS import User
import json

class user(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot
        with open("token.json", 'r', encoding='utf-8') as file:
            t = json.load(file)
            self.TOKEN = t["HSSAPI_TOKEN"]
    user = app_commands.Group(name="user", description="user api")
        

        
    @user.command(name="get", description="ユーザー情報を取得します。")
    async def user_get(self, interaction:discord.Interaction):
        user = User(token=self.TOKEN)
        data = user.get_me()
        embed = discord.Embed(title=f"{data['username']}の情報")
        embed.add_field(name="デベロッパーか", value="はい" if data['developer'] else "いいえ")
        # embed.add_field(name="メールアドレス", value="プライバシー保護のため非表示")
        embed.add_field(name="HSSID", value=data["hid"])
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(user(bot))