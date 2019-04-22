import random
import uuid

import challonge

from anytimebot import config

'''
{
    'tournament': {
        'accept_attachments': False,
        'accepting_predictions': False,
        'allow_participant_match_reporting': True,
        'anonymous_voting': False,
        'auto_assign_stations': None,
        'category': None,
        'check_in_duration': None,
        'completed_at': None,
        'created_at': '2019-03-26T17:30:48.515-07:00',
        'created_by_api': True,
        'credit_capped': False,
        'description': '',
        'description_source': '',
        'donation_contest_enabled': None,
        'event_id': None,
        'full_challonge_url': 'https://challonge.com/anytime_something',
        'game_id': None,
        'game_name': None,
        'grand_finals_modifier': None,
        'group_stages_enabled': False,
        'group_stages_were_started': False,
        'ham': None,
        'hide_forum': False,
        'hide_seeds': False,
        'hold_third_place_match': False,
        'id': 5724538,
        'live_image_url': 'https://challonge.com/anytime_something.svg',
        'locked_at': None,
        'mandatory_donation': None,
        'max_predictions_per_user': 1,
        'name': 'Test Tournament',
        'non_elimination_tournament_data': {},
        'notify_users_when_matches_open': True,
        'notify_users_when_the_tournament_ends': True,
        'only_start_matches_with_stations': None,
        'open_signup': False,
        'participants_count': 0,
        'participants_locked': False,
        'participants_swappable': True,
        'predict_the_losers_bracket': None,
        'prediction_method': 0,
        'predictions_opened_at': None,
        'private': False,
        'progress_meter': 0,
        'pts_for_bye': '1.0',
        'pts_for_game_tie': '0.0',
        'pts_for_game_win': '0.0',
        'pts_for_match_tie': '0.5',
        'pts_for_match_win': '1.0',
        'public_predictions_before_start_time': None,
        'quick_advance': False,
        'ranked': False,
        'ranked_by': None,
        'registration_fee': '0.0',
        'registration_type': 'free',
        'require_score_agreement': False,
        'review_before_finalizing': True,
        'rr_iterations': None,
        'rr_pts_for_game_tie': '0.0',
        'rr_pts_for_game_win': '0.0',
        'rr_pts_for_match_tie': '0.5',
        'rr_pts_for_match_win': '1.0',
        'sequential_pairings': False,
        'show_rounds': False,
        'sign_up_url': None,
        'signup_cap': None,
        'spam': None,
        'start_at': None,
        'started_at': None,
        'started_checking_in_at': None,
        'state': 'pending',
        'subdomain': None,
        'swiss_rounds': 0,
        'team_convertable': False,
        'teams': None,
        'tie_breaks': None,
        'tournament_registration_id': None,
        'tournament_type': 'single elimination',
        'updated_at': '2019-03-26T17:30:48.515-07:00',
        'url': 'anytime_something'
    }
}
'''


async def create_tournament(anytime_id, players):
    my_user = await challonge.get_user(config.CHALLONGE_USERNAME, config.CHALLONGE_API_KEY)
    new_tournament = await my_user.create_tournament(
        name=f'Anytime Tournament #{anytime_id}',
        url=uuid.uuid4().hex,
        check_in_duration=10
    )

    for player in players:
        await new_tournament.add_participant(player["user_name"], misc=player["user_id"])
        await new_tournament.add_participant('One', misc=player["user_id"])
        await new_tournament.add_participant('Two', misc=player["user_id"])
        await new_tournament.add_participant('Three', misc=player["user_id"])

    await new_tournament.shuffle_participants()
    await new_tournament.start()
    print(f'Started Tournament with id={new_tournament.id}: {new_tournament.full_challonge_url}')

    pairing = []
    users_checked = []
    participants = await new_tournament.get_participants()
    for player in participants:
        if player not in users_checked:
            opponent = await player.get_next_opponent()
            pairing.append({'player': player.misc, 'opponent': opponent.misc})
            users_checked.append(opponent)

    return {
        'id': new_tournament.id,
        'url': new_tournament.full_challonge_url,
        'pairings': pairing
    }


async def win(tournament_id, discord_id, score):
    user = await challonge.get_user(config.CHALLONGE_USERNAME, config.CHALLONGE_API_KEY)
    tournament = await user.get_tournament(tournament_id)
    participants = await tournament.get_participants()
    player = next((participant for participant in participants if participant.misc == discord_id), None)
    if player is not None:
        match = await player.get_next_match()
        await match.report_winner(player, score)
        next_match = await player.get_next_match()
        player1 = await tournament.get_participant(next_match.player1_id)
        player2 = await tournament.get_participant(next_match.player2_id)
        next_opponent = player1.misc if player1 == player else player2.misc
        return {
            'opponent': next_opponent.misc
        }


async def finalize(tournament_id):
    user = await challonge.get_user(config.CHALLONGE_USERNAME, config.CHALLONGE_API_KEY)
    tournament = await user.get_tournament(tournament_id)

    await tournament.finalize()

    ranking = await tournament.get_final_ranking()
    if ranking is not None:
        return ranking[0].misc