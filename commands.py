from discord.ext import commands


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
        help='Sets the active channel for the bot. Must be specified before takes can be posted.',
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
        name='disable',
        help='Disables the bot from posting takes',
        brief='Disables the bot from posting takes'
    )
    @can_ban()
    async def disable(self, ctx, arg=None):
        if arg is None:
            self.bots[ctx.guild.id].takes_enabled = False
            self.bots[ctx.guild.id].replies_enabled = False
            await ctx.send('Takes and replies disabled')
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
        help='Enables the bot to post takes',
        brief='Enables the bot to post takes'
    )
    @can_ban()
    async def enable(self, ctx, arg=None):
        bot = self.bots[ctx.guild.id]
        if arg is None:
            bot.takes_enabled = True
            bot.replies_enabled = True
            await ctx.send('Takes and replies enabled')
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