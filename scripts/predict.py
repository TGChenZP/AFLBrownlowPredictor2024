import pandas as pd
import pickle
import json
import os
from collections import defaultdict as dd
import sys

with open(f'../models/final_models/retrain_mlp.pickle', 'rb') as f:
    model = pickle.load(f)

with open('../models/feature_importance_ordering.pickle', 'rb') as f:
    feature_importance_ordering = pickle.load(f)

manip_type = 'NormalisedData'

csv_list = os.listdir(f'../future data/curated/{manip_type}')
csv_list.sort()


def predict_brownlow(csv_list):
    json_dict = dict()

    tally = dd(int)

    data = pd.DataFrame()
    for file in csv_list:
        if file[-4:] != '.csv':
            continue

        game_dict = dict()
        if str(sys.argv[1]) in file:

            round = file.split()[2]
            team1 = file.split()[3]
            team2 = file.split()[5]
            game = team1 + ' v ' + team2

            data = pd.read_csv(f'../future data/curated/{manip_type}/{file}')
            print(file)
            player = data['Player']
            player = data['Player']
            pred = model.predict(
                data[list(list(feature_importance_ordering.keys())[36])])
            pred = pd.DataFrame({'player': player, 'predicted_score': pred})

            three_votes = list(pred.sort_values(
                'predicted_score', ascending=False)['player'])[0]

            two_votes = list(pred.sort_values(
                'predicted_score', ascending=False)['player'])[1]

            one_vote = list(pred.sort_values(
                'predicted_score', ascending=False)['player'])[2]

            game_dict[3] = three_votes
            game_dict[2] = two_votes
            game_dict[1] = one_vote

            if f'Round {round}' in json_dict:
                json_dict[f'Round {round}'][game] = game_dict
            else:
                json_dict[f'Round {round}'] = dict()
                json_dict[f'Round {round}'][game] = game_dict

            tally[three_votes] += 3
            tally[two_votes] += 2
            tally[one_vote] += 1

    return json_dict, tally


json_dict, tally = predict_brownlow(csv_list)


with open('../presentables/game_by_game_prediction.json', 'w') as f:
    json.dump(json_dict, f, indent=2)


tally_list = list(tally.items())
tally_list.sort(key=lambda x: x[1], reverse=True)
tally_df = pd.DataFrame(tally_list, columns=['Player', 'Votes'], index=[
                        i+1 for i in range(len(tally_list))])
tally_df['Ranking'] = tally_df.index
tally_df = tally_df[['Ranking', 'Player', 'Votes']]
tally_df.to_csv('../presentables/leaderboard.csv', index=False)
