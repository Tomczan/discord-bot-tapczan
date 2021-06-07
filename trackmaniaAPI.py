import requests
import base64
import http.client
import json
from decouple import config


class TmApi:
    ticket = ''
    refresh_ticket = ''

    # uplay token
    def level0(self):
        conn = http.client.HTTPSConnection("public-ubiservices.ubi.com")
        payload = ""
        headers = {
            'Content-Type': 'application/json',
            # 'Basic base64.b64encode(b'email:password').decode()',
            'Authorization': 'Basic ' + config('BASE64_AUTH'),
            # Trackmania ID
            'Ubi-AppId': '86263886-327a-4328-ac69-527f0d20a237'
        }
        conn.request("POST", "/v3/profiles/sessions", payload, headers)
        res = conn.getresponse()
        data = res.read()
        decoded_data = data.decode("utf-8")
        response = json.loads(decoded_data)
        return response

    # nadeo token v1
    def level1(self, ticket):
        headers = {
            "Authorization": "ubi_v1 t=" + ticket
        }
        nadeo_accesstoken = requests.post(
            "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices", headers=headers
        )
        return nadeo_accesstoken.json()

    # nadeo token v2
    def level2(self, token):
        payload = {
            'audience': 'NadeoClubServices'
        }
        headers = {
            "Authorization": "nadeo_v1 t=" + token,
        }
        nadeo_services = requests.post(
            "https://prod.trackmania.core.nadeo.online/v2/authentication/token/nadeoservices", headers=headers, data=payload
        )
        return nadeo_services.json()

    def get_tickets(self):
        try:
            response_level0 = self.level0()
            response_level1 = self.level1(response_level0['ticket'])
            response_level2 = self.level2(response_level1['accessToken'])
        except:
            return "Couldnt get a response from apis"
        if response_level2:
            self.ticket = response_level2['accessToken']
            self.refresh_ticket = response_level2['refreshToken']
            return response_level2

    def get_new_refresh_ticket(self):
        url = "https://prod.trackmania.core.nadeo.online/v2/authentication/token/refresh"
        headers = {
            'Authorization': 'nadeo_v1 t=' + self.refresh_ticket
        }
        try:
            refresh_ticket = requests.post(url, headers=headers)
            return refresh_ticket.json()
        except:
            return 'Could not connect with api, try to use "get_ticket" before.'

    def get_player_info(self, player_id):
        url = "https://matchmaking.trackmania.nadeo.club/api/matchmaking/2/leaderboard/players?players[]=" + player_id
        headers = {
            'Authorization': 'nadeo_v1 t=' + self.ticket
        }
        try:
            player_info = requests.get(url, headers=headers)
            return player_info.json()
        except:
            return 'Could not connect with api and get player info.'
