import random
import re
import discord
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook
from mod.roller.expressions import Expression

class RollerParseException(Exception):
	pass

class Roller:
	''' Die Roller Module '''
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(pass_context=True)
	async def rate(self, ctx):
		''' Rates content using a complex algorithm '''
		p = Phrasebook(ctx, self.bot)
		r = random.randrange(9)
		ms = ""
		for i in range(0,8):
			if i <= r:
				ms = ms + '★'
			else:
				ms = ms + '☆'

		await self.bot.say(p.pickPhrase('roller', 'rate', ms))
		await self.bot.delete_message(ctx.message)
	
	@commands.command(pass_context=True)
	async def roll(self, ctx, *dice):
		die = ''
		for d in dice:
			die = die + str(d)
		p = Phrasebook(ctx, self.bot)
		msg = ctx.message.author.name + ' rolls ' + str(die) + '\n'
		res = 0
		try:
			dieRoll = Expression(die)
			res = dieRoll.run()
			await self.bot.say(p.pickPhrase('roller', 'out', str(res)))
		except ExpressionSyntaxError:
			await self.bot.say(p.pickPhrase('roller', 'invalid', str(die)))
			return
		except ExpressionVariableError:
			await self.bot.say(p.pickPhrase('roller', 'invalid', str(die)))
			return

def setup(bot):
	bot.add_cog(Roller(bot))
