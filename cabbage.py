import cabbagerc
import discord
from discord.ext import commands

cabbageNumber = 1000
cabbageStealer = 0

description = '''Bot That Performs Cabbage-Related Functions'''
bot = commands.Bot(command_prefix=cabbagerc.PREF, description=description)
modules = [
	'mod.roller.roller'
]

def autoset():
	''' Setup functions '''
	global modules
	for mod in modules:
		bot.load_extension(mod)


@bot.event
async def on_ready():
	print('CABBAGE IS ONLINE')
	print('USER: ' + bot.user.name + ' [' + bot.user.id + ']')
	print('=================')

@bot.command()
async def intro():
	''' Test Command '''
	await bot.say('This is CabbageBot, here to perform cabbage-related functions!')
	await bot.say('No, I don\'t actually do anything useful, yet. Give it time.')

@bot.command(pass_context=True)
async def cabbages(ctx):
	''' Displays the current number of cabbages '''
	global cabbageNumber
	global cabbageStealer
	print('User ' + str(ctx.message.author) + ' requested cabbage count (currently ' + str(cabbageNumber) + ')')
	await bot.say('Current cabbage level: ' + str(cabbageNumber))
	if cabbageNumber == 0:
		await bot.say('(' + cabbageStealer.name + ' took the last one)')

@bot.command(pass_context=True)
async def takeCabbage(ctx):
	''' Take a cabbage for yourself

Be careful, though: once the cabbages are gone, they're gone until I restart. '''
	global cabbageNumber
	global cabbageStealer
	print('User ' + str(ctx.message.author) + ' took cabbage (now ' + str(cabbageNumber-1) + ')')
	if cabbageNumber > 1:
		cabbageNumber = cabbageNumber - 1
		await bot.say(ctx.message.author.mention + ' took a cabbage! Now there are only ' + str(cabbageNumber) + ' cabbages!')
	elif cabbageNumber == 1:
		cabbageNumber = 0
		await bot.say(ctx.message.author.mention + ' took the last cabbage! Now there are none left for anybody else!')
		cabbageStealer = ctx.message.author
	else:
		await bot.say('Sorry, ' + ctx.message.author.mention + ', but ' + cabbageStealer.name + ' took the last one!')

autoset()
bot.run(cabbagerc.TKN)
