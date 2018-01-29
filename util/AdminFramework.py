import discord
import cabbagerc as rc
from discord.ext import commands
from util.FlagFramework import FlagFramework
from util.Logger import Logger

class ServerMismatchError:
	pass

class AdminFramework:
	''' Framework for administrative permissions, functions, etc. '''
	def __init__(self, server):
		self.flags = FlagFramework()
		self.server = server
		self.log = Logger()

	def check(self, member):
		if member.server.id != self.server.id:
			raise ServerMismatchError
		if self.flags.getFlag('administrator', 'admin', member.server.id):
			return True
		elif member.server_permissions == discord.Permissions.all():
			self.log.log('Auto-promoting user ' + member.name + ' (id ' + member.id + ') -- server administrator', 'admin')
			self.promote(member)
			return True
		return False

	def promote(self, member):
		self.flags.uset('administrator','admin', member.server.id, member.id)
		self.log.log('User ' + member.name + ' (id ' + member.id + ') promoted to admin.', 'admin', 4)

	def demote(self, member):
		self.flags.delFlag('administrator','admin', int(member.server.id), int(member.id))
		self.log.log('User ' + member.name + ' (id ' + member.id + ') demoted.', 'admin', 4)
		
