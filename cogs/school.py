import discord
from discord.ext import commands
from discord import app_commands


from HSS import School
import requests
import json
from typing import Literal
import os
import json

class patch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    school = app_commands.Group(name="school", description="school api")

    @school.command(name="patch", description="school/patch")
    @app_commands.choices(date=[
        app_commands.Choice(name="月曜日", value="mon"),
        app_commands.Choice(name="火曜日", value="tue"),
        app_commands.Choice(name="水曜日", value="wed"),
        app_commands.Choice(name="木曜日", value="thu"),
        app_commands.Choice(name="金曜日", value="fri"),
        app_commands.Choice(name="土曜日", value="sat"),
        app_commands.Choice(name="日曜日", value="sun")
    ]
    )
    async def school_patch(self,interaction:discord.Interaction, date: app_commands.Choice[str], grade:int, class_number:int, time:int):
        await interaction.response.defer()
        school = School(token="token", schoolid="6392060546862023680")
        print(school.get_data())
        class_index = school.search_class(grade, class_number)
        print(class_index)
        timeline = school.get_timeline(class_index, date.value)
        print(timeline)
        
        
        data = {"name":"おいしそうなごはん", "place":"しぜんがかりはうす"}
        jsons = json.dumps(data)
        print(f"{date}{grade}{class_number}{time}{jsons}")
        req = school.patch_timeline(day=date.value, grade=grade, number=class_number, time=time, data=jsons)
        if req != 200:
            await interaction.followup.send("error")
        else:
            await interaction.followup.send("success")
    
    @school.command(name="get", description="school/get")
    async def school_get(self, interaction:discord.Interaction, id):
        school = School(token="token", schoolid=id)
        res = school.get_data()
        await interaction.response.send_message(res)
    

            

async def setup(bot: commands.Bot):
    await bot.add_cog(patch(bot))