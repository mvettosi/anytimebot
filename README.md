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
a token just to run this instance. To achieve this, follow these instructions:

### Create an application in Discord's system
Go to their [Developer site](https://discordapp.com/developers/applications/me) and create an application.  
If you aren't logged in, it will send you to the login page.  
Simply press on the "Create An Application" button.  
![Screenshot](http://i.imgur.com/WdHM5pV.png)

Give the application a name, this should be the name you want your bot on Discord to have.  
![Screenshot](https://i.imgur.com/n8USolW.png)

This will then allow you to create a Bot for the application this can be done by going into the Bot section on the left, and clicking Add Bot   
![Screenshot](https://i.imgur.com/oXxPlmp.png)

From here you can Reveal and Copy the Token which is needed for the config file
![Screenshot](https://i.imgur.com/dHUrdXM.png)

### Add your new Discord bot user to your Discord server/guild
Under the General Information tab, you can see a "Client ID".  
Replace CLIENT_ID in the following URL and go to the page.  
`https://discordapp.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=3072`

![Screenshot](https://chikachi.net/ChikachiDiscord/wiki/discord-token-5.png)

### Get the channel ID of the Discord text channel
On Discord, open your User Settings -> Appearance -> Enable Developer Mode.  
![Screenshot](https://chikachi.net/ChikachiDiscord/wiki/discord-token-6.png)

Rightclick on the Discord text channel you want the bot to interact with and press "Copy ID".  
![Screenshot](https://chikachi.net/ChikachiDiscord/wiki/discord-token-7.png)

### Add the token in the config file
At this point, you can paste your Discord Token into the configuration file, in
the appropriate field.

## Obtain Challonge credentials
To obtain these, just sign up at https://challonge.com and create an API Key following
the instructions in https://api.challonge.com/v1
Once done, paste both your username and the api key inside the config file

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
