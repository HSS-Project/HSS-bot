import discord
from memorization_maker.inc.package import Genre,Share,Delete
import memorization_discord.memorization_maker_play as maker_play
from memorization_discord.memorization_control import MemorizationControlView
class SelectGenre(discord.ui.Select):
    def __init__(self, genres: list, mode:int,classmodes,title=None):
        options = []
        self.mode = mode
        self.genres = genres
        self.classmodes = classmodes
        self.title = title
        for num,genre in enumerate(genres):
            options.append(discord.SelectOption(label=genre, value=str(num)))
        super().__init__(placeholder="ジャンルを選択してください", options=options,min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        genre = Genre()
        share = Share()
        if self.mode == 0:
            sharecode = await share.get_sharecode(self.title)
            await genre.move_genre(str(interaction.user.id),self.genres[int(self.values[0])],sharecode)
            await interaction.response.send_message("移動しました。", ephemeral=True)
        elif self.mode == 1:
            titles = await genre.genres_in_titles(str(interaction.user.id),self.genres[int(self.values[0])])
            await interaction.response.edit_message(view=SelectTitleView(self.genres,titles,self.classmodes))
        elif self.mode == 2:
            sharecode = await Genre().get_genres_sharecode(str(interaction.user.id),self.genres[int(self.values[0])])
            await interaction.response.edit_message(content=f"{self.genres[int(self.values[0])]} このジャンルの共有コード:{sharecode}")
        elif self.mode == 3:
            ch = await Genre().delete_genre(str(interaction.user.id),self.genres[int(self.values[0])])
            if ch:
                await interaction.response.edit_message(content="削除しました。")
            else:
                await interaction.response.edit_message(content="削除に失敗しました。defaultジャンルは削除できません。また、defaultジャンルに100個以上の問題がある場合は削除できません。")

class SelectTitle_1(discord.ui.Select):
    def __init__(self, titles: list,modes:int):
        self.modes = modes
        options = []
        for titles in titles:
            options.append(discord.SelectOption(label=titles))
        super().__init__(placeholder="タイトルを選択してください", options=options,min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "None":
            return await interaction.response.edit_message(content="キャンセルしました。")
        await SelectTitleResponse(interaction,self.values[0],self.modes).select_response()

class SelectTitle_2(discord.ui.Select):
    def __init__(self, titles: list,modes:int):
        self.modes = modes
        options = []
        for titles in titles:
            options.append(discord.SelectOption(label=titles))
        super().__init__(placeholder="タイトルを選択してください", options=options,min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectTitleResponse(interaction,self.values[0],self.modes).select_response()

class SelectTitle_3(discord.ui.Select):
    def __init__(self, titles: list,modes:int):
        self.modes = modes
        options = []
        for titles in titles:
            options.append(discord.SelectOption(label=titles))
        super().__init__(placeholder="タイトルを選択してください", options=options,min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectTitleResponse(interaction,self.values[0],self.modes).select_response()
        
class SelectTitle_4(discord.ui.Select):
    def __init__(self, titles: list,modes:int):
        self.modes = modes
        options = []
        for titles in titles:
            options.append(discord.SelectOption(label=titles))
        super().__init__(placeholder="タイトルを選択してください", options=options,min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectTitleResponse(interaction,self.values[0],self.modes).select_response()
        
class SelectTitleView(discord.ui.View):
    def __init__(self,genres:list,titles:list,modes:int):
        super().__init__()
        self.modes = modes
        #25個ずつに分ける
        self.options_1 = []
        self.options_2 = []
        self.options_3 = []
        self.options_4 = []
        titles_len = len(titles)
        self.options_list = [self.options_1, self.options_2, self.options_3, self.options_4]
        for j in range(4):
            start = j * 25
            end = start + 25
            if start < titles_len:
                for i in range(start, end):
                    if i >= titles_len:
                        break
                    self.options_list[j].append(titles[i])
        self.add_item(SelectGenre(genres,1,self.modes))
        if titles_len == 0:
            self.options_list[0].append("None")
        self.add_item(SelectTitle_1(self.options_list[0],self.modes))
        if titles_len > 25:
            self.add_item(SelectTitle_2(self.options_list[1],self.modes))
        if titles_len > 50:
            self.add_item(SelectTitle_3(self.options_list[2],self.modes))
        if titles_len > 75:
            self.add_item(SelectTitle_4(self.options_list[3],self.modes))

class SelectTitleResponse:
    def __init__(self,intraction:discord.Interaction,title,mode):
        self.intraction = intraction
        self.title = title
        self.modes = mode
        self.genre = Genre()
        self.share = Share()
        self.delete = Delete()

    async def select_response(self):
        if self.modes == 0:
            embed = discord.Embed(title="問題編集",color=0x00ff00)
            await self.intraction.response.edit_message(embed=embed,view=MemorizationControlView(self.title,await self.genre.get_genres_name(str(self.intraction.user.id))))
        elif self.modes == 1:
            embed = discord.Embed(title="出題方式選択",color=0x00ff00)
            sharecode = await self.share.get_sharecode(self.title)
            await self.intraction.response.edit_message(embed=embed,view=maker_play.ChoicePlayMode(sharecode))
        elif self.modes == 2:
            sharecode = await self.share.get_sharecode(self.title)
            genrename = await self.genre.search_genre(str(self.intraction.user.id),sharecode)
            genre_sharecode = await Share().get_genre_sharecode(str(self.intraction.user.id),genrename)
            await self.intraction.response.edit_message(content=f"{self.title} この問題の共有コード:{sharecode}\nこの問題があるジャンルの共有コード:{genre_sharecode}")
        elif self.modes == 3:
            sharecode = await self.share.get_sharecode(self.title)
            genrename = await self.genre.search_genre(str(self.intraction.user.id),sharecode)
            await self.genre.remove_genre(str(self.intraction.user.id),genrename)
            await self.delete.delete_title(str(self.intraction.user.id),self.title)
            await self.intraction.response.edit_message(content="削除しました。")