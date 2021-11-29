from ctypes import resize
from hashlib import new
from logging import error
from flask import Flask, render_template, redirect, request, url_for, session
from flask.globals import g
import register_book
import db
import re
import mail_send
import random
import string
import csv
from werkzeug.utils import secure_filename
import datetime as dt
from datetime import timedelta

app = Flask(__name__)

# 秘密鍵
app.secret_key = "".join(random.choices(string.ascii_letters,k=256))

@app.route("/") #学生ログイン
def login_page():
    session = request.args.get("session")
    error = request.args.get("error")
    return render_template("login.html")

@app.route("/manager_login") #管理者ログイン
def manager_login():
    # テストユーザ:メール→test@test.jp パスワード→plA810nG
    session = request.args.get("session")
    error = request.args.get("error")
    return render_template("manager_login.html", session=session, error=error)

#学生ログイン後トップページ
@app.route("/student_top", methods=["POST"]) 
def stu_top():
    mail = request.form.get("mail")
    password = request.form.get("password")
    result = db.student_login(mail,password)
    session["mail"] = mail
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    print(result)
    if result[1]:
        student_flg = 1
        return render_template("first_login.html", student_flg=student_flg, mail=mail)
    else:
        return render_template("stu_book_rent.html")
    

#管理者ログイン後トップページ
@app.route("/manager_top", methods=['POST'])
def manager_top():
    mail = request.form.get("mail")
    password = request.form.get("password")
    result = db.manager_login(mail,password)
    print(result[1])
    if result[1]: #password_flagの判定
        student_flg = 0
        return render_template("first_login.html", student_flg=student_flg, mail=mail)
    else:
        return render_template("manager_renting_stu.html")

#本の登録
@app.route("/book_register")
def book_register():
    return render_template("book_register.html")

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
            try:
                sales_date = dt.datetime.strptime(sales_date,"%Y年%m月")
            except ValueError:
                sales_date = dt.datetime.strptime(sales_date,"%Y年%m月%d日頃")
            sales_date = sales_date.strftime("%Y/%m/%d")
            book = [isbn, large_image_url, title, author, publisher, sales_date]
            return render_template('book_register.html', book=book)

@app.route("/book_register_result") #登録リザルト
def book_register_result():
    quantity = request.args.get("quantity")
    book = request.args.getlist("book")
    print(book[5])
    book.append(quantity)
    db.book_register(book)
    return "登録完了"
    # return render_template("",book=book)

@app.route("/student_rent_book")
def rent_book():
    return render_template("")

#本の一覧
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
            mail_send.mail(mail_first,pw)
            return render_template("manager_register.html",event=event)
    else:
        error = "正しい形式で入力してください。"
        return render_template("manager_register.html",error=error)


#学生登録
@app.route("/stu_register")
def stu_register():
    return render_template("stu_register.html")
        
@app.route("/student_register", methods=['POST']) 
def student_register():
    stu_number = request.form.get("stu_number")
    name = request.form.get("name")
    course = request.form.get("course")
    year = request.form.get("year")
    mail = request.form.get("mail")
    re_mail = request.form.get("re_mail")
    if mail == re_mail and mail_check(mail) \
     and mail not in db.search_student_mail() \
     and len(stu_number) == 7 and stu_number.isdigit() \
     and len(name) <= 64 :
        pw = db.new_pw()
        result = db.student_register(stu_number, mail, name, course, year, pw)
        if result:
            event = "登録成功"
            mail_send.mail(mail,pw) #新規登録用メールメソッド
            return render_template("stu_register.html")
            # return render_template("stu_register.html",event=event,course_list=session['course_list'],grade_list=session['grade_list'])
        else :
            event = "登録失敗"
            return render_template("stu_register.html", event=event)
            # return render_template("stu_register.html",event=event,course_list=session['course_list'],grade_list=session['grade_list'])
    else :
        error = "正しい形式で入力してください"
        return render_template("stu_register.html", error=error)
        # return render_template("student_register.html",error=error,course_list=session['course_list'],grade_list=session['grade_list'])

# 学生変更検索画面
@app.route("/manager_stu_edit")
def manager_stu_edit():
    return render_template("manager_stu_edit.html")

# 学生変更検索画面名前表示
@app.route("/manager_student_edit",methods=["POST"])
def manager_student_edit():
    name = request.form.get('name')
    if name_check(name):
        result = db.student_search_change(name)
    if result:
        len1 = len(result)
        # name,stu_number,mail
        return render_template("manager_stu_edit.html",name_list=result,len=len1)
    else :
        error = "名前は存在しません"
        return render_template("manger_stu_edit.html",error=error)

# 学生変更
@app.route("/stu_change")
def stu_change():
    stu_number = request.args.get('stu_number')
    result = db.student_search_change_result(stu_number)
    # mail,name,stu_number,course_name,year
    if result:
        return render_template("stu_change.html",result=result)

# 学生変更確認
@app.route("/student_change",methods=["POST"])
def student_change():
    name = request.form.get('name')
    stu_number = request.form.get('stu_number')
    course = request.form.get('course')
    max_year = db.search_max_year(course)
    year = request.form.get('year')
    mail = request.form.get('mail')
    re_mail = request.form.get('re_mail')
    if name_check(name) and student_id_check(stu_number) and \
     mail==re_mail and mail_check(mail) and int(year)<=int(max_year):
        result = db.stu_change_update(stu_number,name,mail,course,year)
        if result:
            event = "変更成功"
            return render_template("stu_change",event=event)
        else :
            print("失敗")
    else :
        error = "正しい形式で入力してください"
        return render_template("stu_change",error=error)

# 学生削除検索
@app.route("/manager_stu_delete")
def manager_stu_delete():
    return render_template("manager_stu_delete.html")

# 学生削除検索結果
@app.route("/manager_stu_delete",methods=["POST"])
def manager_stu_delete():
    name = request.form.get('name')
    if name_check(name):
        result = db.student_search_change(name)
    if result:
        len1 = len(result)
        return render_template("manager_stu_delete.html",name_list=result,len=len1)
    else :
        error="名前は存在しません"
        return render_template("manager_stu_delete.html",error=error)

# 学生削除
@app.route("/stu_delete")
def stu_delete():
    stu_number = request.args.get('stu_number')
    result = db.student_search_change_result(stu_number)
    # mail,name,stu_number,course_name,year
    if result:
        return render_template("stu_delete.html",result=result)

# 学生削除処理
@app.route("/student_delete",methods=["POST"])
def student_delete():
    stu_number = request.form.get('stu_number')
    result = db.delete_flag(stu_number)
    if result:
        event="削除成功"
        return render_template("stu_delete.html",event=event)
    else :
        error="削除失敗"
        return render_template("stu_delete.html",error=error)

# 管理者一覧画面
@app.route("/manager_manager_view")
def manager_manager_view():
    manager_all = db.select_manager_all()
    # name,mail
    if manager_all:
        len1 = len(manager_all)
        return render_template("manager_manager_view.html",list=manager_all,len=len1)
    else :
        error="管理者select_allエラー"
        return render_template("manager_manager_view.html",error=error)

# 管理者削除
@app.route("/manager_delete_result")
def manager_delete_result():
    mail = request.args.get("mail")
    result = db.manager_delete_flag(mail)
    manager_all = db.select_manager_all()
    if result:
        event="削除成功"
        return render_template("manager_delete_result.html",event=event,list=manager_all)
    else :
        error="削除失敗"
        return render_template("manager_manager_view.html",error=error)

# パスワード忘れた方
@app.route('/forget_pw')
def forget_pw():
    return render_template("forget_pw.html")

# メール送信(パスワードを忘れた人用メソッド)
@app.route('/forget_pw_2',methods=['POST'])
def forget_pw_2():
    mail = request.form.get('email')
    if mail_check(mail):
        error="メールアドレスの形式は間違っています"
        return render_template("forget_pw.html",error=error)
    salt = db.search_student_salt(mail)
    # 1の場合は学生
    student_flg = "1"
    # 学生アカウントの場合
    if salt:
        new_pw = db.new_pw()
        new_salt = db.create_salt()
        # 仮パスワードをアップデートしてメール送信
        db.update_student(mail, new_pw, new_salt)
        mail_send.forget_pw_mail(mail, new_pw, student_flg)
        return render_template('pw_change.html', student_flg=student_flg,salt=new_salt,mail=mail)
    else:
        salt = db.manager_search_salt(mail)
        # 管理者アカウントの場合
        if salt:
            new_pw = db.new_pw()
            new_salt = db.create_salt()
            student_flg = "0"
            # 仮パスワードをアップデートしてメール送信
            db.update_manager(mail, new_pw, new_salt)
            mail_send.forget_pw_mail(mail,new_pw,student_flg)
            return render_template('pw_change.html', student_flg=student_flg, new_salt=new_salt, mail=mail)
        else:
            error = "登録されていないメールアドレスです"
            return render_template('forget_pw.html',error=error)
#パスワード変更
@app.route("/pw_change", methods=["POST"])
def pw_change():
    temporary_password = request.form.get("temporary_password")
    password = request.form.get("new_password")
    re_password = request.form.get("re_password")
    flg = request.form.get("student_flg")
    salt = request.form.get("new_salt")
    mail = request.form.get("mail")
    print(flg)
    print(mail)

    if flg == "1":
        stu_tem_pass = db.stu_search_temporary_password(mail)
        if temporary_password == stu_tem_pass:
            if password == re_password:
                db.update_student(mail,password,salt)
                return render_template("login.html")
            else:
                error = "再入力パスワードが間違っています"
                return render_template("pw_change.html",error=error)
        else:
            error = "仮パスワードが間違っています"
            return render_template("pw_change.html",error=error)
    elif flg == "0":
        manager_tem_pass = db.search_temporary_password(mail)
        if temporary_password == manager_tem_pass:
            if password == re_password:
                hash_pw = db.hash_pw(password,salt)
                db.update_manager(mail,hash_pw,salt)
                return render_template("login.html")
            else:
                error = "再入力パスワードが間違っています"
                return render_template("pw_change.html", error=error)
        else:
            error = "仮パスワードが間違っています"
            return render_template("pw_change.html", error=error)
    else:
        return "student_flgエラー"
    

# パスワードリセット(メール送信url) 
@app.route('/pw_reset')
def pw_reset():
    mail = request.args.get('mail')
    student_flg = request.args.get('student_flg')
    session["data"] = [mail,student_flg]
    return render_template('pw_reset.html')

# パスワードリセット(確認)
@app.route('/pw_reset_2',methods=["POST"])
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

#初回ログイン時パスワード変更
@app.route("/first_login", methods=["POST"])
def first_login():
    new_password = request.form.get("new_password")
    re_password = request.form.get("re_password")
    stu_flg = request.form.get("student_flg")
    mail = request.form.get("mail")

    if stu_flg == "1":
        if new_password == re_password:
            salt = db.search_student_salt(mail)
            hashed_pw = db.hash_pw(new_password,salt)
            db.password_update_student(mail,hashed_pw)
            return render_template("stu_book_rent.html")
        else:
            error = "パスワード不一致"
    elif stu_flg == "0":
        if new_password == re_password:
            salt = db.manager_search_salt(mail)
            hashed_pw = db.hash_pw(new_password,salt)
            db.password_update_manager(mail,hashed_pw)
            return render_template("manager_renting_stu.html")
        else:
            error = "パスワード不一致"
    else:
        "student_flgエラー"


# 学生登録(一括)
@app.route('/student_register_all')
def student_register_all():
    return render_template('student_register_all.html')

# 学生登録(一括)テンプレートを表示
@app.route('/student_all_file',methods=['POST'])
def student_all_file():
    file = request.files['file']
    list = []
    with open ('./barcode-library/uploads/'+secure_filename(file.filename)) as f:
        for line in csv.reader(f):
            list.append(line)
    return render_template('student_register_all.html',list=list)

# 学生登録(一括)登録処理
@app.route('/student_all_file_result',methods=['POST'])
def student_all_file_2():
    file = request.files['file']
    list = []
    list_true = []
    list_false = []
    with open ('./barcode-library/uploads/'+secure_filename(file.filename)) as f:
        for line in csv.reader(f):
            list.append(line)
    del list[0]
    for i in list:
        if name_check(i[0]) and student_id_check(i[1]) and \
         i[0] not in db.search_student_mail() and \
         mail_check(i[4]) and int(i[3])>=1 and int(i[3])<=4 and\
         int(i[2])>=1 and int(i[2])<=10 :
            list_true.append(i)
        else :
            list_false.append(i)
    for n in list_true:
        name = n[0]
        stu_id = n[1]
        course = n[2]
        course_year = n[3]
        mail = n[4]
        result = db.student_register(stu_id,mail,name,course,course_year)
        if not result:
            list_false.append(n)
    return render_template('student_all_file_result.html',list_true=list_true,list_false=list_false)
  
#　レビュー画面
@app.route('/review')
def review():
    return render_template("stu_review_book.html")

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

#　本詳細情報
@app.route("/book_detail")
def book_detail():
    return render_template("book_detail.html")    

if __name__ == "__main__":
    app.run(debug=True)