import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

from utils.exceptions import LmsAuthenticationFailed

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(Path(BASE_DIR, ".env"))


def get_one_c_authenticated_session():
    """
    Get authenticated session for LMS.
    """
    session = requests.Session()
    one_c_host = (
        "school.cloud24.com.ua"
        if os.environ.get("ENVIRONMENT") == "development"
        else "localhost"
    )
    try:
        resp = session.get(
            f"https://{one_c_host}:22443/SCHOOL/ru_RU/hs/1cData/TeachersWork/",
            auth=HTTPBasicAuth(
                username=os.environ.get("ONE_C_USERNAME"),
                password=os.environ.get("ONE_C_PASSWORD"),
            ),
        )
    except Exception as auth_exception:
        raise LmsAuthenticationFailed(
            "One C: Unable to authenticate. Something gone wrong in auth process"
        ) from auth_exception

    if resp.ok:
        print("One C: Session creation is successful!")
        return session

    else:
        raise LmsAuthenticationFailed(
            f"One C: Unable to renew cookies. Something gone wrong in auth process {resp.status_code}: {resp.content}"
        )


get_one_c_authenticated_session()
