import cabbagerc
import discord
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook
from datetime import datetime

cabbageNumber = 2
cabbageStealer = 0
cabbageTheftTime = 0

description = cabbagerc.DESC
bot = commands.Bot(command_prefix=cabbagerc.PREF, description=description)
modules = [
	'mod.roller.roller',
	'mod.DJCabbi.DJCabbi'
]

def autoset():
	''' Setup functions '''
	global modules

	discord.opus.load_opus(cabbagerc.OPUS_LOC)

	for mod in modules:
		bot.load_extension(mod)

def timeStrSince(d):
	diff = datetime.now() - d

	ts = int(diff.total_seconds())

	con = ''
	if ts == 0:
		return 'just now'

	con += str(ts % 60) + ' seconds'
	
	minute = int(ts/60)

	if minute == 0:
		return con
	
	con = str(minute % 60) + ' minutes and ' + con

	hour = int(minute/60)
	
	if hour == 0:
		return con
	
	con = str(hour % 24) + ' hours, ' + con

	day = hour / 24
	
	if day == 0:
		return con
	
	con = str(day) + ' days, ' + con
	return con

@bot.event
async def on_ready():
	print('CABBAGE IS ONLINE')
	print('USER: ' + bot.user.name + ' [' + bot.user.id + ']')
	print('=================')

@bot.command(pass_context=True)
async def intro(ctx):
	''' Test Command '''
	p = Phrasebook(ctx, bot)
	await bot.say(p.pickPhrase('core', 'intro1'))
	await bot.say(p.pickPhrase('core', 'intro2'))

@bot.command(pass_context=True)
async def cabbages(ctx):
	''' Displays the current number of cabbages '''
	p = Phrasebook(ctx, bot)
	global cabbageNumber
	global cabbageStealer
	global cabbageTheftTime
	print('User ' + str(ctx.message.author) + ' requested cabbage count (currently ' + str(cabbageNumber) + ')')
	if datetime.now().hour < 5:
		await bot.say(p.pickPhrase('cabbage', 'checkLate'))
		return
	if cabbageNumber == 0:
		await bot.say(p.pickPhrase('cabbage', 'checkOut', cabbageStealer, timeStrSince(cabbageTheftTime)))
	else:
		await bot.say(p.pickPhrase('cabbage', 'check', cabbageNumber))

@bot.command(pass_context=True)
async def takeCabbage(ctx):
	''' Take a cabbage for yourself

Be careful, though: once the cabbages are gone, they're gone until I restart. '''
	p = Phrasebook(ctx, bot)
	global cabbageNumber
	global cabbageStealer
	global cabbageTheftTime
	print('User ' + str(ctx.message.author) + ' took cabbage (now ' + str(cabbageNumber-1) + ')')
	if cabbageNumber > 1:
		cabbageNumber = cabbageNumber - 1
		if cabbageNumber > 100:
			await bot.say(p.pickPhrase('cabbage', 'takePlenty', cabbageNumber))
		else:
			await bot.say(p.pickPhrase('cabbage', 'take', cabbageNumber))
	elif cabbageNumber == 1:
		cabbageNumber = 0
		await bot.say(p.pickPhrase('cabbage', 'takeLast'))
		cabbageStealer = ctx.message.author
		cabbageTheftTime = datetime.now()
	else:
		await bot.say(p.pickPhrase('cabbage', 'checkOut', cabbageStealer.name, timeStrSince(cabbageTheftTime)))

autoset()
bot.run(cabbagerc.TKN)
