# anytime-tournament-bot

A Discord bot to enable mod-less anytime tournaments

# How to run
Here are the instructions to run this bot.

## Prerequisites
The only real prerequisite is having python 3.6+ installed in the system.

## Create a config file
To create a configuration file, just copy the `config.json.sample` file to a file
named 'config.json'.

## Obtain Discord test token
To ensure running this bot won't clash with any existing bot, you should create
a token just to run this instance. To achieve this, follow the instructions at
https://twentysix26.github.io/Red-Docs/red_guide_bot_accounts/.  
At this point, you can paste your Discord Token into the configuration file, in
the appropriate field.

## Obtain Challonge credentials
To obtain these, just sign up at https://challonge.com and create an API Key following
the instructions in https://api.challonge.com/v1.  
Once done, paste both your username and the api key inside the config file.

## Install dependencies
Before running the bot, it is necessary to create a virtual environment and install
the python dependencies within it. These are the commands required:
```
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the bot
Now you can run the bot by simply executing the main script:
```
./main.py
```
Everytime you need to exit from the virtual environment, just run the `deactivate`
command, and to enter again, before running the `main.py` script, remember to execute
`source venv/bin/activate`
