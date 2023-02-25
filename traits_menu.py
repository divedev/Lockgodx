import discord


class TraitsMenu(discord.ui.View):

    @discord.ui.select(
        placeholder="Choose typing style options",
        min_values=0,
        max_values=3,
        options=[
            discord.SelectOption(
                label="No Punctuation",
                description="Don't use punctuation"
            ),
            discord.SelectOption(
                label="No capitalization",
                description="Don't use capital letters"
            ),
            discord.SelectOption(
                label="Frequent typos",
                description="Frequently make typos and misspellings"
            ),
            discord.SelectOption(
                label="Frequent emojis",
                description="Frequently use emojis"
            ),
            discord.SelectOption(
                label="Misuse Homophones",
                description="Bot will misuse words that sound alike"
            )
        ]
    )
    async def select_typing_style(self, select, interaction):
        await interaction.response.defer(invisible=True)

    @discord.ui.select(
        placeholder="Choose emotional state",
        min_values=0,
        max_values=3,
        options=[
            discord.SelectOption(
                label="Happy",
                description="Bot will be happy"
            ),
            discord.SelectOption(
                label="Angry",
                description="Bot will be angry"
            ),
            discord.SelectOption(
                label="Depressed",
                description="Bot will be depressed"
            ),
            discord.SelectOption(
                label="Horny",
                description="Bot will be horny"
            ),
            discord.SelectOption(
                label="Optimistic",
                description="Bot will be optimistic"
            ),
            discord.SelectOption(
                label="Cheerful",
                description="Bot will be cheerful"
            ),
            discord.SelectOption(
                label="Suspicious",
                description="Bot will act suspicious"
            ),
            discord.SelectOption(
                label="Passive Aggressive",
                description="Bot will be passive aggressive"
            ),
            discord.SelectOption(
                label="Judgemental",
                description="Bot will be judgemental"
            )
        ]
    )
    async def select_emotion(self, select, interaction: discord.Interaction):
        await interaction.response.defer(invisible=True)

    @discord.ui.select(
        placeholder="Choose misc. personality traits",
        min_values=0,
        max_values=3,
        options=[
            discord.SelectOption(
                label="Sarcastic",
                description="Bot will be sarcastic"
            ),
            discord.SelectOption(
                label="Inflated Ego",
                description="Bot will have an inflated ego"
            ),
            discord.SelectOption(
                label="Low Self Esteem",
                description="Bot will have low self esteem"
            ),
            discord.SelectOption(
                label="Insulting",
                description="Bot will insult users"
            ),
            discord.SelectOption(
                label="Low Education",
                description="Bot will be simple minded"
            )
        ]
    )
    async def select_misc(self, select, interaction: discord.Interaction):
        await interaction.response.defer(invisible=True)

    @discord.ui.select(
        placeholder="Choose custom traits",
        min_values=0,
        max_values=3,
        options=[
            discord.SelectOption(
                label="Duplicate emojis",
                description="Bot will duplicate/repeat emojis when used"
            ),
            discord.SelectOption(
                label="Southern Accent/Slang",
                description="Bot will use a southern accent and slang"
            ),
            discord.SelectOption(
                label="Nonsensical",
                description="Bot will make nonsensical posts"
            ),
            discord.SelectOption(
                label="Replace word",
                description="Bot will replace \"fun\" with \"shit\""
            ),
            discord.SelectOption(
                label="Low Education",
                description="Bot will be simple minded"
            )
        ]
    )
    async def select_custom_traits(self, select, interaction: discord.Interaction):
        await interaction.response.defer(invisible=True)
