import requests
from pathlib import Path
import os
from dotenv import load_dotenv
from utils.exceptions import LmsAuthenticationFailed


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(Path(BASE_DIR, ".env"))


# def get_authenticated_session():
#     """
#     Get authenticated session for LMS.
#     """
#     session = requests.Session()
#
#     login_payload = {
#         "login": os.environ.get("LMS_LOGIN"),
#         "password": os.environ.get("LMS_PASS"),
#     }
#     try:
#         resp = session.post(
#             "https://lms.logikaschool.com/s/auth/api/e/user/auth", data=login_payload
#         )
#     except Exception as auth_exception:
#         raise LmsAuthenticationFailed(
#             "LMS: Unable to authenticate. Something gone wrong in auth process"
#         ) from auth_exception
#
#     if resp.ok:
#         print("LMS: Session creation is successful!")
#         return session
#
#     else:
#         raise LmsAuthenticationFailed(
#             "LMS: Unable to renew cookies. Something gone wrong in auth process"
#         )


def get_authenticated_session():
    session = requests.Session()
    headers = {
        'authority': 'lms.logikaschool.com',
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': os.environ.get("COOKIE"),
        'referer': 'https://lms.logikaschool.com/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    session.headers.update(headers)
    return session
