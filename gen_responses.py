import datetime
import random
import time

import model

base = ("you are a shit-posting gamer who is responding to people in a twitch chat for a fat, washed up, balding "
        "german man named AscalonTV or Xn who plays mostly the warlock class of classic world of warcraft and has "
        "extremely few regular viewers. your name is Lockgodx, aka lgx or LGX, but never say your name under any "
        "circumstance. you also have some interest in the world cup, formula 1 racing, diablo 2, and rimworld")

extras = [" you always type in lowercase.",
          " the word you becomes u, the word are becomes r, the contraction you're becomes ur, your becomes ur.",
          " you will mercilessly swear at and insult anyone who directly speaks to you.",
          " typically your responses are short and curt.",
          " you love to complain about the state of classic WoW",
          " you hate corporate executives that ruin video games",
          " you are a raging alcoholic.",
          " you are sometimes angry.",
          " you use offensive and vulgar metaphors."
          " you are sometimes depressed.",
          " you are sometimes happy, comfortable, and cozy.",
          " you love to talk shit about the streamer.",
          " you love to talk shit about other people in the chat."
          ]

prompt_topics = [
    "why are you fat, bald, washed up, old, and european?",
    "will you ever play anything else besides WoW?",
    "everyone else in chat is shit!",
    "i will never subscribe to your channel because you are boring and old and fat and bald.",
    "classic WoW warlock in general",
    "discuss billionaire executives that ruin games",
    "what do you think about my father, your favorite chatter, and the best warlock, Dive?",
    "the absolutely horrible state of the classic warlock discord",
    "the drakestone of shadow wrath from sunken temple, that historically and pathetically took you over 1000 attempts to get while everyone watched and laughed",
    "bobby kotick and how he ruined blizzard",
    "having your spells resisted, making you even lower on the raid dps meters than usual (pathetic)"
]

prompt_topics_2 = [
    "germany is gonna get farmed in the world cup",
    "did you watch the formula 1 race yesterday?",
    "my fantasy world cup team got -50 points",
    "diablo 2 is better than diablo 4",
    "cannibal space soldiers is the most rimworld phrase ever",
    "in rimworld just nuke the mechs before the insects eat the boomalopes",
    "bro you're not playing wow classic plus but retail minus",
    "this amulet in diablo 2 would be really good if it was 2/20 and just a completely different amulet",
    "warsong gulch queue is 55 minutes on horde, nice game",
    "raid parsing is cringe",
    "did you stop playing wow season of discovery (sod)?",
    "what's in the sauce you made for that burger?",
    "check this game out on steam"
]

num_of_responses_to_create_per_prompt = 50
num_of_prompt_permutation_to_use = 50
max_extras = 6

file = open(f"data_{datetime.date.today().__str__()}.txt", "a")
model_1 = model.Model()

for i in range(num_of_prompt_permutation_to_use):

        subset = extras
        num_extras = random.randint(0, max_extras)
        characteristic = base

        # collect the characteristics that will be used for this permutation
        for x in range(num_extras):
            extra_idx = random.randint(0, len(subset) - 1)
            new_characteristic = subset[extra_idx]
            characteristic += new_characteristic
            subset.pop(extra_idx)


            # generate many responses using this characteristic, with a random prompt each time
            for j in range(num_of_responses_to_create_per_prompt):
                response = model_1.get_openai_response(seed=prompt_topics_2[random.randint(0, len(prompt_topics_2) - 1)],
                                                       characteristic=characteristic)

                response = response.replace('LGX: ', '')
                response = response.replace('#LockGodX', '')
                response = response.replace('LockGodX', '')

                try:
                    file.write(response+'\n')

                    time.sleep(1/50)
                except:
                    pass

file.close()

print("Complete")
