import json

import discord.abc
from discord.ext import commands

import bot
from traits_view import TraitsView


def can_ban():
    async def predicate(ctx: commands.Context):  # TODO: verify this works

        perm_check = any((role.permissions.ban_members in role.permissions) for role in ctx.author.roles)

        return perm_check

    return commands.check(predicate)


class Commands(commands.Cog, name='Commands'):
    def __init__(self, client: discord.Bot, bots: dict[int, bot.Bot]):
        self.client = client
        self.bots = bots

    @commands.slash_command(
        name='set_channel',
        description='Sets the active channel for the bot. Must be specified before bot posts can be made.',
    )
    @can_ban()
    async def set_channel(self, ctx: discord.ApplicationContext, channel: discord.abc.GuildChannel = None):
        bot = self.bots[ctx.guild.id]

        if channel:
            bot.active_channel_id = channel.id
        else:
            bot.active_channel_id = ctx.channel.id

        active_channel_name = self.client.get_channel(bot.active_channel_id).mention
        await ctx.respond(f'Now active in {active_channel_name}')

        update_setting(ctx.guild.id, 'channel', bot.active_channel_id)

    @set_channel.error
    async def set_channel_error(self, ctx: discord.ApplicationContext, error):
        pass

    @commands.slash_command(
        name='disable',
        description='Disables the bot from posting or replying'
    )
    @can_ban()
    async def disable(self, ctx: discord.ApplicationContext, disable_type: discord.Option(str, choices=['posts', 'replies', 'both']) = None):
        bot = self.bots[ctx.guild.id]

        if disable_type is None:
            bot.posts_enabled = False
            bot.replies_enabled = False
            await ctx.respond('Posts and replies disabled')

            update_setting(ctx.guild.id, 'posts_enabled', False)
            update_setting(ctx.guild.id, 'replies_enabled', False)
        elif disable_type == 'replies':
            bot.replies_enabled = False
            await ctx.respond('Replies disabled')

            update_setting(ctx.guild.id, 'replies_enabled', False)
        elif disable_type == 'posts':
            bot.posts_enabled = False
            await ctx.respond('Posts disabled')

            update_setting(ctx.guild.id, 'posts_enabled', False)
        else:
            pass

    @disable.error
    async def disable_error(self, ctx: discord.ApplicationContext, error):
        pass

    @commands.slash_command(
        name='enable',
        description='Enables the bot to post or reply'
    )
    @can_ban()
    async def enable(self, ctx: discord.ApplicationContext, enable_type: discord.Option(str, choices=['posts', 'replies', 'both']) = None):
        bot = self.bots[ctx.guild.id]

        if enable_type is None:
            bot.posts_enabled = True
            bot.replies_enabled = True
            await ctx.respond('Posts and replies enabled')

            update_setting(ctx.guild.id, 'posts_enabled', True)
            update_setting(ctx.guild.id, 'replies_enabled', True)
        elif enable_type == 'replies':
            bot.replies_enabled = True
            await ctx.respond('Replies enabled')

            update_setting(ctx.guild.id, 'replies_enabled', True)
        elif enable_type == 'posts':
            bot.posts_enabled = True
            await ctx.respond('Posts enabled')

            update_setting(ctx.guild.id, 'posts_enabled', True)
        else:
            pass

    @enable.error
    async def enable_error(self, ctx: discord.ApplicationContext, error):
        pass

    # TODO: set this and set_reply_cd to the same command, with options
    @commands.slash_command(
        name='set_cd',
        description='Sets the minimum delay between posting, in minutes.'
    )
    @can_ban()
    async def set_post_cd(self, ctx: discord.ApplicationContext, minutes_to_wait: float = None):
        bot = self.bots[ctx.guild.id]

        if minutes_to_wait is None:
            await ctx.respond('Specify a post cooldown in minutes')
            return

        bot.post_cd = minutes_to_wait
        await ctx.respond(f'Post cooldown set to {minutes_to_wait} minutes')

        update_setting(ctx.guild.id, 'post_cd', minutes_to_wait)

    @set_post_cd.error
    async def set_cd_error(self, ctx: discord.ApplicationContext, error):
        pass

    @commands.slash_command(
        name='set_reply_cd',
        description='Sets the minimum delay between replying, in minutes.'
    )
    @can_ban()
    async def set_reply_cd(self, ctx: discord.ApplicationContext, minutes_to_wait: float = None):
        bot = self.bots[ctx.guild.id]

        if minutes_to_wait is None:
            await ctx.respond('Specify a cooldown in minutes')
            return

        bot.reply_cd = minutes_to_wait
        await ctx.respond(f'Reply cooldown set to {minutes_to_wait} minutes')

        update_setting(ctx.guild.id, 'reply_cd', minutes_to_wait)

    @set_reply_cd.error
    async def set_reply_cd_error(self, ctx: discord.ApplicationContext, error):
        pass

    @commands.slash_command(
        name='set_msgs_wait',
        description='Sets the number of user messages to wait between posting.'
    )
    @can_ban()
    async def set_msgs_wait(self, ctx: discord.ApplicationContext, msgs_to_wait: int = None):
        bot = self.bots[ctx.guild.id]

        if msgs_to_wait is None:
            await ctx.respond('Specify the number of messages to wait between posts')
            return

        bot.msgs_wait = msgs_to_wait
        await ctx.respond(f'Waiting {msgs_to_wait} messages between posts')

        update_setting(ctx.guild.id, 'msgs_wait', msgs_to_wait)

    @set_msgs_wait.error
    async def set_msgs_wait_error(self, ctx: discord.ApplicationContext, error):
        pass

    def get_cd_text(self, ctx: discord.ApplicationContext):
        bot = self.bots[ctx.guild.id]

        post_cd_remaining = bot.get_remaining_cooldown().__str__()
        post_cd = (bot.post_cd * 60).__str__()
        reply_cd_remaining = bot.get_remaining_cooldown(author=ctx.author).__str__()
        reply_cd = (bot.reply_cd * 60).__str__()

        post_cd_text = f'Post cd: {post_cd_remaining}s of {post_cd}s'
        reply_cd_text = f'Reply cd ({ctx.author.name}): {reply_cd_remaining}s of {reply_cd}s'

        return f'{post_cd_text}\n{reply_cd_text}'

    @commands.slash_command(
        name='cd',
        description='Prints the remaining cooldown for posting or replying to mentions'
    )
    async def cd(self, ctx: discord.ApplicationContext):
        await ctx.respond(self.get_cd_text(ctx), ephemeral=True)

    @cd.error
    async def cd_error(self, ctx: discord.ApplicationContext, error):
        pass

    @commands.slash_command(
        name='status',
        description='Gives the status of the bot\'s internal parameters'
    )
    async def status(self, ctx: discord.ApplicationContext):
        bot = self.bots[ctx.guild.id]
        bot_channel = self.client.get_channel(bot.active_channel_id)

        embed = discord.Embed(title="Status", description="")
        embed.add_field(name="Active channel", value="none" if bot_channel is None else bot_channel.mention)
        embed.add_field(name="Enabled features", value='\n'.join(feat for feat in bot.get_enabled_functions()))
        embed.add_field(name="Personality", value="")  # TODO: implement
        embed.add_field(name="Cooldowns", value=self.get_cd_text(ctx))

        await ctx.respond(embed=embed, ephemeral=True)

    @status.error
    async def status_error(self, ctx: discord.ApplicationContext, error):
        pass

    @commands.slash_command(
        name='traits',
        description='Set the bot\'s personality traits'
    )
    async def traits(self, ctx: discord.ApplicationContext):
        bot = self.bots[ctx.guild.id]
        await ctx.respond(view=TraitsView(bot), ephemeral=True)

    @traits.error
    async def traits_error(self, ctx, error):
        pass


# TODO: handle r/w errors
def update_setting(guild_id: int, setting: str, val):
    settings_file_path = f'guilds/{guild_id}/settings.json'

    with open(settings_file_path, 'r') as settings_file:
        settings_data = json.load(settings_file)

        if setting in settings_data:
            settings_data[setting] = val

    with open(settings_file_path, 'w') as settings_file:
        json.dump(settings_data, settings_file, indent=2)
