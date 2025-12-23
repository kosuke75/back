from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import json
import time

"""
pip install selenium
pip install BeautifulSoup4
pip install requests

"""



#クローリングを行う
def crawling_JRA(driver,):
    options = Options()
    options.headless = True

    driver.get('https://www.jra.go.jp/')
    time.sleep(3)

    shutuba_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#quick_menu > div > ul > li:nth-of-type(1) > a'))
    )
    shutuba_button.click()
    time.sleep(3)
    
    if id == 100:
        kaisai_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#main > div.panel.no-padding.no-border.mt15 > div > div.link_list.multi.div3.center > div:nth-of-type(1) > a'))
        )
        kaisai_button.click()
        time.sleep(3)


    if id == 200:
        kaisai_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#main > div.panel.no-padding.no-border.mt15 > div > div.link_list.multi.div3.center > div:nth-of-type(2) > a'))
        )
        kaisai_button.click()
        time.sleep(3)
    

    if id == 300:
        kaisai_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#main > div.panel.no-padding.no-border.mt15 > div > div.link_list.multi.div3.center > div:nth-of-type(3) > a'))
        )
        kaisai_button.click()
        time.sleep(3)
    



    race_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#race_list > caption > div.layout_grid.mt10 > div.cell.right > div > div > a'))
    )
    race_button.click()
    time.sleep(3)
    
    html = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    return html



#馬のプロフィールと戦績を取得
#======================================================
def get_horse_data(url):
    print('scraping standby')
    time.sleep(3)
    print('scraping running')
    
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    html = BeautifulSoup(res.text, 'html.parser')

    race_score = get_race_score(html)
    horse_profile = get_horse_profile(html)

    horse_data = create_horse_data(race_score, horse_profile)

    print('scraping end')

    return horse_data


def get_race_score(html):
    elements = html.select('#race_unit > div.race_detail > table > tbody')
    race_times = len(elements[0].find_all("tr"))    #レース回数
    race_score = [[] for _ in range(race_times)]          #レースデータ
    for i in range(race_times):
        selecter = '#race_unit > div.race_detail > table > tbody > tr:nth-of-type(' + str(i + 1) + ')'
        result = html.select(selecter)

        for td in result[0].find_all("td"):
            race_score[i].append(td.get_text())
    return race_score


def get_horse_name(html, horse_profile):
    elements = html.select('#contents > div.header_line.no-mb > div > h1 > span > span.txt')
    horse_profile.append(elements[0].contents[1])


def get_horse_profile(html):
    horse_profile = list()
    get_horse_name(html, horse_profile)

    elements = html.select('#horse_detail > div.profile.mt20 > div > ul')
    for i in elements[0].find_all("dd"):
        horse_profile.append(i.get_text())

    if "産駒" in horse_profile[4]:
        horse_profile[4] = horse_profile[4][:-2]
    
    del_index = [3, 7, 9, 10, 12, 14]
    for i in del_index[::-1]:
        del horse_profile[i]
    
    return horse_profile



def create_horse_data(race_score, horse_profile):
    race_key = ["date", "place", "race", "dist", "condition", "entry", "favorite", "result", "jockey", "cWeight", "hWeight", "time", "rating", "winner"]
    horse_key = ["name", "sire", "gender", "dam", "age", "trainer", "birth", "color", "origin"]
    
    race_data= [dict(zip(race_key, i)) for i in race_score]
    horse_data = dict(zip(horse_key, horse_profile))
    horse_data["scores"] = race_data
    
    return horse_data
#======================================================



#レース情報と出走馬を取得
#======================================================
def get_race_member(race_no, html):
    race_member = list()

    entry_num = get_entry_num(race_no, html)

    for i in range(entry_num):
        entry_selecer =  '#syutsuba_' + str(race_no) + 'R > table > tbody' + ' > tr:nth-of-type(' + str(i + 1) + ')'
        elements = html.select(entry_selecer)
        entry_horse_data = list()
        entry_horse = elements[0].find_all('td')
        
        waku = entry_horse[0].find("img").attrs['alt']
        for j in range(1, 7):
            s = entry_horse[j].get_text().replace('\n','').replace(' ','')
            if s != '':
                entry_horse_data.append(s)
        entry_horse_data.insert(1, waku[1:2])
                
        url = 'https://www.jra.go.jp' + elements[0].find("a").attrs['href']
        entry_horse_data.append(url)

        race_member.append(entry_horse_data)

    return race_member, entry_num


def get_race_info(html, id):
    race_count = 1
    race_info = [[] for _ in range(race_count)] 
    for i in range(race_count):
        selecter = '#syutsuba_' + str(i + 1) + 'R > table > caption > div > div > div.race_title > div > div.txt'
        elements = html.select(selecter)

        #IDの情報を追加
        time_, id_ = get_time_and_id(html, i + 1, id)
        race_info[i].append(id_)

        #何レース目かの情報を追加
        race_info[i].append(i + 1)

        #出走時間の情報を追加
        race_info[i].append(time_)

        #何頭立てかの情報を追加
        race_info[i].append(get_entry_num(i + 1, html))

        race_info[i].append(elements[0].find("span", class_="race_name").text)
        for j in elements[0].find_all("div"):
            if j.string != None:
                race_info[i].append(j.string)
    

        selecter += ' > div > div.cell.course'
        elements = html.select(selecter)
        course_info = ""
        for j in elements[0]:
            course_info += j.get_text()
        race_info[i].append(course_info[1:])

    return race_info



def get_entry_num(race_no, html):
    selecter = '#syutsuba_' + str(race_no) + 'R > table > tbody'
    elements = html.select(selecter)
    entry_num = len(elements[0].find_all("tr"))
    return 1 #entry_num
#======================================================



#取得したデータからJSONファイルを出力
#======================================================
def create_json(race_info, html, file_name):
    info_key = ["no", "entry", "title", "category", "class", "rule", "weight", "course"]
    member_key = ["num", "waku", "name", "sexage", "hweight", "cweight", "jockey", "url"]
    
    race_data = dict()
    for i in race_info:
        tmp_dict = dict(zip(info_key, i))
        member, num = get_race_member(i[0], html)
        member_data = [dict(zip(member_key, j)) for j in member]

        for n in range(num):
            url = member_data[n].pop("url")
            member_data[n].update(get_horse_data(url))

        tmp_dict["member"] = member_data

        race_data[str(i[0]) + "race"] = tmp_dict

    with open(file_name + ".json", mode="wt", encoding="utf-8") as f:
        json.dump(race_data, f, ensure_ascii=False, indent=2)



def create_horse_json(race_info, html):
    member_key = ["num", "waku", "name", "sexage", "hweight", "cweight", "jockey", "url"]
    horses_data = dict()
    for i in race_info:
        member, num = get_race_member(i[1], html)
        member_data = [dict(zip(member_key, j)) for j in member]

        for n in range(num):
            url = member_data[n].pop("url")
            member_data[n].update(get_horse_data(url))

        horses_data["horses"] = member_data
    
    with open(r"Horse.json", mode="wt", encoding="utf-8") as f:
        json.dump(horses_data, f, ensure_ascii=False, indent=2)



def create_race_json(race_info, html):
    date, session, place = get_session(html)
    all_race_data = {"date": date}
    race_data = {"name": place, "session": session}


    info_key = ["id", "raceNum", "time", "entry", "title", "category", "class", "rule", "weight", "course"]
    member_key = ["num", "waku", "name", "sexage", "hweight", "cweight", "jockey", "url"]
    
    race_list = list()
    for i in race_info:
        t = dict(zip(info_key, i))
        member, num = get_race_member(i[1], html)
        ts = [dict(zip(member_key, j)) for j in member]
        t["horses"] = ts

        race_list.append(t)
    
    race_data["races"] = race_list
    all_race_data["venues"] = [race_data]

    
    with open(r"Race.json", mode="wt", encoding="utf-8") as f:
        json.dump(all_race_data, f, ensure_ascii=False, indent=2)



#======================================================

def get_session(html):
    elements = html.select('#contentsBody > div > div.contents_header.opt.mt20 > div > div > h2')
    session_data = elements[0].string
    date, place = session_data.split("回")
    session = session_data.split("曜")[1][1:]
    date = date[5:-1]
    place = place[:-2]

    return date, session, place




def get_time_and_id(html, race_no, id):
    selecter = '#syutsuba_' + str(race_no) + 'R > table > caption > div > div > div.date_line > div > div.cell.time > strong'
    elements = html.select(selecter)

    time = elements[0].string
    hour, minute = time.split("時")
    minute = minute[:-1]
    time_ = hour + ":" +  minute
    id_ = id + race_no

    return time_, id_
#======================================================




index = 100

#今週の出馬表で左から順に100, 200, 300
#   index = 100
#   index = 200
#   index = 300

html = crawling_JRA(webdriver.Chrome(), id)

#create_json(get_race_info(html), html, "20251220-nakayama"
index = 100
create_horse_json(get_race_info(html, index), html)
create_race_json(get_race_info(html, index), html)