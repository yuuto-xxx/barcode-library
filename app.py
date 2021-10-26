from logging import debug
from flask import Flask, render_template, redirect, request, url_for, session

import register_book

app = Flask(__name__)

@app.route("/login")
def login_page():
    session = request.args.get("session")
    error = request.args.get("error")
    return render_template("login.html",session=session,error=error)



@app.route("/register_book")
def register_book():
    code = request.args.get["isbn"]
    print(code)
    if len(code) >= 12:
        return "isbnを入力して下さい"
    else:
        json_data = register_book.get_book(code)
        if(json_data == None):
            print("jsonなし")
            return "検索結果なし"
        else:
            title = json_data["title"]
            author = json_data["author"]
            large_image_url = json_data["largeImageUrl"]
            sales_date = json_data["salesDate"]
            return render_template('isbn.html', code=code, title=title, author=author, large_image_url=large_image_url, sales_date=sales_date)    

if __name__ == "__main__":
    app.run(debug=True)