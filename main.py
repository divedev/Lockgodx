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


client: discord.Bot = discord.Bot(intents=get_intents())

bots: dict[int, bot.Bot] = {}


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
async def on_message(message: discord.Message):
    # ignore pins and other non-user messages
    if message.type != discord.MessageType.default:
        return

    bot_instance: bot.Bot = bots[message.guild.id]

    # log message in bot's history for recent conversation context:
    bot_instance.update_recent_history(message)

    # do not respond to own messages
    if message.author == client.user:
        return

    # send the message to the bot instance that is present on the guild where the message was sent
    await bot_instance.respond(message)


# if the main directory doesn't have a 'guilds' directory, create it. if they do have a 'guilds' directory,
# make sure that 'guilds' contains a directory for each guild the bot participates in. if there are any guilds
# that do not have their own directory, create one
def setup_guilds_dir():
    dirs = [f.name for f in os.scandir() if f.is_dir()]
    if 'guilds' not in dirs:
        os.mkdir('guilds')

    guild_id_dirs = [f.name for f in os.scandir('guilds') if f.is_dir()]

    for guild in client.guilds:
        if str(guild.id) not in guild_id_dirs:
            create_new_guild_dir(guild.id)


# set up guild-specific information like bot settings and trait options, initialized to default values
def create_new_guild_dir(guild_id: int):
    os.mkdir(f'guilds/{guild_id}')
    os.mkdir(f'guilds/{guild_id}/traits')

    with open(f'guilds/{guild_id}/settings.json', 'w', newline='\n') as json_file:
        json.dump({'channel': None,
                   'posts_enabled': True,
                   'replies_enabled': True,
                   'post_cd': 5,
                   'reply_cd': 5,
                   'msgs_wait': 10}, json_file, indent=2)

    default_trait_options = load_default_trait_options()
    for trait_option_type in default_trait_options.keys():
        with open(f'guilds/{guild_id}/traits/{trait_option_type}.json', 'w', newline='\n') as json_file:
            json.dump(default_trait_options[trait_option_type], json_file, indent=2)


def load_default_trait_options() -> dict:
    # TODO: handle errors
    with open('default_trait_options.json', 'r') as json_file:
        return json.load(json_file)


client.add_cog(commands.Commands(client=client, bots=bots))
client.run(DISCORD_TOKEN)
