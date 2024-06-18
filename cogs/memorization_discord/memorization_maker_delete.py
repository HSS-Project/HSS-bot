import discord
from memorization_maker.inc.pakege import Read_and_Write, Add, Get, OwnerManager, Edit, Delete, Share, Genre
from cogs.memorization_discord.memorization_maker_add import MemorizationControlView

class MemorizationMakerDelete(discord.ui.Select):
    def __init__(self,questions:list,sharecode:int):
        super().__init__()
        self.share = Share()
        questions_len = len(questions)

        options_1 = []
        options_2 = []
        options_3 = []
        options_4 = []
        #最初の25個の選択肢を追加
        self.options_list = [options_1, options_2, options_3, options_4]
        for j in range(4):
            start = j * 25
            end = start + 25
            if start < questions_len:
                for i in range(start, end):
                    if i >= questions_len:
                        break
                    self.options_list[j].append(discord.SelectOption(label=questions[i]["question"], value=str(i)))

    def get(self,num):
        return self.options_list[num]

    @discord.ui.select(
        cls=discord.ui.Select,
        placeholder="選択してください",
        options=get(0)
    )
    async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
        await self.delete(interaction,select)
    
    if not get(1) == []:
        @discord.ui.select(
            cls=discord.ui.Select,
            placeholder="選択してください",
            options=get(1)
        )
        async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
            await self.delete(interaction,select)
    
    if not get(2) == []:
        @discord.ui.select(
            cls=discord.ui.Select,
            placeholder="選択してください",
            options=get(2)
        )
        async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
            await self.delete(interaction,select)
    
    if not get(3) == []:
        @discord.ui.select(
            cls=discord.ui.Select,
            placeholder="選択してください",
            options=get(3)
        )
        async def select(self, interaction: discord.Interaction, select: discord.ui.Select):
            await self.delete(interaction,select)
    
    async def delete(self,interaction: discord.Interaction,select: discord.ui.Select):
        select_len_number = int(select.values[0])
        title = self.share.get_sharedata(str(interaction.user.id),select_len_number)["title"]
        await Delete().delete_misson_select(str(interaction.user.id),title,select_len_number)
        embed = discord.Embed(title="問題追加",color=0x00ff00)
        return await interaction.response.edit_message(embed=embed,view=MemorizationControlView(str(interaction.user.id),title))
        