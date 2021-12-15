from ctypes import resize
from hashlib import new
from logging import error
from typing import Reversible
import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask.globals import g
from flask.sessions import SessionInterface
import register_book
import db
import re
import mail_send
import random
import string
import csv
from werkzeug.utils import secure_filename
import datetime as dt
from datetime import datetime, timedelta
import json
import pathlib

app = Flask(__name__)

# 秘密鍵
app.secret_key = "".join(random.choices(string.ascii_letters,k=256))
# upload_folder = './library_application/uploads/image/'
# app.config['UPLOAD_FOLDER'] = upload_folder

@app.route("/") #学生ログイン
def login_page():
    session = request.args.get("session")
    error = request.args.get("error")
    print(session)
    print(error)
    return render_template("login.html", session=session, error=error)

@app.route("/manager_login") #管理者ログイン
def manager_login():
    session = request.args.get("session")
    error = request.args.get("error")
    return render_template("manager_login.html", session=session, error=error)

#学生ログイン後トップページ
@app.route("/student_top", methods=["POST"]) 
def stu_top():
    mail = request.form.get("mail")
    password = request.form.get("password")
    result = db.student_login(mail,password)
    if result == None:
        error = "メールアドレス又はパスワードが間違っています"
        return render_template("login.html",session=error)
    #session(stu_number, name, password_flag,mail)
    session["user"] = (result[0],result[1],result[2],mail)
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

    if result == None:
        error = "メールアドレス又はパスワードが間違っています"
        return render_template("login.html",error=error)
    elif result[2]:
        student_flg = 1
        return render_template("first_login.html", student_flg=student_flg, mail=mail)
    else:
        renting_list = db.book_renting(result[0])
        detail_list = []
        for i in range(len(renting_list)):
            book_detail = db.book_detail(renting_list[i])
            detail_list.append(book_detail)
        print(detail_list)
        return render_template("stu_book_rent.html", detail_list=detail_list)

#自分が借りている一覧
@app.route("/stu_book_renting")
def stu_book_renting():
    if "user" in session:
        user = session["user"]
        stu_number = user[0]
        renting_list = db.book_renting(stu_number)
        detail_list = []
        for i in range(len(renting_list)):
            book_detail = db.book_detail(renting_list[i])
            detail_list.append(book_detail)
        return render_template("stu_book_rent.html", detail_list=detail_list)
    else:
        return redirect(url_for('login_page'))
    
#管理者ログイン後トップページ
@app.route("/manager_top", methods=['POST'])
def manager_top():
    mail = request.form.get("mail")
    password = request.form.get("password")
    result = db.manager_login(mail,password)
    
    session["user"] = (result[0],result[1],mail)
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    if result[1]: #password_flagの判定
        student_flg = 0
        return render_template("first_login.html", student_flg=student_flg, mail=mail)
    else:
        renting_list = db.student_renting()
        return render_template("manager_renting_stu.html", renting_list=renting_list)

#学生が借りている本の一覧(貸出一覧)
@app.route("/manager_renting_student")
def manager_renting():
    renting_list = db.student_renting()
    return render_template("manager_renting_stu.html", renting_list=renting_list)

#貸出一覧検索結果
@app.route("/manager_renting_search")
def renting_search():
    key = request.args.get("key")
    renting_list = db.student_renting_search(key)
    return render_template("manager_renting_stu.html", renting_list=renting_list)

#本の登録
@app.route("/book_register")
def book_register():
    return render_template("book_register.html")

# 本登録(カメラ)
@app.route('/book_register_camera')
def book_register_camera():
    return render_template("book_register_camera.html")

#本登録の確認画面
@app.route("/book_register_verification")
def book_register_verification():
    isbn = request.args.get("isbn")
    print(isbn)
    if len(isbn) <= 9:
        return "isbnを入力して下さい"
    else:
        json_data = register_book.get_book(isbn)
        if(json_data == None):
            error = "検索結果なし"
            return render_template("book_register_camera.html",error=error)
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
    book.append(quantity)
    db.book_register(book)
    return render_template("book_register_camera.html")

#　本手入力登録
@app.route("/manual_book_register")
def manual_book_register():
    return render_template('manual_book_register.html')    

@app.route("/manual_book_register_result", methods=['POST'])
def manual_book_register_result():
    print("pathlib:",pathlib.Path.cwd())
    file = request.files.get('file')
    if 'file' not in request.files:
        return "画像ファイルなし"
    file_name = secure_filename(file.filename)
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    publisher = request.form.get("publisher")
    release_day = request.form.get("release_day")
    quantity = request.form.get("quantity")
    img_url = os.path.join('./static/image/', file_name )
    print("パス:",os.path.exists('./static/image/'))
    file.save(img_url)
    book = [isbn, img_url, title, author, publisher, release_day, quantity]
    print(book)
    db.book_register(book)
    return render_template("book_register_camera.html")

#本を借りる
@app.route("/stu_camera_rent")
def stu_camera_rent():
    return render_template("stu_camera_rent.html")

#JSON作成
@app.route("/stu_book_rent")
def stu_book_rent():
    print("stu_book_rent実行")
    data = request.args.get("result")
    if data != None:
        result = db.book_detail(data)
        book = {
            "isbn": result[0],
            "title": result[2]
        }
        book_json = json.dumps(book, ensure_ascii=False)
    else:
        print("isbn読み込みエラー")

    return book_json

@app.route("/stu_book_rent_result")
def stu_book_rent_result():
    if "user" in session:
        user = session["user"]
        stu_number = user[0]
        isbn = request.args.get("isbn")
        isbn_list = isbn.split()
        db.rent_book(stu_number,isbn_list)
        renting_list = db.book_renting(user[0])
        detail_list = []
        for i in range(len(renting_list)):
            book_detail = db.book_detail(renting_list[i])
            detail_list.append(book_detail)
        print(detail_list)

        return render_template("stu_book_rent.html", detail_list=detail_list)
    else:
        return redirect(url_for('login_page'))

#本を返す
@app.route("/stu_camera_return")
def stu_camera_return():
    return render_template("stu_camera_return.html")

@app.route("/student_book_return")
def student_book_return():
    print("student_book_return実行")
    data = request.args.get("result")
    if data != None:
        result = db.book_detail(data)
        book = {
            "isbn": result[0],
            "title": result[2]
        }
        book_json = json.dumps(book, ensure_ascii=False)
    else:
        print("isbn読み込みエラー")

    return book_json

@app.route("/student_book_return_result")
def student_book_return_result():
    if "user" in session:
        user = session["user"]
        stu_number = user[0]
        isbn = request.args.get("isbn")
        isbn_list = isbn.split()
        db.book_return(stu_number, isbn_list)
        renting_list = db.book_renting(user[0])
        detail_list = []
        for i in range(len(renting_list)):
            book_detail = db.book_detail(renting_list[i])
            detail_list.append(book_detail)
        print(detail_list)

        return render_template("stu_book_rent.html", detail_list=detail_list)
    else:
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

#履歴
@app.route("/stu_book_history")
def stu_book_history():
    if "user" in session:
        user = session["user"]
        stu_number = user[0]
        history = db.book_history(stu_number)
        return render_template("stu_book_history.html", history=history)
    else:
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

#本の一覧(学生)
@app.route("/student_book_list")
def book_list():
    if "user" in session:
        book_list = db.book_list()
        tag = []
        rent_flag = []
        book_amount_list = []
        for i in range(len(book_list)):
            review_avg = 0
            review = db.book_review_score(book_list[i][0])
            review_score = 0
            review_count = 0
            for j in range(len(review)):
                review_score += review[j]
                review_count += 1
            try:
                if review_count == 0:
                    review_avg = 0
                else:
                    review_avg = review_score / review_count
            except Exception as e:
                review_avg = 0
                print(e)
            t = db.select_tag(book_list[i][0])
            book_list[i] = book_list[i] + (round(review_avg,1),)
            # print(review_avg)
            tag.append(t)
            amount_flag = db.select_amount(book_list[i][0])
            if amount_flag:
                if amount_flag[1] >= amount_flag[2]:
                    rent_flag.append("X")
                    book_amount_list.append(0)
                else :
                    rent_flag.append("O")
                    book_amount_list.append(int(amount_flag[2]-amount_flag[1]))
            else :
                rent_flag.append("O")
                book_amount_list.append(int(book_list[i][6]))
        return render_template("stu_book_list.html",book_list=book_list,tag=tag,rent_flag=rent_flag,book_amount_list=book_amount_list)
    else:
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

# 本の検索(学生)
@app.route("/stu_book_search")
def stu_book_search():
    if "user" in session:
        key = request.args.get("key")
        tag_flag = request.args.get("tag_flag")
        if tag_flag == "0":
            tag = []
            rent_flag = []
            result = db.stu_book_search(key)
            
            for i in range(len(result)):
                t = db.select_tag(result[i][0])
                tag.append(t)
            for i in range(len(result)):
                amount_flag = db.select_amount(result[i][0])
                print(amount_flag)
                print(result[i][0])
                
                if amount_flag:
                    if amount_flag[1] >= amount_flag[2]:
                        rent_flag.append("X")
                    else :
                        rent_flag.append("O")
                else :
                    rent_flag.append("O")
                print(rent_flag)

            for i in range(len(result)):
                review_avg = 0
                review = db.book_review_score(result[i][0])
                review_score = 0
                review_count = 0
                for j in range(len(review)):
                    review_score += review[j]
                    review_count += 1
                try:
                    if review_count == 0:
                        review_avg = 0
                    else:
                        review_avg = review_score / review_count
                except Exception as e:
                    review_avg = 0
                result[i] = result[i] + (review_avg,)
                # print("0",result)
        else :
            tag =[]
            result = db.tag_book_search(key)
            rent_flag = []
            for i in range(len(result)):
                t = db.select_tag(result[i][0])
                tag.append(t)
            for i in range(len(result)):
                t = db.select_tag(result[i][0])
                tag.append(t)
            for i in range(len(result)):
                review_avg = 0
                review = db.book_review_score(result[i][0])
                review_score = 0
                review_count = 0
                for j in range(len(review)):
                    review_score += review[j]
                    review_count += 1
                try:
                    if review_count == 0:
                        review_avg = 0
                    else:
                        review_avg = review_score / review_count
                except Exception as e:
                    review_avg = 0
                result[i] = result[i] + (review_avg,)
                amount_flag = db.select_amount(result[i][0])
                
                if amount_flag:
                    if amount_flag[1] >= amount_flag[2]:
                        rent_flag.append("X")
                    else :
                        rent_flag.append("O")
                else :
                    rent_flag.append("O")
            # print("1",result)
        if result !=[]:
            return render_template("stu_book_sreach.html",book_list=result,tag=tag,rent_flag=rent_flag)
        else :
            return redirect(url_for("book_list"))
    else :
        return redirect(url_for('login_page'))
#         <!-- {{redirect(url_for('book_detail'))}} -->


# 本の一覧(管理者)
@app.route("/manager_book_list")
def manager_book_list():
    if "user" in session:
        result = db.book_list()
        if result:
            return render_template("manager_book_list.html",book_list=result)
    else :
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

# 本の一覧(管理者検索)
@app.route("/delete_search")
def delete_search():
    if "user" in session:
        key = request.args.get("key")
        result = db.book_search(key)
        if result !=[]:
            return render_template("manager_book_list.html",book_list=result)
        else :
            return redirect(url_for("manager_book_list"))
    else :
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))


# 本情報変更
@app.route('/book_change')
def book_change():
    if "user" in session:
        book = request.args.getlist('book')
        return render_template("book_change.html",book=book)
    else :
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))


# 本の情報変更
@app.route('/book_change_main')
def book_change_main():
    if "user" in session:
        book_isbn = request.args.get('book')
        title = request.args.get('title')
        author = request.args.get('author')
        pub = request.args.get('pub')
        day = request.args.get('day')
        num = request.args.get('quantity')
        if num=='' or title==""or author==""or pub==""or day=="":
            max = request.args.get('max')
            tit = request.args.get('tit')
            aut = request.args.get('aut')
            p = request.args.get('p')
            d = request.args.get('d')
            result = db.book_change(book_isbn,tit,aut,p,d,max)
        else :
            if int(num) <= 0:
                result = db.book_delete_flag(book_isbn)
            else:
                result = db.book_change(book_isbn,title,author,pub,day,num)
        if result:
            return redirect(url_for('manager_book_list'))
        else :
            return render_template('book_change_main.html',error="error")
    else :
        return redirect(url_for("login_page",session="セッション有効期限切れです。"))

# 本削除
@app.route('/book_delete')
def book_delete():
    if "user" in session:
        book = request.args.getlist("book")
        print(book)
        # isbn,image,title,author,publisher,release_day,amount_max,book_delete_flag
        if book:
            # session["book"] = book
            return render_template("book_delete.html",book=book)
    else:
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

# 本削除
@app.route("/book_delete_main")
def book_delete_main():
    if "user" in session:
        isbn = request.args.get('isbn')
        max = request.args.get('max')
        max1 = int(max)
        quantity = request.args.get('quantity')
        quantity1 = int(quantity)
        # return render_template("book_delete_main.html",num=quantity)
        if quantity1 >= max1:
            result = db.book_delete_flag(isbn)
        else :
            result = db.book_delete_amount(isbn,quantity)
        if result:
            return redirect(url_for('manager_book_list'))
    else :
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

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
    visibility = 0
    return render_template("stu_register.html",visibility=visibility)

# def stu_register(list):
#     list = request.ar
#     return render_template("stu_register.html")
        
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
    student_list = db.student_list()
    return render_template("manager_stu_edit.html", student_list=student_list)

# 学生変更検索画面名前表示
@app.route("/manager_student_edit", methods=["POST"])
def manager_student_edit():
    name = request.form.get('name')
    if name_check(name):
        result = db.student_search_change(name)
    if result:
        print(result)
        # name,stu_number,mail
        return render_template("manager_stu_edit.html", name_list=result)
    else :
        error = "名前は存在しません"
        print("名前検索なし")
        return render_template("manager_stu_edit.html", error=error)

# 学生変更
@app.route("/stu_change")
def stu_change():
    stu_number = request.args.get('stu_number')
    result = db.student_search_change_result(stu_number)
    # mail,name,stu_number,course_name,year
    if result:
        visibility = 0
        return render_template("stu_change.html",result=result, visibility=visibility)

def stu_change(stu_number):
    result = db.student_search_change_result(stu_number)
    print("りだいれくと")
    visibility = 1
    if result:
        return render_template("stu_change.html",result=result, visibility=visibility)

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
            print("学生変更成功")
            return redirect(url_for('stu_change', stu_number=stu_number))
        else :
            print("失敗")
    else :
        error = "正しい形式で入力してください"
        print("学生変更エラー(python)バリエーションチェックエラー606")
        # return redirect(url_for('stu_change', error=error))

# 学生削除検索
@app.route("/manager_stu_delete")
def manager_stu_delete():
    return render_template("manager_stu_delete.html")

# 学生削除検索結果
@app.route("/manager_student_delete",methods=["POST"])
def manager_student_delete():
    name = request.form.get('name')
    if name_check(name):
        result = db.student_search_change(name)
    if result:
        return render_template("manager_stu_delete.html", name_list=result)
    else :
        error="名前は存在しません"
        return render_template("manager_stu_delete.html",error=error)

@app.route("/manager_student_delete_detail")
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
        return render_template("manager_stu_delete.html")
    else :
        print("削除失敗")
        return render_template("manager_stu_delete.html")

# 管理者一覧画面
@app.route("/manager_manager_view")
def manager_manager_view():
    manager_all = db.select_manager_all()
    # name,mail
    if manager_all:
        return render_template("manager_manager_view.html", list=manager_all)
    else :
        error="管理者select_allエラー"
        return render_template("manager_manager_view.html", error=error)

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
        mail_send.forget_pw_mail(mail, new_pw, student_flg,new_salt)
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
    if "user" in session:
        return render_template('pw_reset.html')
    else :
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

# パスワードリセット(確認)
@app.route('/pw_reset_2',methods=["POST"])
def pw_reset_2():
    if "user" in session:
        mail = session["user"][3]
        password = request.form.get('password')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if password == password1:
            error = "過去のパスワードと新規パスワードは同じです"
            return redirect(url_for('pw_reset',error=error))        
        if password1 != password2:
            error = "パスワードとパスワード(確認)は一致していません"
            return redirect(url_for('pw_reset',error=error))
        if passwd_check(password1):
            result = db.student_login(mail,password)
            print(result)
            if result:
                result2 = db.pw_reset(mail,password1)
                if result2:
                    return redirect(url_for('stu_book_renting'))
                else :
                    return redirect(url_for('pw_reset',error="登録失敗"))
            else :
                return redirect(url_for('pw_reset',error="アカウントが存在しません"))
        else :
            error = "バリエーションエラー"
            return redirect(url_for('pw_reset',error=error))
    else :
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

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
            print(error)
    elif stu_flg == "0":
        if new_password == re_password:
            salt = db.manager_search_salt(mail)
            hashed_pw = db.hash_pw(new_password,salt)
            db.password_update_manager(mail,hashed_pw)
            return render_template("manager_renting_stu.html")
        else:
            error = "パスワード不一致"
    else:
        return "student_flgエラー"

# 学生登録(一括)
@app.route('/student_register_all')
def student_register_all():
    return render_template('manager_group_regist.html')

# 学生登録(一括)登録処理
@app.route('/student_all_file_result',methods=['POST'])
def student_all_file_2():
    file = request.files['fileinput']
    list = []
    list_true = []
    list_true2 = []
    list_false = []
    with open ('./barcode-library/uploads/'+secure_filename(file.filename),encoding="Shift_JIS") as f:
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
        pw=db.new_pw()
        # pw = "Morijyobi111"
        result = db.student_register(stu_id,mail,name,course,course_year,pw)
        # stu_number,mail,name,course_id,year,pw
        if result:
            mail_send.mail(mail,pw)
        else :
            list_true2.append(n)
            list_false.append(n)
    for i in list_true2:
        list_true.remove(i)

    return render_template('manager_group_regist_result.html',list_true=list_true,list_false=list_false)

# 学生進級
@app.route('/manager_promotion')
def manager_promotion():
    if "user" in session:
        # mail,day
        result = db.last_promotion_history()
        flagnum = 0
        if result == []:
            flagnum = 1
        # id,name,course_name
        student_list = db.promotion_student_list()
        today = dt.datetime.today()
        time = today - result[4]
        print(time.days)
        return render_template('manager_promotion.html',result=[result[1],result[4]],student_list=student_list,flagnum=flagnum)
    else :
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

@app.route('/manager_promotion_result')
def manager_promotion_result():
    if "user" in session:
        mail = session["user"][2]
        result = db.manager_promotion()
        result2 = db.manager_promotion_delete()
        result3 = db.promotion_history(mail)
        if result and result2 and result3:
            return redirect(url_for('manager_promotion',event="進級完了"))
        else :
            return "error"
    else :
        return redirect(url_for('login_page',session="セッション有効期限切れです。"))

#　レビュー画面
@app.route('/review')
def review():
    if "user" in session:
        user = session["user"]
        stu_number = user[0]
        name = user[1]
        isbn = request.args.get("isbn")
        return render_template("stu_review_book.html", stu_number=stu_number, name=name, isbn=isbn)
    else:
        redirect(url_for('login_page',session="セッション有効期限切れです。"))

@app.route("/register_review", methods=["POST"])
def register_review():
    if "user" in session:
        user = session["user"]
        stu_number = user[0]

        isbn = request.form.get("isbn")
        anonymous = request.form.get("anonymous") #匿名
        star = request.form.get("star")
        review = request.form.get("review")
        print("匿名表示:" , anonymous)
        print("レビュー内容:" , review)

        if len(review) == 0:
            if anonymous == None:
                anonymous = False
            book_review = [isbn, stu_number, star, anonymous]
            db.book_review_star(book_review)
            return book_detail(isbn)
        else:
            if anonymous == None:
                anonymous = 0
            book_review = [isbn, stu_number, review, star, anonymous]
            db.book_review(book_review)
            return book_detail(isbn)
    else:
        return redirect("/", session=session)

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

# 本詳細情報(レビューも)
@app.route("/book_detail")
def book_detail():
    isbn = request.args.get("book")
    book_amount = request.args.get("book_amount")
    book = db.book_detail(isbn)
    review = db.book_show_review(isbn)
    tag_pd,tag = db.tag_pull_down(isbn)
    return render_template("book_detail.html", book=book, review=review,tag=tag,tag_pd=tag_pd,book_amount=book_amount)

def book_detail(isbn):
    book = db.book_detail(isbn)
    review = db.book_show_review(isbn)
    tag_pd,tag = db.tag_pull_down(isbn)
    amount_flag = db.select_amount(isbn)
    if amount_flag:
        if amount_flag[1] >= amount_flag[2]:
            book_amount = 0
        else :
            book_amount = (int(amount_flag[2]-amount_flag[1]))
    else :
            book_amount = (int(book[6]))

    return render_template("book_detail.html", book=book,tag=tag,tag_pd=tag_pd,book_amount=book_amount, review=review)

def book_detail(isbn,tag_name):
    book = db.book_detail(isbn)
    review = db.book_show_review(isbn)
    tag_pd,tag = db.tag_pull_down(isbn)
    amount_flag = db.select_amount(isbn)
    if amount_flag:
        if amount_flag[1] >= amount_flag[2]:
            book_amount = 0
        else :
            book_amount = (int(amount_flag[2]-amount_flag[1]))
    else :
            book_amount = (int(book[6]))

    return render_template("book_detail.html", book=book,tag=tag,tag_pd=tag_pd,book_amount=book_amount, review=review,tag_name=tag_name)

# タグ追加
@app.route("/tag_add",methods=["POST"])
def tag_add():
    isbn = request.form.get("book_number")
    tag_name = request.form.get("tag")
    print(tag_name)
    tag_search = db.tag_result(isbn,tag_name)
    if tag_search:
        return book_detail(isbn,tag_name+"タグが存在します。")
    result =  db.tag_add_book(isbn,tag_name)
    if result:
        return book_detail(isbn,tag_name+"タグを追加しました")
    else :
        return "@tag_add_error"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)