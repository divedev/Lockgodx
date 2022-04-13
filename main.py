import discord
import os
import random
import time
from discord.ext import commands
from dotenv import load_dotenv

import bot
import commands

cmd_prefix = '$'

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.members = True
client = discord.ext.commands.Bot(command_prefix=cmd_prefix, intents=intents)

bots = {}

restricted_roles = ['Vending Machine', 'Vanilla Warrior']


@client.event
async def on_ready():
    for guild in client.guilds:
        bots[guild.id] = bot.Bot(guild.id)
        await guild.get_member(client.user.id).edit(nick=None)

    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    guild_id = message.guild.id
    bot = bots[guild_id]

    # do not respond to own messages, pins, or messages from unpermitted roles
    if (message.author == client.user) or (message.type != discord.MessageType.default) or not is_permitted(message.author):
        return
    # respond to commands
    elif message.content.startswith(cmd_prefix):
        await client.process_commands(message)
        return

    # if the message was posted in the bot's set channel, log it -- otherwise ignore it
    if message.channel.id == bot.channel_id:
        # if bot is set to warlocks only and the message is sent from a non-warlock, do not train. else train
        if bot.restricted & (not is_permitted(message.author)):
            return
        else:
            if len(bot.previous_messages) >= 10:
                bot.previous_messages = bot.previous_messages[1:]
            bot.previous_messages.append(message.content)
            bot.msgs_waited += 1 # increment the anti-spam message counter
            await bot.train(message)
    else:
        return

    # respond to mentions if ready
    if client.user in message.mentions:
        # check if there is an outstanding cooldown for the user
        if message.author.id in bot.user_mention_times.keys():
            # check if the cooldown time has elapsed
            if cooldown_check(bot.user_mention_times[message.author.id], bot.mention_wait):
                async with message.channel.typing():
                    take = bot.generate_take(message=message, trigger_icd=True)
                    await message.reply(take)
                    return
            # do not reply if user is on cooldown
            else:
                return
        else:
            async with message.channel.typing():
                take = bot.generate_take(message=message, trigger_icd=True)
                await message.reply(take)
                return

    # post randomly if ready
    if cooldown_check(bot.time_of_random, bot.random_wait):
        async with message.channel.typing():
            bot.time_of_random = time.time()

            if random.random() * 100 > bot.rant_chance:
                output = bot.generate_take(None, trigger_icd=True)
            else:
                output = bot.generate_rant(trigger_icd=True)

            bot.msgs_waited = 0 # reset the anti-spam message counter to 0
            await message.channel.send(output)


def is_permitted(author):
    roles = author.roles
    return not any(role.name in restricted_roles for role in roles)


def cooldown_check(time_of_cooldown, cooldown_length):
    return (time.time() - time_of_cooldown) > cooldown_length*60


client.add_cog(commands.Commands(client=client, bots=bots))
client.run(TOKEN)
