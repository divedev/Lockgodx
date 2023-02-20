import os

import discord
from dotenv import load_dotenv

import bot
import commands

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

bad_words_file = 'bad_words.txt'

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.emojis_and_stickers = True
intents.reactions = True

client = discord.Bot(intents=intents)

bots = {}


@client.event
async def on_ready():
    setup_guilds_dir()

    for guild in client.guilds:
        bots[guild.id] = bot.Bot(client, guild.id)

        bots[guild.id].bad_words = get_bad_words()

        await guild.get_member(client.user.id).edit(nick=None)

    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    # do not respond to own messages or pins
    if (message.author == client.user) \
            or (message.type != discord.MessageType.default):
        return

    guild_id = message.guild.id
    bot_instance = bots[guild_id]

    await bot_instance.respond(message)


@client.event
async def on_command_error():
    pass


def setup_guilds_dir():
    dirs = [f.name for f in os.scandir() if f.is_dir()]
    if 'guilds' not in dirs:
        os.mkdir('guilds')

    guild_id_dirs = [f.name for f in os.scandir('guilds') if f.is_dir()]

    for guild in client.guilds:
        if str(guild.id) not in guild_id_dirs:
            os.mkdir(f'guilds/{guild.id}')


def get_bad_words():
    bad_words = []

    try:
        with open(bad_words_file, 'r') as f:
            for line in f.readlines():
                if len(line.strip()) > 0:
                    bad_words.append(line.strip())
    except:
        print("Could not load bad words file. "
              "Create 'bad_words.txt' in the main directory to enable bad word filtering.")

    return bad_words


client.add_cog(commands.Commands(client=client, bots=bots))
client.run(DISCORD_TOKEN)
