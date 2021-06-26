import praw
import schedule
import time
from termcolor import colored
from PIL import Image
import urllib.request
import io
import pytesseract
import re
import requests
import json
import os

# create the objects from the imported modules

# Push notification webhook details
webhook = os.environ.get('webhook')

# reddit api login
reddit = praw.Reddit(client_id= os.environ.get('clientid'),
                     client_secret= os.environ.get('clientsecret'),
                     username= os.environ.get('usr'),
                     password= os.environ.get('pswrd'),
                     user_agent= os.environ.get('useragent'))
titles = []
gp1 = []
gp2 = []
regex1 = r'(g|G)ame\s*(p|P)ass'
regex2 = r'(D|d)ays'
regex3 = r'(C|c)ode'
regex4 = r'(F|f)ree'
regex5 = r'14'
regexList = [regex1, regex1, regex3, regex4, regex5]
gamepass_pattern = '\s*([A-Z-\d-]{5,5})\s*-\s*([A-Z-\d-]{5,5})\s*-*\s*([A-Z-\d-]{0,5})\s*-\s*([A-Z-\d-]{0,5})\s*-\s*([A-Z-\d-]{0,5})\s*'
subreddit = reddit.subreddit('xbox+xboxone+greatxboxdeals+gamepassgameclub+xboxgamepass')

def gamepass_schedule():
    for submission in subreddit.new():
        for x in regexList:
            match1 = re.search(x, submission.title )
            if match1:
                if submission.title not in titles:
                    print("--------------------------------")
                    print("Title: ", submission.title)
                    print("Text: ", submission.selftext)
                    print("URL: ", submission.url)
                    gamepass_search(submission.title,submission.selftext)
                    check_image(submission.title,submission.url)
                    titles.append(submission.title)
                    data = {"text": titles}
                    requests.post( webhook, json.dumps( data ) )
                    print("--------------------------------\n")

def gamepass_search(title,stringtext):
    print('Pattern check begins......')
    found = re.search(gamepass_pattern,stringtext)
    if found:
        if stringtext not in gp1:
            comb1 = title + "\n" + found.group()
            data = {
                "text": comb1
            }
            requests.post( webhook, json.dumps( data ) )
            gp1.append(stringtext)
            print(found.group(),'Pattern found')
    else:
        print('No GamePass Code here in Text')
    print('Pattern check ends......')

def check_image(title,link):
    if 'jpg' in link or 'png' in link:
        print(colored('************Image File found************', 'yellow'))
        URL = link
        with urllib.request.urlopen(URL) as url:
            f = io.BytesIO(url.read())
        img = Image.open(f)
        pytesseract.pytesseract.tesseract_cmd =(r‘/app/.apt/usr/bin/tesseract’) #(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
        result = pytesseract.image_to_string(img)
        # print(result)
        image_search(title,result,link)

def image_search(title,stringtext, url):
     print('Image search begins........')
     print( stringtext )
     gp = re.search(gamepass_pattern,stringtext)

     if gp:
        print('GP pattern found')
        if stringtext not in gp2:
            Comb2 = title + '\n' + gp.group() + '\n' + url
            data2 = {
                        "text": Comb2
            }
            requests.post( webhook, json.dumps ( data2 ) )
            gp2.append(stringtext)
            print(colored('Pattern available','yellow'))
     else:
         print('GP pattern not found')
         for x in regexList:
            code = re.search(x,stringtext)
            if code:
                print('Regex found')
                print(url)
                Comb3 = title + '\n' + url
                data3 = {
                    "text": Comb3
                }
                requests.post( webhook, json.dumps( data3 ) )
                #send JPG and title

     print('Image search ends..........')

schedule.every(30).seconds.do(gamepass_schedule)

while True:
    # Checks whether a scheduled task
    # is pending to run or not
    schedule.run_pending()
    time.sleep(1)
