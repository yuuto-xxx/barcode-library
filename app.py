from flask import Flask, render_template, redirect, request, url_for, session
import register_book
import db
import re


app = Flask(__name__)

@app.route("/") #学生ログイン
def login_page():
    db.test()
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

# @app.route("manager_top") #管理者ログイン後トップページ
# def manager_top():
#     if "user" in session:
#         return render_template("manager.html")
#     else:
#         return redirect('manager_login')

@app.route("/sign_up")
def sign_up():
    if "user" in session:
        return render_template('sign_up.html')
    else:
        return render_template('login.html', session="セッション有効期限切れです。")
        

@app.route("/student_register", methods=['POST']) #学生登録
def stu_register():
    stu_number = request.form.get("stu_number")
    name = request.form.get("name")
    course = request.form.get("")
    mail = request.form.get("mail")
    re_mail = request.form.get("re_mail")

@app.route("/book_register") #本の登録
def book_register():
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

# 管理者登録
@app.route("/manager_register")
def manager_register():
    return render_template("manager_register.html")
    # if "user" in session:
    #     return render_template("manager_register.html")
    # else:
    #     return render_template("login.html", session="セッション有効期限切れです。")

# 管理者登録結果
@app.route("/manager_register_result", methods=['POST'])
def manager_register_result():
    name = request.form.get("name")
    mail_first = request.form.get("mail_first")
    mail_second = request.form.get("mail_second")
    if mail_first == mail_second and mail_check(mail_first):
        salt = db.create_salt()
        pw = db.new_pw()
        result = db.manager_insert(name,mail_first,salt,pw)
        if result:
            event = "登録完了"
            return render_template("manager_register.html",event=event)
    else:
        error = "正しい形式で入力してください。"
        return render_template("manager_register.html",error=error)

# メールアドレスのバリエーションチェック
def mail_check(mail):
    pattren = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattren,mail)\
        and len(mail) <= 256 :
        return True
    else :
        return False

# パスワードのバリエーションチェック
def passwd_check(pw):
    if pw == None:
        return False
    if  len(pw)>=8 \
        and len(pw)<=64 \
        and re.search("[A-Z]",pw)\
        and re.search("[a-z]",pw)\
        and re.search("[0-9]",pw):
            return True
    else :
        return False

if __name__ == "__main__":
    app.run(debug=True)