# cabbage-bot
Discord.py bot with miscellaneous utilities

## Installation
1. Clone this repository into a local folder
`git clone https://github.com/alexandershuping/cabbage-bot.git`
2. Install all requirements, except for the python libraries (see below)
3. Install the python libraries
This can be done in one step by running `pip install -U -r pyreqs`
4. Copy the file `cabbagerc.py.skel` to `cabbagerc.py`
5. Edit the newly-created `cabbagerc.py` and fill in your bot token, etc.
6. Perform important setup steps
	* Use psql to create a database with the same name as you specified in cabbagerc.py
	* run `PlantCabbage.py` to complete setup
7. Run cabbage.py

## Requirements
### Programs / Non-Python Libraries
Make sure to install these before you try installing the libraries below.
* Recommended Python version: 3.5.2
* [PostgreSQL][https://www.postgresql.org/]

### Python libraries
Note that these libraries can be installed automatically by running `pip install -U -r pyreqs`
If the command fails with `Error: pg_config executable not found`, then you may not have installed postgresql. Please install all non-python-library components before trying to install the below libraries.
* [discord.py][https://github.com/Rapptz/discord.py]
* [Psycopg2][https://github.com/psycopg/psycopg2]
