from flask import Flask, render_template,redirect, url_for
from datetime import datetime
from find import get_nba_data,get_values,find_news
from datetime import timedelta
import pandas as pd
from genai import get_info

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('error'))

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/')
def home():
    return render_template('index.html',find_news=find_news,tag='nba',number=1)

@app.route('/tag=<tag>/number=<number>')
def hometag(tag,number):
    try:
        tag=tag
        number=int(number)
        if number>20:
            number=20
        elif number<1:
            number=1
        return render_template('index.html',find_news=find_news,tag=tag,number=number)
    except:
        return redirect(url_for('error'))

@app.route('/games/getmore=<getmore>')
def todaygame(getmore):
    today=datetime.now()
    date=today.strftime("%Y-%m-%d")
    for i in range(14,25):
        if datetime.strptime(date,"%Y-%m-%d")<datetime(i+2001,9,1):
            season=f'20{i}-{i+1} '
            year=i+2000
            break
    getmore=True if getmore=='True' else False
    in_pros,pres,ends=get_nba_data(date,getmore=getmore)
    date_obj=datetime.strptime(date, "%Y-%m-%d")
    previous_day = date_obj - timedelta(days=1)
    next_day = date_obj + timedelta(days=1)
    date_1 = previous_day.strftime("%Y-%m-%d")
    date1 = next_day.strftime("%Y-%m-%d")
    return render_template('games.html',in_pros=in_pros,pres=pres,ends=ends,date_1=date_1,date1=date1,year=year,getmore=getmore)

@app.route('/games/date=<date>')
def game(date):
    in_pros,pres,ends=get_nba_data(date)
    date_obj=datetime.strptime(date, "%Y-%m-%d")
    previous_day = date_obj - timedelta(days=1)
    next_day = date_obj + timedelta(days=1)
    date_1 = previous_day.strftime("%Y-%m-%d")
    date1 = next_day.strftime("%Y-%m-%d")
    return render_template('games.html',in_pros=in_pros,pres=pres,ends=ends,date=date,date1=date1,date_1=date_1)

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/team/season=<season>/team1=<team1>/team2=<team2>')
def myteam(season,team1,team2):
    season=int(season)
    season=f'20{season}-{season+1} '
    values1=get_values(team1,season)
    values2=get_values(team2,season)
    df=pd.read_csv('球隊名稱中英對照.csv')
    team1_zh=df[df['英文']==team1]['中文'].values[0]
    team2_zh=df[df['英文']==team2]['中文'].values[0]
    message=f'{team1_zh} & {team2_zh} {season}賽季 數據比較'
    return render_template('team.html',values1=values1,values2=values2,team1_zh=team1_zh,team2_zh=team2_zh,message=message,season=season,team1=team1,team2=team2)

@app.route('/player')
def player():
    return render_template('player.html')

@app.route('/player/season=<season>/team=<team>/getinfo=<getinfo>')
def myplayer(season,team,getinfo):
    df=pd.read_csv('id球員資料_yahoo.csv')
    titles=['name', 'G', 'time', 'FGM', 'FGA', '3FGM', '3FGA', 'FTM', 'FTA',
                                  'OREB', 'DREB', 'REB', 'AST', 'TO', 'STL', 'BLK', 'PF', 'PTS']
    df_result=df[(df['team']==team)&(df['year']==int(season))][titles]
    datas=df_result.values.tolist()
    titles_min=['name', 'FGM', 'FGA', '3FGM', '3FGA', 'FTM', 'FTA','OREB', 'DREB', 'REB', 'AST', 'TO', 'STL', 'BLK', 'PF', 'PTS']
    datas_min=[]
    for data in datas:
        data_min=[data[0]]+[round(x/data[2],3) for x in data[3:]]
        datas_min.append(data_min)
    message=f'{season}-{int(season)+1}賽季{team}球員每分鐘數據'
    sentence='此數據以每分鐘為單位，簡單說明隊伍中誰的哪個能力強，並標註重點數據'
    if getinfo=='True':
        info=get_info(titles_min,datas_min,sentence)
        info=info.replace('```html','').replace('```','').replace('**','')
    else:
        info=None
    return render_template('player.html',season=season,team=team,message=message,info=info,titles_min=titles_min,datas_min=datas_min)

@app.route('/player/season=<season>/team=<team>/by=<by>/ascending=<ascending>/getinfo=<getinfo>')
def myplayersort(season,team,by,ascending,getinfo):
    df=pd.read_csv('id球員資料_yahoo.csv')
    titles=['name', 'G', 'time', 'FGM', 'FGA', '3FGM', '3FGA', 'FTM', 'FTA',
                                  'OREB', 'DREB', 'REB', 'AST', 'TO', 'STL', 'BLK', 'PF', 'PTS']
    df_result=df[(df['team']==team)&(df['year']==int(season))][titles]
    datas=df_result.values.tolist()
    titles_min=['name', 'FGM', 'FGA', '3FGM', '3FGA', 'FTM', 'FTA','OREB', 'DREB', 'REB', 'AST', 'TO', 'STL', 'BLK', 'PF', 'PTS']
    datas_min=[]
    for data in datas:
        data_min=[data[0]]+[round(x/data[2],3) for x in data[3:]]
        datas_min.append(data_min)
    df_r=pd.DataFrame(datas_min,columns=titles_min)
    #依照sort排序
    ascending=True if ascending=='True' else False
    df_r=df_r.sort_values(by=by,ascending=ascending)
    datas_min=df_r.values.tolist()
    message=f'{season}-{int(season)+1}賽季{team}每分鐘球員數據'
    sentence='此數據以每分鐘為單位，簡單說明隊伍中誰的哪個能力強，並標註重點數據'
    if getinfo=='True':
        info=get_info(titles_min,datas_min,sentence)
        info=info.replace('```html','').replace('```','').replace('**','')
    else:
        info=None
    return render_template('player.html',season=season,team=team,datas_min=datas_min,titles_min=titles_min,message=message,info=info,by=by,ascending=ascending)

@app.route('/player/name=<name>/getinfo=<getinfo>')
def playername(name,getinfo):
    df=pd.read_csv('id球員資料_yahoo.csv')
    titles=['year','team', 'G', 'time', 'FGM', 'FGA', '3FGM', '3FGA', 'FTM', 'FTA','OREB', 'DREB', 'REB', 'AST', 'TO', 'STL', 'BLK', 'PF', 'PTS']
    df_result=df[df['name']==name][titles]
    datas=df_result.values.tolist()
    message=f'{name} 球員每分鐘數據'
    titles_min=['year','team', 'FGM', 'FGA', '3FGM', '3FGA', 'FTM', 'FTA','OREB', 'DREB', 'REB', 'AST', 'TO', 'STL', 'BLK', 'PF', 'PTS']
    datas_min=[]
    for data in datas:
        data_min=[data[0],data[1]]+[round(x/data[3],3) for x in data[4:]]
        datas_min.append(data_min)
    sentence='此數據以每分鐘為單位，簡單說明球員在不同隊伍的表現，以及在不同年份的表現如何，請勿給我原始表格，但給我整理後的表格，並標註重點數據'
    if getinfo=='True':
        info=get_info(titles_min,datas_min,sentence)
        info=info.replace('```html','').replace('```','').replace('**','')
    else:
        info=None
    return render_template('playername.html',message=message,info=info,name=name,datas_min=datas_min,titles_min=titles_min)

@app.route('/description')
def description():
    return render_template('description.html')

# 啟動伺服器
if __name__ == '__main__':
    app.run(debug=True)