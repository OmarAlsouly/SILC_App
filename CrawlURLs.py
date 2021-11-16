from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
import re
import math
from random import randint
from urllib.parse import urlparse
from urllib.parse import urljoin
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from CrawlGoogle import get_results

bert_tokenizer = AutoTokenizer.from_pretrained('dslim/bert-large-NER') #chosen nlp model
bert_model = AutoModelForTokenClassification.from_pretrained('dslim/bert-large-NER')
nlp = pipeline('ner', model=bert_model, tokenizer=bert_tokenizer)

chrome_options = Options()  
chrome_options.add_argument("--headless") # Opens the browser up in background
chrome_driver_path = "static\chromedriver.exe"
#function to check if the url exists in the url list
def existingURL_checker(url,list):
    return any([any([i==url for i in row])for row in list])

#function to crawl website and extract links that are found in these websites
def get_links(searchterm):
    
    google_result = get_results(searchterm)
    
    #initiate driver
    driver = webdriver.Chrome(options=chrome_options,executable_path = chrome_driver_path)

    #iterate through the given list
    for url, level in google_result: 

        if len(google_result) >= 500: #limiting the results to 500 for now ---to be removed
            break    

        if level > 1: #limiting the results to level 2
            continue

        #getting the content of the page
        page = driver.get(url);
        page = driver.page_source
        soup = BeautifulSoup(page, 'html.parser')

        #iterating through the links in the page, and checking if these links already exist
        for links in soup.find_all("a", href=True):
            new_url = links.get('href')
            new_url = urljoin(url, new_url) 

            if existingURL_checker(new_url,google_result): #checking if they exist
                continue

            #appending the result to the list, which will be also used in the loop
            google_result.append((new_url, level+1)) 

        sleep(randint(2,10))
    
    UrlsWithNames = []
    #iterating throught the urls list, to check if name is present in the url. if yes, url is added to the output
    for url in google_result: 
        Checker = False #checker which will be used to flag if name is found in url
        urlpath = urlparse(url[0]) #taking only the path of the url
        textStrip = urlpath[2].split("/") #seperating the path into different tokens, using '/'
        for strings in textStrip: #iterating through words in the path
            newString = re.sub('[^0-9a-zA-Z]+', ' ', strings).title() #replacing all non alphanumeric character with space
            ner_list = nlp(newString) #applying the model on the string

            for word in ner_list: #iterating through the output of the model, to check if it output contain names
                if word['entity'] in ('B-PER', 'I-PER') and word['score'] >= 0.95:
                    Checker = True #assign true when name is found
            if Checker: #break the loop when name is found, since no further iterating is needed
                break

        if Checker: #only adding urls with names to the new list
            UrlsWithNames.append((url[0]))
            
    driver.close()        
    #output of function is urls with names in them            
    return UrlsWithNames


# Obtain text
def ObtainText(URL):
    driver = webdriver.Chrome(options=chrome_options,executable_path = chrome_driver_path)
    driver.get(URL)
    page = driver.page_source
    
    soup = BeautifulSoup(page, 'html.parser')
    unfiltered=soup.get_text()
    unfiltered_text=" ".join(unfiltered.split())
    
    
    footer_class_remove=soup.find_all(class_=re.compile("footer")) #Elements with class names containing footer
    header_class_remove=soup.find_all(class_=re.compile("header")) #Elements with class names containing header
    footer_tag_remove=soup.find_all('footer') #All tag names footer
    header_tag_remove=soup.find_all('header') #All tag names header
    head_tag_remove=soup.find_all('head') #All tag names header
    script_tag_remove=soup.find_all('script')
    
#Removes all the Unnecessary information from tag named footer and 
#header and tag with class names that contain footer and header.
    for foot in footer_class_remove:
        foot.decompose()
    for head in header_class_remove:
        head.decompose()
    for footer in footer_tag_remove:
        footer.decompose()
    for header in header_tag_remove:
        header.decompose()
    for header in head_tag_remove:
        header.decompose()
    for script in script_tag_remove:
        script.decompose()
    final=soup.get_text()
    final_text=" ".join(final.split())
    if(len(final_text)>100):
        final_text=final_text
    else:
        final_text=unfiltered_text
    return final_text
    driver.close()    
    sleep(randint(2,5))
    
# Text Size    
def Text_size(text, size):
    textSet = []
    
    if len(text) > size:
        i = math.ceil(len(text)/ size)
        for x in range(i):
            texti = text[x*(size + 1):(x + 1)*size]
            textSet.append(texti)
        return textSet
    else:
        return text    