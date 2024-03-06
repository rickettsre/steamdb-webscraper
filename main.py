from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from random import randint
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
import datetime as dt
import os

##Add User Agent
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

## Setup chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument(f"user-agent={user_agent}")

REPORT_TIME = dt.datetime.now()
base_url = "https://steamdb.info/charts/"
game_output = []

webdriver_service = Service(ChromeDriverManager().install())


def get_game_info(url):
    page_count = 1
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    driver.get(url)

    while True:
        steam_page = driver.page_source
        soup = BeautifulSoup(steam_page, "html.parser")
        table_data = soup.find("table", class_="table-products")
        table_rows = table_data.find_all("tr", class_="app")

        print(f"Getting page {page_count}")

        for row in table_rows:
            cols = row.find_all("td")
            game_info = {
                "No.": int(cols[0].text.strip(".")),
                "Title": cols[2].text,
                "Current": int(cols[3].text.replace(",", "")),
                "24h Peak": int(cols[4].text.replace(",", "")),
                "All-Time Peak": int(cols[5].text.replace(",", "")),
                "Detailed Information": f"https://steamdb.info{cols[1].find('a').get('href')}",
            }
            game_output.append(game_info)
            
        try:
            if driver.find_element(
                By.CSS_SELECTOR, "button.dt-paging-button.disabled.next"
            ).is_displayed():
                print("No more pages left to scrape")
                driver.close()
                return False

        except NoSuchElementException:
            if driver.find_element(
                By.CSS_SELECTOR, "button.dt-paging-button.next"
            ).is_enabled():
                driver.find_element(By.CSS_SELECTOR, "button.dt-paging-button.next").click()
                sleep(10)
        page_count += 1
            
            
def output():
    df = pd.DataFrame(game_output)
    df.to_csv(
        f"game_info_{REPORT_TIME.strftime('%d%m%y_%H%M')}.csv",
        index=False,
    )
    df.to_excel(
        f"game_info_{REPORT_TIME.strftime('%d%m%y_%H%M')}.xlsx",
        index=False,
    )


def main():
    get_game_info(base_url)
    output()


if __name__ == "__main__":
    main()
