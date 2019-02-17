User->AnyChannel: !enteranytime
AnyChannel->Commands: enteranytime(tournySize)
alt missingRole
    Commands->User: sorry you cant
else
    alt server needs decklist
        Commands->+Anytimes: addToWaitingList(server, user, tournySize)
            Anytimes->Persistence: addToWaitingList(server, user, tournySize)
        Anytimes-->-Commands:
        Commands->User: please submit deck
        
        User->Commands: <sends deck>
        Commands->Commands: checkIsUrl(deckUrl)
        Commands->Anytimes: addDeckToWaiting(deckUrl)
        Anytimes->Persistence: addDeckToWaiting(deckUrl)
        
        User->Commands: <sends sideDeck>
        Commands->Commands: checkIsUrl(sideDeck)
        Commands->Anytimes: addDeckToWaiting(sideDeck)
        Anytimes->Persistence: addDeckToWaiting(sideDeck)
        
        User->Commands: <sends extraDeck>
        Commands->Commands: checkIsUrl(extraDeck)
        Commands->Anytimes: addDeckToWaiting(extraDeck)
        Anytimes->Persistence: addDeckToWaiting(extraDeck)
        
        User->Commands: !submit
    end

    Commands->+Anytimes: addPlayer(server, user, tournySize)
        Anytimes->+Persistence: addPlayer(server, user, tournySize)
        Persistence-->-Anytimes: tourneyData
        alt tourneyData is full
            Anytimes->Persistence: markInProgress(tourneyData.id)
            Anytimes->+Tournaments: createTournament(tourneyData.players)
            Tournaments-->-Anytimes: signUrl
        end
    Anytimes-->-Commands: tourneyData
    
    alt channel tourneyData.id does not exist
        Commands->Commands: createChannel(tourneyData.id)
    end
    
    Commands->TourneyChannel: hello @User, tourney here
    
    alt tourneyData.isComplete
        Commands->TourneyChannel: guys, tourney ready at tourneyData.signUrl
    end
end