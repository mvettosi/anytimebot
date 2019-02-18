User->AnyChannel: !enteranytime
AnyChannel->Bot: enteranytime(tournySize)
Bot->AnyChannel: deleteMessage()
Bot->Bot:checkTicket(user)
alt no ticket
    Bot->User: sorry you cant
else
    Bot->+Persistence: addToWaitingList(server, user, tournySize)
    Persistence-->-Bot:
    Bot->User: please submit deck
    
    Bot->+User: waitForMessage()
    User->-Bot: <sends deck>
    Bot->Bot: checkIsUrl(deckUrl)
    Bot->Persistence: addDeckToWaiting(deckUrl)
    
    Bot->+User: waitForMessage()
    User->-Bot: <sends sideDeck>
    Bot->Bot: checkIsUrl(sideDeck)
    Bot->Persistence: addDeckToWaiting(sideDeck)
    
    Bot->+User: waitForMessage()
    User->-Bot: <sends extraDeck>
    Bot->Bot: checkIsUrl(extraDeck)
    Bot->Persistence: addDeckToWaiting(extraDeck)
    
    Bot->+User: waitForMessage()
    User->-Bot: !submit

    Bot->+Persistence: addPlayer(server, user, tournySize)
    Persistence-->-Bot: tourneyData
    alt tourneyData is full
        Bot->Persistence: markInProgress(tourneyData.id)
        Bot->+Tournaments: createTournament(tourneyData.players)
        Tournaments-->-Bot: signUrl
    end
    
    alt channel tourneyData.id does not exist
        Bot->Bot: createChannel(tourneyData.id)
    end
    
    Bot->TourneyChannel: addUserToChannel(user)
    Bot->TourneyChannel: hello @User, tourney here
    
    alt tourneyData.isComplete
        Bot->TourneyChannel: guys, tourney ready at tourneyData.signUrl
        alt require ticket
            loop for each partecipant
                Bot->Bot: removeTicket(user)
            end
        end
    end
end
