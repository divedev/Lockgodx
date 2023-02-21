import json
import math
import time

import discord

import model


class Bot:

    def __init__(self, client, guild_id):
        self.client = client
        self.guild_id = guild_id

        # openai interaction
        self.model = model.Model()

        # user-changeable settings. initialize to defaults then load any saved values
        self.active_channel_id = ''
        self.post_cd = 5
        self.reply_cd = 5
        self.msgs_wait = 10  # TODO: reimplement this
        self.posts_enabled = True
        self.replies_enabled = True
        self.load_settings(guild_id)

        # cooldown trackers
        self.user_reply_times = {}
        self.last_post_time = time.time() - self.post_cd * 60
        self.msgs_waited = 0

    def load_settings(self, guild_id:int):
        with open(f'guilds/{guild_id}/settings.json', 'r') as settings_file:
            data = json.load(settings_file)

            self.active_channel_id = data.get('channel', '')
            self.post_cd = data.get('post_cd', 5)
            self.reply_cd = data.get('reply_cd', 5)
            self.msgs_wait = data.get('msgs_wait', 10)
            self.posts_enabled = data.get('posts_enabled', True)
            self.replies_enabled = data.get('replies_enabled', True)

    async def respond(self, message=None):
        if message.channel.id != self.active_channel_id:
            return

        self.msgs_waited += 1

        # reply if bot mentioned
        if self.client.user in message.mentions and self.replies_enabled:
            await self.reply(message)
            return

        # post in conversation
        if self.cooldown_check(self.last_post_time, self.post_cd) and (self.msgs_waited >= self.msgs_wait)\
                and self.posts_enabled:
            await self.post(message)

    async def reply(self, message):
        # check if there is an outstanding cooldown for the user
        if self.cooldown_check(self.user_reply_times.get(message.author.id, 0), self.reply_cd):
            async with message.channel.typing():
                await message.reply(self.generate_response_text(message=message))

            self.start_reply_cd(message.author)

        return

    async def post(self, message):
        async with message.channel.typing():
            self.last_post_time = time.time()

            output = self.generate_response_text(message)

            self.msgs_waited = 0  # reset the anti-spam message counter to 0

            if output is not None:
                await message.channel.send(output)
            else:
                pass

    def generate_response_text(self, message: discord.message = None) -> str:
        response = self.model.respond(message.content)
        return response

    def start_post_cd(self):
        self.last_post_time = time.time()

    def start_reply_cd(self, author):
        self.user_reply_times[author.id] = time.time()

    def cooldown_check(self, time_of_cooldown, cooldown_length):
        return (time.time() - time_of_cooldown) > cooldown_length * 60

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

    def update_setting(self, setting: str, val):
        settings_file_path = f'guilds/{self.guild_id}/settings.json'

        with open(settings_file_path, 'r') as settings_file:
            settings_data = json.load(settings_file)

            if setting in settings_data:
                settings_data[setting] = val

        with open(settings_file_path, 'w') as settings_file:
            json.dump(settings_data, settings_file, indent=2)
