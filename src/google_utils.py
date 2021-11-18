import requests


def get_google_user_data(access_token):
    return requests.get('https://www.googleapis.com/userinfo/v2/me?access_token=%s' % access_token).json()
