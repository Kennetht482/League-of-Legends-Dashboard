import requests
import pandas as pd

url = "https://ddragon.leagueoflegends.com/cdn/14.13.1/data/en_US/champion.json"

champ_columns = ['name', 'img']

resp = requests.get(url)
champ_list = pd.DataFrame(columns=champ_columns)

print("start")
for i in resp.json()['data']:
    champ_data = {
            "name" : resp.json()['data'][i]['name'],
            "img" : resp.json()['data'][i]['image']['full']
        }
    champ_list.loc[len(champ_list)] = champ_data
    
print(champ_list)
champ_list.to_csv("champ_list.csv")