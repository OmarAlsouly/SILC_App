from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from time import sleep
import re
from random import randint
from urllib.parse import urlparse
import torch
import warnings
from transformers import AutoTokenizer,AutoModelForTokenClassification,pipeline,AutoModelForSeq2SeqLM,AutoModelForQuestionAnswering
from CrawlURLs import Text_size

model_nameSum = "sshleifer/distilbart-cnn-12-6"
tokenizerSum = AutoTokenizer.from_pretrained(model_nameSum)
modelSum = AutoModelForSeq2SeqLM.from_pretrained(model_nameSum)

model_nameQA = "deepset/roberta-base-squad2"
tokenizerQA = AutoTokenizer.from_pretrained(model_nameQA)
modelQA = AutoModelForQuestionAnswering.from_pretrained(model_nameQA)

bert_tokenizer = AutoTokenizer.from_pretrained('dslim/bert-large-NER') #chosen nlp model
bert_model = AutoModelForTokenClassification.from_pretrained('dslim/bert-large-NER')
nlp = pipeline('ner', model=bert_model, tokenizer=bert_tokenizer)

chrome_options = Options()  
chrome_options.add_argument("--headless") # Opens the browser up in background
chrome_driver_path = "static\chromedriver.exe"

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
    
    
def most_common(list):
    return max(set(list), key=list.count)


def get_org(PageContent):
    # List with the orgs
    orgs_list = []
    
    Text = Text_size(PageContent, 1500)
    
    for slices in Text:
        
        nlp_result = nlp(slices)
        
        # Buffer for orgs belonging to the most recent entity
        current_entity_tokens = []
        current_entity = None

        # Iterate over the tagged tokens
        for token in nlp_result:

            #if entity not org or score < 0.9, ignore
            if token['entity'] not in ('B-ORG', 'I-ORG') or token['score'] < 0.90:
                continue

            # If an enitity is the start
            if token['entity']  == 'B-ORG':
                # ... if we have a previous entity in the buffer, store it in the result list
                if current_entity is not None:
                    orgs_list.append(
                        (''.join(current_entity_tokens)))

                current_entity = token['entity'][2:]
                # The new entity has so far only one token
                current_entity_tokens = [token['word'].replace('##', '')+' ']
            # If the entity continues ...
            elif token['entity'] == 'I-ORG':
                # Just add the token buffer
                current_entity_tokens.append(token['word'].replace('##', ''))

        # The last entity is still in the buffer, so add it to the result
        # ... but only if there were some entity at all
        if current_entity is not None:
            orgs_list.append(
                (''.join(current_entity_tokens)))
            

    if orgs_list:
        return most_common(orgs_list)
    else:
        return 'N/A'
    
    
def get_name(url):
    name = []
    
    urlpath = urlparse(url) #taking only the path of the url
    textStrip = urlpath[2].split("/") #seperating the path into different tokens, using '/'
    for strings in textStrip: #iterating through words in the path
        newString = re.sub('[^0-9a-zA-Z]+', ' ', strings).title() #replacing all non alphanumeric character with space
        nlp_result = nlp(newString) #applying the model on the string

        for word in nlp_result: #iterating through the output of the model, to check if it output contain names
            if word['entity'] in ('B-PER', 'I-PER') and word['score'] >= 0.90:
                if word['entity'].startswith("B-"):
                    name.append(word['word'].replace('##', '')+' ')
                    
                elif word['entity'].startswith("I-"):
                    name.append(word['word'].replace('##', ''))
                    
    return ''.join(name)


def summarise(text):
    warnings.filterwarnings('ignore')
    tokenized_text = tokenizerSum.prepare_seq2seq_batch([text], return_tensors='pt')
    summarise = modelSum.generate(**tokenized_text)
    summarise_text = tokenizerSum.batch_decode(summarise, skip_special_tokens=True)[0]

    return summarise_text    


def QnA(question, text):
    size = 1000
    Text = Text_size(text, size)
    answers = []
    
    while True:
        try:
            for x in range(len(Text)):  
                while True:
                    try:
                        a = str(question_answer(question, list(Text_size(text, size))[x]))
                        ans = a
                        if len(a) > 2:
                            if len(a) < 100:
                                if "<s>" not in a:
                                    answers.append(ans)
                        break
                    except UnboundLocalError:
                        break
            return answers
        except:
            size = size - 200
            continue


def question_answer(question,answer_text):
    inputs = tokenizerQA.encode_plus(question, answer_text, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"].tolist()[0]

    text_tokens = tokenizerQA.convert_ids_to_tokens(input_ids)

    outputs = modelQA(**inputs)
    answer_start_scores=outputs.start_logits
    answer_end_scores=outputs.end_logits

    answer_start = torch.argmax(answer_start_scores)
    answer_end = torch.argmax(answer_end_scores) + 1
    
    answer = tokenizerQA.convert_tokens_to_string(tokenizerQA.convert_ids_to_tokens(input_ids[answer_start:answer_end]))

    # Combine the tokens in the answer and print it out.""
    answer = answer.replace("#","")

    #print('Answer: "' + answer + '"')
    return answer


def getAnswer(Question, Text, sText):
    AnswerSet = set()
    Answer = []
    Ans1 = QnA(Question, Text)
    Ans2 = QnA(Question,sText)
              
    for A1 in Ans1:
        if A1 != "<s>":
            AnswerSet.add(A1)
    for A2 in Ans2:
        if A2 != "<s>":
            AnswerSet.add(A2)
    if len(AnswerSet) == 0:        
        AnswerSet.add("N/A")
        
    for x in AnswerSet:
        Answer.append(x)
            
    return Answer