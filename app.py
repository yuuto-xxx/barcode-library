from hashlib import new
from flask import Flask, render_template, redirect, request, url_for, session
from flask.globals import g
import register_book
import db
import re
import mail_send
import random
import string

app = Flask(__name__)

# 秘密鍵
app.secret_key = "".join(random.choices(string.ascii_letters,k=256))

@app.route("/") #学生ログイン
def login_page():
    session = request.args.get("session")
    error = request.args.get("error")
    return render_template("login.html", session=session, error=error)

@app.route("/manager_login") #管理者ログイン
def manager_login():
    # テストユーザ:メール→test@test.jp パスワード→plA810nG
    session = request.args.get("session")
    error = request.args.get("error")
    return render_template("manager_login.html", session=session, error=error)

@app.route("/student_top") #学生ログイン後トップページ
def stu_top():
    return render_template("stu_top.html")

@app.route("/manager_top", methods=['POST']) #管理者ログイン後トップページ
def manager_top():
    mail = request.form.get("mail")
    password = request.form.get("password")
    result = db.manager_login(mail,password)
    print(result[0])
    return render_template("manager.html")

@app.route("/sign_up")
def sign_up():
    return render_template("sign_up.html")
    # if "user" in session:
    #     return render_template('sign_up.html')
    # else:
    #     return render_template('login.html', session="セッション有効期限切れです。")
        

@app.route("/student_register", methods=['POST']) #学生登録
def stu_register():
    stu_number = request.form.get("stu_number")
    name = request.form.get("name")
    course = request.form.get("")
    mail = request.form.get("mail")
    re_mail = request.form.get("re_mail")

@app.route("/book_register") #本の登録
def book_register():
    return render_template("book_register.html")

# 本登録(カメラ)
@app.route('/book_register_camera')
def book_register_camera():
    return render_template("book_register_camera.html")

@app.route("/book_register_verification") #確認画面
def book_register_verification():
    isbn = request.args.get("isbn")
    print(isbn) #テスト
    if len(isbn) <= 9:
        return "isbnを入力して下さい"
    else:
        json_data = register_book.get_book(isbn)
        if(json_data == None):
            print("jsonなし")
            return "検索結果なし"
        else:
            large_image_url = json_data["largeImageUrl"]
            title = json_data["title"]
            author = json_data["author"]
            publisher = json_data["publisherName"]
            sales_date = json_data["salesDate"]
            book = [isbn, large_image_url, title, author, publisher, sales_date]
            return render_template('book_register.html', book=book)

@app.route("/book_register_result") #登録リザルト
def book_register_result():
    # quantity = request.args.get("") #数量
    quantity = request.args.get("quantity")
    book = request.args.getlist("book")
    book.append(quantity)
    print(book)
    db.book_register(book)
    return "登録完了"
    # return render_template("",book=book)

@app.route("/student_rent_book")
def rent_book():
    return render_template("")

@app.route("/student_book_list")
def book_list():
    book_list = db.book_list()
    print(book_list)
    return render_template("stu_book_list.html",book_list=book_list)


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
    mail_first = request.form.get("mail")
    mail_second = request.form.get("re_mail")
    if mail_first == mail_second and mail_check(mail_first):
        salt = db.create_salt()
        pw = db.new_pw()
        print("パスワード:", pw)
        result = db.manager_insert(mail_first,name,pw,salt)
        if result:
            event = "登録完了"
            # mail_send(mail_first,pw)
            return render_template("manager_register.html",event=event)
    else:
        error = "正しい形式で入力してください。"
        return render_template("manager_register.html",error=error)

# 学生登録(個人)
@app.route("/student_register")
def student_register():
    return render_template("sign_up.html")
    # if "user" in session:
    #     return render_template("manager_register.html")
    # else:
    #     return render_template("login.html", session="セッション有効期限切れです。")


# 学生登録結果(個人)
@app.route("/student_register_result", methods=['POST'])
def student_register_result():
    name = request.form.get("name")
    student_id = request.form.get("student_id")
    course = request.form.get("course")
    grade = request.form.get("grade")
    print(grade)
    mail_first = request.form.get("mail_first")
    mail_second = request.form.get("mail_second")
    if mail_first == mail_second and mail_check(mail_first) \
     and len(student_id) == 7 and student_id.isdigit() \
     and len(name) <= 64 :
        salt = db.create_salt()
        pw = db.new_pw()
        result = db.student_register(mail_first,name,student_id,course,grade,pw,salt)
        if result:
            event = "登録成功"
            # mail_send(mail_first,pw)
            return render_template("student_register.html",event=event,course_list=session['course_list'],grade_list=session['grade_list'])
        else :
            event = "登録失敗"
            return render_template("student_register.html",event=event,course_list=session['course_list'],grade_list=session['grade_list'])
    else :
        error = "正しい形式で入力してください"
        return render_template("student_register.html",error=error,course_list=session['course_list'],grade_list=session['grade_list'])


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

# パスワード忘れた方
@app.route('/forget_pw')
def forget_pw():
    return render_template("forget_pw.html")

#　レビュー画面
@app.route('/review')
def review():
    return render_template("review.html")
    
if __name__ == "__main__":
    app.run(debug=True)