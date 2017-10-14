# How to phrasebook
The phrasebook is a series of simple JSON-formatted files that represent possible responses to different commands. Using this system, instead of having a single hard-coded set of responses, it has a series of possible phrasings for anything it says, and it chooses between them randomly.

Entries are divided into **contexts**, **modules**, and **phrases**.

## Contexts
A context is a group of phrases which have similar meanings. Instead of saying a single phrase, Cabbage will look up all phrases with a certain context and module and choose randomly among them.

## Modules
Modules mean the same thing here as they mean in the rest of the bot. However, it is very important to note that contexts are normally module-specific; that is, even if two modules have contexts with the same name, they are treated as two separate contexts unless specifically requested to pull from both.

## Phrases
A phrase is a mix of text and escape-sequences. 

## Phrasefile Format
### File naming
Phrasefiles should be placed in phrasebook/phrases. They are to be named according to the format `X.phrases`, where X is a descriptive name for the set of phrases. Usually, this will just be the module name, but it is possible to define phrasefiles that provide phrases for multiple modules.

### JSON format
```
[
	{
		"module" : "MODULE NAME GOES HERE",
		"phrases" : {
			"CONTEXT NAME GOES HERE" : [
				"PHRASE GOES HERE",
				"OTHER PHRASE GOES HERE",
				...
			],
			"OTHER CONTEXT NAME GOES HERE" : [
				"OTHER PHRASE GOES HERE",
				...
			],
			...
		}
	},
	{
		"module" : "OTHER MODULE NAME GOES HERE",
		...
	},
	...
]
```

### Escape Sequences
All escape sequences begin with % (to insert a literal % character, use %%)
The following escape sequences are recognized by the Phrasebook, and will be translated as follows:
* %% -- A literal % character
* %u -- The username for that issued the command to which Cabbage is responding
* %U -- As %u, but tag the user instead of just printing the name
* %m -- CabbageBot's username
* %E -- Mention @everyone
* %t -- The current time
* %T -- The current time and date
* %i -- The command string ('!cabbage ' by default, but customizable in cabbagerc)
* %1-%0 -- Custom substitutions (see documentation for Phrasebook.get())
