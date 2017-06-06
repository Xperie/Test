import discord
import collections
import datetime
import math
import subprocess
import asyncio
import random
import glob
import psutil
import strawpy
import sys
import re
import os
import gc
from bs4 import BeautifulSoup
from datetime import timezone
from .utils.dataIO import fileIO
from discord_webhooks import *
from .utils import checks
from discord.ext import commands
from discord.ext.commands import Context
from __main__ import send_cmd_help
from .utils.allmsgs import *

class Avatar:

	def __init__(self, bot):
		self.bot = bot
		self.bot.avatar = None	
		self.bot.avatar_interval = None
		if not os.path.exists('data/avatars'):
			os.makedirs('data/avatars')
			os.makedirs('data/avatars/settings')
		if not os.path.isfile('data/avatars/settings/avatars.json'):
			with open('data/avatars/settings/avatars.json', 'w') as avis:
				json.dump({'password': '', 'interval': '0', 'type': 'random'}, avis, indent=4)
		with open('data/avatars/settings/avatars.json', 'r') as g:
			avatars = json.load(g)
		self.bot.avatar_interval = avatars['interval']
		if os.listdir('data/avatars') and avatars['interval'] != '0':
			all_avis = os.listdir('data/avatars')
			all_avis.sort()
			avi = random.choice(all_avis)
			self.bot.avatar = avi	
		with open('data/avatars/settings/avatars.json', 'r') as g:
			avatars = json.load(g)
		self.bot.avatar_interval = avatars['interval']
		if os.listdir('data/avatars') and avatars['interval'] != '0':
			all_avis = os.listdir('data/avatars')
			all_avis.sort()
			avi = random.choice(all_avis)
			self.bot.avatar = avi
		

		

	@commands.group(aliases=['avatars'], pass_context=True)
	async def avatar(self, ctx):
		if ctx.invoked_subcommand is None:
			with open('data/avatars/settings/avatars.json', 'r+') as a:
				avi_config = json.load(a)
			if avi_config['password'] == '':
				return await self.bot.send_message(ctx.message.channel, 'Cycling avatars requires you to input your password. Your password will not be sent anywhere and no one will have access to it. '
                                                                                     'Enter your password with``>avatar password <password>`` Make sure you are in a private channel where no one can see!')
			if avi_config['interval'] != '0':
				self.bot.avatar = None
				self.bot.avatar_interval = None
				avi_config['interval'] = '0'
				with open('data/avatars/settings/avatars.json', 'w') as avi:
					json.dump(avi_config, avi, indent=4)
				await self.bot.send_message(ctx.message.channel, 'Disabled cycling of avatars.')
			else:
				if os.listdir('data/avatars'):
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
					elif int(interval.content) < 10:
						return await self.bot.send_message(ctx.message.channel, 'Cancelled. Interval is too short. Must be at least 1800 seconds (30 minutes).')
					else:
						avi_config['interval'] = int(interval.content)
					if len(os.listdir('data/avatars')) != 2:
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
					with open('data/avatars/settings/avatars.json', 'r+') as avi:
						avi.seek(0)
						avi.truncate()
						json.dump(avi_config, avi, indent=4)
					self.bot.avatar_interval = interval.content
					self.bot.avatar = random.choice(os.listdir('data/avatars'))

	@avatar.command(aliases=['pass', 'pw'], pass_context=True)
	async def password(self, ctx, *, msg):
		"""Set your discord acc password to rotate avatars. See wiki for more info."""
		with open('data/avatars/settings/avatars.json', 'r+') as a:
			avi_config = json.load(a)
			avi_config['password'] = msg.strip().strip('"').lstrip('<').rstrip('>')
			a.seek(0)
			a.truncate()
			json.dump(avi_config, a, indent=4)
		await self.bot.delete_message(ctx.message)
		return await self.bot.send_message(ctx.message.channel, 'Password set. Do ``>avatar`` to toggle cycling avatars.')
		
	# Set/cycle game
	async def game_and_avatar(self):
		await self.bot.wait_until_ready()
		self.bot.loop.create_task(game_and_avatar(self))
		current_game = next_game = current_avatar = next_avatar = 0
		while not self.bot.is_closed:
			# Cycles avatar if avatar cycling is enabled.
			if hasattr(bot, 'avatar_time') and hasattr(bot, 'avatar'):
				if self.bot.avatar:
					if self.bot.avatar_interval:
						if avatar_time_check(bot, self.bot.avatar_time, self.bot.avatar_interval):
							with open('data/avatars/settings/avatars.json') as g:
								avi_config = json.load(g)
							all_avis = glob.glob('data/avatars/*.jpg')
							all_avis.extend(glob.glob('data/avatars/*.jpeg'))
							all_avis.extend(glob.glob('data/avatars/*.png'))
							all_avis = os.listdir('data/avatars')
							all_avis.sort()
							if avi_config['type'] == 'random':
								while next_avatar == current_avatar:
									next_avatar = random.randint(0, len(all_avis) - 1)
								current_avatar = next_avatar
								self.bot.avatar = all_avis[next_avatar]
								with open('data/avatars/%s' % self.bot.avatar, 'rb') as fp:
									await self.bot.edit_profile(password=avi_config['password'], avatar=fp.read())
							else:
								if next_avatar + 1 == len(all_avis):
									next_avatar = 0
								else:
									next_avatar += 1
								self.bot.avatar = all_avis[next_avatar]
								with open('data/avatars/%s' % self.bot.avatar, 'rb') as fp:
									await self.bot.edit_profile(password=avi_config['password'], avatar=fp.read())
								
			if hasattr(bot, 'gc_time'):
				if gc_clear(bot, self.bot.gc_time):
					gc.collect()

			await asyncio.sleep(5)
			
	
								
def setup(bot):
	n = Avatar(bot)
	bot.add_cog(n)