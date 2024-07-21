import requests
import pandas as pd
import time

key = 'RGAPI-b3207b89-c720-4bfa-a580-3b9a7874f76b' # API key

TOP_N_PLAYERS = 150 # Number of players at the top of the ladder to get data from
NUM_GAMES_LADDER = 50 # Number of games per top player
NUM_GAMES_INDIVIDUAL = 200 # Number of games for individual accounts selected

specific_players = [
    {'SummonerName': 'Kenneth','tag': 'Boom', 'region': 'na1', 'region_group': 'americas'},
    {'SummonerName': 'JAGAAAAAAN', 'tag': 'Boom', 'region': 'na1', 'region_group': 'americas'},
    {'SummonerName': 'chaewon toes','tag': 'Boom', 'region': 'na1', 'region_group': 'americas'},
    {'SummonerName': 'Hide on bush','tag': 'KR1', 'region': 'kr', 'region_group': 'asia'},
    {'SummonerName': '허거덩','tag': '0303', 'region': 'kr',  'region_group': 'asia'}, # Chovy
    {'SummonerName': 'Shok','tag': 'OCE', 'region': 'oc1',  'region_group': 'sea'},
    {'SummonerName': 'Viper','tag': 'G170', 'region': 'kr',  'region_group': 'asia'},
    {'SummonerName': 'DK ShowMaker', 'tag': 'KR1', 'region': 'kr', 'region_group': 'asia'},
    {'SummonerName': 'TheShackledOne', 'tag': '003', 'region': 'eun1', 'region_group': 'europe'}, # Caps
    {'SummonerName': 'RAT KING', 'tag': 'xpp', 'region': 'euw1', 'region_group': 'europe'} # Caedrel
]

def get_matches(region, puuid, num_games, api_key):
    num_games_list = []
    while(num_games > 100):
        num_games_list.append(100)
        num_games -= 100
    num_games_list.append(num_games)
    game_start_index = 0
    match_list = []
    for n in num_games_list:
        url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&start={str(game_start_index)}&count={str(n)}&api_key={api_key}'
        match_list.extend(get_matches_from_api(url))
        game_start_index += 100
    return match_list
        
def get_matches_from_api(url):
    while True:
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f'ERROR: {resp.statuscode} Sleeping for 50 Seconds')
            time.sleep(50)
            continue
        return resp.json()

def get_match_data(region, match_id, api_key):
    url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'

    while True:
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f'ERROR: {resp.status_code} ---- Sleeping for 50 Seconds')
            time.sleep(50)
            continue
        return resp.json()

def get_stats(puuid, match_data, abb_region):
   
    player_index = match_data['metadata']['participants'].index(puuid)
    if match_data['info']['participants'] == []:
        print(match_data['metadata']['matchId'])
        return None      

    try:
        stats = {
            'champion' : match_data['info']['participants'][player_index]['championName'],
            'position' : match_data['info']['participants'][player_index]['individualPosition'],
            'kills' : match_data['info']['participants'][player_index]['kills'],
            'deaths' : match_data['info']['participants'][player_index]['deaths'],
            'assists' : match_data['info']['participants'][player_index]['assists'],
            'gold' : match_data['info']['participants'][player_index]['goldEarned'],
            'game time' : match_data['info']['participants'][player_index]['timePlayed'],
            'damage to champions' : match_data['info']['participants'][player_index]['totalDamageDealtToChampions'],
            'wards placed' : match_data['info']['participants'][player_index]['wardsPlaced'],
            'win' : int(match_data['info']['participants'][player_index]['win']),
            'puuid' : puuid,
            'match_id' : match_data['metadata']['matchId'],
            'region' : abb_region
        }
    except:
        print(match_data['metadata']['matchId'])
        print(puuid)
        print(player_index)
    return stats

def get_timeline(puuid, match_id, region, api_key):
    match_timeline_url = f'https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline?api_key={api_key}'
    while True:
        tl = requests.get(match_timeline_url)

        if tl.status_code == 429:
            print('Rate Limit Exceeded While Getting Timeline Data ---- Sleeping for 30 Seconds')
            time.sleep(30)
            continue
        tl = tl.json()
        if tl == {'status' : {'message': 'Data not found - match file not found', 'status_code': 404}}:
            print('timeline data not found')
            continue
        if list(tl.keys())[0] != 'metadata':
            print(str(tl) + 'Sleeping for 30 Seconds')
            time.sleep(30)
            continue
        player_index = tl['metadata']['participants'].index(puuid) + 1
        timeline = []
        for frame in range(len(tl['info']['frames'])):
            timeline.append(
                {
                    'match id' : match_id,
                    'frame' : frame,
                    'timestamp' : tl['info']['frames'][frame]['timestamp'],
                    'total gold' : tl['info']['frames'][frame]['participantFrames'][str(player_index)]['totalGold'],
                    'minions killed' : tl['info']['frames'][frame]['participantFrames'][str(player_index)]['minionsKilled'],
                    'magic damage to champion' : tl['info']['frames'][frame]['participantFrames'][str(player_index)]['damageStats']['magicDamageDoneToChampions'],
                    'physical damage to champion' : tl['info']['frames'][frame]['participantFrames'][str(player_index)]['damageStats']['physicalDamageDoneToChampions'],
                    'true damage to champion' : tl['info']['frames'][frame]['participantFrames'][str(player_index)]['damageStats']['trueDamageDoneToChampions'],
                    'total damage to champion' : tl['info']['frames'][frame]['participantFrames'][str(player_index)]['damageStats']['totalDamageDoneToChampions']
                })

        return timeline

def get_player_stats(region, puuid, num_matches):
    abb_region = None
    if region == 'na1':
        abb_region = 'Americas'
    if region == 'kr':
        abb_region = 'Asia'
    if region == 'eun1':
        abb_region = 'Europe'
    if region == 'euw1':
        abb_region = 'Europe'
    if region == 'oc1':
        abb_region = 'Sea'
    matches = get_matches(abb_region, puuid, num_matches, key)

    player_stats_list = []
    i = 0
    for match_id in matches:
        try:
            match_data = get_match_data(abb_region, match_id, key)
        except:
            print(f"match data not found")
        match_data = get_match_data(abb_region, match_id, key)
        stats = get_stats(puuid, match_data, abb_region)
        if stats == None:
            print('Match not added to list')
        else:
            player_stats_list.append(stats)
        i += 1

    stats_table = pd.DataFrame(player_stats_list)
    
    return stats_table

def get_puuid_from_summoner_id(region, id):
    url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/{id}?api_key={key}'
    while True:
        resp = requests.get(url)
        
        if resp.status_code == 429:
            print('Error getting puuid -- Sleeping for 10 seconds')
            time.sleep(10)
            continue
        return resp.json()['puuid']
    
def get_ladder(top, region):
    root_url = f'https://{region}.api.riotgames.com/lol/league/v4/'
    chall_url = 'challengerleagues/by-queue/RANKED_SOLO_5x5' # Challenger ladder url
    # gm_url = 'grandmasterleagues/by-queue/RANKED_SOLO_5x5' # Grandmaster ladder url
    # master_url = 'masterleagues/by-queue/RANKED_SOLO_5x5'  # Master ladder url
    api = '?api_key=' + key

    while True:
        chall_resp = requests.get(root_url + chall_url + api)
        # gm_resp = requests.get(root_url + gm_url + api)
        # master_resp = requests.get(root_url + master_url + api)

        if chall_resp.status_code == 429:
            print('Rate Limit Exceeded While Getting Ladder Data---- Sleeping for 10 Seconds')
            time.sleep(10)
            continue  

        ladder = pd.DataFrame(chall_resp.json()['entries']).sort_values('leaguePoints', ascending=False)[:top].reset_index(drop=True)
        ladder['rank'] = ladder.index + 1
        ladder['region'] = region
        return ladder

def create_ladder():
    na_ladder = get_ladder(TOP_N_PLAYERS, 'na1')
    eu1_ladder = get_ladder(TOP_N_PLAYERS / 2, 'eun1')
    eu2_ladder = get_ladder(TOP_N_PLAYERS / 2, 'euw1') 
    kr_ladder = get_ladder(TOP_N_PLAYERS, 'kr')
    na_ladder.to_csv("na_ladder.csv")
    eu_ladder = pd.concat([eu1_ladder, eu2_ladder])
    eu_ladder.to_csv("eu_ladder.csv")
    kr_ladder.to_csv("kr_ladder.csv")

def get_ladder_stats():
    na_ladder = pd.read_csv('na_ladder.csv')
    eu_ladder = pd.read_csv('eu_ladder.csv')
    kr_ladder = pd.read_csv('kr_ladder.csv')
    stats_columns = ['champion', 'position', 'kills', 'deaths', 'assists', 'gold', 'game time', 'damage to champions', 'wards placed', 'win', 'puuid']
    stats_of_top_players = pd.DataFrame(columns=stats_columns)

    na_ladder_stats = pd.DataFrame(columns=stats_columns)
    eu_ladder_stats = pd.DataFrame(columns=stats_columns)
    kr_ladder_stats = pd.DataFrame(columns=stats_columns)
    

    print('STARTING-------')
    if len(na_ladder) == len(eu_ladder) == len(kr_ladder):
        print("Lengths Match")
        length = len(na_ladder)
    else:
        print("Lengths are not the same")
    for i in range(length):
        na_puuid = get_puuid_from_summoner_id(na_ladder['region'][i], na_ladder['summonerId'][i])
        na_player_stats = get_player_stats(na_ladder['region'][i], na_puuid, NUM_GAMES_LADDER)
        na_ladder_stats = pd.concat([na_ladder_stats, na_player_stats])
        print(f'{na_ladder['summonerId'][i]}----------NA RANK:{na_ladder['rank'][i]}')
        
        eu_puuid = get_puuid_from_summoner_id(eu_ladder['region'][i], eu_ladder['summonerId'][i])
        eu_player_stats = get_player_stats(eu_ladder['region'][i], eu_puuid, NUM_GAMES_LADDER)
        eu_ladder_stats = pd.concat([eu_ladder_stats, eu_player_stats])
        print(f'{eu_ladder['summonerId'][i]}----------EU RANK:{eu_ladder['rank'][i]}')
        
        kr_puuid = get_puuid_from_summoner_id(kr_ladder['region'][i], kr_ladder['summonerId'][i])
        kr_player_stats = get_player_stats(kr_ladder['region'][i], kr_puuid, NUM_GAMES_LADDER)
        kr_ladder_stats = pd.concat([kr_ladder_stats, kr_player_stats])
        print(f'{kr_ladder['summonerId'][i]}----------KR RANK:{kr_ladder['rank'][i]}')

        if i % 50 == 0:
            stats_of_top_players = pd.concat([na_ladder_stats, eu_ladder_stats, kr_ladder_stats])
            stats_of_top_players.to_csv(f"ladder_stats_top_{i}.csv")
        
    stats_of_top_players = pd.concat([na_ladder_stats, eu_ladder_stats, kr_ladder_stats])
    stats_of_top_players.to_csv("ladder_stats.csv")

    print('FINISHED-----')

def ladder_timeline():
    ladder_stats = pd.read_csv('ladder_stats_top_150.csv')
    ladder_stats.drop(columns=['match id'], axis=1, inplace=True)
    ladder_stats['region'] = ''
    for i in range(len(ladder_stats)):
        match ladder_stats['match_id'][i][0:2]:
            case 'NA':
                ladder_stats.loc[i, 'region'] = 'Americas'
            case 'EU':
                ladder_stats.loc[i, 'region'] = 'Europe'
            case 'KR':
                ladder_stats.loc[i, 'region'] = 'Asia'
            case 'OC':
                ladder_stats.loc[i, 'region'] = 'Sea'
    all_game_stats = ladder_stats[['match_id', 'puuid', 'region']]
    na_df = all_game_stats[all_game_stats['region'] == 'Americas'].reset_index()
    eu_df = all_game_stats[all_game_stats['region'] == 'Europe'].reset_index()
    kr_df = all_game_stats[all_game_stats['region'] == 'Asia'].reset_index()

    timeline_columns = ['match id', 'frame', 'timestamp', 'total gold', 'minions killed', 'magic damage to champion', 'physical damage to champion', 'true damage to champion', 'total damage to champion']

    timeline_table = pd.DataFrame(columns=timeline_columns)

    print('------Starting------')
    print(len(na_df))
    print(len(eu_df))
    print(len(kr_df))
    length = min([len(na_df), len(eu_df), len(kr_df)])
    print(f'getting timeline for {length} games')
    for i in range(length):
        na_timeline = get_timeline(na_df['puuid'][i], na_df['match_id'][i], na_df['region'][i], key)
        na_df.drop(index=i, axis=0)
        print(f'{i}----------game---------------{na_df['match_id'][i]}')
        for frame in range(0, len(na_timeline)):
            timeline_table.loc[len(timeline_table.index)] = na_timeline[frame]

        eu_timeline = get_timeline(eu_df['puuid'][i], eu_df['match_id'][i], eu_df['region'][i], key)
        eu_df.drop(index=i, axis=0)
        print(f'{i}----------game---------------{eu_df['match_id'][i]}')
        for frame in range(0, len(eu_timeline)):
            timeline_table.loc[len(timeline_table.index)] = eu_timeline[frame]

        kr_timeline = get_timeline(kr_df['puuid'][i], kr_df['match_id'][i], kr_df['region'][i], key)
        kr_df.drop(index=i, axis=0)
        print(f'{i}----------game---------------{kr_df['match_id'][i]}')
        for frame in range(0, len(kr_timeline)):
            timeline_table.loc[len(timeline_table.index)] = kr_timeline[frame]

    timeline_table.to_csv('timeline_v1.csv')
    overflow_games = pd.concat([na_df, eu_df, kr_df]).reset_index()
    print(f'there are {len(overflow_games)} left')
    for i in range(len(overflow_games)):
        overflow_timeline = get_timeline(overflow_games['puuid'][i], overflow_games['match_id'][i], overflow_games['region'][i], key)
        print(f'{i}----------game---------------{overflow_games['match_id'][i]}')
        for frame in range(0, len(overflow_games)):
            timeline_table.loc[len(timeline_table.index)] = overflow_games[frame]

    timeline_table.to_csv('all_timeline.csv')
    print('----Finished-----')

def get_puuid_from_name(region, name, tag):
    if region == 'sea':
        region = 'asia'
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={key}'

    while True:
        resp = requests.get(url)

        if resp.status_code != 200:
            print(f'ERROR {resp.status_code} ---- Sleeping for 10 Seconds')
            time.sleep(10)
            continue        

        return resp.json()['puuid']
def get_specific_player_stats():   
    for player in specific_players:
        print('----------STARTING------------')
        puuid = get_puuid_from_name(player['region_group'], player['SummonerName'], player['tag'])
        player_stats_table = get_player_stats(player['region'], puuid, NUM_GAMES_INDIVIDUAL)
        player_stats_table.to_csv(f'{player['SummonerName']}_stats.csv')

        print('----------STATS CALCULATED------------')

        game_table = player_stats_table[['match_id', 'puuid']]

        timeline_columns = ['match id', 'frame', 'timestamp', 'total gold', 'minions killed', 'magic damage to champion', 'physical damage to champion', 'true damage to champion', 'total damage to champion']
        timeline_table = pd.DataFrame(columns=timeline_columns)

        print('----------GETTING TIMELINE------------')
        for i in range(len(game_table)):
            timeline = get_timeline(game_table['puuid'][i], game_table['match_id'][i], player['region_group'], key)

            print(f'{i}----------game---------------{ game_table['match_id'][i]}')

            for f in range(0, len(timeline)):
                timeline_table.loc[len(timeline_table.index)] = timeline[f]

        timeline_table.to_csv(f'{player['SummonerName']}_timeline.csv')

        print('----------FINISHED------------')

def main():
    get_ladder_stats()
    ladder_timeline()
    get_specific_player_stats()

main()

