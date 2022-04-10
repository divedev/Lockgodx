import math
import os
import random
import re


def remove_url(text):
    return re.sub("https?:\/\/.*[\r\n]*", "", text)


def remove_mentions(text):
    text = re.sub("@\S+", "", text)
    return re.sub("<@\S+", "", text)


def remove_special(text):
    chars = ['â', '€', '™', '‰', 'ð', 'Ÿ', '¤', '¡', 'š', '~', '˜', 'Γ', 'Ç', 'Ö', 'ª',
             '¥', '£', '≡', 'ƒ', 'Æ', '¬', 'Å', '┐', 'é', 'Ñ', 'ö', 'ÿ', '¢', '┬', '»', 'π',
             'ä', 'ñ', 'í']

    for char in chars:
        text = text.replace(char, '')

    return text.replace('\n', '.')


def strip_question(text):
    if len(text) > 2:
        # remove the period from the end of sentences that should end with ? or !
        if text[-2] == '?' or text[-2] == '!':
            text = text[:-1]

    return text


def strip_period(text):
    # strip the ending period
    if random.randrange(0, 100) > 20:
        if text[-1] == '.':
            text = text[:-1]

    return text


def add_period_if_needed(text):
    punc = ['?', '!', '.']
    if text[-1] in punc:
        return text
    else:
        return text + '.'


def text_cleaner(text, remove_periods=True):
    try:
        text = remove_url(text)
        text = remove_mentions(text)
        text = remove_special(text)
        text = strip_question(text)

        if remove_periods:
            text = strip_period(text)

        text = censor_mage(text)
    except:
        pass

    return text


def add_suffix(text):
    leads = ['...', 'ok', 'okay', 'w/e', 'smh']
    laughs = ['LOL', 'lul', 'KEKW', 'hahaha', 'lmao', 'lmfao', 'XD', 'xD', 'xd', 'Xd']
    insults = ['noob', 'shitter', 'bad', 'casual', 'cringe', 'w h o ?', ':clown:', 'idiot', 'literal dad gamer', 'pussy'
        , 'trash', 'so toxic', '2ez', 'just parse bro', 'get good', 'ratio', 'based', 'BASED', 'pog', 'what a joke'
        , 'clown world', 'forsen', 'no cap']

    suffix = ''

    if random.random() * 100 > 85:
        suffix = f'{suffix} {random.choice(leads)}'

    if random.random() * 100 > 75:
        suffix = f'{suffix} {random.choice(laughs)}'
        if random.random() * 100 > 80:
            suffix = f'{suffix} {random.choice(insults)}'

    return text + suffix


def censor_mage(text):
    return text.replace('mage', 'm\\*ge')


def time_to_text(seconds=0, minutes=0):
    total_seconds = seconds + 60 * minutes

    seconds_text = f'{math.floor(total_seconds % 60)}s'
    minutes_text = f'{math.floor(total_seconds / 60)}m'

    if minutes_text == '0m':
        minutes_text = ''
    if seconds_text == '0s':
        seconds_text = ''

    text = f'{minutes_text}{seconds_text}'

    if text == '':
        text = '0s'

    return text


def remove_all_punctuation(text):
    for char in ['!', ',', '.', '?', ';', ':', '\'', '\"', '(', ')']:
        text = text.replace(char, '')

    return text


# removes mentions and "boring" words from query text to result in a better response from the bot
def remove_boring_words(query_text):
    boring = ['who', 'what', 'when', 'where', 'why', 'you', 'me', 'he', 'she', 'it', 'do', 'will', 'did', 'can', 'with',
              'is', 'am', 'if', 'was', 'are', 'i', 'should', 'would', 'does', 'this', 'oh', 'um', 'huh', 'heh', 'as',
              'a', 'an', 'or', 'be', 'on', 'in', 'for', 'thoughts', 'and', 'your', 'u', 'ur', 'about', 'to', 'my',
              'mine', 'too', 'about', 'at', 'arent', 'there', 'their', 'opinion', 'not', 'that', 'i', 'how', 'so', 'of',
              'them', 'but', 'than', 'much', 'yet', 'unto', 'have', 'us']

    query_text = [word for word in query_text if str.lower(word) not in boring]
    query_text = [remove_all_punctuation(word) for word in query_text if not word.startswith('<')]

    return query_text


def write_history(hist, root_dir, file_name):
    if f'{file_name}.txt' not in os.listdir(root_dir):
        with open(f'{root_dir}/{file_name}.txt', 'w', encoding='cp437') as f:
            for line in hist:
                try:
                    f.write(f'{text_cleaner(line)}\n')
                except:
                    pass

