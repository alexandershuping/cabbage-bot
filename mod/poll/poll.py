import discord
import re
import math
import cabbagerc as rc
from discord.ext import commands
from datetime import datetime, timedelta
from phrasebook.Phrasebook import Phrasebook
from sql.cabbagebase import CabbageBase as DB
from poll.PollFramework import PollFramework

class Poll:
	''' Polling module '''
	def __init__(self, bot):
		self.bot = bot
		self.base = DB()
		self.saved = None

	async def on_reaction_add(self, reaction, user):
		print('I J O M E  A LLEMS I')
		if user == self.bot.user:
			return
		res = self.base.query('activemessages', ('pollid',), (('messid', int(reaction.message.id)),))
		if len(res) > 0:	
			pollid = res[0][0]
			poll = PollFramework.fromSQL(self.base.query('polls', filters=(('pollid',int(pollid)),))[0])
			resp = poll.voteEmoji(user.id, reaction.emoji) 
			await self.updatePoll(pollid)
	
	@commands.command(pass_context=True)
	async def react(self, ctx, *emojis):
		print(emojis)
		for emoji in emojis:
			if re.match('<:.+:[0-9]+>', emoji):
				# Custom emoji -- parse it as such
				await self.bot.add_reaction(ctx.message, emoji[1:-1])
			else:
				# Maybe a unicode emoji -- try it, I guess
				await self.bot.add_reaction(ctx.message, emoji[0])
	
	@commands.command(pass_context=True)
	async def saveme(self, ctx):
		p = Phrasebook(ctx, self.bot)
		await self.bot.say(p.pickPhrase('poll', 'saveme'))
	
	@commands.command(pass_context=True)
	async def wakemeup(self, ctx):
		p = Phrasebook(ctx, self.bot)
		await self.bot.say(p.pickPhrase('poll', 'wakemeup'))
	
	@commands.group(invoke_without_command=True)
	async def poll(self):
		await self.bot.say('Test')

	@poll.command(pass_context=True)
	async def test1(self, ctx):
		if ctx.message.server:
			f = PollFramework(ctx.message.author.id, ctx.message.server.id, ctx.message.channel.id, ctx.message.id)
		else:
			f = PollFramework(ctx.message.author.id, None, ctx.message.channel.id, ctx.message.id)
		f.setName('Motion to Test The Poll Module')
		f.setDescription('Approval or rejection of this motion will have tested the Poll module, so feel free to do either (or try to do both!)')
		f.setOpenTime(datetime.now())
		f.setCloseTime(datetime.now() + timedelta(seconds=30))
		f.setAbsoluteThreshold(10)
		f.setPercentThreshold(0.80)
		f.setPercentThresholdMinimum(5)
		f.setThresholdTime(datetime.now() + timedelta(seconds=10))
		f.addOption('Support', 'Support the addition of the polling module', '✅')
		f.addOption('Oppose', 'Oppose the addition of the polling module', '❌')
		f.addOption('Woah', 'Woah', '<:woah:382379019993350145>')
		mess = await self.render(f)
		f.addTrackingMessage(mess.id, mess.channel.id)
	
	@poll.command(pass_context=True)
	async def create(self, ctx, name, description):
		if ctx.message.server:
			f = PollFramework(ctx.message.author.id, ctx.message.server.id, name, description)
		else:
			f = PollFramework(ctx.message.author.id, None, name, description)
		await self.bot.say('Created a new poll with id ' + str(f.get()['pollid']))
	
	@poll.group()
	async def set(self):
		pass
	
	@set.command(pass_context=True)
	async def name(self, ctx, name, pollid=None):
		poll = await self.lookupPoll(ctx, pollid)
		if not poll:
			return

		poll.setName(name)
		await self.updatePoll(pollid)
	
	@set.command(pass_context=True)
	async def description(self, ctx, desc, pollid=None):
		poll = await self.lookupPoll(ctx, pollid)
		if not poll:
			return

		poll.setDescription(desc)
		await self.updatePoll(pollid)
	
	@set.command(pass_context=True)
	async def numThreshold(self, ctx, thresh, pollid=None):
		poll = await self.lookupPoll(ctx, pollid)
		if not poll:
			return

		poll.setAbsoluteThreshold(thresh)
		await self.updatePoll(pollid)
	
	@set.command(pass_context=True)
	async def percThreshold(self, ctx, thresh, minimum=1, pollid=None):
		poll = await self.lookupPoll(ctx, pollid)
		if not poll:
			return

		poll.setPercentThreshold(thresh)
		poll.setPercentThresholdMinimum(minimum)
		await self.updatePoll(pollid)
	
	@poll.command(pass_context=True)
	async def addResp(self, ctx, short, med, emoji=None, pollid=None):
		poll = await self.lookupPoll(ctx, pollid)
		if not poll:
			return

		poll.addOption(short, med, emoji)
		await self.updatePoll(pollid)
	
	@poll.command(pass_context=True)
	async def open(self, ctx, closeTime=1, closeIncrement='day', pollid=None):
		poll = await self.lookupPoll(ctx, pollid)
		if not poll:
			return

		now = datetime.now()
		closeIncrement = closeIncrement.lower()
		if closeIncrement == 'second' or closeIncrement == 'seconds':
			t = timedelta(seconds=int(closeTime))
		elif closeIncrement == 'minute' or closeIncrement == 'minutes':
			t = timedelta(minutes=int(closeTime))
		elif closeIncrement == 'hour' or closeIncrement == 'hours':
			t = timedelta(hours=int(closeTime))
		elif closeIncrement == 'day' or closeIncrement == 'days':
			t = timedelta(days=int(closeTime))
		elif closeIncrement == 'week' or closeIncrement == 'weeks':
			t = timedelta(weeks=int(closeTime))
		elif closeIncrement == 'month' or closeIncrement == 'months':
			t = timedelta(months=int(closeTime))
		elif closeIncrement == 'year' or closeIncrement == 'years':
			t = timedelta(years=int(closeTime))
		else:
			await self.bot.say('Unknown time interval "' + closeIncrement + '"')

		closeTime = now + t
		poll.setOpenTime(now)
		poll.setCloseTime(closeTime)
		await self.updatePoll(pollid)
		print('test')
	
	@poll.command(pass_context=True)
	async def vote(self, ctx, vote, pollid=None):
		if not pollid:
			res = await self.autoGuessPollid(ctx)
			if res:
				pollid = res
			else:
				return

		poll = PollFramework.fromSQL(self.base.query('polls', filters=(('pollid',int(pollid)),))[0])
		toDel = None
		resp = poll.vote(ctx.message.author.id, vote) 
		if resp == 0:
			toDel = await self.bot.say('Successfully voted on poll ID ' + str(pollid))
		elif resp == 1:
			toDel = await self.bot.say('Invalid option "' + vote + '" for poll ID ' + str(pollid) + '!')
		elif resp == 2:
			toDel = await self.bot.say('Poll ID ' + str(pollid) + ' is not open!')
		
		mark = datetime.now()
		await self.updatePoll(pollid)
		while datetime.now() - mark < timedelta(seconds=5):
			pass

		await self.bot.delete_message(toDel)
		await self.bot.delete_message(ctx.message)

	@poll.command()
	async def put(self, pollid):
		poll = PollFramework.fromSQL(self.base.query('polls', filters=(('pollid',int(pollid)),))[0])
		mess = await self.render(poll)
		poll.addTrackingMessage(mess.id, mess.channel.id)

	@poll.command(pass_context=True)
	async def update(self, ctx, single=None):
		await self.updatePoll(single)

	async def updatePoll(self, single=None):
		if single:
			res = self.base.query('activemessages', ('messid', 'chanid', 'pollid'), (('pollid',int(single)),))
		else:
			res = self.base.query('activemessages', ('messid', 'chanid', 'pollid'))
		for active in res:
			print('Attempting to update poll with id ' + str(active[2]))
			try:
				chan = self.bot.get_channel(str(active[1]))
				if not chan:
					raise TypeError
				mess = await self.bot.get_message(chan, str(active[0]))
				poll = PollFramework.fromSQL(self.base.query('polls', filters=(('pollid',active[2]),))[0])
				await self.render(poll, mess)
			except (discord.errors.NotFound, TypeError):
				rc.pwarn('Message id ' + str(active[0]) + ' on channel id ' + str(active[1]) + ' no longer valid! Deleting.')
				cur = self.base.getCursor()
				cmd = 'DELETE FROM activemessages WHERE messid=%s AND chanid=%s'
				cur.execute(cmd, (active[0], active[1]))
				self.base.commit()
				cur.close()
	
	async def lookupPoll(self, ctx, pollid=None):
		if not pollid:
			pollid = await self.autoGuessPollid(ctx)
			if not pollid:
				return None
		poll = PollFramework.fromSQL(self.base.query('polls', filters=(('pollid',int(pollid)),))[0])
		return poll



	async def autoGuessPollid(self, ctx):
		res = self.guessPollid(ctx)
		if res[0] == 0:
			return res[1]
		elif res[1] == 1:
			await self.bot.say('No polls active in this channel. Please specify a pollid.')
			return None
		else:
			await self.bot.say('More than one poll active in this channel. Please specify a pollid.')
			return None
			

	def guessPollid(self, ctx):
		res = self.base.query('activemessages', ('pollid',), (('chanid', int(ctx.message.channel.id)),))
		if len(res) == 0:
			return (1, None) # No polls active in this channel
		elif len(res) == 1:
			return (0, res[0][0])
		else:
			return (2, None) # More than one poll active in the channel
	
	async def render(self, framework, existingMess=None):
		res = framework.get()
		s = 'Poll ID ' + str(res['pollid']) + '\n'
		s = s + '**' + res['name'] + '**\n' + res['description'] + '\n\n'
		opened = False
		final = False

		if res['openTime'] > datetime.now():
			# Poll is not open yet
			s = s + 'This poll is **not open yet**! It will open on ' + res['openTime'].strftime('%A, %d %B %Y at %H:%M:%S')\
			      + ' and close on ' + res['closeTime'].strftime('%A, %d %B %Y at %H:%M:%S') + '.'
		elif res['closeTime'] < datetime.now():
			# Poll has already closed
			opened = True
			final = True
			s = s + 'This poll is **closed**! It opened on ' + res['openTime'].strftime('%A, %d %B %Y at %H:%M:%S')\
			      + ' and closed on ' + res['closeTime'].strftime('%A, %d %B %Y at %H:%M:%S') + '.'
		else:
			# Poll is open
			opened = True
			s = s + 'This poll is **open**! It has been open since ' + res['openTime'].strftime('%A, %d %B %Y at %H:%M:%S')\
			      + ' and will close on ' + res['closeTime'].strftime('%A, %d %B %Y at %H:%M:%S') + '.'

		# Render options
		s = s + '\n\n**Accepted responses**'
		for dex, option in enumerate(res['options']['short']):
			s = s + '\n\n**' + option + '**'
			emoj = None
			if res['options']['emoji'][dex]:
				emoj = self.typeEmoji(res['options']['emoji'][dex])
				s = s + ' (' + emoj + ')'
			s = s + ': ' + res['options']['long'][dex] + '\n' + self.genCmdString(option, emoj)

		if opened:
			s = s + '\n\n**'
			if final:
				s = s + 'Final '
			else:
				s = s + 'Current '
			s = s + 'Vote Totals**\n'
			# Render votes
			votes = framework.getVoteTotals()
			s = s + '```\n'
			scale = self.getScale(votes)
			scaleFactor = scale[0]
			padLength = scale[1]
			for key, vote in votes.items():
				s = s + self.pad(key, padLength) + ' ' + str(vote) + '|'
				if scaleFactor > 0:
					for i in range(0, int(vote * scaleFactor)):
						s = s + '#'
				s = s + '\n'

			s = s + '```'

			if existingMess:
				await self.bot.edit_message(existingMess, s)
			else:
				existingMess = await self.bot.say(s)
				
			for em in res['options']['emoji']:
				if em:
					await self.bot.add_reaction(existingMess, em)
	
			return existingMess

		
	def pad(self, toPad, padLength):
		while len(toPad) < padLength:
			toPad = toPad + ' '

		return toPad
	
	def getScale(self, votes):
		maxVote = 0
		longestShortString = 0
		scaleFactor = 1
		for vote in votes.values():
			if vote > maxVote:
				maxVote = vote
		voteDigits = 0
		if maxVote > 0:
			voteDigits = int(math.log10(maxVote)) + 1

		for shortString in votes.keys():
			if len(shortString) > longestShortString:
				longestShortString = len(shortString)

		while maxVote * scaleFactor + voteDigits + longestShortString + 2 > 80:
			scaleFactor = scaleFactor - 0.1
			
		return (scaleFactor, longestShortString)
	
	def genCmdString(self, option, emoji):
		s = '(run ' + rc.PREF + 'poll vote ' + option
		if emoji:
			s = s + ' or click the reaction button below'
		s = s + ' to vote for this option)'
		return s
	
	def typeEmoji(self, emoji):
		emojiRx = re.compile('(:.+:)[0-9]+')
		res = emojiRx.match(emoji)
		if res:
			return res.group(1)
		else:
			return emoji
			

def setup(bot):
	bot.add_cog(Poll(bot))
