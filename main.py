import json
import os

import discord
from dotenv import load_dotenv

import bot
import commands

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')


def get_intents() -> discord.Intents:

    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    intents.members = True
    intents.typing = True
    intents.reactions = True
    intents.emojis_and_stickers = True

    return intents


client = discord.Bot(intents=get_intents())

bots = {}


@client.event
async def on_ready():
    setup_guilds_dir()

    for guild in client.guilds:
        bots[guild.id] = bot.Bot(client, guild.id)
        await guild.get_member(client.user.id).edit(nick=None)

    print('Logged in as {0.user}'.format(client))
    for guild in client.guilds:
        print(f'Active in guild: {guild.name}')


@client.event
async def on_message(message):
    # do not respond to own messages, pins, or other non-user messages
    if (message.author == client.user) or (message.type != discord.MessageType.default):
        return

    # send the message to the bot instance that is present on the guild where the message was sent
    await bots[message.guild.id].respond(message)


def setup_guilds_dir():
    dirs = [f.name for f in os.scandir() if f.is_dir()]
    if 'guilds' not in dirs:
        os.mkdir('guilds')

    guild_id_dirs = [f.name for f in os.scandir('guilds') if f.is_dir()]

    for guild in client.guilds:
        if str(guild.id) not in guild_id_dirs:
            create_new_guild_dir(guild.id)


def create_new_guild_dir(guild_id: int):
    os.mkdir(f'guilds/{guild_id}')
    os.mkdir(f'guilds/{guild_id}/prompts')

    # make a new settings file with default values
    with open(f'guilds/{guild_id}/settings.json', 'w', newline='\n') as json_file:
        json.dump({'channel': None,
                   'posts_enabled': True,
                   'replies_enabled': True,
                   'post_cd': 5,
                   'reply_cd': 5,
                   'msgs_wait': 10}, json_file, indent=2)


client.add_cog(commands.Commands(client=client, bots=bots))
client.run(DISCORD_TOKEN)
