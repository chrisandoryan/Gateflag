#!/usr/bin/env python3
"""
Provides a simple Python wrapper for invoking an API Gateway endpoint using IAM signed requests.
Example:
   python3 take_flag.py https://ydkmhri03l.execute-api.ap-southeast-1.amazonaws.com/stable/user_flag
   python3 take_flag.py https://ydkmhri03l.execute-api.ap-southeast-1.amazonaws.com/stable/root_flag
"""

try:
    from urllib.parse import urlparse, urlencode, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs
    from urllib import urlencode

import re
import sys
import os

import requests
from boto3 import Session
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

def signing_headers(method, url_string, body):
    region = re.search("execute-api.(.*).amazonaws.com", url_string).group(1)
    url = urlparse(url_string)
    path = url.path or '/'
    querystring = ''
    if url.query:
        querystring = '?' + urlencode(
            parse_qs(url.query, keep_blank_values=True), doseq=True)

    safe_url = url.scheme + '://' + url.netloc.split(
        ':')[0] + path + querystring
    request = AWSRequest(method=method.upper(), url=safe_url, data=body)
    SigV4Auth(Session().get_credentials(), "execute-api",
              region).add_auth(request)
    return dict(request.headers.items())


if __name__ == "__main__":
    METHOD = "GET"

    if len(sys.argv) <= 1:
        url = os.getenv('FLAG_GATEWAY')
    else:
        url = sys.argv[1]

    if not sys.stdin.isatty():
        body = sys.stdin.read()
    else:
        body = None

    r = requests.get(url, headers=signing_headers(METHOD, url, body))
    print(r.content.decode("utf-8"))


