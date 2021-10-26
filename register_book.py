import requests
import requests_cache

RAKUTEN_BOOKS_API_URL = "https://app.rakuten.co.jp/services/api/BooksBook/Search/20170404"
RAKUTEN_APP_ID = "1067663368120859116"

def get_book(isbn):
  print("book_search呼出し:" + isbn)
  with requests_cache.disabled():
    requests_cache.clear()
    response = ""
    response = requests.get("{}?applicationId={}&isbn={}".format(RAKUTEN_BOOKS_API_URL, RAKUTEN_APP_ID, isbn))

    print(response.status_code)

    if response.status_code != requests.codes.ok:
      print("Requests failed")
      return None
    elif response.json()["count"] == 0:
      print("No book found: isbn {}".format(isbn))
    else:
      print("Book found: {}".format(response.json()["Items"][0]["Item"]))
      json_data = response.json()["Items"][0]["Item"]
      return json_data
