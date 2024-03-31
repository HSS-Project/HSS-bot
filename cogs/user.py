import discord
from discord.ext import commands
from discord import app_commands

from HSS.HSS import User


class user(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot):
        self.bot = bot

    user = app_commands.Group(name="user", description="user api")
        
    @user.command(name="get", description="User/get")
    async def user_get(self, interaction:discord.Interaction):
        """ユーザー情報を取得します。"""
        user = User(token="token")
        data = user.get_me()
        embed = discord.Embed(title=f"{data['username']}の情報")
        embed.add_field(name="デベロッパーか", value="はい" if data['developer'] else "いいえ")
        # embed.add_field(name="メールアドレス", value="プライバシー保護のため非表示")
        embed.add_field(name="Discordと連携済か", value = "はい" if data["discordAccount"] else "いいえ")
        embed.add_field(name="HSSID", value=data["hid"])
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(user(bot))