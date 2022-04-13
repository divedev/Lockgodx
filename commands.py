import os
import re
from discord.ext import commands

import format


def can_ban():
    async def predicate(ctx):
        author_roles = ctx.author.roles
        perms = [role.permissions for role in author_roles]
        can_ban = False

        for perm in perms:
            if perm.ban_members:
                can_ban = True

        return can_ban

    return commands.check(predicate)


class Commands(commands.Cog, name='Commands'):
    def __init__(self, client, bots):
        self.client = client
        self.bots = bots

    @commands.command(
        name='set_channel',
        help='Sets the active channel for the bot. Must be specified before takes or rants can be posted.',
        brief='Sets the active channel for the bot.'
    )
    @can_ban()
    async def set_channel(self, ctx, arg=None):
        if arg is not None:
            self.bots[ctx.guild.id].channel_id = int(arg[2:-1])
        else:
            self.bots[ctx.guild.id].channel_id = ctx.channel.id

        await ctx.send(f'Now active in {self.client.get_channel(self.bots[ctx.guild.id].channel_id).mention}')

    @set_channel.error
    async def set_channel_error(self, ctx, error):
        return

    @commands.command(
        name='take',
        help='Posts a single take, based on its current model. Bypasses internal cooldown',
        brief='Posts a single take. Bypasses internal cooldown'
    )
    @can_ban()
    async def take(self, ctx):
        if self.bots[ctx.guild.id].channel_id != '':
            async with ctx.typing():
                await ctx.send(self.bots[ctx.guild.id].generate_take(message=None))
        else:
            await ctx.send('Must set an active channel first')

    @take.error
    async def take_error(self, ctx, error):
        return

    @commands.command(
        name='rant',
        help='Posts a rant made by stitching together individual takes. Size can be set by `rant_size`. Bypasses internal cooldown',
        brief='Posts a rant. Bypasses internal cooldown'
    )
    @can_ban()
    async def rant(self, ctx, arg=None):
        if self.bots[ctx.guild.id].channel_id != '':
            async with ctx.typing():
                if arg is not None:
                    rant = self.bots[ctx.guild.id].generate_rant(rant_size=int(arg))
                else:
                    rant = self.bots[ctx.guild.id].generate_rant()

                await ctx.send(rant)
        else:
            await ctx.send('Must sent an active channel first')

    @rant.error
    async def rant_error(self, ctx, error):
        return

    @commands.command(
        name='rant_chance',
        help='Sets the chance of a random take being a rant instead. Is specified in %, i.e. `$rant_chance 5` corresponds to a 5% chance',
        brief='Sets the chance of a random take being a rant instead'
    )
    @can_ban()
    async def rant_chance(self, ctx, arg):
        self.bots[ctx.guild.id].rant_chance = float(arg)
        await ctx.send(f'Chance of ranting set to {self.bots[ctx.guild.id].rant_chance}%')

    @rant_chance.error
    async def rant_chance_error(self, ctx, error):
        return

    @commands.command(
        name='rant_size',
        help='Changes rant size. Must specify an integer, corresponding to the number of takes to generate for the rant. Capped at 2000 characters',
        brief='Changes rant size. Must specify an integer'
    )
    @can_ban()
    async def rant_size(self, ctx, arg):
        self.bots[ctx.guild.id].rant_size = int(arg)
        await ctx.send(f'Rant size set to {self.bots[ctx.guild.id].rant_size}')

    @rant_size.error
    async def rant_size_error(self, ctx, error):
        return

    @commands.command(
        name='reset',
        help='Resets the bot to untrained status.',
        brief='Resets the bot to untrained status.'
    )
    @can_ban()
    async def reset(self, ctx):
        await ctx.guild.get_member(self.client.user.id).edit(nick=None)
        self.bots[ctx.guild.id].reset()
        await ctx.send('Model reset.')

    @reset.error
    async def reset_error(self, ctx, error):
        return

    @commands.command(
        name='save',
        help='Saves the bot\'s model to json file. Name can be specified, otherwise it overwrites "default"',
        brief='Saves the bot\'s model to specified file'
    )
    @can_ban()
    async def save(self, ctx, arg=None):
        if arg is None:
            arg = 'default'

        if self.bots[ctx.guild.id].model.save_model(model_name=arg) is not None:
            await ctx.send(f'Model \"{arg}\" saved.')
        else:
            await ctx.send('Failed to save model.')

    @save.error
    async def save_error(self, ctx, error):
        return

    @commands.command(
        name='load',
        help='Loads a previous model from the specified file',
        brief='Loads a previous model from the specified file'
    )
    @can_ban()
    async def load(self, ctx, arg=None):
        bot = self.bots[ctx.guild.id]
        await ctx.guild.get_member(self.client.user.id).edit(nick=None)

        if arg is None:
            arg = 'default'

        bot.reset()
        bot.current_data_set = arg
        if bot.model.load_model(model_name=arg) is not None:
            await ctx.send(f'Model \"{arg}\" loaded.')
        else:
            await ctx.send('Failed to load model.')

    @load.error
    async def load_error(self, ctx, error):
        return

    @commands.command(
        name='train',
        help='Resets the bot\'s model, then trains on the specified data set',
        brief='Trains on the specified data set'
    )
    @can_ban()
    async def train(self, ctx, arg):
        if self.bots[ctx.guild.id].current_data_set == arg:
            await ctx.send(f'Already trained on {arg}')
        else:
            try:
                await ctx.guild.get_member(self.client.user.id).edit(nick=None)
                await ctx.send(f'Training on {arg} set')
                self.bots[ctx.guild.id].train_on_files(arg)
                await ctx.send(f'Trained on {arg} set')
            except FileNotFoundError:
                await ctx.send(f'Dataset {arg} not found')

    @train.error
    async def train_error(self, ctx, error):
        return

    @commands.command(
        name='disable',
        help='Disables the bot from posting takes or rants',
        brief='Disables the bot from posting takes or rants'
    )
    @can_ban()
    async def disable(self, ctx, arg=None):
        if arg is None:
            self.bots[ctx.guild.id].takes_enabled = False
            self.bots[ctx.guild.id].replies_enabled = False
            self.bots[ctx.guild.id].gifs_enabled = False
            await ctx.send('Takes, replies, and gifs disabled')
        elif arg == 'gifs':
            self.bots[ctx.guild.id].gifs_enabled = False
            await ctx.send('Gifs disabled')
        elif arg == 'replies':
            self.bots[ctx.guild.id].replies_enabled = False
            await ctx.send('Replies disabled')
        elif arg == 'takes':
            self.bots[ctx.guild.id].takes_enabled = False
            await ctx.send('Takes disabled')
        else:
            pass

    @disable.error
    async def disable_error(self, ctx, error):
        return

    @commands.command(
        name='enable',
        help='Enables the bot to post takes and rants',
        brief='Enables the bot to post takes and rants'
    )
    @can_ban()
    async def enable(self, ctx, arg=None):
        bot = self.bots[ctx.guild.id]
        if arg is None:
            bot.takes_enabled = True
            bot.replies_enabled = True
            bot.gifs_enabled = True
            await ctx.send('Takes, replies, and gifs enabled')
        elif arg == 'gifs':
            if bot.TENOR_TOKEN is not None:
                bot.gifs_enabled = True
                await ctx.send('Gifs enabled')
            else:
                await ctx.send('Cannot use gifs without Tenor token')
        elif arg == 'replies':
            bot.replies_enabled = True
            await ctx.send('Replies enabled')
        elif arg == 'takes':
            bot.takes_enabled = True
            await ctx.send('Takes enabled')
        else:
            pass

    @enable.error
    async def enable_error(self, ctx, error):
        return

    @commands.command(
        name='wait',
        help='Sets the minimum delay between posting random takes, in minutes. Example: `$wait 5` sets his random post '
             'internal cooldown to 5 minutes',
        brief='Sets the delay between posting random takes, in minutes'
    )
    @can_ban()
    async def wait(self, ctx, arg=None):
        if arg is not None:
            self.bots[ctx.guild.id].random_wait = float(arg)

            await ctx.send(f'Random post delay set to {arg} minutes')
        else:
            await ctx.send('Specify a wait time e.g. `$wait 5`')

    @wait.error
    async def wait_error(self, ctx, error):
        return

    @commands.command(
        name='rwait',
        help='Sets the minimum delay between replying to mentions, in minutes. Example: `$wait 5` sets his mention reply '
             'internal cooldown to 5 minutes',
        brief='Sets the delay between replying to mentions, in minutes'
    )
    @can_ban()
    async def rwait(self, ctx, arg=None):
        if arg is not None:
            self.bots[ctx.guild.id].mention_wait = float(arg)

            await ctx.send(f'Mention reply delay set to {arg} minutes')
        else:
            await ctx.send('Specify a wait time e.g. `$rwait 5`')

    @rwait.error
    async def rwait_error(self, ctx, error):
        return

    @commands.command(
        name='learn',
        help='Toggles the bot\'s ability to learn from new messages. The bot will only learn from messages posted in the '
             'same channel that it is active in.',
        brief='Toggles the bot\'s ability to learn from new messages'
    )
    @can_ban()
    async def learn(self, ctx, arg=None):
        if arg is None:
            self.bots[ctx.guild.id].learn = not self.bots[ctx.guild.id].learn
        elif arg.lower() == 'true':
            self.bots[ctx.guild.id].learn = True
        elif arg.lower() == 'false':
            self.bots[ctx.guild.id].learn = False

        await ctx.send(f'Learning set to {self.bots[ctx.guild.id].learn}')

    @learn.error
    async def learn_error(self, ctx, error):
        return

    @commands.command(
        name='lock_only',
        help='Toggles the bot\'s ability to train on messages from users with Vending Machine or Vanilla Warrior roles',
        brief='Toggles the bot\'s ability to train from blue or brown names'
    )
    @can_ban()
    async def lock_only(self, ctx, arg=None):
        if arg is None:
            self.bots[ctx.guild.id].restricted = not self.bots[ctx.guild.id].restricted
        elif arg.lower() == 'true':
            self.bots[ctx.guild.id].restricted = True
        elif arg.lower() == 'false':
            self.bots[ctx.guild.id].restricted = False

        await ctx.send(f'Learning from warlocks only: {self.bots[ctx.guild.id].restricted}')

    @lock_only.error
    async def lock_only_error(self, ctx, error):
        return

    @commands.command(
        name='cd',
        help='Prints the remaining cooldown for posting random takes or replying to mentions',
        brief='Prints remaining message cooldowns'
    )
    async def cd(self, ctx):
        random_cd_remaining = self.bots[ctx.guild.id].get_remaining_cooldown(string=True)
        random_cd = format.time_to_text(minutes=self.bots[ctx.guild.id].random_wait)
        mention_cd_remaining = self.bots[ctx.guild.id].get_remaining_cooldown(author=ctx.author, string=True)
        mention_cd = format.time_to_text(minutes=self.bots[ctx.guild.id].mention_wait)

        random_cd_text = f'Random post cd: {random_cd_remaining} of {random_cd}'
        mention_cd_text = f'Mention reply cd ({ctx.author.name}): {mention_cd_remaining} of {mention_cd}'

        await ctx.send(f'{random_cd_text}\n{mention_cd_text}')

    @cd.error
    async def cd_error(self, ctx, error):
        return

    @commands.command(
        name='status',
        help='Gives the status of the bot\'s internal parameters',
        brief='Gives the status of the bot\'s internal parameters'
    )
    async def status(self, ctx):
        channel = self.client.get_channel(self.bots[ctx.guild.id].channel_id)

        if channel is not None:
            status_text = f'LGX STATUS\n\n**Active channel**: {channel.mention}\n' + self.bots[ctx.guild.id].status(ctx.author)
        else:
            status_text = f'LGX STATUS\n\n**Active channel**: none\n' + self.bots[ctx.guild.id].status(ctx.author)
        await ctx.reply(status_text)

    @status.error
    async def status_error(self, ctx, error):
        return


    @commands.command(
        name='sim',
        help='Simulates the specified user. Must use their tag/mention',
        brief='Simulates the specified user'
    )
    @can_ban()
    async def sim(self, ctx, arg):
        await ctx.guild.get_member(self.client.user.id).edit(nick=None)
        self.bots[ctx.guild.id].reset()

        channel = ctx.channel

        user_id = int(re.sub('[^0-9]', '', arg))
        user = ctx.guild.get_member(user_id)
        usertag = f'{user.name}#{user.discriminator}'
        full_path = f'{self.bots[ctx.guild.id].training_root_dir}/users/'

        if f'{usertag}.txt' not in os.listdir(full_path):
            await channel.send(f'Collecting data for {usertag}')
            hist = [msg.content for msg in await channel.history(limit=99999).flatten() if msg.author.id == user_id]
            format.write_history(hist, root_dir=f'{self.bots[ctx.guild.id].training_root_dir}/users/',
                                 file_name=usertag)
        else:
            await channel.send(f'Found existing data for {usertag}')

        self.bots[ctx.guild.id].train_on_files(train_dir='users', file=f'{usertag}.txt')
        await channel.send(f'Now simulating {usertag}')
        await ctx.guild.get_member(self.client.user.id).edit(nick=f'{user.name}bot')

    @sim.error
    async def sim_error(self, ctx, error):
        return

    @commands.command(
        name='data',
        help='Displays the list of available datasets for use by calling `$train <dataset name>`. User data can be found with `$data @user`',
        brief='Gives info about available datasets or userdata'
    )
    @can_ban()
    async def data(self, ctx, arg=None):
        if arg is None:
            datasets = [f.name for f in os.scandir(self.bots[ctx.guild.id].training_root_dir) if f.is_dir()]
            await ctx.send(f'Available datasets: {datasets}')
        else:
            user_id = int(arg[3:-1])
            user = ctx.guild.get_member(user_id)
            usertag = f'{user.name}#{user.discriminator}'
            full_path = f'{self.bots[ctx.guild.id].training_root_dir}/users/'

            if f'{usertag}.txt' in os.listdir(full_path):
                entire_path = f"{full_path}{usertag}.txt"
                ct = 0
                with open(entire_path, "r", encoding='cp437') as f:
                    for line in f:
                        if line.strip():
                            ct += 1
                    await ctx.send(f'{ct} lines found for {usertag}')
            else:
                await ctx.send(f'No data found for {arg}')

    @data.error
    async def data_error(self, ctx, error):
        return

    @commands.command(
        name='models',
        help='Displays the list of previously-saved markov models',
        brief='Displays the list of previously-saved markov models'
    )
    @can_ban()
    async def models(self, ctx):
        model_dir = self.bots[ctx.guild.id].model.root_dir
        await ctx.send(f'Saved models: {[f.split(".")[0] for f in os.listdir(model_dir) if f.endswith(".json")]}')

    @models.error
    async def models_error(self, ctx, error):
        return

    @commands.command(
        name='gif_chance',
        help='Sets the % chance of posting a gif',
        brief='Sets the % chance of posting a gif'
    )
    @can_ban()
    async def gif_chance(self, ctx, arg):
        self.bots[ctx.guild.id].gif_chance = float(arg)
        await ctx.send(f'Chance of posting a gif set to {self.bots[ctx.guild.id].gif_chance}%')

    @gif_chance.error
    async def gif_chance_error(self, ctx, error):
        return