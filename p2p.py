#!/usr/bin/env python3

########################################################################
#
# This script reads from the Pocket account linked to the Google account
#
########################################################################

# Based on https://medium.com/@alexdambra/getting-your-reading-history-out-of-pocket-using-python-b4253dbe865c

import json
#import pandas as pd
import requests
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import webbrowser

class Pocket2Pocket:
    def __init__(self):
        self.consumer_key ='103033-bbd1a3fd911ac96f4aef898'
        self.authentication_token=''
        self.access_token=''
        self.request=None

    def get_authentication_token(self, authentication_callback):
        print('Sending request for authentication token')
        url = 'https://getpocket.com/v3/oauth/request' # Set destination URL here
        post_fields = {
            "consumer_key":self.consumer_key,
            "redirect_uri":f"pocket2pocket:{authentication_callback}"
        }

        self.request = Request(url, urlencode(post_fields).encode())

        self.authentication_token = urlopen(self.request).read().decode().split('=')[1]
        print (f'Got authentication token: {self.authentication_token}')

    def authorize(self, authorization_callback):
        print('Opening authorization URL')
        AUTHORIZATION_URL=f'https://getpocket.com/auth/authorize?request_token={self.authentication_token}&redirect_uri=pocket2pocket:{authorization_callback}'
        webbrowser.open(AUTHORIZATION_URL)
        cont = input("Press Enter after authorization")

    def get_access_token(self):
        print('Sending request for access token')
        url = 'https://getpocket.com/v3/oauth/authorize' # Set destination URL here
        post_fields = {
            "consumer_key":self.consumer_key,
            "code":self.authentication_token
        }

        self.request = Request(url, urlencode(post_fields).encode())
        response = urlopen(request).read().decode()
        data = response.split('&')
        self.access_token=data[0].split('=')[1]
        self.username=data[1].split('=')[1]
        print(f'Got access token {self.access_token}')

def read_authentication_callback():
    print('In authentication_callback!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    p2p.authorize(read_authorization_callback)

def read_authorization_callback():
    print('In authorization_callback!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')

    # POST request an access token
    #---------------------------------------------------------
    # Getting the lisk of links
    post_fields = {
        "consumer_key":CONSUMER_KEY,
        "access_token":ACCESS_TOKEN,
        "sort":"newest",
        "detailType":"complete"
    }
    #response = requests.get(“https://getpocket.com/v3/get", params=parameters)
    url='https://getpocket.com/v3/get'
    p2p.request = Request(url, urlencode(post_fields).encode())
    response = urlopen(request).read().decode()

    IMPORTED_LINKS_FILENAME='imported.json'
    with open(IMPORTED_LINKS_FILENAME, 'w', encoding="UTF-8") as f:
        f.write(response)

    print(f'Saved in {IMPORTED_LINKS_FILENAME}')
    # TODO: Now, start auths for writing to the other account

if __name__ == '__main__':
    p2p = Pocket2Pocket()
    p2p.get_authentication_token('http://www.google.com')
    p2p.authorize('http://www.google.com')
    p2p.get_access_token()
    read_authorization_callback()

