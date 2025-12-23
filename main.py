import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

app = FastAPI()

# React(Vercel)からのアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 本番はVercelのURLに限定すると安全
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Render環境でChromeを動かすための設定
    if os.path.exists("/usr/bin/google-chrome"):
        options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(options=options)
    return driver

@app.get("/scrape-race")
def scrape_race(venue_index: int, race_num: int):
    driver = get_driver()
    try:
        # 1. 既存の crawling_JRA のロジックを実行
        # venue_index(100, 200, 300) と race_num を使って対象ページへ
        # ... (元のコードのcrawling_JRAやget_race_infoのロジックをここに移植) ...
        
        # 2. Race.json形式の辞書を作成して返す
        # ここでは例としてダミー構造を返しますが、元の関数の戻り値を return してください
        return {"date": "2025/12/23", "venues": [{"name": "東京", "races": [...]}]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.quit()