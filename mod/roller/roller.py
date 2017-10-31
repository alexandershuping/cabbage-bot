import random
import re
import discord
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook

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
	
	@commands.command(hidden=True, pass_context=True)
	async def rollerTest(self, ctx):
		''' Test Command '''
		await self.bot.say('Roller module is enabled!')
	
	@commands.command(pass_context=True)
	async def roll(self, ctx, *dice):
		''' Rolls the given die

		Call with !cabbage roll xdy+n, where x is the number of dice, y is the number of sides on each die, and n is a constant to be added or subtracted from the result.'''
		die = ''
		for d in dice:
			die = die + str(d)
		p = Phrasebook(ctx, self.bot)
		msg = ctx.message.author.name + ' rolls ' + str(die) + '\n'
		try:
			dieRoll = self.parseDieRoll(die)
		except RollerParseException:
			await self.bot.say(p.pickPhrase('roller', 'invalid', str(die)))
			return
		except ValueError:
			await self.bot.say(p.pickPhrase('roller', 'invalid', str(die)))
			return
		else:
			totes = []
			for dex, die in enumerate(dieRoll):
				d = die['val']
				if die['type'] == 'die':
					msg = msg + '(' + str(d['num']) + 'd' + str(d['die']) + '='
					runningTotal = 0
					for i in range(0,d['num']):
						if d['die'] < 0: # Handle negative numbers
							toAdd = random.randrange(d['die'],0)
							runningTotal = runningTotal + toAdd
							msg = msg + str(toAdd) + ' '
						elif d['die'] > 0: # Positive numbers
							toAdd = random.randrange(d['die']) + 1
							runningTotal = runningTotal + toAdd
							msg = msg + str(toAdd) + ' '
						else: # Zero
							toAdd = 0
							msg = msg + str(toAdd) + ' '
							pass
					msg = msg + ') = ' + str(runningTotal) + '\n'
					totes.append(runningTotal)
				elif die['type'] == 'add':
					totes.append(d)
				elif die['type'] == 'mul' and dex > 0:
					dexi = dex-1
					try:
						while (not totes[dexi]) and dexi > 0:
								dexi = dexi - 1
						if dexi:
							totes[dexi-1] = totes[dexi-1] * d
						totes.append(None)
					except IndexError:
						print(str(dexi) + ' in ' + str(totes) + '(' + str(die) + ')')

			msg = msg + '['
			runningTotal = 0
			for dex, i in enumerate(totes):
				if not i:
					continue
				runningTotal = runningTotal + i
				if dex != 0:
					if i < 0:
						i = i * -1
						msg = msg + ' - '
					else:
						msg = msg + ' + '
				msg = msg + str(i)
			msg = msg + ']\n'
			msg = msg + p.pickPhrase('roller', 'out', str(runningTotal))
			await self.bot.say(msg)
			
	def parseDieRoll(self, dieStr):
		''' Parses a die-roll string into a dictionary organized as follows:
		{
			number -- number of dice
			die -- number of sides per die
			modifier -- constant modifier to add/subtract from total
			            Note that this is the absolute value of the actual modifier
			sign -- Sign of the modifier
			difference -- true if part of the string appears to have been changed
			              by the int parsing.
		}'''
		dice = []
	
		dieRx = re.compile('([0-9]*) ?d ?(-?[0-9]+)', flags=re.IGNORECASE)
		addRx = re.compile('([+-])? ?(-?[0-9]+)(d?)', flags=re.IGNORECASE)
		multRx = re.compile('([*/]) ?(-?[0-9]+)(d?)', flags=re.IGNORECASE)
	
		for die in dieRx.finditer(dieStr):
			dic = {}
			if die.group(1):
				dic['num'] = int(die.group(1))
			else:
				dic['num'] = 1
			if die.group(2):
				dic['die'] = int(die.group(2))
			else:
				raise RollerParseException('Invalid die string')
			dice.append({'type':'die', 'val':dic})
			
		for adder in addRx.finditer(dieStr):
			if adder.group(1) and adder.group(2) and not adder.group(3):
				conadd = float(adder.group(2))
				if adder.group(1) == '-':
					conadd = conadd * float(-1)
				dice.append({'type':'add', 'val':conadd})
		
		for multer in multRx.finditer(dieStr):
			if multer.group(1) and multer.group(2) and not multer.group(3):
				conmul = float(multer.group(2))
				if multer.group(1) == '/':
					conmul = 1.0/float(conmul)
				dice.append({'type':'mul', 'val':conmul})
		
		return dice

def setup(bot):
	bot.add_cog(Roller(bot))
