# coding:utf-8
import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
from pyquery import PyQuery as pq

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(options=chrome_options) # 无头模式 options = ?
# browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)
KEYWORD = 'iPad'

def index_page(page):
    """
    抓取索引页
    :param page:页码
    :return:
    """
    print('正在爬取第',page,'页')
    try:
        url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
        browser.get(url)
        if page > 1:
            input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-page div.form > input')))
            submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainsrp-page div.form > span.btn.J_Submit')))
            input.clear()
            input.send_keys(page)
            submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'.m-itemlist .items .item'),str(page))
        )
        get_products()
    except TimeoutException:
        index_page(page)

def get_products():
    """
    提取商品数据
    :return:
    """
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image':item.find('.pic .img').attr('data-src'),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text(),
            'title':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)

MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_COLLECTION = 'products'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def save_to_mongo(result):
    """
    保存至Mongodb
    :param result:
    :return:
    """
    try:
        if db[MONGO_COLLECTION].insert(result):
            print('存储到Mongodb成功')
    except Exception:
        print('存储到Mongodb失败')


MAX_PAGE = 100

def main():
    """
    遍历每一页
    :return:
    """
    for i in range(1,MAX_PAGE+1):
        index_page(i)

if __name__ == '__main__':
    main()