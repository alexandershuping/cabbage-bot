import random

import discord
import cabbagerc as rc
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook
from util.FlagFramework import FlagFramework
from util.AdminFramework import AdminFramework
from util.Logger import Logger
from util.StarFramework import Starboard, StarMessage

class Starboard:
	''' Allows users to "star" significant messages by command or by emoji
	    reaction. With enough stars, the message is copied onto a
			"starboard" channel.
	'''
	def __init__(self, bot):
		self.bot = bot
		self.flags = FlagFramework()
		self.log = Logger()
	


	@commands.group(invoke_without_command=True,pass_context=True)
	async def star(self, ctx):
		''' Starboard-related commands ''' 
		p = Phrasebook(ctx, self.bot)
		if self.flags.hasFlag('channel', 'star', ctx.message.server):
			cha = self.bot.get_channel(self.flags.getFlag('channel', 'star', ctx.message.server))
			if cha:
				await self.bot.say(p.pickPhrase('starboard', 'working', cha.mention))
		else:
			await self.bot.say(p.pickPhrase('starboard', 'offline'))
	


	@star.command(pass_context=True)
	async def setup(self, ctx, threshold=None, channel=None):
		''' Sets up the starboard. Provide a channel id to start it in that
		    channel; otherwise, it will start in whatever channel you send 
				the command from.

				threshold (int): (optional) the minimum number of stars required 
				  to put a message on the starboard. If not provided, the
					program first checks if it has been set previously in the
					database (probably through the threshold command). If so, it
					uses that. Otherwise, it prompts the user. If the user does
					not respond in time, it picks a random threshold between 1 and
					20.

				channel (int): (optional) channel ID to set up the starboard in.
				  If not provided, the program uses the current channel.
		'''
		a = AdminFramework(ctx.message.server)
		p = Phrasebook(ctx, self.bot)
		if not a.check(ctx.message.author):
			await self.bot.say("This command is for administrators only!")
			return
		else:
			cha = None
			if channel:
				cha = self.bot.get_channel(str(channel))
			else:
				cha = ctx.message.channel

			if not cha:
				await self.bot.say("I couldn't find a channel with that ID! Check that you entered it right!")
			else:
				await self.bot.say(p.pickPhrase('starboard', 'setup', cha.mention))
				sthresh = random.randrange(1,20)
				if self.flags.hasFlag('thresh', 'star', ctx.message.server):
					sthresh = self.flags.getFlag('thresh', 'star', ctx.message.server)
				else:
					await self.bot.say(p.pickPhrase('starboard', 'needsthresh'))
					msg = None
					while True:
						msg = self.bot.wait_for_message(timeout=10)
						if not msg:
							await self.bot.say(p.pickPhrase('starboard', 'nothresh', sthresh))
							break
						elif not a.check(msg.author):
							await self.bot.say(p.pickPhrase('starboard', 'badconfirmer', msg.author.name))
						else:
							try:
								if int(msg.content) > 0:
									sthresh = int(msg.content)
									await self.bot.say(p.pickPhrase('starboard', 'working', cha.mention))
									break
								else:
									await self.bot.say(p.pickPhrase('starboard', 'negative'))
							except Exception:
								await self.bot.say(p.pickPhrase('starboard', 'badthresh', thresh))

				Starboard s(ctx.message.server)
				s.reset(cha, sthresh)

					
	
	@star.command(pass_context=True)
	async def threshold(self, ctx, thresh):
		p = Phrasebook(ctx, self.bot)
		a = AdminFramework(ctx.message.server)
		if not a.check(ctx.message.author):
			await self.bot.say("This command is for administrators only!")
			return
		else:
			Starboard s(ctx.message.server)
			if not s.isWorking():
				await self.bot.say(p.pickPhrase('starboard','offline')
			else:
				if thresh <= 0:
					await self.bot.say("The star threshold has to be greater than zero!")
				else:
					s.reset(s.channel, thresh)
	


	@star.command(pass_context=True)
	async def star(self, ctx, messid, chanid=None):
		p = Phrasebook(ctx, self.bot)
		cha = ctx.message.channel
		if chanid:
			cha = chanid

		found = self.bot.get_message(cha, str(messid))
		if not found:
			await self.bot.say(p.pickPhrase('starboard', 'messagenotfound'))
			return

		sm = StarMessage(ctx.message.server, ctx.message.channel, messid)
		sb = Starboard(ctx.message.server)
		sm.star(ctx.message.author.id)
		if #TODO left off here
	


def setup(bot):
	bot.add_cog(Admin(bot))
