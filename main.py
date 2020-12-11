import requests

r = requests.get('https://xkcd.com/1906')
r.status_code   #200 means 'OK'

