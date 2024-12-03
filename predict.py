import pandas as pd
import joblib  # 新版可以直接使用

df=pd.read_csv('球隊名稱中英對照.csv')
df1=pd.read_csv('season_team_info_com_min.csv')
columns=['PTS','FGM','FGA','3PM','3PA','FTM','FTA','OREB','DREB','REB','AST','TOV','STL','BLK','PF','+/-']
keys=columns+['h' + s for s in columns]

def predict(season, team_name1, team_name2):
    team1 = df[df['中文'] == team_name1]['英文'].values[0]
    model1 = joblib.load('model_1.pkl')
    list_data1 = list(df1[(df1['team'] == team1) & (df1['season'] == season)][df1.columns[2:]].values[0])
    team2 = df[df['中文'] == team_name2]['英文'].values[0]
    model2 = joblib.load('model_2.pkl')
    list_data2 = list(df1[(df1['team'] == team2) & (df1['season'] == season)][df1.columns[2:]].values[0])
    input_data = pd.DataFrame([list_data1 + list_data2], columns=keys)
    prediction1 = model1.predict(input_data)
    prediction2 = model2.predict(input_data)
    return prediction1, prediction2

def predictML2(list):
    model1 = joblib.load('M2_1.pkl')
    model2 = joblib.load('M2_2.pkl')
    input_data = pd.DataFrame([list], columns=['FGM', 'FGA', '3PM', '3PA', 'FTM', 'FTA','OREB', 'DREB', 'REB', 'AST', 'TO', 'STL', 'BLK', 'PF','PTS','hFGM', 'hFGA', 'h3PM', 'h3PA', 'hFTM', 'hFTA','hOREB', 'hDREB', 'hREB', 'hAST', 'hTO', 'hSTL', 'hBLK', 'hPF','hPTS'])
    prediction1 = model1.predict(input_data)
    prediction2 = model2.predict(input_data)
    return prediction1, prediction2