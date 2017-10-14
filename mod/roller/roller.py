import random
import discord
from discord.ext import commands

class RollerParseException(Exception):
	pass

class Roller:
	''' Die Roller Module '''
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(hidden=True, pass_context=True)
	async def rollerTest(self, ctx):
		''' Test Command '''
		await self.bot.say('Roller module is enabled!')
	
	@commands.command(pass_context=True)
	async def roll(self, ctx, die):
		''' Rolls the given die

		Call with !cabbage roll xdy+n, where x is the number of dice, y is the number of sides on each die, and n is a constant to be added or subtracted from the result.'''
		msg = ctx.message.author.name + ' rolls ' + str(die) + '\n'
		try:
			dieRoll = parseDieRoll(die)
		except RollerParseException:
			msg = msg + 'Wait, what? That isn\'t even a valid die! I mean, seriously, "' + die + '"? You want me to roll ' + die + ' for you. Could you kindly explain how I would roll a ' + die + '? How many sides does ' + die + ' even have? Who do you think I am, ' + ctx.message.author.name + '?!'
			await self.bot.say(msg)
			return
		except ValueError:
			msg = msg + 'Wait, what? That isn\'t even a valid die! I mean, seriously, "' + die + '"? You want me to roll ' + die + ' for you. Could you kindly explain how I would roll a ' + die + '? How many sides does ' + die + ' even have? Who do you think I am, ' + ctx.message.author.name + '?!'
			await self.bot.say(msg)
			return
		else:
			print(str(ctx.message.author) + ' asked to roll ' + str(dieRoll['number']) + 'd' + str(dieRoll['die']) + ' + ' + str(dieRoll['modifier']))
			if dieRoll['difference']:
				msg += 'Right, then. I\'m just going to interpret that as ' \
				     + str(dieRoll['number']) + 'd' + str(dieRoll['die'])
				if dieRoll['modifier'] < 0:
					msg += ' - '
				else:
					msg += ' + '
				msg += str(abs(dieRoll['modifier']))
				await self.bot.say(msg)
			

def parseDieRoll(die):
	''' Parses a die-roll string into a dictionary organized as follows:
	{
		number -- number of dice
		die -- number of sides per die
		modifier -- constant modifier to add/subtract from total
		difference -- true if part of the string appears to have been changed
		              by the int parsing.
	}'''
	dieResult = {}
	dLoc = die.find('d')
	mLoc = die.find('+')
	
	if mLoc == -1:
		mLoc = die.find('-')

	if dLoc == -1 or (mLoc != -1 and mLoc < dLoc):
		''' No idea what this string is, but it isn't a die roll '''
		raise RollerParseException('Couldn\'t parse "' + die + '"')
	
	dieResult['difference'] = False
	
	if dLoc == 0:
		dieResult['number'] = 1
	else:
		dieResult['number'] = int(die[:dLoc])
		dieResult['difference'] |= str(int(die[:dLoc])) == die[:dLoc]

	if mLoc == -1:
		dieResult['die'] = int(die[dLoc+1:])
		dieResult['difference'] |= str(int(die[dLoc+1:])) == die[dLoc+1:]
		dieResult['modifier'] = 0
	else:
		dieResult['die'] = int(die[dLoc+1:mLoc])
		dieResult['difference'] |= str(int(die[dLoc+1:mLoc])) == die[dLoc+1:mLoc]
		dieResult['modifier'] = int(die[mLoc+1:])
		dieResult['difference'] |= str(int(die[mLoc+1:])) == die[mLoc+1]
	
	
	return dieResult

def setup(bot):
	bot.add_cog(Roller(bot))
