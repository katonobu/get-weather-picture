import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Chromeのオプション設定
chrome_options = Options()
chrome_options.add_argument("--headless")  # GUIなしで動作
chrome_options.add_argument("--window-size=1280,1000")  # 幅1280px, 高さ1000px

# ChromeDriverのセットアップ
driver = webdriver.Chrome(options=chrome_options)

# 対象ページを開く
url = "https://www.jma.go.jp/bosai/nowc/#zoom:5/lat:35.029996/lon:135.791016/colordepth:normal/elements:hrpns&slmcs&slmcs_fcst"
driver.get(url)

# ページの読み込み待機（適宜調整）
time.sleep(5)

# 現在時刻文字列の出力ディレクトリ作成
now_str = time.strftime("%Y%m%d%H%M%S", time.localtime())
output_dir = os.path.join(os.path.dirname(__file__), 'output', now_str)
os.makedirs(output_dir, exist_ok=True)

button = driver.find_element("xpath", "/html/body/div[2]/div[1]/div[3]/div[1]/button[1]")
selected_time = driver.find_element("xpath", "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[1]/div[2]/div/div[2]").text
selected_date_time = driver.find_element("xpath", "/html/body/div[2]/div[18]/div/div[4]/div[2]/div/div/table[1]/tr/td[2]").text
print(selected_time, selected_date_time)
for _ in range(36): # 5分毎 x 36 = 3時間分遡る
    # **ボタンをクリック**
    button.click()
    time.sleep(1)
    selected_time = driver.find_element("xpath", "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[1]/div[2]/div/div[2]").text
    if selected_time.endswith(":00") or selected_time.endswith(":30"):
        selected_date_time = driver.find_element("xpath", "/html/body/div[2]/div[18]/div/div[4]/div[2]/div/div/table[1]/tr/td[2]").text
        [year,remain] = selected_date_time.split("年")
        [month, remain] = remain.split("月")
        [day, remain] = remain.split("日")
        [hour, remain] = remain.split("時")
        [minute, remain] = remain.split("分")
        date_time_str = f'{year}{int(month,10):02d}{int(day,10):02d}{int(hour,10):02d}{int(minute,10):02d}'
        file_name = os.path.join(output_dir, f'{date_time_str}.png')
        print(f'save to {file_name}')
        driver.save_screenshot(file_name)

shutil.make_archive("output", format='zip', root_dir=os.path.dirname(output_dir), base_dir=os.path.basename(output_dir))

# 終了処理
driver.quit()
