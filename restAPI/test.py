import requests

URL = "http://127.0.0.1:5000/"



result = requests.post(URL + "/video/" + "?id=1", {"name": "jag", "views":10, "likes":100})
print("url is ", result.request.url)
print("body is ", result.request.body)
print("header is ", result.request.headers)
print("Status code is ", result.status_code)
print("POST result is ", result.json())

input()

result = requests.get(URL + "/video/" + "?id=1")
print("url is ", result.request.url)
print("body is ", result.request.body)
print("header is ", result.request.headers)
print("Status code is ", result.status_code)
print("GET result is ", result.json())

print("-------------FAIL----------------------------")
input()

result = requests.get(URL + "/video/" + "?id=1000")
print("url is ", result.request.url)
print("body is ", result.request.body)
print("header is ", result.request.headers)
print("Status code is ", result.status_code)
print("GET result is ", result.json())

input()

result = requests.post(URL + "/video/" + "?id=1", {"name": "jag", "views":10, "likes":100})
print("url is ", result.request.url)
print("body is ", result.request.body)
print("header is ", result.request.headers)
print("Status code is ", result.status_code)
print("POST result is ", result.json())








# python .\test.py
# url is  http://127.0.0.1:5000//video/1
# body is  name=jag&views=10&likes=100
# header is  {'User-Agent': 'python-requests/2.28.2', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive', 'Content-Length': '27', 'Content-Type': 'application/x-www-form-urlencoded'}
# POST result is  {'data': {'name': 'jag', 'likes': 100, 'views': 10}}
# url is  http://127.0.0.1:5000//video/1
# body is  None
# header is  {'User-Agent': 'python-requests/2.28.2', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}
# GET result is  {'name': 'jag', 'likes': 100, 'views': 10}
