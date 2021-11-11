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
    course = request.form.get("course")
    mail = request.form.get("mail")
    re_mail = request.form.get("re_mail")
    
# 本登録(カメラ)
@app.route('/book_register_camera')
def book_register_camera():
    return render_template("book_register_camera.html")

@app.route("/book_register_verification") #確認画面
def book_register_verification():
    isbn = request.args.get("isbn")
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
    quantity = request.args.get("quantity")
    book = request.args.getlist("book")
    book.append(quantity)
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


# パスワード忘れた方
@app.route('/forget_pw')
def forget_pw():
    return render_template("forget_pw.html")

# メール送信
@app.route('/forget_pw_2',methods=['POST'])
def forget_pw_2():
    mail = request.form.get('email')
    salt = db.search_student_salt(mail)
    # 1の場合は学生
    student_flg = 1
    # 学生アカウントの場合
    if salt:
        new_pw = db.new_pw()
        new_salt = db.create_salt()
        # 仮パスワードをアップデートしてメール送信
        # db.update_student(new_pw,new_salt)
        mail_send.mail_2(mail,new_pw,student_flg)
        return render_template('mail_result.html')
    else:
        salt = db.manager_search_salt(mail)
        # 管理者アカウントの場合
        if salt:
            new_pw = db.new_pw()
            new_salt = db.create_salt()
            student_flg = 0
            # 仮パスワードをアップデートしてメール送信
            # db.update_manger(new_pw,new_salt)
            mail_send.mail_2(mail,new_pw,student_flg)
            return render_template('mail_result.html')
        else:
            error = "登録していないメールアドレスです"
            return render_template('forget_pw.html',error=error)

# パスワードリセット(メール送信url) 
@app.route('/pw_reset')
def pw_reset():
    mail = request.args.get('mail')
    student_flg = request.args.get('student_flg')
    session["data"] = [mail,student_flg]
    return render_template('pw_reset.html')

# パスワードリセット(確認)
@app.route('/pw_reset_2',menthods=["POST"])
def pw_reset_2():
    if "data" in session:
        flg = session["data"][1]  
        mail = session["data"][0]
        pw = request.form.get("pw_first")
        pw_2 =  request.form.get("pw_2")
        pw_3 = request.form.get("pw_3")
        if pw_2 != pw_3:
            error = "パスワードとパスワード(確認)は一致していません"
            return render_template('pw_reset.html',error=error)
        if passwd_check(pw_2):
            error = "バリエーションエラー"
            return render_template('pw_reset.html',error=error)
        # 学生の場合
        if flg == 1:
            result = db.student_login(mail,pw)
            if result:
                # 学生パスワードリセット
                # result_2 = db.student_update(mail,pw_2)
                event = "パスワードリセット成功"
                return render_template('login.html',event=event)
        # 管理者の場合
        elif flg == 0:
            result = db.manager_login(mail,pw)
            if result:
                # 管理者パスワードリセット
                # result_2 = db.manager_update(mail,pw_2)
                event = "パスワードリセット成功"
                return render_template('login.html',event=event)

# 学生登録(一括)
def student_register_all():
    return render_template('student_register_all.html')



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

# 名前バリエーションチェック
def name_check(name):
    if name == None:
        return False
    if len(name)>0\
        and len(name)<=64:
        return True
    else :
        return False

# 学籍番号バリエーションチェック
def student_id_check(student_id):
    if student_id == None:
        return False
    if re.fullmatch('[0-9]+', student_id)\
        and len(student_id) == 7:
        return True
    else:
        return False

    
if __name__ == "__main__":
    app.run(debug=True)