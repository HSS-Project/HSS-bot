import discord
import memorization_discord.select_mission as select_mission
import memorization_discord.select_title as select_title
from memorization_maker.share import Share
from memorization_maker.owner_manager import OwnerManager
from memorization_discord.memorization_maker_add import MemorizationAddModal,MemorizationAddTextModal,TitleSetModal,MemorizationMakeGenre,OwnerAddModal,OwnerDeleteSelect

class MemorizationControlView(discord.ui.View):
    def __init__(self,title:str,genres:list):
        super().__init__()
        self.title = title
        self.view = discord.ui.View()
        self.share = Share()
        self.select_mission = select_mission
        self.select_title = select_title
        self.owner = OwnerManager()
        
        self.genre_list = genres
        self.add_item(self.select_title.SelectGenre(genres,0,0,title))

    @discord.ui.button(label="問題追加", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(MemorizationAddModal(self.title))
        
    @discord.ui.button(label="選択問題追加", style=discord.ButtonStyle.green)
    async def select_add(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(TitleSetModal(self.title))

    @discord.ui.button(label="文章問題追加", style=discord.ButtonStyle.green)
    async def text_add(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(MemorizationAddTextModal(self.title))

    @discord.ui.button(label="問題編集", style=discord.ButtonStyle.green)
    async def edit(self, interaction: discord.Interaction, _:discord.ui.Button):
        sharecode = await self.share.get_sharecode(self.title)
        data = await self.share.get_sharedata(sharecode)
        missions_question:list = []
        missions = data["questions"]
        for mission in missions:
            missions_question.append(mission["question"][:90])
        embed = discord.Embed(title="問題編集", color=0x00ff00)
        await interaction.response.send_message(embed=embed,view=self.select_mission.SelectMissionView(self.title,missions_question,1), ephemeral=True)

    @discord.ui.button(label="問題削除", style=discord.ButtonStyle.green)
    async def delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        sharecode = await self.share.get_sharecode(self.title)
        data = await self.share.get_sharedata(sharecode)
        missions_question:list = []
        missions = data["questions"]
        for mission in missions:
            missions_question.append(mission["question"][:90])
        embed = discord.Embed(title="問題削除", color=0x00ff00)
        await interaction.response.send_message(embed=embed,view=self.select_mission.SelectMissionView(self.title,missions_question,0), ephemeral=True)

    @discord.ui.button(label="ジャンル作成", style=discord.ButtonStyle.blurple)
    async def genre(self, interaction: discord.Interaction, _:discord.ui.Button):
        await interaction.response.send_modal(MemorizationMakeGenre(self.title))

    @discord.ui.button(label="ジャンル削除", style=discord.ButtonStyle.blurple)
    async def genre_delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        embed = discord.Embed(title="選択してください",description="")
        view = discord.ui.View()
        view.add_item(self.select_title.SelectGenre(self.genre_list,3,0,self.title))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    @discord.ui.button(label="管理者権限追加", style=discord.ButtonStyle.grey)
    async def admin_add(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.send_modal(OwnerAddModal(self.title))
    
    @discord.ui.button(label="管理者権限削除", style=discord.ButtonStyle.grey)
    async def admin_delete(self, interaction: discord.Interaction, _:discord.ui.Button):
        guild = interaction.guild
        owner_id_list:list = await self.owner.owner_list(str(interaction.user.id),self.title)
        owner_name:list = []
        owner_id_list.remove(str(interaction.user.id))
        for owner_id in owner_id_list:
            owner = guild.get_member(int(owner_id))
            owner_name.append(owner.name)
        if len(owner_name) == 0:
            return await interaction.response.send_message("管理者が他にいないため、削除できません", ephemeral=True)
        view = discord.ui.View()
        view.add_item(OwnerDeleteSelect(self.title,owner_id_list,owner_name))
        await interaction.response.send_message("管理者を選択してください",view=view, ephemeral=True)
    
    @discord.ui.button(label="終了", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, _:discord.ui.Button):
        sharecode = await self.share.get_sharecode(self.title)
        await interaction.response.edit_message(content=f"終了\nこの問題の共有コード:{sharecode}",embed=None,view=None)