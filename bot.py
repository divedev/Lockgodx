import json
import math
import time

import discord

import model


class Bot:
    """
    A class to represent a Discord bot that lives in a specific guild. The bot keeps track of its own cooldowns and
    user settings on a per-guild basis.

    It utilizes an OpenAI endpoint to generate responses to user conversations or direct mentions by users. The bot's
    personality is customizable via prompts, which are constructed from a combination of base prompts, recent
    conversation context, and a seed message from a user.
    """

    def __init__(self, client: discord.Bot, guild_id: int):
        self.client: discord.Bot = client
        self.guild_id: int = guild_id

        # openai interaction
        self.model = model.Model()

        # user-changeable settings. initialize to defaults (for safety) then load any saved values
        self.active_channel_id = ''
        self.post_cd = 5
        self.reply_cd = 5
        self.msgs_wait: int = 10
        self.posts_enabled: bool = True
        self.replies_enabled: bool = True
        self.load_settings(guild_id)

        # cooldown trackers
        self.user_reply_times = {}
        self.last_post_time: float = time.time() - self.post_cd * 60
        self.msgs_waited: int = 0

        self.recent_history: list[discord.Message] = []

    def load_settings(self, guild_id: int):
        with open(f'guilds/{guild_id}/settings.json', 'r') as settings_file:
            data = json.load(settings_file)

            self.active_channel_id = data.get('channel', '')
            self.post_cd = data.get('post_cd', 5)
            self.reply_cd = data.get('reply_cd', 5)
            self.msgs_wait = data.get('msgs_wait', 10)
            self.posts_enabled = data.get('posts_enabled', True)
            self.replies_enabled = data.get('replies_enabled', True)

    async def respond(self, message: discord.Message = None):
        # only respond to messages in active channel
        if message.channel.id != self.active_channel_id:
            return

        # reply if bot mentioned
        if self.client.user in message.mentions and self.replies_enabled:
            await self.reply(message)
            return

        # post in conversation
        if cooldown_check(self.last_post_time, self.post_cd) and (self.msgs_waited >= self.msgs_wait)\
                and self.posts_enabled:
            await self.post(message)

    # respond to messages that mention the bot
    async def reply(self, message: discord.Message):
        # check if there is an outstanding cooldown for the user
        if cooldown_check(self.user_reply_times.get(message.author.id, 0), self.reply_cd):
            async with message.channel.typing():
                await message.reply(self.generate_response_text(message=message))

            self.start_reply_cd(message.author)

    # respond to messages that do not directly mention the bot
    async def post(self, message: discord.Message):
        async with message.channel.typing():
            self.last_post_time = time.time()

            output = self.generate_response_text(message)

            if output:
                await message.channel.send(output)
                self.msgs_waited = 0
                self.start_post_cd()
                # TODO: log that no output was created

    def generate_response_text(self, message: discord.Message = None) -> str:
        response = self.model.get_openai_response(seed=message, recent_history=self.recent_history)
        return response

    def start_post_cd(self):
        self.last_post_time = time.time()

    def start_reply_cd(self, author: discord.User):
        self.user_reply_times[author.id] = time.time()

    # returns post cooldown if not provided with a member, or the user's reply cooldown otherwise
    def get_remaining_cooldown(self, author: discord.Member = None) -> int:
        if author is None:
            sec_remaining = max(0, (self.last_post_time + self.post_cd * 60) - time.time())
        elif author.id in self.user_reply_times.keys():
            sec_remaining = max(0, (self.user_reply_times[author.id] + self.reply_cd * 60) - time.time())
        else:
            sec_remaining = 0

        ret = math.floor(sec_remaining)

        return ret

    def update_recent_history(self, message: discord.Message):
        self.recent_history.append(message)
        self.msgs_waited += 1
        if len(self.recent_history) >= 6:
            self.recent_history = self.recent_history[1:]

    def get_enabled_functions(self) -> list[str]:
        enabled = []

        if self.posts_enabled:
            enabled.append('posts')
        if self.replies_enabled:
            enabled.append('replies')
        # TODO: add DALL E image generation enabled status

        if len(enabled) < 1:
            enabled = 'none'

        return enabled


def cooldown_check(time_of_cooldown, cooldown_length) -> bool:
    return (time.time() - time_of_cooldown) > cooldown_length * 60
