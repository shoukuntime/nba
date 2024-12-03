import requests
from bs4 import BeautifulSoup
from predict import predict,predictML2
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

df=pd.read_csv('球隊名稱中英對照.csv')
df1=pd.read_csv('season_team_info_com_min_zscore.csv')
df2=pd.read_csv('id球員資料_yahoo.csv')
columns=['PTS','FGM','FGA','3PM','3PA','FTM','FTA','OREB','DREB','REB','AST','TOV','STL','BLK','PF','+/-']
keys=columns+['h' + s for s in columns]

def get_soup(url): 
    soup=None 
    try:
        resp=requests.get(url)          
        if resp.status_code==200:
            soup=BeautifulSoup(resp.text,'lxml')
        else:
            print('網頁取得失敗',resp.status_code)
    except Exception as e:
        print('網址不正確!',e)
    return soup

def get_players_data(year,url,team1,team2):
    names=[]
    soup=get_soup(url)
    tables=soup.find_all('table',class_='W(100%) Py(8px) Px(4px) Mt(15px)')
    data1=[0]*16
    divs=tables[0].find_all('div',class_='D(ib)')
    for div in divs:
        id=div.find('a').get('href').split('/')[-1]
        list=df2[(df2['id']==int(id))&(df2['year']==year)&(df2['team']==team1)].values[0][5:]
        name=df2[(df2['id']==int(id))&(df2['year']==year)&(df2['team']==team1)].values[0][1]
        data1=[a+b for a,b in zip(data1,list)]
        names.append(name)
    result1=[x / data1[0] for x in data1[1:]]
    data2=[0]*16
    divs=tables[1].find_all('div',class_='D(ib)')
    for div in divs:
        id=div.find('a').get('href').split('/')[-1]
        list=df2[(df2['id']==int(id))&(df2['year']==year)&(df2['team']==team2)].values[0][5:]
        name=df2[(df2['id']==int(id))&(df2['year']==year)&(df2['team']==team2)].values[0][1]
        data2=[a+b for a,b in zip(data2,list)]
        names.append(name)
    result2=[x / data1[0] for x in data2[1:]]
    return result1+result2,names

def get_players_data_s(year,url,team1,team2):
    names=[]
    path=r'chromedriver-win64\chromedriver.exe' #chromedriver的位置
    # 設置 Chrome 無頭模式
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無頭模式
    chrome_options.add_argument("--disable-gpu")  # 避免一些 GPU 渲染問題
    chrome_options.add_argument("--no-sandbox")  # 適用於 Linux 環境，避免權限問題
    service=Service(path)
    chrome = webdriver.Chrome(service=service,options=chrome_options)
    chrome.get(url)
    html=chrome.page_source
    soup=BeautifulSoup(html,'lxml')
    tables=soup.find_all('table',class_='W(100%) Py(8px) Px(4px) Mt(15px) Ov(h)')
    data1=[0]*16
    players=tables[0].find_all('div',class_='D(ib)')
    for i in range(len(players)):
        name=players[i].text
        id=players[i].find('a').get('href').split('/')[-1]
        list=df2[(df2['id']==int(id))&(df2['year']==year)&(df2['team']==team1)].values[0][5:]
        name=df2[(df2['id']==int(id))&(df2['year']==year)&(df2['team']==team1)].values[0][1]
        data1=[a+b for a,b in zip(data1,list)]
        names.append(name)
    result1=[x / data1[0] for x in data1[1:]]
    data2=[0]*16
    players=tables[2].find_all('div',class_='D(ib)')
    for i in range(len(players)):
        name=players[i].text
        id=players[i].find('a').get('href').split('/')[-1]
        list=df2[(df2['id']==int(id))&(df2['year']==year)&(df2['team']==team2)].values[0][5:]
        name=df2[(df2['id']==int(id))&(df2['year']==year)&(df2['team']==team2)].values[0][1]
        data2=[a+b for a,b in zip(data2,list)]
        names.append(name)
    result2=[x / data1[0] for x in data2[1:]]
    chrome.quit()
    return result1+result2,names


def get_values(team,season):
    l=list(df1[(df1['team']==team)&(df1['season']==season)].values[0][2:])
    pts=l[0]
    p2=l[1]-l[2]
    p3=l[3]-l[4]
    p1=l[5]-l[6]
    reb=l[9]
    other=(l[10]+l[12]+l[13]-l[11]-l[14])/3
    result=[i+3 for i in [pts,p2,p3,p1,reb,other]]
    return result

def get_nba_data(date,getmore=False):
    url='https://tw.sports.yahoo.com/nba/scoreboard/?confId=&schedState=2&dateRange='+date
    #以9/1為界線分賽季(2024/9/1-2025/8/31為2024賽季)
    for i in range(14,25):
        if datetime.strptime(date,"%Y-%m-%d")<datetime(i+2001,9,1):
            season=f'20{i}-{i+1} '
            year=i+2000
            break
    soup=get_soup(url)
    end=soup.find('div',id="scoreboard-group-2").find_all('li',class_='Bgc(bg-mod) Pos(r) Mb(20px) D(ib) W(270px) Mend(20px) Va(t) final Bgc(secondary):h')
    in_progress=soup.find('div',id="scoreboard-group-2").find_all('li',class_='Bgc(bg-mod) Pos(r) Mb(20px) D(ib) W(270px) Mend(20px) Va(t) in_progress Bgc(secondary):h')
    pregame=soup.find('div',id="scoreboard-group-2").find_all('li',class_='Bgc(bg-mod) Pos(r) Mb(20px) D(ib) W(270px) Mend(20px) Va(t) pregame Bgc(secondary):h')
    in_pros=[]
    for in_pro in in_progress:
        time=in_pro.find('div',class_='D(tb) W(100%) Pos(r)').find('div',class_='Ta(end) Cl(b) Fw(b) YahooSans Fw(700)! Fz(11px)!').text
        team1_img=in_pro.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team').find('img').get('src')
        team1_loc=in_pro.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team').find('span').text
        team1_name=in_pro.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team').find('div',class_='Fw(n) Fz(12px)').text
        team1_score=in_pro.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team').find('div',class_='Whs(nw) D(tbc) Va(m) Fw(b) Fz(27px)').text
        team2_img=in_pro.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team Pt(10px)').find('img').get('src')
        team2_loc=in_pro.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team Pt(10px)').find('span').text
        team2_name=in_pro.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team Pt(10px)').find('div',class_='Fw(n) Fz(12px)').text
        team2_score=in_pro.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team Pt(10px)').find('div',class_='Whs(nw) D(tbc) Va(m) Fw(b) Fz(27px)').text
        team1_name_en=df[df['中文']==team1_name]['英文'].values[0]
        team2_name_en=df[df['中文']==team2_name]['英文'].values[0]
        values1=get_values(team1_name_en,season)
        values2=get_values(team2_name_en,season)
        predict1,predict2=predict(season,team1_name,team2_name)
        if getmore:
            game_url='https://tw.sports.yahoo.com'+in_pro.find('a').get('href')
            data,names=get_players_data_s(year,game_url,team1_name,team2_name)
            predict2_1,predict2_2=predictML2(data)
        else:
            names,predict2_1,predict2_2=None,None,None
        in_pros.append([time,team1_img,team1_loc,team1_name,team1_score,team2_img,team2_loc,team2_name,team2_score,predict1,predict2,values1,values2,names,predict2_1,predict2_2])
    pres=[]
    for pre in pregame:
        team1_loc=pre.find('div',class_='D(tb) W(100%) Pos(r)').find('div',class_='Fw(b) Fz(14px)').text
        team1_name=pre.find('div',class_='D(tb) W(100%) Pos(r)').find('div',class_='Fw(n) Fz(12px)').text
        team1_score=pre.find('div',class_='D(tb) W(100%) Pos(r)').find('span',class_='YahooSans Fw(700)!').text
        team1_img=df[df['中文']==team1_name]['img_url'].values[0]
        team2_loc=pre.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team Pt(10px)').find('span').text
        team2_name=pre.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team Pt(10px)').find('div',class_='Fw(n) Fz(12px)').text
        team2_score=pre.find('div',class_='D(tb) W(100%) Pos(r)').find('li',class_='D(tb) team Pt(10px)').find('span',class_='YahooSans Fw(700)!').text
        team2_img=df[df['中文']==team2_name]['img_url'].values[0]
        team1_name_en=df[df['中文']==team1_name]['英文'].values[0]
        team2_name_en=df[df['中文']==team2_name]['英文'].values[0]
        values1=get_values(team1_name_en,season)
        values2=get_values(team2_name_en,season)
        predict1,predict2=predict(season,team1_name,team2_name)
        game_url='https://tw.sports.yahoo.com'+pre.find('a').get('href')
        data,names=get_players_data(year,game_url,team1_name,team2_name)
        predict2_1,predict2_2=predictML2(data)
        pres.append([team1_img,team1_loc,team1_name,team1_score,team2_img,team2_loc,team2_name,team2_score,predict1,predict2,values1,values2,names,predict2_1,predict2_2])
    ends=[]
    for e in end:
        team1_loc=e.find('div',class_='D(tb) W(100%) Pos(r)').find('div',class_='Fw(b) Fz(14px)').text
        team1_name=e.find('div',class_='D(tb) W(100%) Pos(r)').find('div',class_='Fw(n) Fz(12px)').text
        team1_score=e.find('div',class_='D(tb) W(100%) Pos(r)').find('div',class_='Whs(nw) D(tbc) Va(m) Fw(b) Fz(27px)').text
        team1_img=df[df['中文']==team1_name]['img_url'].values[0]
        team2_loc=e.find('div',class_='D(tb) W(100%) Pos(r)').find_all('div',class_='Fw(b) Fz(14px)')[1].text
        team2_name=e.find('div',class_='D(tb) W(100%) Pos(r)').find_all('div',class_='Fw(n) Fz(12px)')[1].text
        team2_score=e.find('div',class_='D(tb) W(100%) Pos(r)').find_all('div',class_='Whs(nw) D(tbc) Va(m) Fw(b) Fz(27px)')[1].text
        team2_img=df[df['中文']==team2_name]['img_url'].values[0]
        team1_name_en=df[df['中文']==team1_name]['英文'].values[0]
        team2_name_en=df[df['中文']==team2_name]['英文'].values[0]
        values1=get_values(team1_name_en,season)
        values2=get_values(team2_name_en,season)
        predict1,predict2=predict(season,team1_name,team2_name)
        game_url='https://tw.sports.yahoo.com'+e.find('a').get('href')
        data,names=get_players_data(year,game_url,team1_name,team2_name)
        predict2_1,predict2_2=predictML2(data)
        ends.append([team1_img,team1_loc,team1_name,team1_score,team2_img,team2_loc,team2_name,team2_score,predict1,predict2,values1,values2,names,predict2_1,predict2_2])
    return [in_pros,pres,ends]

def find_news(tag,number):
    url="https://tw.news.yahoo.com/tag/"+tag
    resp=requests.get(url)
    soup=BeautifulSoup(resp.text,"lxml")
    mbs=soup.find_all('h3',class_="Mb(5px)")[:number]
    data=[]
    for mb in mbs:
        href=mb.find('a').get('href')
        newurl=url+href
        resp=requests.get(newurl)
        soup=BeautifulSoup(resp.text,"lxml")
        title=soup.find('div',class_='caas-title-wrapper').text
        tv=soup.find('img',class_='caas-img').text
        source=soup.find('div',class_='caas-attr-item-author').text
        time=soup.find('div',class_='caas-attr-time-style').text
        body_html=soup.find('div',class_='caas-body').find_all('p')
        data.append([title,tv,source,time,body_html,newurl])
    return data