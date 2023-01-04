#!/usr/bin/env python3

########################################################################
#
# This script reads from one Pocket account and saves to another
#
########################################################################

# Based on https://medium.com/@alexdambra/getting-your-reading-history-out-of-pocket-using-python-b4253dbe865c

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import webbrowser

STEP = 500

def show_status(msg):
    print(msg)

class Pocket2Pocket:
    def __init__(self):
        self.consumer_key ='103033-bbd1a3fd911ac96f4aef898'
        self.authentication_token=''
        self.access_token=''
        self.request=None
        self.imported_links = []

    def get_authentication_token(self, authentication_callback):
        show_status('Sending request for authentication token...')
        url = 'https://getpocket.com/v3/oauth/request' # Set destination URL here
        post_fields = {
            "consumer_key":self.consumer_key,
            "redirect_uri":f"{authentication_callback}"
        }

        self.request = Request(url, urlencode(post_fields).encode())
        decoded_response = urlopen(self.request).read().decode()
        self.authentication_token = decoded_response.split('=')[1]
        show_status (f'Got authentication token.') #: {self.authentication_token}')

    def authorize(self, authorization_callback):
        show_status('pocket2pocket is preparing to login and make a request to obtain a request token from Pocket.')
        cont = input("Press Enter when you are ready to confirm login.")
        AUTHORIZATION_URL=f'https://getpocket.com/auth/authorize?request_token={self.authentication_token}&redirect_uri={authorization_callback}'
        webbrowser.open(AUTHORIZATION_URL)
        cont = input("Press Enter after authorization.")

    def get_access_token(self):
        show_status('Sending request for access token...')
        url = 'https://getpocket.com/v3/oauth/authorize' # Set destination URL here
        post_fields = {
            "consumer_key":self.consumer_key,
            "code":self.authentication_token
        }

        self.request = Request(url, urlencode(post_fields).encode())
        response = urlopen(self.request).read().decode()
        data = response.split('&')
        self.access_token=data[0].split('=')[1]
        self.username=data[1].split('=')[1]
        # show_status(f'Got access token {self.access_token}')
        show_status(f'Got access token.')

    def parse_link_data(self, link_data):
        result = {}
        if 'resolved_url' in link_data.keys():
            result['url'] = link_data["resolved_url"]
        elif 'given_url' in link_data.keys():
            result['url'] = link_data["given_url"]
        else:
            raise Exception('No urls in link data.')

        if 'given_title' in link_data.keys():
            result['title'] = link_data["given_title"]
        elif 'resolved_title' in link_data.keys():
            result['title'] = link_data["resolved_title"]

        if 'tags' in link_data.keys():
            result['tags'] = ','.join(link_data["tags"].keys())
            # result['tags'] = ','.join(list(link_data["tags"].keys()))

        if 'time_added' in link_data.keys():
            result['time'] = link_data["time_added"]

        return result

    # TODO: implement get_all_links with 'count' parameter

    # def get_all_links(self):
    #     show_status('Getting all links...')
    #     count = STEP
    #     offset = 0
    #     total = 0
    #     while count > 0:
    #         post_fields = {
    #             "consumer_key":self.consumer_key,
    #             "access_token":self.access_token,
    #             "detailType":"simple",
    #             "count":count,
    #             "offset":offset,
    #         }

    #         url = 'https://getpocket.com/v3/get'
    #         self.request = Request(url, urlencode(post_fields).encode())
    #         response = urlopen(self.request).read().decode()
    #         json_response = json.loads(response)

    #         links = []
    #         for item_id in json_response['list'].keys():
    #             link = self.parse_link_data(json_response['list'][item_id])
    #             link['action'] = 'add'
    #             links.append(link)
            

    #         count = len(json_response['list'])
    #         total = total + count
    #         self.imported_links.extend(links)
    #         show_status(f'Loaded {total} links.')

    #     show_status(f'Loaded all links.')

    def get_all_links(self):
        show_status('Getting all links...')

        post_fields = {
            "consumer_key":self.consumer_key,
            "access_token":self.access_token,
            "detailType":"simple",
        }

        url = 'https://getpocket.com/v3/get'
        self.request = Request(url, urlencode(post_fields).encode())
        response = urlopen(self.request).read().decode()
        json_response = json.loads(response)
        show_status(f"Count: {len(json_response['list'])}")

        links = []
        for item_id in json_response['list'].keys():
            # show_status(f"Key: {item_id}")
            link = self.parse_link_data(json_response['list'][item_id])
            link['action'] = 'add'
            # show_status(f"Link: {link}")
            links.append(link)
        
        self.imported_links = links
        total = len(self.imported_links)
        show_status(f'Loaded {total} links.')

        show_status(f'Loaded all links.')


    def batch_add_links(self):
        show_status('Adding all links...')
        actions = self.imported_links

        cont = True
        total = 0

        while cont:
            end = STEP if STEP < len(actions) else len(actions)
            batch = actions[0:end]
            actions = actions[end:]
            self._batch_add_links(batch)
            if end != STEP:
                cont = False
            show_status(f"Added {len(batch)} actions.")
            total = total + len(batch)
            show_status(f"Total progress: {total} of {len(self.imported_links)}.")

        show_status(f'Added all actions.')

    def _batch_add_links(self, actions):
        post_fields = {
            "consumer_key":self.consumer_key,
            "access_token":self.access_token,
            "actions":json.dumps(actions),
            # "actions":actions,
        }

        # show_status (f'Post fields: {post_fields}')

        url = 'https://getpocket.com/v3/send'
        self.request = Request(url, urlencode(post_fields).encode())
        response = urlopen(self.request).read().decode()



if __name__ == '__main__':
    p2p = Pocket2Pocket()
    p2p.get_authentication_token('http://www.google.com')
    p2p.authorize('http://www.google.com')
    p2p.get_access_token()
    p2p.get_all_links()
    
    # TODO: Now, start auths for writing to the other account
    p2p.get_authentication_token('http://www.google.com')
    p2p.authorize('http://www.google.com')
    p2p.get_access_token()
    p2p.batch_add_links()


# TODO: Best Practices

# [] Native mobile applications should register a unique URI scheme and supply a redirect URI using that scheme if the platform you are developing on supports this setup.
# [] If you support multiple platforms (e.g. iPhone, iPad, and Mac OS X), you are strongly encouraged to use separate consumer keys for each. You can set them up in a parent/child configuration, so that your credentials are related. Users who authorize one application will authorize all of them.
# [] If you detect the user has a Pocket app installed on their device that supports OAuth login, you are strongly encouraged to send the user to the Pocket app to handle authorization.
# [] If you send the user to the Pocket website to handle authentication, you are must not open that web page as a screen or a popup within your application. Instead, open a new page in the user's default web browser. For security purposes, using an in application screen or pop up may result in your Pocket access being disabled.
# [x] When the user taps a "Login" or "connect with Pocket" button in your application, you should present some UI to indicate that your application is preparing to login and make a request to obtain a request token from Pocket.