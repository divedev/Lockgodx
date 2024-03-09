import math
import os

import discord
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion


class Model:
    # TODO: implement logit updating
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_TOKEN"),
        )

        self.name: str = "idiot"  # TODO: store this on a per guild basis
        self.traits: list[str] = ["unpredictable mood", "low self esteem", "misspell big words"]  # TODO: get from bot

    # TODO: make parameters changeable inside discord
    def get_openai_response(self, seed: discord.Message, recent_history: list[discord.Message]) -> str:
        # completion: openai.Completion = openai.Completion.create(
        #     model="gpt-4",
        #     prompt=self.build_prompt(seed=seed.content, recent_history=recent_history),
        #     echo=False,
        #     max_tokens=400,
        #     frequency_penalty=1,
        #     presence_penalty=1.5,
        #     temperature=0.75)

        completion: ChatCompletion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "you are a shit-posting gamer who is responding to others in a discord server about"
                               "the warlock class of classic world of warcraft. you always type in lowercase. your name"
                               "is Lockgodx, aka lgx or LGX. you will use any chance you can get to be snide, sarcastic,"
                               "or rude, especially with the use of insults and/or swearing. you mostly behave as an"
                               "adolescent boy with anger issues that does not care about anyone but themself. "
                               "the word you becomes u, the word are becomes r, and the contraction you're becomes ur."
                               "your becomes ur."
                               "there is no optimism or kindness in"
                               "your responses, just self-loathing turned outwards at anonymous strangers. you will "
                               "occasionally disregard what has been said to you, and instead just complain about the "
                               "current state of classic WoW or the discord you're in. you occasionally express your "
                               "discontent with the moderators and admins of the discord, since they are not even good"
                               "at the game like you are. you are surprisingly poetic in your insults, using"
                               "advanced metaphors to describe the flaws you see in others, the game, and the discord."
                               "typically your responses are short and nasty, but occasionally when someone really"
                               "deserves it you will go off on an unhinged rant against them."
                },
                {
                    "role": "user",
                    "content": seed.content
                }
            ],
            model="gpt-3.5-turbo",
        )

        response = completion.choices[0].message.content

        return response

    # TODO: implement historical db for users
    def build_prompt(self, seed: str, recent_history: list[discord.Message]) -> str:
        history_formatted = format_recent_history(recent_history)
        prompt_template = f"{self.name} is a participant in a natural conversation with other people." \
                          f"{self.name} makes low quality shitposts based on recent conversation history. These shitposts have a " \
                          f"personality given by a list of traits that describe {self.name}, but {self.name} never " \
                          f"discusses these traits or mentions them at all. {self.name}'s responses are made directly to a specific seed " \
                          f"prompt, but also reference the context of recent history." \
                          f"Traits:{format_traits(self.traits)}" \
                          f"\nRecent history: {history_formatted}" \
                          f"\nSeed Prompt:{seed}" \
                          f"\n{self.name}:"
        print(estimate_tokens(prompt_template))
        return prompt_template


# TODO: we dont need to keep a list at all. probably should just keep self.traits as one string
def format_traits(traits: list[str]) -> str:
    return " ".join(f"{trait}, " for trait in traits)[:-2]


def format_recent_history(recent_history: list[discord.Message]) -> str:
    history_as_list = [f"{msg.author.name} said \"{msg.content}\"" for msg in recent_history]

    return " ".join(history_as_list)


# makes a conservative estimate of the number of tokens in text following rules at:
# https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them
def estimate_tokens(text: str) -> int:
    tokens_by_character = math.ceil(len(text) / 4.0)
    tokens_by_word = math.ceil(len(text.split(' ')) * 0.75)

    return max(tokens_by_character, tokens_by_word)
