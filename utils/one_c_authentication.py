import requests
from pathlib import Path
import os
from dotenv import load_dotenv
from utils.exceptions import LmsAuthenticationFailed


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(Path(BASE_DIR, ".env"))


def get_one_c_authenticated_session():
    """
    Get authenticated session for LMS.
    """
    session = requests.Session()
    one_c_host = "school.cloud24.com.ua" if os.environ.get("ENVIRONMENT") == "development" else "localhost"
    login_payload = {
        "username": os.environ.get("ONE_C_LOGIN"),
        "password": os.environ.get("ONE_C_PASSWORD"),
    }
    try:
        resp = session.post(
            f"https://{one_c_host}:22443/SCHOOL/ru_RU/hs/1cData/TeachersWork/?from=20230901&till=20230901&businessDirection=Школы%20Программирования", data=login_payload
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
