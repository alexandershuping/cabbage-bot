import psycopg2
import sys
import os
import json
import eyed3.mp3 as eyeD3
import cabbagerc as rc

cdb = psycopg2.connect(dbname=rc.DBNAME, user=rc.DBUSERNAME, password=rc.DBPASSWORD, host=rc.DBHOST, port=rc.DBPORT)

module_tables = []

rc.pinfo('Scanning table lists...')
for dirname, dirnames, filenames in os.walk('./sql/tables'):
	for filename in filenames:
		if '.tables' in filename:
			rc.pcmd('  >>found ' + dirname + '/' + filename)
			module_tables.append(dirname + '/' + filename)
rc.pinfo('Done.')

def initialize():
	''' Initializes the database to have all of the proper tables '''
	rc.pinfo('Preparing to initialize the database...')
	cur = cdb.cursor()
	cur.execute('SELECT table_name FROM information_schema.tables WHERE table_type = \'BASE TABLE\' AND table_schema = \'public\';')
	if cur.fetchone() != None:
		rc.pwarn('There\'s already some data in the database. If you continue, it\'ll all be deleted.')
		if not queryTF('Delete all data and re-initialize?'):
			rc.pinfo('Aborted.')
			return
		else:
			rc.pinfo('Alright. Purging...')
			purge(cur)
			rc.pinfo('Done. Re-initializing')
	for tname in module_tables:
		makeTable(tname, cur)
	rc.pinfo('Database initialized successfully.')
	updatePhrasebook(cdb)
	updateSongbook(cdb)

def makeTable(tname, cur):
	rc.pinfo('Parsing tables from ' + tname.strip())
	with open(tname.strip()) as tables:
		for table in tables:
			if table.strip() == '':
				continue
			if (table.strip())[0] == '#':
				continue
			rc.pcmd('	>>CREATE TABLE ' + table.strip() + ';')
			cur.execute('CREATE TABLE ' + table + ';')
	

def purge(cur):	
	cur.execute('SELECT table_name FROM information_schema.tables WHERE table_type = \'BASE TABLE\' AND table_schema = \'public\';')
	toDelete = cur.fetchall()
	for table in toDelete:
		rc.pcmd('	>>DROP TABLE ' + table[0] + ';')
		cur.execute('DROP TABLE ' + table[0] + ';')

def updatePhrasebook(con):
	cur = con.cursor()
	try:
		cur.execute('SELECT * FROM phrasebook;')
	except psycopg2.ProgrammingError:
		con.rollback()
		rc.perr('It looks like the phrasebook table hasn\'t been created. Did you try initializing the database first?')
		return
	
	cur.execute('SELECT * FROM phrasebook;')
	if not cur.fetchone() == None:
		rc.pwarn('It looks like the phrasebook table is already populated. I will delete it and re-populate from sql/tables/phrasebook.tables.')
		rc.pcmd('  >>DROP TABLE phrasebook;')
		cur.execute('DROP TABLE phrasebook;')
		makeTable('./sql/tables/phrasebook.tables', cur)

	rc.pinfo('Table is initialized. Scanning for phrasefiles...')
	phrasefiles = []
	for dirname, dirnames, filenames in os.walk('./phrasebook/phrases'):
		for filename in filenames:
			if '.phrases' in filename:
				rc.pcmd('  >>found ' + dirname + '/' + filename)
				phrasefiles.append(dirname + '/' + filename)
	rc.pinfo('Done. Reading phrasefiles and adding to database...')

	for phrasefile in phrasefiles:
		rc.pinfo('Parsing phrases from file ' + phrasefile.strip())
		with open(phrasefile.strip()) as phrases:
			jsonTranslation = json.load(phrases)
			for module in jsonTranslation:
				rc.pinfo('  In module ' + module["module"] + ':')
				for context, cPList in module['phrases'].items():
					rc.pinfo('    In context ' + context)
					for phrase in cPList:
						if len(phrase) > 25:
							shortPhrase = phrase[:25] + '...'
						else:
							shortPhrase = phrase
						rc.pcmd('      >>INSERT INTO phrasebook (' + context + ', ' + shortPhrase + ');')
						cur.execute('INSERT INTO phrasebook (module, context, phrase) VALUES (%s, %s, %s);', (module['module'], context, phrase))
	con.commit()
	rc.pinfo('Done.')


def updateSongbook(con):
	cur = con.cursor()
	try:
		cur.execute('SELECT * FROM songbook;')
	except psycopg2.ProgrammingError:
		con.rollback()
		rc.perr('It looks like the songbook table hasn\'t been created. Did you try initializing the database first?')
		return

	cur.execute('SELECT * FROM songbook;')
	if not cur.fetchone() == None:
		rc.pwarn('It looks like the songbook table is already populated. I will delete it and re-populate from sql/tables/songbook.tables.')
		rc.pcmd('  >>DROP TABLE songbook;')
		cur.execute('DROP TABLE songbook;')
		makeTable('./sql/tables/songbook.tables', cur)
	
	rc.pinfo('Table is initialized. Scanning library for songs and metadata...')
	songs = []
	for dirname, dirnames, filenames in os.walk('./music'):
		for filename in filenames:
			rc.pcmd('  >>examining ' + dirname + '/' + filename)
			if not '.mp3' in filename or not eyeD3.Mp3AudioFile(dirname + '/' + filename).tag:
				rc.pwarn('File "' + str(filename) + '" is not valid mp3')
			else:
				tag = eyeD3.Mp3AudioFile(dirname + '/' + filename).tag
				name = tag.title
				album = tag.album
				artist = tag.artist
				if not name:
					rc.perr('Song at ' + dirname + '/' + filename + ' has no title! Discarding.')
					continue
				if not album:
					rc.pwarn('Caution: ' + tag.title + ' has no album information.')
					album = ''
				if not artist:
					rc.pwarn('Caution: ' + tag.title + ' has no artist information.')
					artist = ''
				rc.pcmd('  >>found "' + name + '" at ' + dirname + '/' + filename)
				songs.append({'name':name.lower(), 'album':album.lower(), 'artist':artist.lower(), 'path':dirname + '/' + filename})

	rc.pinfo('Done. Adding to database...')
	for song in songs:
		if not song:
			continue
		cphr = song['name'] + ', ' + song['album'] + ', ' + song['artist'] + ', ' + song['path']
		if len(cphr) > 50:
			cphr = cphr[:50] + '...'
		rc.pcmd('  >>INSERT INTO songbook (' + cphr + ');')
		cur.execute('INSERT INTO songbook (name, album, artist, path) VALUES (%s, %s, %s, %s);', (song['name'], song['album'], song['artist'], song['path']))
		con.commit()
	rc.pinfo('Done.')

def queryTF(prompt):
	while True:
		resp = input(rc.cPrompt + '[' + prompt + ']: (Y/N)>' + rc.cUserIn).upper()
		if resp == 'Y' or resp == 'YES':
			return True
		elif resp == 'N' or resp == 'NO':
			return False
		else:
			rc.pwarn("Unknown response. Please type Y or N")

argc = len(sys.argv)
if argc == 1:
	initialize()
	cdb.commit()
else:
	for arg in sys.argv[1:]:
		if arg.upper() == "PURGE":
			rc.pwarn('You\'ve asked to delete all data in the database. I can\'t undo this action.')
			if queryTF('Are you absolutely sure?'):
				rc.pinfo('Purging...')
				purge(cdb.cursor())
				cdb.commit()
				rc.pinfo('Done.')
			else:
				rc.pinfo('Aborted.')
		elif arg.upper() == 'INITIALIZE':
			initialize()
			cdb.commit()
		elif arg.upper() == 'PHRASES' or arg.upper() == 'PHRASEBOOK':
			updatePhrasebook(cdb)
		elif arg.upper() == 'SONGS' or arg.upper() == 'SONGBOOK':
			updateSongbook(cdb)
		else:
			rc.pwarn('Unknown command "' + arg + '"')

cdb.close()
