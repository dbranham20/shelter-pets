import requests
import os
import math
from dotenv import load_dotenv
from auth import attempt_authorization
from bs4 import BeautifulSoup
import base64

load_dotenv()

bearer_token = os.getenv("BEARER_TOKEN")
user_id = os.getenv("USER_ID")
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserMentionsPython"
    return r

def connect_and_send_request(verb, url, params):
    response = requests.request(verb, url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        print(response.status_code)
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def make_tweet(pet):
    print(pet)
    url = "https://api.twitter.com/2/tweets"
    mediaUrl = "https://upload.twitter.com/1.1/media/upload.json"
    
    media = get_animal_media(list(pet.values())[0])
    oauth = attempt_authorization(consumer_key, consumer_secret)

    mediaResponse = oauth.post(mediaUrl + '?media=' + media.decode('ISO-8859-1') + '&' + 'media_category=tweet_image')
    print(mediaResponse.text)
    # response = oauth.post(url, json = {"text": "ANSLEY"})
    # if response.status_code != 201:
    #     print(response.status_code)
    #     raise Exception(
    #         "Request returned an error: {} {}".format(
    #             response.status_code, response.text
    #         )
    #     )

def get_animal_media(url):
  response = requests.request('GET', url, auth=bearer_oauth, stream=True)
  # with open(response.content, 'rb') as f:
  #   contents = f.read()
  #   print(contents)
  return response.content

URL = "http://petharbor.com/results.asp?searchtype=ADOPT&start=4&friends=1&samaritans=1&nosuccess=0&rows=10&imght=120&imgres=Detail&tWidth=200&view=sysadm.v_chrl1&bgcolor=000099&text=ffffff&link=ffffff&alink=ffffff&vlink=ffffff&fontface=arial&fontsize=10&col_hdr_bg=ffffff&col_hdr_fg=0000ff&col_bg=ffffff&col_fg=000000&miles=20&shelterlist=%27CHRL%27&atype=&where=type_CAT&PAGE=1"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
resultsTable = soup.find_all("table", class_="ResultsTable")

finalPetList = []

for result in resultsTable:
  currentPetImg = ''
  currentPetName = ''
  for idx, row in enumerate(result.find_all("td")):
    if row.get("class")[0] != 'TableTitle' and idx != 0:
      img = row.find("img")
      if (img != None):
        currentPetImg = 'http://petharbor.com/' + img['src']
      else:
        for e in row.findAll('br'):
          e.extract()
        renderedText = row.renderContents().decode("utf-8").split("My name is",1)
        if len(renderedText) > 1:
          catName = renderedText[1].split(".",1)[0]
          if catName:
            currentPetName = renderedText[1].split(".",1)[0]
            finalPetList.append({currentPetName: currentPetImg})
            currentPetImg = ''
          else:
            currentPetName = "No Name"
            finalPetList.append({currentPetName: currentPetImg})
            currentPetImg = ''

# print('results', finalPetList)
make_tweet(finalPetList[0])




