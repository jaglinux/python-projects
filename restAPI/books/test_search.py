import requests

URL = "http://127.0.0.1:5000/"

result = requests.get(URL + "/book/search" + "?price=5&size=100")
print(result.json())
