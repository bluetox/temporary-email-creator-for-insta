import requests
import time
from bs4 import BeautifulSoup
import os

DOMAINS = [
    "sharklasers.com",
    "guerrillamail.info",
    "grr.la",
    "guerrillamail.biz",
    "guerrillamail.com",
    "guerrillamail.de",
    "guerrillamail.net",
    "guerrillamail.org",
    "guerrillamailblock.com",
    "pokemail.net",
    "spam4.me"
]

BASE_URL = "https://www.guerrillamail.com"
EMAIL_CHECK_URL = f"{BASE_URL}/ajax.php?f=check_email&seq=1&site=guerrillamail.com&in="
EMAIL_SET_URL = f"{BASE_URL}/ajax.php?f=set_email_user"

def extract_api_key(html):
    soup = BeautifulSoup(html, 'html.parser')
    script_tag = soup.find('script', string=lambda text: text and 'gm_init_vars' in text)
    
    if not script_tag:
        raise ValueError("API key not found in the HTML")

    script_content = script_tag.string
    for line in script_content.split('\n'):
        if 'api_token' in line:
            print("\033[92m[SUCCESSFUL]\033[0m APItoken")
            return line.split(':')[-1].strip().strip("',")
    

    
    raise ValueError("API key not found in the script content")

def initialize_session():
    response = requests.get(f"{BASE_URL}/inbox")
    api_token = extract_api_key(response.text)
    
    try:
        cookies = response.headers['Set-Cookie'].split(';')
        phpsessid = cookies[0].split('=')[1]
        print("\033[92m[SUCCESSFUL]\033[0m PHPSESS")
    except (KeyError, IndexError):
        raise RuntimeError("Error grabbing the Session ID")
    
    headers = {
        'Cookie': f'PHPSESSID={phpsessid}',
        'Authorization': f'ApiToken {api_token}',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': BASE_URL,
        'Referer': BASE_URL,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.0 (Edition std-2)',
        'X-Requested-With': 'XMLHttpRequest',
    }
    return headers

def check_email_availability(headers, username, domain):
    data = {'email_user': username, 'lang': 'en', 'site': domain, 'in': '+Set+cancel'}
    response = requests.post(EMAIL_SET_URL, data=data, headers=headers)
    response.raise_for_status()
    email = response.json().get('email_addr')
    
    if not email:
        raise RuntimeError("Error retrieving email address")

    print(f"\033[92m[SUCCESSFUL]\033[0m New email {email}")
    return email

def get_insta_code(maildata):
    return maildata['list'][0]['mail_subject'][:6]

def main():
    global DOMAINS 

    try:
        username = input("Choose what username you want: ")
        domain_number = int(input("Choose between those domains:\n"
                                  "1. sharklasers.com\n"
                                  "2. guerrillamail.info\n"
                                  "3. grr.la\n"
                                  "4. guerrillamail.biz\n"
                                  "5. guerrillamail.com\n"
                                  "6. guerrillamail.de\n"
                                  "7. guerrillamail.net\n"
                                  "8. guerrillamail.org\n"
                                  "9. spam4.me\n"
                                  "10. pokemail.net\n"
                                  "11. guerrillamailblock.com\n")) - 1
        
        if domain_number < 0 or domain_number >= len(DOMAINS):
            raise ValueError("Invalid domain number")

        domain = DOMAINS[domain_number]
        os.system('cls' if os.name == 'nt' else 'clear')
        headers = initialize_session()
        check_email_availability(headers, username, domain)
        print("Waiting for the email...")
        
        while True:
            response = requests.get(f"{EMAIL_CHECK_URL}{username}", headers=headers)
            response.raise_for_status()
            maildata = response.json()

            if not maildata.get('list'):
                time.sleep(2)
            else:
                insta_code = get_insta_code(maildata)
                print(f"\033[92m[SUCCESSFUL]\033[0m CODE: \033[31m{insta_code}\033[0m")
                break

    except (ValueError, RuntimeError, requests.RequestException) as e:
        print(f"\033[91m[ERROR]\033[0m {e}")

if __name__ == "__main__":
    main()
