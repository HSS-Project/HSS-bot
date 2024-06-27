from discord.ext import commands
import sys
import discord
import datetime
import os
import json
import traceback
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class MyBot(commands.Bot):
    def __init__(self, prefix: str, intents: discord.Intents):
        super().__init__(command_prefix=prefix, intents=intents)
    
    async def on_ready(self):
        await self.change_presence(activity=discord.Game(name="/help"))
        for file in os.listdir("./cogs"):
            if file.endswith('.py') and not file.startswith('_'):#_で始まるファイルは読み込まない
                try:
                    await self.load_extension(f'cogs.{file[:-3]}')
                    print(f"Loaded cogs: cogs.{file[:-3]}")
                except Exception as e:
                    print(f"cogs.{file[:-3]} failed to load", e)
                    traceback.print_exc()
        await self.load_extension("jishaku")
        dt_now = datetime.datetime.now()
        print("-----------------------")
        print(f"{self.user.display_name}が起動しました ")
        print(dt_now.strftime('%Y-%m-%d %H:%M'))
        print("-----------------------")
        print(discord.version_info)
        print(sys.version)
        print("-----------------------")
        for guild in self.guilds:
            print(guild.name)
        print(f"導入数 {(len(self.guilds))}")
        print("-----------------------")
        await self.tree.sync()

bot = MyBot(intents=discord.Intents.all(), prefix='k!')

if __name__ == '__main__':
    with open("token.json", 'r', encoding='utf-8') as file:
        t = json.load(file)
        TOKEN = t["TOKEN"]
    bot.run(token=TOKEN)