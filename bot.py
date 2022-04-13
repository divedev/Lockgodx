import json
import math
import os
import random
import requests
import time

import format
import model


class Bot:

    def __init__(self, guild_id, TENOR_TOKEN):
        self.model = model.Model()

        self.channel_id = ''
        self.guild_id = guild_id

        self.TENOR_TOKEN = TENOR_TOKEN

        self.random_wait = 5
        self.msgs_wait = 10
        self.mention_wait = 2
        self.rant_size = 10
        self.rant_chance = 5
        self.gif_chance = 1

        self.can_generate_unique_takes = False
        self.max_previous_takes = 20
        self.previous_takes = []

        self.takes_enabled = True
        self.replies_enabled = True
        self.gifs_enabled = True
        self.learn = True
        self.restricted = False
        self.training_root_dir = 'train'
        self.current_data_set = 'none'

        self.user_mention_times = {}
        self.time_of_random = time.time() - self.random_wait*60
        self.msgs_waited = 0
        self.previous_messages = []

    def generate_take(self, message=None):
        # do not generate take if:
        # 1. channel is not set
        # 2. a random take is being requested, but random takes are disabled
        # 3. a reply is being requested, but repies are disabled
        if (self.channel_id == '') \
                or ((message is None) and (not self.takes_enabled)) \
                or ((message is not None) and (not self.replies_enabled)):
            return
        else:
            if message is None:
                # probabilistically pick a random word from recent conversation to seed a take
                if random.random() < 0.8 and (len(self.previous_messages)>5):
                    seed_text = self.get_seed_word_from_previous_msgs()
                else:
                    seed_text = None

                take_text = self.model.make_sentence(tries=50, message=seed_text)
                take_text = self.ensure_unique(format.text_cleaner(take_text))
            else:
                # seed the take with the message content
                take_text = self.model.make_sentence(tries=50,
                                                     message=message.content,
                                                     smart_eligible=self.enough_unique_words(message.content))
                take_text = self.ensure_unique(format.text_cleaner(take_text), message=message.content)

            self.log_take(take_text)

            take_text = format.add_suffix(format.text_cleaner(take_text))

            if message is not None:
                # sometimes add "because" to the beginning, if it's a "why" question
                if ('why' in message.content.split(' ')) and (random.random() < 0.8):
                    pre = random.choice(['because', 'Because', 'bc'])
                    take_text = f'{pre} {take_text}'

                # sometimes answer yes/no questions
                yes_no_q = any([x in ['are', 'is', 'will', 'do', 'does', 'doesnt', 'am', 'should', 'have', 'would', 'did'] for x in message.content.split(' ')[:2]])
                if yes_no_q & (random.random() < 0.8):
                    pre = random.choice(['yea', 'ya', 'yeah', 'yep', 'na', 'nah', 'no', 'nope'])
                    punc = random.choice(['', '.', ','])
                    pre = f'{pre}{punc}'
                    take_text = f'{pre} {take_text}'

            return take_text

    def generate_rant(self, rant_size=None, trigger_icd=False):
        if rant_size is None:
            rant_size = self.rant_size

        # do not post if the channel hasn't been set or if the bot has been manually disabled
        if (self.channel_id == '') | (not self.takes_enabled):
            return
        else:
            rant = ''

            for i in range(rant_size):
                sentence = self.ensure_unique(self.model.make_sentence())
                sentence = format.text_cleaner(sentence, remove_periods=False)
                sentence = format.add_period_if_needed(sentence)
                self.log_take(sentence)

                if len(rant + sentence) < 2000 - 30:
                    rant = f'{rant} {sentence}'
                else:
                    break

            if rant != '':
                rant = format.add_suffix(rant)

                return rant
            else:
                pass

    def generate_gif(self, seed=None):
        num_gifs_to_request = 8

        if seed is None:
            seed = self.get_seed_word_from_previous_msgs()

            if seed is None:
                return

        seed = format.remove_boring_words(seed)
        seed = random.choices(seed, k=min(3, len(seed)))

        r = requests.get(
            "https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (seed, self.TENOR_TOKEN, num_gifs_to_request))

        if r.status_code == 200:
            top_5gifs = json.loads(r.content)
            gif_urls = [result['media'][0]['gif']['url'] for result in top_5gifs['results']]

            return random.choice(gif_urls)
        else:
            return

    def log_take(self, text):
        if len(self.previous_takes) >= self.max_previous_takes:
            self.previous_takes = self.previous_takes[1:]

        self.previous_takes.append(text)

    def ensure_unique(self, text, max_tries=20, message=None):
        # do not re-use previous takes
        tries = 0
        while (text in self.previous_takes) & (tries < max_tries):
            if message is None:
                text = self.model.make_sentence()
            else:
                text = self.model.make_sentence(message=message)
            tries += 1

        return text

    def start_random_cd(self):
        self.time_of_random = time.time()

    def start_reply_cd(self, author):
        self.user_mention_times[author.id] = time.time()

    def status(self, author):
        status = f'**Enabled features**: {", ".join(str(x) for x in self.get_enabled_functions())}\n' \
                 f'**Learning**: {self.learn}\n' \
                 f'**Warlock-only**: {self.restricted}\n' \
                 f'**Parsed sentences**: {len(self.model.generator.parsed_sentences)}\n' \
                 f'**Chain**: {self.model.state_size}\n' \
                 f'**Data set**: {self.current_data_set}\n' \
                 f'**Mention reply cooldown** ({author.name}): {self.get_remaining_cooldown(author=author, string=True)} of {math.floor(self.mention_wait)}m\n' \
                 f'**Random take cooldown**: {self.get_remaining_cooldown(string=True)} of {math.floor(self.random_wait)}m\n' \
                 f'**Rant chance**: {self.rant_chance}%\n' \
                 f'**Rant size**: {self.rant_size}\n' \
                 f'**Gif chance**: {self.gif_chance}%\n'
        return status

    def train_on_files(self, train_dir=None, file=None):
        if train_dir is None:
            full_train_dir = self.training_root_dir
        else:
            full_train_dir = f'{self.training_root_dir}/{train_dir}'

        if not os.path.isdir(full_train_dir):
            raise FileNotFoundError

        if full_train_dir == f'{self.training_root_dir}/prophet':
            state_size = 3
        else:
            state_size = 2

        self.reset(state_size=state_size)

        training_files = [f for f in os.listdir(full_train_dir) if f.endswith('.txt')]

        for f in training_files:
            training_file_path = f'{full_train_dir}/{f}'

            lines = []

            if (file is None) or (f == file):
                with open(training_file_path, 'r', encoding='cp437') as f_data:
                    try:
                        for line in f_data:

                            if line.strip():
                                clean_line = format.text_cleaner(line)

                                if clean_line != '':
                                    lines.append(clean_line)
                    except:
                        pass

                self.model.update_model(lines)

        # in trained mode, disable further learning and ascension
        self.learn = False
        if train_dir != self.training_root_dir:
            self.current_data_set = train_dir

    def reset(self, state_size=2):
        self.current_data_set = 'none'
        self.learn = True

        self.can_generate_unique_takes = False

        self.model = model.Model(state_size=state_size)

    # adds message to markov model and checks if the model knows enough to generate multiple unique outputs
    async def train(self, message):
        # incorporate the message into the model if learning is enabled and the message is long enough to learn from
        if self.learn & (len(message.content.split()) > self.model.generator.state_size):
            self.model.update_model(message.content)

        # set readiness flag
        self.can_generate_unique_takes = self.test_take_readiness()

    # if the model can spit out test_size unique takes, its model is "ready". once readiness is determined, do not check
    # again unless reset
    def test_take_readiness(self, test_size=15):
        if not self.can_generate_unique_takes:
            takes = [self.model.make_sentence() for x in range(test_size)]
            all_takes_unique = len(takes) == len(set(takes))

            return all_takes_unique
        else:
            return True

    def get_remaining_cooldown(self, author=None, string=False):
        if author is None:
            sec_remaining = max(0, (self.time_of_random + self.random_wait*60) - time.time())
        elif author.id in self.user_mention_times.keys():
            sec_remaining = max(0, (self.user_mention_times[author.id] + self.mention_wait * 60) - time.time())
        else:
            sec_remaining = 0

        ret = math.floor(sec_remaining)

        if not string: # return numeric value in seconds
            return ret
        else: # return string of minutes and seconds
            return format.time_to_text(sec_remaining)

    def get_seed_word_from_previous_msgs(self):
        seed_candidates = [msg for msg in self.previous_messages[4:] if len(msg.split(' ')) > 5]

        if len(seed_candidates) > 0:
            return random.choice(seed_candidates)
        else:
            return None

    def get_enabled_functions(self):
        enabled = []

        if self.gifs_enabled:
            enabled.append('gifs')
        if self.takes_enabled:
            enabled.append('takes')
        if self.replies_enabled:
            enabled.append('replies')

        if len(enabled)==0:
            enabled = 'none'

        return enabled

    def enough_unique_words(self, message, min_unique_words=5):
        word_set = set(message.split(' '))
        return len(word_set) > min_unique_words