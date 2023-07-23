import requests
from pathlib import Path
import os
from dotenv import load_dotenv
from utils.exceptions import LmsAuthenticationFailed


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(Path(BASE_DIR, ".env"))


def get_authenticated_session():
    """
    Get authenticated session for LMS.
    """
    session = requests.Session()

    login_payload = {
        "login": os.environ.get("LMS_LOGIN"),
        "password": os.environ.get("LMS_PASS"),
    }
    resp = session.post(
        "https://lms.logikaschool.com/s/auth/api/e/user/auth", data=login_payload
    )
    if resp.ok:
        print("Session creation is successful!")
        return session

    else:
        raise LmsAuthenticationFailed(
            "Unable to renew cookies. Something gone wrong in auth process"
        )
