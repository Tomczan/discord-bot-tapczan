import requests
import base64
import http.client


def level0_uplay_token():
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
    return response['ticket']


def level1_nadeo_token(token):
    headers = {
        "Authorization": "ubi_v1 t=" + token
    }
    nadeo_accesstoken = requests.post(
        "https://prod.trackmania.core.nadeo.online/v2/authentication/token/ubiservices", headers=headers
    )
    return nadeo_accesstoken.json()


def level2_nadeo_token(token):
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
