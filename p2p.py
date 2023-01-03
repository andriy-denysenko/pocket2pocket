#!/usr/bin/env python3

# Based on https://medium.com/@alexdambra/getting-your-reading-history-out-of-pocket-using-python-b4253dbe865c

import json
#import pandas as pd
import requests
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CONSUMER_KEY=103033-e946a42340531b8fb55548b

# POST request for token
url = 'https://getpocket.com/v3/oauth/request' # Set destination URL here
post_fields = {"consumer_key":"your_consumer_key","redirect_uri":"http://www.google.com"}   # Set POST fields here
request = Request(url, urlencode(post_fields).encode())
json = urlopen(request).read().decode()
print(json)