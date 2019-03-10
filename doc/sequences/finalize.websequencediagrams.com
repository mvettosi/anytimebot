User->AnyChannel: !finalize
AnyChannel->Bot: finalize
Bot->AnyChannel: deleteMessage()
Bot->Bot:checkUser()
alt not a mod
    Bot->User: sorry not authorized
end
Bot->Bot:checkChannel()
alt not a tournament channel
    Bot->User: use it in a tournament channel
else
    Bot->Bot: extractTournamentId(channel)
    Bot->+Tournaments: getTournamentData(id)
    Tournaments-->-Bot: tournamentData
    alt tournament is not finished
        Bot->User: wait for tournament completion
    else
        Bot->Tournaments: finalize()
        Bot->Tournament_Channel: tournament is finalized
    end
end
