from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import pandas as pd
import warnings
from datetime import datetime
from ScrapeURLs import ObtainText, get_name, get_org, summarise , getAnswer
from CrawlURLs import get_links

chrome_options = Options()  
chrome_options.add_argument("--headless") # Opens the browser up in background
chrome_driver_path = "static\chromedriver.exe"

def create_dataset(searchterm):
    url_list = get_links(searchterm)
    driver = webdriver.Chrome(options=chrome_options,executable_path = chrome_driver_path)
    number_list=[]
    email_list=[]
    name_list=[]
    organisation_list=[]
    occupation_list=[]
    summary_list=[]
    ####location=[]#####
    url_lis_finalt=[]
    for each_url in url_list:
        driver.get(each_url)
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')
        unfiltered=soup.get_text()
        unfiltered_text=" ".join(unfiltered.split())
        filtered_text=ObtainText(each_url)
        number_regex = re.findall("[+]* *6*1* *0*[0-9]* *[0-9]{4} *[0-9]{4}|[0-9]{4} *[0-9]{3} *[0-9]{3}", unfiltered_text)
        numbers = list(set(number_regex))
        final_numbers = '/'.join(str(e) for e in numbers)
        number_list.append(final_numbers)
        email_regex = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',unfiltered_text)
        email=list(set(email_regex))
        final_email = ','.join(str(e) for e in email)
        email_list.append(final_email)
        name_list.append(get_name(each_url))
        organisation_list.append(get_org(filtered_text))
        warnings.filterwarnings('ignore')
        summary = summarise(filtered_text)
        occupation_list.append(getAnswer('What is this person job', filtered_text, summary))
        ####location.append(getAnswer('What is the location', filtered_text, summary))####
        summary_list.append(summary)
        url_lis_finalt.append(each_url)
    data=[]
    for i in range(0,len(url_lis_finalt)):
        data.append([name_list[i], organisation_list[i], occupation_list[i], number_list[i], email_list[i], summary_list[i], url_lis_finalt[i]])
    final_data = pd.DataFrame(data, columns=['Name', 'Organisation', 'Occupation', 'Contact Number', 'Email ID', 'Website Summary', 'Website URL'])
    now = datetime.now()
    current_time = now.strftime("%d-%m-%Y-%H-%M")
    filename = 'outputs\\'+ str(current_time) +'.csv'
    final_data.to_csv(filename)

    return filename
