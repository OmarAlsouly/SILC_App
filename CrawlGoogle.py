# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from time import sleep
from random import randint

chrome_options = Options()  
chrome_options.add_argument("--headless") # Opens the browser up in background
chrome_options.add_argument("--window-size=1920x1080")
chrome_driver_path = "static\chromedriver.exe"

def get_results(search_term):
    url_list=[]
    url="https://www.google.com/search?q="
    search_list=search_term.split()
    #Loop that appends the user input at the end of google search url
    for x in search_list:
        url=url+x+" "
    driver = webdriver.Chrome(options=chrome_options,executable_path = chrome_driver_path)
    page = driver.get(url);
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    #loops through and fetches url from the first three pages of the google.
    for page_number in range(2,5):
        find_href = driver.find_elements_by_xpath('//div[@id=\'rso\']/div//div[@class=\'yuRUbf\']/a')
        
        #Append the urls to the list
        for my_href in find_href:
            url_list.append((my_href.get_attribute("href"),0))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")#Scroller that scrolls to bottom of the page
        sleep(randint(2,5))
        submit_button = driver.find_elements_by_xpath('//div[@role=\'navigation\']//td')[page_number]#path to page number element on Google.
        submit_button.click()#clicks on different page number based on the number of pages to be crawled through
    driver.close()#closes the window after crawling through all the required number of pages.
    
    final_url_list = list(set(url_list))
    return final_url_list