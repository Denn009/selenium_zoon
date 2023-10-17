import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from urllib.parse import unquote
import time
import random
import json

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
}


def get_source_html(url):
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        driver.get(url=url)
        time.sleep(3)

        while True:
            find_more_element = driver.find_element(By.CSS_SELECTOR, "div.catalog-button-showMore")

            if driver.find_elements(By.CSS_SELECTOR, "div.hasmore-text"):
                with open("source-page.html", 'w') as file:
                    file.write(driver.page_source)
                    get_links()
                break
            else:
                actions = ActionChains(driver)
                actions.move_to_element(find_more_element).perform()
                time.sleep(3)

                if driver.find_elements(By.CSS_SELECTOR, "span.button-show-more"):
                    driver.find_element(By.CSS_SELECTOR, "span.button-show-more").click()
                    time.sleep(3)

    except Exception as _ex:
        print(_ex)

    finally:
        driver.close()
        driver.quit()


def get_links():
    with open('source-page.html') as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')
    items_link = soup.find_all('a', class_='title-link js-item-url')

    links_list = []
    for link in items_link:
        links_list.append(link.get('href'))

    with open("links_txt", "w") as file:
        for link in links_list:
            file.write(f"{link}\n")

    get_pages()


def get_pages():
    with open('links_txt') as file:
        url_list = [url.strip() for url in file.readlines()]

    total_list = []
    i = 0

    for url in url_list:

        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        # Get title
        try:
            title = soup.find("h1", "service-page-header--text").text.replace("\xa0", " ").strip()

        except Exception as _ex:
            title = None

        # Get phone
        item_phone_list = []
        try:
            numbers = soup.find('div', class_="service-phones-list").find_all("a", "js-phone-number")

            for num in numbers:
                item_phone_list.append(num.get('href').split(":")[-1].strip())

        except Exception as _ex:
            item_phone_list = None

        # Get link on site
        links_site_list = []
        try:
            links_site = soup.find_all(string=re.compile("Сайт|Официальный сайт"))[-1].find_next().find_all("a")
            for link in links_site:
                link_edit = unquote(link.get("href")).split("?to=")[-1].split("&hash=")[0].split("?token=")[0]
                links_site_list.append(link_edit)

        except Exception as _ex:
            links_site_list = None

        # Get address
        try:
            address = soup.find(attrs={"itemprop": "address"}).text
            address = " ".join(address.split())

        except Exception as _ex:
            address = None

        # Get worktime
        try:
            worktime = soup.find("dd", class_="upper-first").find("div")
            worktime = str(worktime).split("<br/>")[0].replace("<div>", "").replace("</div>", "").strip()

        except Exception as _ex:
            worktime = None

        # Get social
        social_link_list = []
        try:
            social_element = soup.find(attrs={"data-uitest": "org-social-list"}).find_all("a")
            for social in social_element:
                social = unquote(social.get("href")).split("?to=")[-1].split("&hash=")[0]
                print(social)
                social_link_list.append(social)

        except Exception as _ex:
            social_link_list = None

        total_list.append(
            {
                "id": i,
                "title": title,
                "number": item_phone_list,
                "links": links_site_list,
                "address": address,
                'worktime': worktime,
                "social": social_link_list,
            }
        )

        time.sleep(random.randint(3, 5))
        i += 1
        print(f"Page {i} successfully")

    with open("total.json", "w") as file:
        json.dump(total_list, file, indent=4, ensure_ascii=False)

def main():
    get_source_html("https://zoon.ru/spb/trainings/type/kursy_massazha/")

if __name__ == "__main__":
    main()
