import discord
import collections
import datetime
import math
import subprocess
import asyncio
import random
import glob
import gc
import psutil
import sys
import re
import os
from datetime import timezone
from .utils.dataIO import fileIO
from discord_webhooks import *
from .utils import checks
from discord.ext import commands

class Avatar:

def __init__(self, bot):
        self.bot = bot
		bot.avatar = none
		bot.avatar_interval = none
    with open('settings/avatars.json', 'r') as g:
        avatars = json.load(g)
    bot.avatar_interval = avatars['interval']
    if os.listdir('avatars') and avatars['interval'] != '0':
        all_avis = os.listdir('avatars')
        all_avis.sort()
        avi = random.choice(all_avis)
        bot.avatar = avi
		

    @commands.group(aliases=['avatars'], pass_context=True)
    async def avatar(self, ctx):
        """Rotate avatars. See wiki for more info."""

        if ctx.invoked_subcommand is None:
            with open('settings/avatars.json', 'r+') as a:
                avi_config = json.load(a)
            if avi_config['password'] == '':
                return await self.bot.send_message(ctx.message.channel, 'Cycling avatars requires you to input your password. Your password will not be sent anywhere and no one will have access to it. '
                                                                                     'Enter your password with``>avatar password <password>`` Make sure you are in a private channel where no one can see!')
            if avi_config['interval'] != '0':
                self.bot.avatar = None
                self.bot.avatar_interval = None
                avi_config['interval'] = '0'
                with open('settings/avatars.json', 'w') as avi:
                    json.dump(avi_config, avi, indent=4)
                await self.bot.send_message(ctx.message.channel, 'Disabled cycling of avatars.')
            else:
                if os.listdir('avatars'):
                    await self.bot.send_message(ctx.message.channel, 'Enabled cycling of avatars. Input interval in seconds to wait before changing avatars (``n`` to cancel):')

                    def check(msg):
                        return msg.content.isdigit() or msg.content.lower().strip() == 'n'

                    def check2(msg):
                        return msg.content == 'random' or msg.content.lower().strip() == 'r' or msg.content.lower().strip() == 'order' or msg.content.lower().strip() == 'o'
                    interval = await self.bot.wait_for_message(author=ctx.message.author, check=check, timeout=60)
                    if not interval:
                        return
                    if interval.content.lower().strip() == 'n':
                        return await self.bot.send_message(ctx.message.channel, 'Cancelled.')
                    elif int(interval.content) < 1800:
                        return await self.bot.send_message(ctx.message.channel, 'Cancelled. Interval is too short. Must be at least 1800 seconds (30 minutes).')
                    else:
                        avi_config['interval'] = int(interval.content)
                    if len(os.listdir('avatars')) != 2:
                        await self.bot.send_message(ctx.message.channel, 'Change avatars in order or randomly? Input ``o`` for order or ``r`` for random:')
                        cycle_type = await self.bot.wait_for_message(author=ctx.message.author, check=check2, timeout=60)
                        if not cycle_type:
                            return
                        if cycle_type.content.strip() == 'r' or cycle_type.content.strip() == 'random':
                            await self.bot.send_message(ctx.message.channel,
                                                        'Avatar cycling enabled. Avatar will randomly change every ``%s`` seconds' % interval.content.strip())
                            loop_type = 'random'
                        else:
                            loop_type = 'ordered'
                    else:
                        loop_type = 'ordered'
                    avi_config['type'] = loop_type
                    if loop_type == 'ordered':
                        await self.bot.send_message(ctx.message.channel,
                                                    'Avatar cycling enabled. Avatar will change every ``%s`` seconds' % interval.content.strip())
                    with open('settings/avatars.json', 'r+') as avi:
                        avi.seek(0)
                        avi.truncate()
                        json.dump(avi_config, avi, indent=4)
                    self.bot.avatar_interval = interval.content
                    self.bot.avatar = random.choice(os.listdir('avatars'))

                else:
                    await self.bot.send_message(ctx.message.channel, 'No images found under ``avatars``. Please add images (.jpg .jpeg and .png types only) to that folder and try again.')

    @avatar.command(aliases=['pass', 'pw'], pass_context=True)
    async def password(self, ctx, *, msg):
        """Set your discord acc password to rotate avatars. See wiki for more info."""
        with open('settings/avatars.json', 'r+') as a:
            avi_config = json.load(a)
            avi_config['password'] = msg.strip().strip('"').lstrip('<').rstrip('>')
            a.seek(0)
            a.truncate()
            json.dump(avi_config, a, indent=4)
        await self.bot.delete_message(ctx.message)
        return await self.bot.send_message(ctx.message.channel, 'Password set. Do ``>avatar`` to toggle cycling avatars.')
		
		
def check_folders():
    if not os.path.exists("data/avatars"):
        print("Creating data/avatars folder...")
        os.makedirs("data/avatars")
		
def check_files():
    settings = {'password': '', 'interval': '0', 'type': 'random'}, avis, indent=4

    f = "data/avatars/avatars.json"
    if not fileIO(f, "check"):
        print("Creating empty settings.json...")
        fileIO(f, "save", settings)
		

		        # Cycles avatar if avatar cycling is enabled.
        if hasattr(bot, 'avatar_time') and hasattr(bot, 'avatar'):
            if bot.avatar:
                if bot.avatar_interval:
                    if avatar_time_check(bot, bot.avatar_time, bot.avatar_interval):
                        with open('settings/avatars.json') as g:
                            avi_config = json.load(g)
                        all_avis = glob.glob('avatars/*.jpg')
                        all_avis.extend(glob.glob('avatars/*.jpeg'))
                        all_avis.extend(glob.glob('avatars/*.png'))
                        all_avis = os.listdir('avatars')
                        all_avis.sort()
                        if avi_config['type'] == 'random':
                            while next_avatar == current_avatar:
                                next_avatar = random.randint(0, len(all_avis) - 1)
                            current_avatar = next_avatar
                            bot.avatar = all_avis[next_avatar]
                            with open('avatars/%s' % bot.avatar, 'rb') as fp:
                                await bot.edit_profile(password=avi_config['password'], avatar=fp.read())
                        else:
                            if next_avatar + 1 == len(all_avis):
                                next_avatar = 0
                            else:
                                next_avatar += 1
                            bot.avatar = all_avis[next_avatar]
                            with open('avatars/%s' % bot.avatar, 'rb') as fp:
                                await bot.edit_profile(password=avi_config['password'], avatar=fp.read())



								
def setup(bot):
    check_folders()
    check_files()
    n = Avatar(bot)
    bot.add_cog(n)