import math
import time


class Bot:

    def __init__(self, guild_id):
        self.channel_id = ''
        self.guild_id = guild_id

        self.random_wait = 5
        self.msgs_wait = 10
        self.mention_wait = 2

        self.bad_words = []

        self.takes_enabled = True
        self.replies_enabled = True
        self.learn = True
        self.guild_dir = f'guilds/{guild_id}'
        self.rules_path = f'guilds/{guild_id}/rules.txt'

        self.user_mention_times = {}
        self.time_of_random = time.time() - self.random_wait * 60
        self.msgs_waited = 0
        self.previous_messages = []

    def generate_take(self, message=None):
        # TODO: do it
        return

    def start_random_cd(self):
        self.time_of_random = time.time()

    def start_reply_cd(self, author):
        self.user_mention_times[author.id] = time.time()

    def status(self, author):
        status = f'**Enabled features**: {", ".join(str(x) for x in self.get_enabled_functions())}\n' \
                 f'**Mention reply cooldown** ({author.name}): {self.get_remaining_cooldown(author=author, string=True)} of {math.floor(self.mention_wait)}m\n' \
                 f'**Random take cooldown**: {self.get_remaining_cooldown(string=True)} of {math.floor(self.random_wait)}m\n'
        return status

    def get_remaining_cooldown(self, author=None, string=False):
        if author is None:
            sec_remaining = max(0, (self.time_of_random + self.random_wait * 60) - time.time())
        elif author.id in self.user_mention_times.keys():
            sec_remaining = max(0, (self.user_mention_times[author.id] + self.mention_wait * 60) - time.time())
        else:
            sec_remaining = 0

        ret = math.floor(sec_remaining)

        if not string:  # return numeric value in seconds
            return ret
        else:  # return string of minutes and seconds
            return format.time_to_text(sec_remaining)

    def get_enabled_functions(self):
        enabled = []

        if self.takes_enabled:
            enabled.append('takes')
        if self.replies_enabled:
            enabled.append('replies')

        if len(enabled) == 0:
            enabled = 'none'

        return enabled

    def no_bad_words(self, message):
        for word in message.split(' '):
            if word.lower() in self.bad_words:
                return False

        return True
