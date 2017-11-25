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
	async def test1(self, ctx):
		f = PollFramework(ctx.message.author.id, ctx.message.server.id)
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
		await self.render(f)
	
	async def render(self, framework):
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

			mess = await self.bot.say(s)

			for em in res['options']['emoji']:
				if em:
					await self.bot.add_reaction(mess, em)

		
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
		s = '(run ' + rc.PREF + 'vote ' + option
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
