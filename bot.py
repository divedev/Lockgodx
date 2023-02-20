import math
import time


class Bot:

    def __init__(self, client, guild_id):
        self.client = client

        self.channel_id = ''
        self.guild_id = guild_id

        # TODO: change these after dev
        self.random_wait = 0
        self.msgs_wait = 0
        self.mention_wait = 0

        self.bad_words = []    # TODO: will we even need this

        self.takes_enabled = True
        self.replies_enabled = True
        self.learn = True
        self.guild_dir = f'guilds/{guild_id}'

        self.user_mention_times = {}
        self.time_of_random = time.time() - self.random_wait * 60
        self.msgs_waited = 0
        self.previous_messages = []

    async def respond(self, message=None):
        self.msgs_waited += 1

        # respond to mentions if ready
        if self.client.user in message.mentions\
                and self.replies_enabled:
            await self.respond_to_mention(message)
            return

        # post randomly if ready
        if self.cooldown_check(self.time_of_random, self.random_wait) and (self.msgs_waited >= self.msgs_wait)\
                and self.takes_enabled:
            await self.respond_randomly(message)

    async def respond_to_mention(self, message):
        # check if there is an outstanding cooldown for the user
        if self.cooldown_check(self.user_mention_times.get(message.author.id, 0), self.mention_wait):
            async with message.channel.typing():
                await message.reply(self.generate_take(message=message))

        self.start_reply_cd(message.author)

        return

    async def respond_randomly(self, message):
        async with message.channel.typing():
            self.time_of_random = time.time()

            output = f"test: {message.content}"  # TODO: put openai response here

            self.msgs_waited = 0  # reset the anti-spam message counter to 0

            if output is not None:
                await message.channel.send(output)
            else:
                pass

    def generate_take(self, message=None) -> str:
        # TODO: put openai response here
        return f"test: {message.content}"

    def start_random_cd(self):
        self.time_of_random = time.time()

    def start_reply_cd(self, author):
        self.user_mention_times[author.id] = time.time()

    def status(self, author):
        # TODO: make ephemeral, convert to an embed
        status = f'**Enabled features**: {", ".join(str(x) for x in self.get_enabled_functions())}\n' \
                 f'**Mention reply cooldown** ({author.name}): {self.get_remaining_cooldown(author=author).__str__()} ' \
                    f'of {math.floor(self.mention_wait)}m\n' \
                 f'**Random take cooldown**: {self.get_remaining_cooldown().__str__()} of {math.floor(self.random_wait)}m\n'
        return status

    def cooldown_check(self, time_of_cooldown, cooldown_length):
        return (time.time() - time_of_cooldown) > cooldown_length * 60

    def get_remaining_cooldown(self, author=None) -> int:
        if author is None:
            sec_remaining = max(0, (self.time_of_random + self.random_wait * 60) - time.time())
        elif author.id in self.user_mention_times.keys():
            sec_remaining = max(0, (self.user_mention_times[author.id] + self.mention_wait * 60) - time.time())
        else:
            sec_remaining = 0

        ret = math.floor(sec_remaining)

        return ret

    def get_enabled_functions(self):
        enabled = []

        if self.takes_enabled:
            enabled.append('takes')
        if self.replies_enabled:
            enabled.append('replies')

        if enabled.count() < 1:
            enabled = 'none'

        return enabled

    # TODO: will we even need this
    def no_bad_words(self, message):
        for word in message.split(' '):
            if word.lower() in self.bad_words:
                return False

        return True
