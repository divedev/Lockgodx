import json
from enum import Enum

import discord

import bot


class TraitsOptionType(Enum):
    TYPING_STYLE = "typing_style"
    EMOTIONAL_STATE = "emotional_state"
    SPECIAL_INTERESTS = "special_interests"
    MISC = "misc"
    CUSTOM = "custom"


class TraitsView(discord.ui.View):

    def __init__(self, bot_instance: bot.Bot):
        super().__init__()

        self.guild_id = bot_instance.guild_id

        for option_type in TraitsOptionType:
            options = self.get_options_for_type(option_type)
            self.add_item(TraitsSelect(option_type, options))

    def get_options_for_type(self, option_type: TraitsOptionType) -> list[discord.SelectOption]:
        ret: list[discord.SelectOption] = []

        with open(f"guilds/{self.guild_id}/traits/{option_type.value}_options.json", "r") as options_json:
            data = json.load(options_json)

            # TODO: convert descriptions to the actual prompt tokens (should find out how many tokens each trait costs)
            for label, description in data.items():
                ret.append(discord.SelectOption(label=label, description=description))

        return ret


class TraitsSelect(discord.ui.Select):
    def __init__(self, option_type: TraitsOptionType, options: list[discord.SelectOption]):
        super().__init__(
            placeholder=f"Select {option_type.value.replace('_',' ')}",
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(invisible=True)

