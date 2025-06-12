import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_element(driver, xpath, retry_count = 10, retry_interval = 1):
    """指定されたXPathの要素を取得する。見つからない場合はNoneを返す。"""
    for _ in range(retry_count):
        try:
            element = driver.find_element("xpath", xpath)
            if element:
                print("O")
                return element
        except Exception as e:
            print(f"Error finding elements with xpath '{xpath}': {e}")
        time.sleep(retry_interval)
        print('.', end="", flush=True)

def wait_with_dots(message, retry_count=10, retry_interval=1):
    """指定されたメッセージを表示し、指定回数だけドットを出力する。"""
    print(message, end="", flush=True)
    for _ in range(retry_count):
        time.sleep(retry_interval)
        print('.', end="", flush=True)
    print("O")

if __name__ == "__main__":
    # Chromeのオプション設定
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUIなしで動作
    chrome_options.add_argument("--window-size=1280,1000")  # 幅1280px, 高さ1000px

    # ChromeDriverのセットアップ
    driver = webdriver.Chrome(options=chrome_options)

    # 対象ページを開く
    url = "https://www.jma.go.jp/bosai/nowc/#zoom:5/lat:35.029996/lon:135.791016/colordepth:normal/elements:hrpns&slmcs&slmcs_fcst"
    driver.get(url)

    # ページの読み込み待機
    wait_with_dots("Waiting for page to load", retry_count=5, retry_interval=1)

    # 現在時刻文字列の出力ディレクトリ作成
    now_str = time.strftime("%Y%m%d%H%M%S", time.localtime())
    output_dir = os.path.join(os.path.dirname(__file__), 'output', now_str)
    os.makedirs(output_dir, exist_ok=True)

    # ボタンが見つかるまで待機
    button_ele = get_element(driver, "/html/body/div[2]/div[1]/div[3]/div[1]/button[1]")
    selected_time_ele = get_element(driver, "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[1]/div[2]/div/div[2]")
    selected_date_time_ele = get_element(driver, "/html/body/div[2]/div[18]/div/div[4]/div[2]/div/div/table[1]/tr/td[2]")
    if button_ele is None or selected_time_ele is None or selected_date_time_ele is None:
        print("can't find button or selected time or selected date time element.")
        driver.quit()
        exit(1)

    selected_time = selected_time_ele.text
    selected_date_time = selected_date_time_ele.text
    print(selected_time, selected_date_time)
    for _ in range(36): # 5分毎 x 36 = 3時間分遡る
        # **ボタンをクリック**
        button_ele.click()
        wait_with_dots("Prev button clicked, waiting for page to load", retry_count=5, retry_interval=1)
        selected_time_ele = get_element(driver, "/html/body/div[2]/div[1]/div[3]/div[1]/div/div[1]/div[2]/div/div[2]")
        selected_date_time_ele = get_element(driver, "/html/body/div[2]/div[18]/div/div[4]/div[2]/div/div/table[1]/tr/td[2]")
        if selected_time_ele is None or selected_date_time_ele is None:
            print("can't find button or selected time or selected date time element.")
            driver.quit()
            exit(1)

        selected_time = selected_time_ele.text
        selected_date_time = selected_date_time_ele.text
        print(selected_time, selected_date_time)
        if selected_time.endswith(":00") or selected_time.endswith(":30"):
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
