import discord
from discord import ui
from memorization_maker.inc.pakege import Add, Get, OwnerManager, Edit, Delete, Share, Genre


class SelectGenre(discord.ui.Select):
    def __init__(self, genres: list, mode:int):
        options = []
        self.mode = mode
        self.genres = genres
        for num,genre in enumerate(genres):
            options.append(discord.SelectOption(label=genre, value=str(num)))
        super().__init__(placeholder="ジャンルを選択してください", options=options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        genre = Genre()
        if self.mode == 0:
            await genre.move_genre(str(interaction.user.id),self.genres[int(self.values[0])])
        elif self.mode == 1:
            await interaction.response.edit_message(view=SelectTitleView(self.genres[int(self.values[0])],await Get().get_titles(str(interaction.user.id))))

class SelectTitle_1(discord.ui.Select):
    def __init__(self, titles: list):
        options = []
        for num,titles in enumerate(titles):
            options.append(discord.SelectOption(label=titles, value=str(num)))
        super().__init__(placeholder="タイトルを選択してください", options=options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectTitleResponse(interaction,self.values[0]).select_response()
class SelectTitle_2(discord.ui.Select):
    def __init__(self, titles: list):
        options = []
        for num,titles in enumerate(titles):
            options.append(discord.SelectOption(label=titles, value=str(num)))
        super().__init__(placeholder="タイトルを選択してください", options=options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectTitleResponse(interaction,self.values[0]).select_response()
        
class SelectTitle_3(discord.ui.Select):
    def __init__(self, titles: list):
        options = []
        for num,titles in enumerate(titles):
            options.append(discord.SelectOption(label=titles, value=str(num)))
        super().__init__(placeholder="タイトルを選択してください", options=options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectTitleResponse(interaction,self.values[0]).select_response()
        
class SelectTitle_4(discord.ui.Select):
    def __init__(self, titles: list):
        options = []
        for num,titles in enumerate(titles):
            options.append(discord.SelectOption(label=titles, value=str(num)))
        super().__init__(placeholder="タイトルを選択してください", options=options, row=1, min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        await SelectTitleResponse(interaction,self.values[0]).select_response()
        
class SelectTitleView(discord.ui.View):
    def __init__(self,genres:list,titles:list):
        super().__init__()
        self.add_item(SelectGenre(genres,1))
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
                    
        self.add_item(SelectTitle_1(self.options_1))
        if titles_len > 25:
            self.add_item(SelectTitle_2(self.options_2))
        if titles_len > 50:
            self.add_item(SelectTitle_3(self.options_3))
        if titles_len > 75:
            self.add_item(SelectTitle_4(self.options_4))

class SelectTitleResponse:
    def __init__(self,intraction,title):
        self.intraction = intraction
        self.title = title

    async def select_response(self):
        pass