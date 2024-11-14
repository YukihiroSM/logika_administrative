import requests
import time


class AutoRefreshJWTSession(requests.Session):
    _auth_url = 'https://api.logikaschool.com.ua/auth/login/employee'
    _refresh_url = 'https://example.com/api/refresh'
    _username = 'statistic_tech_user'
    _password = 'OG1hL0o7NHRWTFti'

    def __init__(self):
        super().__init__()
        self.headers["Origin"] = "https://backoffice.logikaschool.com.ua"
        self.headers["Referer"] = "https://backoffice.logikaschool.com.ua"
        self.headers["Content-Type"] = "application/json"
        self.token_expiry = 0
        self.jwt_token = None
        self.refresh_token = None
        self._get_new_token()

    def _get_new_token(self):
        response = self.post(self._auth_url, json={
            'login': self._username,
            'password': self._password
        })

        if response.status_code == 200:
            token_data = response.json()
            self.jwt_token = token_data['accessToken']
            self.refresh_token = token_data['refreshToken']
            self.token_expiry = time.time() + 3600
            self.headers.update({'Authorization': f'Bearer {self.jwt_token}'})
        else:
            raise Exception(f"Authorization failed: {response.status_code} {response.text}")

    def _refresh_access_token(self):
        response = self.post(self._refresh_url, json={
            'refresh_token': self.refresh_token
        })

        if response.status_code == 200:
            token_data = response.json()
            self.jwt_token = token_data['access_token']
            self.token_expiry = time.time() + token_data['expires_in']
            self.headers.update({'Authorization': f'Bearer {self.jwt_token}'})
        else:
            raise Exception(f"Token refresh failed: {response.status_code} {response.text}")

    def request(self, method, url, **kwargs):
        response = super().request(method, url, **kwargs)
        if response.status_code == 401:
            self._get_new_token()
            response = super().request(method, url, **kwargs)
        return response


if __name__ == "__main__":
    session = AutoRefreshJWTSession()
    response = session.get("https://api.logikaschool.com.ua/sync/statistics/group")
    print(response.status_code)
    print(response.json())
