User->AnyChannel: !decklist @User tournamentID
AnyChannel->Bot: decklist(user, tournamentID)
Bot->AnyChannel: deleteMessage()
Bot->+Persistence: getPlayerInfo(user, tournamentID)
Persistence-->-Bot: playerInfo
alt user didn't play in tournament
    Bot->User: sorry, @User didn't plat that
else
    Bot->User: @User used this deck:
    loop for each deck in playerInfo.decks
        Bot->User: deck
    end
end