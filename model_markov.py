import markovify
import random
import os
import time

import format


def enough_unique_and_nonboring_words(message, min_unique_words=5, min_nonboring_words=2):
    message = format.remove_special(message)
    word_set = set(message.split(' '))
    enough_unique_words = len(word_set) > min_unique_words
    enough_nonboring_words = len(format.remove_boring_words(message)) > min_nonboring_words
    return enough_unique_words & enough_nonboring_words


def no_spammed_words(message, spam_threshold=3):
    message = format.remove_boring_words(message)

    word_frequency = {}

    for word in message:

        if word in word_frequency:
            word_frequency[word] += 1
            if word_frequency[word] >= spam_threshold:
                return False
        else:
            word_frequency[word] = 1

    return True


class Model:

    def __init__(self, state_size=2):
        self.random_wait = 5
        self.msgs_wait = 10
        self.mention_wait = 2
        self.rant_size = 10
        self.rant_chance = 5

        self.can_generate_unique_takes = False
        self.max_previous_takes = 20
        self.previous_takes = []

        self.bad_words = []

        self.takes_enabled = True
        self.replies_enabled = True
        self.learn = True
        self.restricted = False
        self.current_data_set = 'none'

        self.user_mention_times = {}
        self.time_of_random = time.time() - self.random_wait * 60
        self.msgs_waited = 0
        self.previous_messages = []

        self.root_dir = 'models/'
        self.training_root_dir = 'train'
        self.state_size = state_size
        self.init_text = 'i am a bot'
        self.no_take_text = 'cum'
        self.smart_reply_chance = 80
        self.generator = markovify.Text(self.init_text, state_size=state_size, well_formed=False)

    def make_sentence(self, message=None, tries=30, smart_eligible=True):
        sentence = self.generator.make_sentence(tries=tries)

        if (message is not None) and (random.random() < self.smart_reply_chance / 100) and smart_eligible:
            content = list(set(format.remove_boring_words(message)))
            random.shuffle(content)

            for word in content:
                try:
                    sentence = self.generator.make_sentence_with_start(beginning=word, tries=tries, strict=False)
                    break
                except markovify.text.ParamError:
                    pass

        if sentence:
            return sentence
        else:
            return self.no_take_text

    def update_model(self, text):
        try:
            new_model = markovify.Text(text, state_size=self.generator.state_size, well_formed=False)
            self.generator = markovify.combine(models=[self.generator, new_model])

        except:
            pass

    def save_model(self, model_name=None):
        if model_name is None:
            model_name = 'default'

        try:
            model_json = self.generator.to_json()
            with open(f'{self.root_dir}{model_name}.json', 'w', encoding='iso-8859-1') as outfile:
                outfile.write(model_json)
            return 1
        except:
            return None

    def load_model(self, model_name=None):
        if model_name is None:
            model_name = 'default'

        try:
            with open(f'{self.root_dir}{model_name}.json') as f:
                model_json = f.read()
                self.generator = markovify.Text.from_json(model_json)
                self.state_size = self.generator.state_size
            return 1
        except:
            return None

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
                with open(training_file_path, 'r', encoding='iso-8859-1') as f_data:
                    try:
                        for line in f_data:

                            if line.strip():
                                clean_line = format.text_cleaner(line)

                                if clean_line != '':
                                    lines.append(clean_line)
                    except:
                        pass

                self.update_model(lines)

        # in trained mode, disable further learning and ascension
        self.learn = False
        if train_dir != self.training_root_dir:
            self.current_data_set = train_dir

    def reset(self, state_size=2):
        self.current_data_set = 'none'
        self.learn = True

        self.can_generate_unique_takes = False

    # adds message to markov model and checks if the model knows enough to generate multiple unique outputs
    async def train(self, message):
        message = message.content
        eligible_for_training = enough_unique_and_nonboring_words(message, min_unique_words=3) \
                                & no_spammed_words(message) \
                                & self.no_bad_words(message)

        # incorporate the message into the model if learning is enabled and the message is long enough to learn from
        if self.learn & eligible_for_training:
            self.update_model(message)

        # set readiness flag
        self.can_generate_unique_takes = self.test_take_readiness()

    # if the model can spit out test_size unique takes, its model is "ready". once readiness is determined, do not check
    # again unless reset
    def test_take_readiness(self, test_size=15):
        if not self.can_generate_unique_takes:
            takes = [self.make_sentence() for _ in range(test_size)]
            all_takes_unique = len(takes) == len(set(takes))

            return all_takes_unique
        else:
            return True

    def no_bad_words(self, message):
        for word in message.split(' '):
            if word.lower() in self.bad_words:
                return False

        return True
