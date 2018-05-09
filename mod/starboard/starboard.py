import random

import discord
import cabbagerc as rc
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook
from util.FlagFramework import FlagFramework
from util.AdminFramework import AdminFramework
from util.Logger import Logger
from util.StarFramework import Starboard, StarMessage

class Starboard_cog:
	''' Allows users to "star" significant messages by command or by emoji
	    reaction. With enough stars, the message is copied onto a
			"starboard" channel.
	'''
	def __init__(self, bot):
		self.bot = bot
		self.flags = FlagFramework()
		self.log = Logger()



	async def on_reaction_add(self, reaction, user):
		''' Check for actual star emoji adding '''
		if user == self.bot.user:
			return # Prevent recursion
		ACCEPTABLE_REACTIONS = ['⭐','🌠','🌟','🔯','✡','✴','❇',]
		if reaction.emoji in ACCEPTABLE_REACTIONS:
			sb = Starboard(reaction.message.server, self.bot)
			if sb.isWorking():
				sm = sb.getStarboardMessage(reaction.message.channel.id, reaction.message.id)
				sm.star(user.id)
				await sm.updateStarboard(reaction.message.server, reaction.message.channel, self.bot)
			

	


	@commands.command(pass_context=True)
	async def startest(self, ctx):
		await self.bot.say('test')
	


	@commands.group(pass_context=True, invoke_without_command=True)
	async def stars(self, ctx):
		''' Starboard-related commands ''' 
		p = Phrasebook(ctx, self.bot)
		if self.flags.hasFlag('channel', 'star', ctx.message.server.id):
			cha = self.bot.get_channel(self.flags.getFlag('channel', 'star', ctx.message.server.id)[0]['flag'])
			if cha:
				await self.bot.say(p.pickPhrase('starboard', 'working', cha.mention))
		else:
			await self.bot.say(p.pickPhrase('starboard', 'offline'))
	


	@stars.command(pass_context=True)
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
				if self.flags.hasFlag('thresh', 'star', ctx.message.server.id):
					sthresh = self.flags.getFlag('thresh', 'star', ctx.message.server.id)[0]['flag']
				else:
					await self.bot.say(p.pickPhrase('starboard', 'needsthresh') + '\n\n**(waiting for response)**')
					msg = None
					while True:
						msg = await self.bot.wait_for_message(timeout=10)
						if not msg:
							await self.bot.say(p.pickPhrase('starboard', 'nothresh', sthresh))
							break
						elif msg.author == self.bot.user:
							continue
						elif not a.check(msg.author):
							await self.bot.say(p.pickPhrase('starboard', 'badconfirmer', msg.author.name) + '\n\n**(waiting for _administrator_ response)**')
						else:
							try:
								if int(msg.content) > 0:
									sthresh = int(msg.content)
									await self.bot.say(p.pickPhrase('starboard', 'working', cha.mention))
									break
								else:
									await self.bot.say(p.pickPhrase('starboard', 'negative') + '\n\n**(waiting for ``P O S I T I V E`` response)**')
							except Exception:
								await self.bot.say(p.pickPhrase('starboard', 'badthresh', sthresh) + '\n\n**(waiting for _valid_ response)**')

				s = Starboard(ctx.message.server, self.bot)
				s.reset(cha, sthresh)

					
	
	@stars.command(pass_context=True)
	async def threshold(self, ctx, thresh):
		''' [Administrators only]
				Set the starboard threshold to the value specified in <thresh>.
				Note that the value must be greater than zero.
		'''
		p = Phrasebook(ctx, self.bot)
		a = AdminFramework(ctx.message.server)
		if not a.check(ctx.message.author):
			await self.bot.say("This command is for administrators only!")
			return
		else:
			s = Starboard(ctx.message.server, self.bot)
			if not s.isWorking():
				await self.bot.say(p.pickPhrase('starboard','offline'))
			else:
				if int(thresh) <= 0:
					await self.bot.say(p.pickPhrase('starboard', 'negative'))
				else:
					s.reset(s.sbChannel, int(thresh))
					await self.bot.say('Confirmed.')
	


	@stars.command(pass_context=True)
	async def star(self, ctx, messid, chanid=None, servid=None):
		''' Add a star to the message with the given ID. Provide a channel
				or server id if you want to star a message from a different 
				channel/server
		'''
		p = Phrasebook(ctx, self.bot)
		srv = ctx.message.server
		cha = ctx.message.channel
		mes = None
		if servid:
			userSrv = self.bot.get_server(servid)
			if usrSrv:
				srv = usrSrv
		if chanid:
			usrCha = srv.get_channel(chanid)
			if usrCha:
				cha = usrCha

		mes = await self.bot.get_message(cha, messid)
		if not mes:
			await self.bot.say(p.pickPhrase('starboard', 'messagenotfound'))
			return

		sb = Starboard(ctx.message.server, self.bot)
		if sb.isWorking():
			sm = sb.getStarboardMessage(mes.channel.id, mes.id)
			sm.star(ctx.message.author.id)
			await sm.updateStarboard(ctx.message.server, mes.channel, self.bot)
	


def setup(bot):
	bot.add_cog(Starboard_cog(bot))
