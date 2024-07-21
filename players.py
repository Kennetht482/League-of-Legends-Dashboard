import requests
import pandas as pd
import time

key = 'RGAPI-fabec8a2-beb2-4f18-902a-b2672af563cf'

player_columns = ['name', 'tag', 'region', 'puuid']

player_names = pd.DataFrame(columns=player_columns)

ladder_players = pd.read_csv('top_150_ladder.csv',index_col=False)[['region', 'puuid']]
ladder_players = ladder_players.drop_duplicates().reset_index()
print(ladder_players)

def get_name_from_puuid(region, puuid):
    url = f'https://{region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={key}'

    while True:
        resp = requests.get(url)

        if resp.status_code != 200:
            print(f'ERROR: {resp.status_code}  ---- Sleeping for 30 Seconds')
            time.sleep(30)
            continue        
        player_data = {
            'name' : resp.json()['gameName'],
            'tag' : resp.json()['tagLine'],
            'region' : region,
            'puuid' : puuid
        }
        print(f'Player: {resp.json()['gameName']} #{resp.json()['tagLine']} has been added')
        return player_data
print('-----STARTING-----')
for i in range(len(ladder_players)):
    player_names.loc[len(player_names)] = get_name_from_puuid(ladder_players['region'][i], ladder_players['puuid'][i])
    
print("DONE")
player_names.to_csv('player_names.csv')

    