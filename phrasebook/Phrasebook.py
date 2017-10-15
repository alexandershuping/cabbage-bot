''' Phrasebook Parser for CabbageBot '''

import random
import discord
from datetime import datetime
from discord.ext import commands

from sql.cabbagebase import CabbageBase
import cabbagerc as rc

class Phrasebook:
	def __init__(self, cmdCtx, bot):
		self.base = CabbageBase()
		self.cmdCtx = cmdCtx
		self.bot = bot
		random.seed()

	def phrasebookScan(self, ctx):
		''' Scan the phrasebook for the given context and return all results '''
		scRes = self.base.queryFilter('phrasebook', 'context', ctx)
		phrases = []
		for res in scRes:
			phrases.append(res[1])
		
		return phrases

	def pickPhraseRaw(self, ctx):
		''' Randomly select a phrase from the given context; do not perform
		    substitution '''
		return random.choice(self.phrasebookScan(ctx))

	def pickPhrase(self, ctx, *customSubs):
		''' Randomly select a phrase from the given context, and perform %
		    substitutions '''
		return self.doSubstitutions(self.pickPhraseRaw(ctx), customSubs)
	
	def doSubstitutions(self, subs, *cSubs):
		''' Performs % subsitutions on the given string '''
		modSt = ''
		isEscaped = False
		for c, actual in enumerate(subs):
			if subs[c] == '%':
				isEscaped = True
			elif not isEscaped:
				modSt += (subs[c])
			else:
				isEscaped = False
				if subs[c] == '%':
					modSt += ('%')
				elif subs[c] == 'u':
					modSt += (self.cmdCtx.message.author.name)
				elif subs[c] == 'U':
					modSt += (self.cmdCtx.message.author.mention)
				elif subs[c] == 'm':
					modSt += (self.bot.user.name)
				elif subs[c] == 'E':
					modSt += ('@everyone')
				elif subs[c] == 't':
					modSt += (datetime.strftime('%H:%M:%S'))
				elif subs[c] == 'T':
					modSt += (datetime.now().strftime('%H:%M:%S on %A, %d %B, %Y'))
				elif subs[c] == 'i':
					modSt += (rc.PREF)
				else:
					try:
						intSub = int(subs[c])
					except ValueError:
						pass
					else:
						if intSub == 0:
							intSub = 10
						if len(cSubs) > 0 and intSub <= len(cSubs[0]):
							modSt += str(cSubs[0][intSub-1])
		return modSt
