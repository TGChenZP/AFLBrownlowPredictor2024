import pandas as pd
import os
import sys

choice = 'OriginalData'

# Grabs a list of the files
filelist = os.listdir(f'../future data/raw/{choice}')
filelist = [file for file in filelist if file[:4] == str(sys.argv[1])]
# Remove the first file (an ipynb checkpoint file)
filelist.sort()

try:
    processed_filelist = os.listdir(f'../future data/raw/NormalisedData')
except:
    processed_filelist = list()

filelist = [
    file for file in filelist if f'../future data/raw/NormalisedData/{file.strip("(O).csv")} (N).csv' not in processed_filelist]

if not os.path.exists(f'../future data/curated/OriginalData_AddDerived'):
    os.makedirs(f'../future data/curated/OriginalData_AddDerived')

if not os.path.exists(f'../future data/curated/NormalisedData'):
    os.makedirs(f'../future data/curated/NormalisedData')

for file in filelist:
    df = pd.read_csv(f'../future data/raw/{choice}/{file}')

    df['Uncontested Marks'] = df['Marks'].sub(df['Contested Marks'])
    df['Marks Outside 50'] = df['Marks'].sub(df['Marks Inside 50'])
    df['Tackles Outside 50'] = df['Tackles'].sub(df['Tackles Inside 50'])
    df['Behind Assists'] = df['Score Involvements'].sub(df['Goal Assists'])
    df['Effective Disposals'] = df['Disposals'].mul(
        df['Disposal Efficiency %']*0.01).round(0)
    df['Ineffective Disposals'] = df['Disposals'].sub(
        df['Effective Disposals'])

    df.to_csv(
        f'../future data/curated/OriginalData_AddDerived/{file}', index=False)


def norm_BT(col):
    """ Takes in input of a dataframe column """

    game_mean = col.mean()
    game_std = col.std()

    return (col-game_mean)/game_std


filelist = os.listdir(f'../future data/curated/OriginalData_AddDerived')
filelist = [file for file in filelist if file[:4] == str(sys.argv[1])]
filelist.sort()

# First make dictionaries which direct the flow of control as to whether a column should receive manipulation and whether it should be positive or inversed direction.

# Unchanged
Orig = ['Player', 'Winloss', 'Brownlow Votes', 'HomeAway']

# First make dictionaries which direct the flow of control as to whether a column should receive manipulation and whether it should be positive or inversed direction.

# Unchanged
Orig = ['Player', 'Winloss', 'Brownlow Votes', 'HomeAway']

# Normal manipulation
normal = ['Kicks', 'Handballs', 'Disposals', 'Marks', 'Goals', 'Behinds', 'Tackles', 'Hitouts', 'Goal Assists', 'Inside 50s',
          'Clearances', 'Rebound 50s', 'Frees For', 'Contested Possessions', 'Uncontested Possessions',
          'Effective Disposals', 'Contested Marks', 'Marks Inside 50', 'One Percenters', 'Bounces', 'Centre Clearances',
          'Stoppage Clearances', 'Score Involvements', 'Metres Gained', 'Intercepts', 'Tackles Inside 50', 'Time On Ground %', 'Uncontested Marks',
          'Marks Outside 50', 'Tackles Outside 50', 'Behind Assists', 'Effective Disposals', 'Ineffective Disposals', 'Clangers', 'Turnovers', 'Frees Agains', 'Disposal Efficiency %', 'Supercoach']


def get_target(norm):
    norm[norm['Brownlow Votes'] == 3].loc[:, 'Supercoach'] = 30000
    norm[norm['Brownlow Votes'] == 2].loc[:, 'Supercoach'] = 20000
    norm[norm['Brownlow Votes'] == 1].loc[:, 'Supercoach'] = 10000

    norm = norm.sort_values(['Supercoach'])
    norm['rank'] = range(len(norm))
    norm['target'] = (norm['rank'] - min(norm['rank'])) / \
        (max(norm['rank'])-min(norm['rank']))

    return norm


for file in filelist:

    df = pd.read_csv(f'../future data/curated/OriginalData_AddDerived/{file}')

    norm = pd.DataFrame()

    for column in df.columns:

        if column in Orig:
            norm[column] = list(df[column])

        elif column in normal:
            norm[f'{column} BTN'] = norm_BT(df[column])
            norm[f'{column} OTN'] = norm_OT(df[[column, 'HomeAway']], column)

        elif column in invert:
            norm[f'{column} BTN'] = norm_BT_inv(df[column])
            norm[f'{column} OTN'] = norm_OT_inv(
                df[[column, 'HomeAway']], column)

        else:
            # Error mechanism
            pass

    norm = get_target(norm)

    norm.to_csv(
        f'../future data/curated/NormalisedData/{file.strip("(O).csv")} (N).csv', index=False)
