import requests

URL = "http://127.0.0.1:5000/"



result = requests.post(URL + "/book/" + "?id=1", {"name": "book1", "price":10, "author":"author1"})
print("url is ", result.request.url)
print("body is ", result.request.body)
print("header is ", result.request.headers)
print("Status code is ", result.status_code)
print("POST result is ", result.json())


result = requests.get(URL + "/book/" + "?id=1")
print("url is ", result.request.url)
print("body is ", result.request.body)
print("header is ", result.request.headers)
print("Status code is ", result.status_code)
print("GET result is ", result.json())


result = requests.get(URL + "/book/" + "?id=1000")
print("url is ", result.request.url)
print("body is ", result.request.body)
print("header is ", result.request.headers)
print("Status code is ", result.status_code)
print("GET result is ", result.json())


for i in range(2, 10):
    print(f"{i} BOOK to create --------------")
    result = requests.post(URL + "/book/" + f"?id={i}", {"name": f"book{i}", "price":i, "author":f"author{i}"})
    print("url is ", result.request.url)
    print("body is ", result.request.body)
    print("header is ", result.request.headers)
    print("Status code is ", result.status_code)
    print("POST result is ", result.json())


for i in range(2, 10):
    print(f"{i} BOOK GET --------------")
    result = requests.get(URL + "/book/" + f"?id={i}")
    print("url is ", result.request.url)
    print("body is ", result.request.body)
    print("header is ", result.request.headers)
    print("Status code is ", result.status_code)
    print("GET result is ", result.json())

