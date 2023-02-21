import discord.abc
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

    @commands.slash_command(
        name='set_channel',
        description='Sets the active channel for the bot. Must be specified before takes can be posted.',
    )
    @can_ban()
    async def set_channel(self, ctx, channel: discord.abc.GuildChannel = None):
        if channel is None:
            self.bots[ctx.guild.id].active_channel_id = ctx.channel.id
        else:
            self.bots[ctx.guild.id].active_channel_id = channel.id

        active_channel_name = self.client.get_channel(self.bots[ctx.guild.id].active_channel_id).mention
        await ctx.respond(f'Now active in {active_channel_name}')

    @set_channel.error
    async def set_channel_error(self, ctx, error):
        pass

    @commands.slash_command(
        name='disable',
        description='Disables the bot from posting takes'
    )
    @can_ban()
    async def disable(self, ctx, disable_type: discord.Option(str, choices=['takes', 'replies', 'both']) = None):
        if disable_type is None:
            self.bots[ctx.guild.id].takes_enabled = False
            self.bots[ctx.guild.id].replies_enabled = False
            await ctx.respond('Takes and replies disabled')
        elif disable_type == 'replies':
            self.bots[ctx.guild.id].replies_enabled = False
            await ctx.respond('Replies disabled')
        elif disable_type == 'takes':
            self.bots[ctx.guild.id].takes_enabled = False
            await ctx.respond('Takes disabled')
        else:
            pass

    @disable.error
    async def disable_error(self, ctx, error):
        pass

    @commands.slash_command(
        name='enable',
        description='Enables the bot to post takes'
    )
    @can_ban()
    async def enable(self, ctx, enable_type: discord.Option(str, choices=['takes', 'replies', 'both']) = None):
        bot = self.bots[ctx.guild.id]
        if enable_type is None:
            bot.takes_enabled = True
            bot.replies_enabled = True
            await ctx.respond('Takes and replies enabled')
        elif enable_type == 'replies':
            bot.replies_enabled = True
            await ctx.respond('Replies enabled')
        elif enable_type == 'takes':
            bot.takes_enabled = True
            await ctx.respond('Takes enabled')
        else:
            pass

    @enable.error
    async def enable_error(self, ctx, error):
        pass

    @commands.slash_command(
        name='wait',
        description='Sets the minimum delay between posting random takes, in minutes.'
    )
    @can_ban()
    async def wait(self, ctx, minutes_to_wait: float = None):
        if minutes_to_wait is None:
            await ctx.respond('Specify a wait time in minutes')
            return

        self.bots[ctx.guild.id].random_wait = minutes_to_wait
        await ctx.respond(f'Random post delay set to {minutes_to_wait} minutes')

    @wait.error
    async def wait_error(self, ctx, error):
        pass

    @commands.slash_command(
        name='rwait',
        description='Sets the minimum delay between replying to mentions, in minutes.'
    )
    @can_ban()
    async def rwait(self, ctx, minutes_to_wait: float = None):
        if minutes_to_wait is None:
            await ctx.respond('Specify a wait time in minutes')
            return

        self.bots[ctx.guild.id].mention_wait = minutes_to_wait
        await ctx.respond(f'Mention reply delay set to {minutes_to_wait} minutes')

    @rwait.error
    async def rwait_error(self, ctx, error):
        pass

    def get_cd_text(self, ctx: discord.ApplicationContext):
        bot = self.bots[ctx.guild.id]

        random_cd_remaining = self.bots[ctx.guild.id].get_remaining_cooldown().__str__()
        random_cd = (bot.random_wait * 60).__str__()
        mention_cd_remaining = self.bots[ctx.guild.id].get_remaining_cooldown(author=ctx.author).__str__()
        mention_cd = (bot.mention_wait * 60).__str__()

        random_cd_text = f'Random post cd: {random_cd_remaining}s of {random_cd}s'
        mention_cd_text = f'Reply cd ({ctx.author.name}): {mention_cd_remaining}s of {mention_cd}s'

        return f'{random_cd_text}\n{mention_cd_text}'

    @commands.slash_command(
        name='cd',
        description='Prints the remaining cooldown for posting random takes or replying to mentions'
    )
    async def cd(self, ctx):
        await ctx.respond(self.get_cd_text(ctx), ephemeral=True)

    @cd.error
    async def cd_error(self, ctx, error):
        pass

    @commands.slash_command(
        name='status',
        description='Gives the status of the bot\'s internal parameters'
    )
    async def status(self, ctx):
        bot = self.bots[ctx.guild.id]
        bot_channel = self.client.get_channel(bot.active_channel_id)

        embed = discord.Embed(title="Status", description="")
        embed.add_field(name="Active channel", value=bot_channel.mention if bot_channel is not None else "none")
        embed.add_field(name="Enabled features", value='\n'.join(feat for feat in bot.get_enabled_functions()))
        embed.add_field(name="Personality", value="")
        embed.add_field(name="Cooldowns", value=self.get_cd_text(ctx))

        await ctx.respond(embed=embed, ephemeral=True)

    @status.error
    async def status_error(self, ctx, error):
        pass
