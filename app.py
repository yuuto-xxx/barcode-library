from flask import Flask, render_template, redirect, request, url_for, session

# import register_book

app = Flask(__name__)

@app.route("/") #学生ログイン
def login_page():
    session = request.args.get("session")
    error = request.args.get("error")
    return render_template("login.html", session=session, error=error)

@app.route("/manager_login") #管理者ログイン
def manager_login():
    session = request.args.get("session")
    error = request.args.get("error")
    return render_template("manager_login.html", session=session, error=error)

@app.route("/student_top") #学生ログイン後トップページ
def stu_top():
    if "user" in session:
        return render_template("stu_top.html")
    else:
        return render_template("login.html", session="セッション有効期限切れです。")

@app.route("/register_student") #学生登録
def stu_register():
    if "user" in session:
        return render_template("")
    else:
        return render_template("login.html", session="セッション有効期限切れです。")


@app.route("/register_book") #本の登録
def register_book():
    code = request.args.get["isbn"]
    print(code) #テスト
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

@app.route("/sign_up")
def sign_up():
    return render_template('sign_up.html')

if __name__ == "__main__":
    app.run(debug=True)