import requests
url = 'https://www.just-whisky.co.uk/search'
data = {}
data['search'] = 'rosebank 31'
#data['submit'] = 'Submit'
response = requests.post(url, data=data)
print(response)
