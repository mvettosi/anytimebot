User->AnyChannel: !win 2 1
AnyChannel->Bot: win(2, 1)
Bot->AnyChannel: deleteMessage()
Bot->+Bot: get_anytime_info(AnyChannel)
    Bot->+Bot: extract_anytime_id(AnyChannel)
    Bot-->-Bot: anytime_id
    Bot->+Persistence: get_antime(anytime_id)
    Persistence-->-Bot: anytime_data
    alt no anytime found
        Bot->User: no anytime found
    end
Bot-->-Bot: anytime_data
alt anytime found
    Bot->+Tournament: win(anytime_data.tournament_id, User.id)
        Tournament->+Tournament: get_tournament(anytime_data.tournament_id)
        Tournament-->-Tournament: tournament
        Tournament->+Tournament: get_partecipant(User.id)
        Tournament-->-Tournament: partecipant
        Tournament->+Tournament: get_next_match(partecipant)
        Tournament-->-Tournament: match
        Tournament->+Tournament: win(match)
        Tournament-->-Tournament:
        Tournament->+Tournament: get_next_match(partecipant)
        Tournament-->-Tournament: next_match
    Tournament-->-Bot: next_match_data
    alt tournament is not finished
        Bot->+Bot: get_discord_user(next_match_data.opponent)
        Bot-->-Bot: opponent
        Bot->User: Your next opponent is @{opponent.mention}
    else
        Bot->User: Congratulations with @{User.mention) for winning the tournament!
end