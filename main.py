import os
import time

import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv

import bot
import commands

cmd_prefix = '$'

load_dotenv()
TOKEN = os.getenv('TOKEN')

bad_words_file = 'bad_words.txt'

intents = discord.Intents.default()
intents.members = True
client = discord.ext.commands.Bot(command_prefix=cmd_prefix, intents=intents)

bots = {}


@client.event
async def on_ready():
    setup_guilds_dir()

    for guild in client.guilds:
        bots[guild.id] = bot.Bot(guild.id)

        bots[guild.id].bad_words = get_bad_words()

        await guild.get_member(client.user.id).edit(nick=None)

    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    guild_id = message.guild.id
    bot = bots[guild_id]

    # do not respond to own messages or pins
    if (message.author == client.user) \
            or (message.type != discord.MessageType.default):
        return
    # respond to commands
    elif message.content.startswith(cmd_prefix):
        await client.process_commands(message)
        return

    # respond to mentions if ready
    if client.user in message.mentions:
        # check if there is an outstanding cooldown for the user
        if message.author.id in bot.user_mention_times.keys():
            # check if the cooldown time has elapsed
            if cooldown_check(bot.user_mention_times[message.author.id], bot.mention_wait):
                async with message.channel.typing():
                    output = bot.generate_take(message=message)

                    await message.reply(output)
            # do not reply if user is on cooldown
            else:
                return
        else:
            async with message.channel.typing():
                take = bot.generate_take(message=message)
                await message.reply(take)

        bot.start_reply_cd(message.author)

        return

    # post randomly if ready
    if cooldown_check(bot.time_of_random, bot.random_wait) and (bot.msgs_waited >= bot.msgs_wait):
        async with message.channel.typing():
            bot.time_of_random = time.time()

            output = bot.generate_take()

            bot.msgs_waited = 0  # reset the anti-spam message counter to 0

            if output is not None:
                await message.channel.send(output)
            else:
                pass


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error


def setup_guilds_dir():
    dirs = [ f.name for f in os.scandir() if f.is_dir() ]
    if 'guilds' not in dirs:
        os.mkdir('guilds')

    guild_id_dirs = [ f.name for f in os.scandir('guilds') if f.is_dir() ]

    for guild in client.guilds:
        if str(guild.id) not in guild_id_dirs:
            os.mkdir(f'guilds/{guild.id}')


def cooldown_check(time_of_cooldown, cooldown_length):
    return (time.time() - time_of_cooldown) > cooldown_length*60


def get_bad_words():
    bad_words = []

    try:
        with open(bad_words_file, 'r') as f:
            for line in f.readlines():
                if len(line.strip()) > 0:
                    bad_words.append(line.strip())
    except:
        print("Could not load bad words file. Create 'bad_words.txt' in the main directory to enable bad word filtering.")

    return bad_words


client.add_cog(commands.Commands(client=client, bots=bots))
client.run(TOKEN)
