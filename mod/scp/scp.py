import discord
import re
import requests
import lxml.html as lh
import cabbagerc as rc
import datetime
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook
from util.FlagFramework import FlagFramework

class SCP:
	''' SCP lookup functions '''
	def __init__(self, bot):
		self.bot = bot
		self.flags = FlagFramework()
	
	@commands.group(pass_context=True, invoke_without_command=True)
	async def scp(self, ctx, skip):
		''' Look up information on the scp specified by 'skip'.
		    Invoke like this:
				
				?scp 3999 -- look up information on SCP-3999
		'''
		p = Phrasebook(ctx, self.bot)

		# Allow many variations on the SCP-XXXX format when checking for SCPs
		skip_regex = re.compile('(?i)^(?:scp)? *-* *([0-9]{1,4}(-(?:EX|J|N))?)')
		skip_numbers = skip_regex.search(str(skip))
		skip_number = None

		if skip_numbers:
			if len(skip_numbers.groups()) > 0:
				skip_number = skip_numbers.groups()[0]

		if skip_number:
			url = 'http://scp-wiki.net/scp-'+str(skip_number)
			r = requests.get(url)
			if r.status_code == 404:
				await self.bot.say(p.pickPhrase('scp','scp-404',skip_number))
			elif r.status_code == 200:
				# Parse document with lxml
				doc = lh.fromstring(r.content)

				# Look for title
				title_candidates = doc.xpath('//div[@id="page-title"]/text()')
				if len(title_candidates) > 0:
					title = title_candidates[0].strip()
				else:
					await self.bot.say(p.pickPhrase('scp','scp-too-meta',url))
					return

				# Look for object class, special containment, description
				paras = doc.xpath('//div[@id="page-content"]/p/text() | //div[@id="page-content"]/p/strong/text()')
				ob_class = None
				containment_procedures = None
				description = None
				for dex,para in enumerate(paras):
					if para.lower() == 'object class:' and dex+1 < len(paras):
						idex = dex+1
						while idex < len(paras):
							if len(paras[idex].strip()) > 0:
								ob_class = paras[idex].strip()
								break
							else:
								idex = idex + 1
						if not ob_class:
							ob_class = '[DATABASE RETREIVAL ERROR]'
					elif para.lower() == 'special containment procedures:' and dex+1 < len(paras):
						idex = dex+1
						while idex < len(paras):
							if len(paras[idex].strip()) > 0:
								containment_procedures = paras[idex].strip()
								break
							else:
								idex = idex + 1
						if not containment_procedures:
							containment_procedures = '[DATABASE RETRIEVAL ERROR]'
						if len(containment_procedures) > 200:
							containment_procedures = containment_procedures[0:200] + '...'
					elif para.lower() == 'description:' and dex+1 < len(paras):
						idex = dex+1
						while idex < len(paras):
							if len(paras[idex].strip()) > 0:
								description = paras[idex].strip()
								break
							else:
								idex = idex + 1
						if not description:
							description = '[DATABASE RETRIEVAL ERROR]'
						if len(description) > 200:
							description = description[0:200] + '...'

					if ob_class and containment_procedures and description:
						break

				# Look for page image
				page_img = None
				img_candidates = doc.xpath('//div[@class="scp-image-block block-right"]/img')
				if len(img_candidates) > 0:
					page_img = img_candidates[0].attrib['src']

				# Construct embed
				embed = discord.Embed(colour = discord.Colour(0x606060), title = title, url = url, timestamp = datetime.datetime.now())

				if ob_class:
					embed.add_field(name='Object Class', value=str(ob_class))

				if containment_procedures and containment_procedures != '':
					embed.add_field(name='Special Containment Procedures', value=str(containment_procedures))

				if description:
					embed.add_field(name='Description', value=str(description))

				if page_img:
					embed.set_thumbnail(url=str(page_img))

				embed.set_footer(text=url)

				await self.bot.say(content=p.pickPhrase('scp','success'), embed=embed)
			else:
				await self.bot.say(p.pickPhrase('scp','other-http-error'))
		else:
			# Parse the tale name into a URL
			ACCEPTABLE_CHARACTERS = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9','-'}
			url_pass1 = ''
			skip_l = skip.lower()
			for char in skip_l:
				if char in ACCEPTABLE_CHARACTERS:
					url_pass1 = url_pass1 + char
				else:
					url_pass1 = url_pass1 + '-'
			
			# pass 2 -- compress '-' characters and add the http://scp-wiki.net/
			url = ''
			for dex,char in enumerate(url_pass1):
				if char == '-':
					if dex == len(url_pass1)-1 or dex == 0:
						break # URLs never end or start with a -
					if len(url) > 0:
						if url[-1] == '-':
							pass
						else:
							url = url + '-'
				else:
					url = url + char

			if url == 'iteration-f':
				await self.bot.say(p.pickPhrase('scp','iteration-f', ctx.message.author.mention))
				return
			url = 'http://scp-wiki.net/' + url

			# Attempt to retrieve tale
			r = requests.get(url)
			if r.status_code == 404:
				await self.bot.say(p.pickPhrase('scp','tale-404',skip_number))
			elif r.status_code == 200:
				# Parse document with lxml
				doc = lh.fromstring(r.content)

				# Look for title
				title_candidates = doc.xpath('//div[@id="page-title"]/text()')
				if len(title_candidates) > 0:
					title = title_candidates[0].strip()
				else:
					await self.bot.say(p.pickPhrase('scp','scp-too-meta',url))
					return
				
				# Take the first paragraph
				paras = doc.xpath('//div[@id="page-content"]/p/text()')
				if len(paras) > 0:
					first_paragraph = paras[0]
					if len(first_paragraph) > 200:
						# Truncate
						first_paragraph = first_paragraph[0:200] + '...'
				else:
					first_paragraph = None

				# Construct embed
				embed = discord.Embed(colour = discord.Colour(0x606060), title = title, url = url, timestamp = datetime.datetime.now(), description=first_paragraph)
				embed.set_footer(text=url)
				await self.bot.say(content=p.pickPhrase('scp','success'), embed=embed)
			else:
				await self.bot.say(p.pickPhrase('scp','other-http-error'))


def setup(bot):
	bot.add_cog(SCP(bot))
