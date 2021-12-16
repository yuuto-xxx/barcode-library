from typing import Text
import psycopg2
import string
import random
import hashlib
import os
import urllib.parse
import datetime

from requests.api import get

os.environ["DATABASE_URL"] = "postgres://sudfwfyugnjfdf:46a5575767a9c88ebcb1930e8afe9c557df8911a3b4021ce902a500ba47a4e8b@ec2-23-23-199-57.compute-1.amazonaws.com:5432/d146sdrtncr1rm"

# 管理者の新規登録
def manager_insert(mail,name,pw,salt):
    conn = get_connection()
    cur = conn.cursor()
    sql = "INSERT INTO manager VALUES(%s,%s,%s,%s)"
    hashed_pw = hash_pw(pw,salt)
    try:
        cur.execute(sql,(mail,name,hashed_pw,salt))
    except Exception as e:
        print("SQL実行に失敗：", e)
    
    conn.commit()
    cur.close()
    conn.close()
    
    return True

# 学生の新規登録(個人)
def student_register(stu_number,mail,name,course_id,year,pw):
    conn = get_connection()
    cur = conn.cursor()
    salt = create_salt()
    sql = "INSERT INTO student VALUES(%s,%s,%s,%s,%s,%s,%s)"
    hashed_pw = hash_pw(pw,salt)
    try:
        cur.execute(sql,(stu_number,mail,name,hashed_pw,salt,course_id,year))
        print(hashed_pw)
    except Exception as e:
        print("SQL実行に失敗：", e)
        return False
    
    conn.commit()
    cur.close()
    conn.close()
    
    return True

# パスワードリセット(学生ログイン後)
def pw_reset(mail,password):
    conn = get_connection()
    cur = conn.cursor()
    salt = create_salt()
    sql = "update student set password=%s,salt=%s where mail=%s"
    hashed_pw = hash_pw(password,salt)
    try:
        cur.execute(sql,(hashed_pw,salt,mail,))
        print(hashed_pw)
    except Exception as e:
        print("SQL実行に失敗：", e)
        return False
    
    conn.commit()
    cur.close()
    conn.close()
    
    return True

# ソルトの新規作成
def create_salt():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

# パスワードの新規作成
def new_pw():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# パスワードとソルトのハッシュ
def hash_pw(pw,salt):
    b_pw = bytes(pw,"utf-8")
    b_salt = bytes(salt,"utf-8")

    hash_pw = hashlib.pbkdf2_hmac("sha256",b_pw,b_salt,1000).hex()

    return hash_pw

def manager_login(mail, password): #管理者のログイン
    salt = manager_search_salt(mail)

    if salt == None:
        return None

    b_pw = bytes(password,"utf-8")
    b_salt = bytes(salt,"utf-8")
    hashed_pw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 1000).hex()

    result = search_manager_account(mail,hashed_pw)

    return result

def manager_search_salt(mail):
    conn = get_connection()
    cur = conn.cursor()

    sql = "SELECT salt from manager where mail=%s"

    try:
        cur.execute(sql,(mail,))
    except Exception as e:
        print("salt_error",e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result :
        return result[0]
    else:
        return None

def search_manager_account(mail, pw):
    conn = get_connection()
    cur = conn.cursor()

    sql = "SELECT name, password_flag from manager where mail=%s and password=%s"

    try:
        cur.execute(sql,(mail,pw))
    except Exception as e:
        print("search_manage_account_error",e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

def student_login(mail, password): #学生のログイン
    salt = search_student_salt(mail)

    if salt == None:
        return None

    b_pw = bytes(password,"utf-8")
    b_salt = bytes(salt,"utf-8")
    hashed_pw = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 1000).hex()

    result = search_student_account(mail,hashed_pw)

    return result

def search_student_salt(mail):
    conn = get_connection()
    cur  = conn.cursor()

    sql = "SELECT salt from student where mail=%s"

    try:
        cur.execute(sql,(mail,))
    except Exception as e:
        print("salt_error", e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    if result:
        return result[0]
    else:
        return None

def search_student_account(mail, password):
    conn = get_connection()
    cur = conn.cursor()

    sql = "SELECT stu_number, name, password_flag FROM student where mail=%s and password=%s"

    try:
        cur.execute(sql,(mail,password))
    except Exception as e:
        print("search_student_account_error",e)
        return None

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

#本の登録
def book_register(book):
    conn = get_connection()
    cur = conn.cursor()

    sql = "insert into book values(%s,%s,%s,%s,%s,%s,%s)"

    try:
        cur.execute(sql,(book[0],book[1],book[2],book[3],book[4],book[5],book[6]))
    except Exception as e:
        print("本の登録エラー", e)

    conn.commit()
    cur.close()
    conn.close()

#本テーブルのレコード数
def book_count():
    conn = get_connection()
    cur = conn.cursor()

    sql = "select count(book_isbn) from book"

    try:
        cur.execute(sql,)
    except Exception as e:
        print(e)

    count = cur.fetchone()
    cur.close()
    conn.close()

    return count

#本の一覧表示
def book_list():
    conn = get_connection()
    cur = conn.cursor()
    
    sql = "select * from book where book_delete_flag = false"

    try:
        cur.execute(sql,())
    except Exception as e:
        print("図書一覧表示エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    if result != []:
        return result
    else:
        result = False
        return result

def book_review_score(isbn):
    conn = get_connection()
    cur = conn.cursor()
    list = []

    sql = "select review_star from review where book_isbn=%s"

    try:
        cur.execute(sql,(isbn,))
    except Exception as e:
        print("レビュー検索エラー",e)

    for i in cur:
        list.append(i[0])

    cur.close()
    conn.close()

    return list

# 借りている本の数
def select_amount(isbn):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select rent_book.book_isbn,count(rent_book.amount),book.amount_max from rent_book join book on (rent_book.book_isbn=book.book_isbn) where rent_book.return_day is null and book.book_isbn =%s group by (rent_book.book_isbn,book.amount_max)"

    try:
        cur.execute(sql,(isbn,))
    except Exception as e:
        print("本の数selectエラー[def book_review_score(isbn):]",e)
        return None


    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


# 本の詳細情報
def book_detail(isbn):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select * from book where book_isbn=%s"

    try:
        cur.execute(sql,(isbn,))
    except Exception as e:
        print("本の詳細情報取得エラー",e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

#本のレビュー表示
def book_show_review(isbn):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select student.name, review.book_isbn, review.review_comment, review.review_star, review.name_flag \
         from student, review where student.stu_number = review.stu_number and \
            book_isbn=%s"

    try:
        cur.execute(sql,(isbn,))
    except Exception as e:
        print("レビュー取得エラー", e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

#貸出一覧
def student_renting():
    conn = get_connection()
    cur = conn.cursor()

    sql = "select student.name, book.title, rent_book.rent_day, \
            rent_book.return_day from student, book, rent_book\
            where student.stu_number = rent_book.stu_number \
            and book.book_isbn = rent_book.book_isbn"

    try:
        cur.execute(sql,)
    except Exception as e:
        print("貸出一覧取得エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

#貸出一覧検索
def student_renting_search(key):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select student.name, book.title, rent_book.rent_day, \
            rent_book.return_day from student, book, rent_book\
            where student.stu_number = rent_book.stu_number \
            and book.book_isbn = rent_book.book_isbn \
            and (student.name ilike %s or book.title ilike %s)"
    key_like = "%"+key+"%"
    try:
        cur.execute(sql,(key_like,key_like,))
    except Exception as e:
        print("貸出一覧検索取得エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

#本を借りる
def rent_book(stu_number, isbn_list):
    conn = get_connection()
    cur = conn.cursor()
    date = datetime.date.today()

    for i in isbn_list:
        sql = "insert into rent_book values(%s,%s,%s,%s,%s)"
        try:
            cur.execute(sql,(stu_number,i,date,None,1))
        except Exception as e:
            print("借りるエラー", e)
        conn.commit()
    
    cur.close()
    conn.close()

#借りている一覧
def book_renting(stu_number):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select book_isbn from rent_book where stu_number=%s and return_day is null"

    try:
        cur.execute(sql,(stu_number,))
    except Exception as e:
        print("借りている一覧表示エラー", e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

#本の返却
def book_return(stu_number, isbn_list):
    conn = get_connection()
    cur = conn.cursor()
    date = datetime.date.today()

    for i in isbn_list:
        sql = "update rent_book set return_day=%s where stu_number=%s and book_isbn=%s"
        try:
            cur.execute(sql,(date,stu_number,i))
        except Exception as e:
            print("返却エラー",e)
        conn.commit()
    cur.close()
    conn.close()

#履歴
def book_history(stu_number):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select book.title, book,author, book.publisher,\
         rent_book.rent_day, rent_book.return_day from book,rent_book \
             where rent_book.stu_number=%s and rent_book.book_isbn=book.book_isbn \
                 and return_day is not null"

    try:
        cur.execute(sql,(stu_number,))
    except Exception as e:
        print("本の履歴取得エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# 本の削除(一部)
def book_delete_amount(isbn,amount):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update book set amount_max = amount_max - %s where book_isbn=%s"

    try:
        cur.execute(sql,(amount,isbn,))
    except Exception as e:
        print("本の最大数量変更エラー")


    conn.commit()
    cur.close()
    conn.close()

    return True

# 本の削除
def book_delete_flag(isbn):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update book set book_delete_flag = true where book_isbn=%s"

    try:
        cur.execute(sql,(isbn,))
    except Exception as e:
        print("本の削除flag変更エラー")


    conn.commit()
    cur.close()
    conn.close()

    return True

# 本の検索
def book_search(key):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select * from book where (title like %s or author like %s or publisher like %s )and book_delete_flag = false"
    key_like = "%"+ key +"%"
    try:
        cur.execute(sql,(key_like,key_like,key_like,))
    except Exception as e:
        print("本の検索取得エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# タグのselect
def select_tag(isbn):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select * from tag join book_tag on (tag.tag_id=book_tag.tag_id) where book_isbn=%s"

    try:
        cur.execute(sql,(isbn,))
    except Exception as e:
        print("本のtag情報取得エラー")

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# タグのselect(詳細画面に表示)
def select_tag_2(isbn):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select tag.tag_name from tag join book_tag on (tag.tag_id=book_tag.tag_id) where book_isbn=%s"

    try:
        cur.execute(sql,(isbn,))
    except Exception as e:
        print("本のtag情報取得エラー")

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# タグのプルダウン
def tag_pull_down(isbn):
    old_tag = select_tag_2(isbn)
    conn = get_connection()
    cur = conn.cursor()

    sql = "select tag_name from tag"

    try:
        cur.execute(sql,(isbn,))
    except Exception as e:
        print("本のtag情報取得エラー")

    result = cur.fetchall()

    cur.close()
    conn.close()
    for i in old_tag:
        result.remove(i)
    return result,old_tag

# タグの確認
def tag_result(isbn,tag_name):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select tag.tag_name from tag join book_tag on (tag.tag_id=book_tag.tag_id) where book_tag.book_isbn=%s and tag.tag_name=%s"

    try:
        cur.execute(sql,(isbn,tag_name))
    except Exception as e:
        print("本のtag情報取得エラー")
        return None

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


# 本の検索(学生)
def stu_book_search(key):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select DISTINCT ON(book.title) * from book join book_tag on (book.book_isbn=book_tag.book_isbn) join tag on (tag.tag_id=book_tag.tag_id) where (book.title ilike %s or book.author ilike %s or book.publisher ilike %s or tag.tag_name ilike %s) and book.book_delete_flag = false"
    key_like = "%"+ key +"%"
    try:
        cur.execute(sql,(key_like,key_like,key_like,key_like,))
    except Exception as e:
        print("(学生)本の検索取得エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# タグで本を検索
def tag_book_search(key):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select DISTINCT ON(book.title) * from book join book_tag on (book.book_isbn=book_tag.book_isbn) join tag on (tag.tag_id=book_tag.tag_id) where tag.tag_name ilike %s and book.book_delete_flag = false"

    key_like = "%"+key+"%"
    try:
        cur.execute(sql,(key_like,))
    except Exception as e:
        print("タグで本の検索取得エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# タグの追加
def tag_add_book(isbn,tag):
    conn = get_connection()
    cur = conn.cursor()

    tag_id = select_tag_id(tag)
    print(isbn)
    print(tag_id)
    if tag_id:
        sql = "insert into book_tag(book_isbn,tag_id) values(%s,%s)"
        try:
            cur.execute(sql,(isbn,tag_id))
        except Exception as e:
            print("タグ追加エラー",e)

        conn.commit()
        cur.close()
        conn.close()
        return True
    else :
        tag_add(tag)
        tag_id = select_tag_id(tag)
        sql = "insert into book_tag(book_isbn,tag_id) values(%s,%s)"
        try:
            cur.execute(sql,(isbn,int(tag_id)))
        except Exception as e:
            print("タグ追加エラー(else)",e)

        conn.commit()
        cur.close()
        conn.close()
        return True

 
# タグIDのselect
def select_tag_id(tag_name):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select tag_id from tag where tag_name= %s"

    try:
        cur.execute(sql,(tag_name,))
    except Exception as e:
        print("タグID検索エラー",e)

    result = cur.fetchone()

    cur.close()
    conn.close()
    if result:
        return result[0]
    else :
        return None

# タグテーブルのタグ追加
def tag_add(tag):
    conn = get_connection()
    cur = conn.cursor()

    sql = "insert into tag(tag_name) values (%s);"

    try:
        cur.execute(sql,(tag,))
    except Exception as e:
        print("タグテーブルタグinsertエラー", e)

    conn.commit()
    cur.close()
    conn.close()

    return True

# 本の情報変更
def book_change(isbn,title,author,pub,day,num):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update book set title=%s,author=%s,publisher=%s,release_day=%s,amount_max=%s where book_isbn=%s"

    try:
        cur.execute(sql,(title,author,pub,day,num,isbn))
    except Exception as e:
        print("本UPDATEエラー", e)

    conn.commit()
    cur.close()
    conn.close()

    return True


# 学生一覧
def student_list():
    conn = get_connection()
    cur = conn.cursor()

    sql = "select * from student"

    try:
        cur.execute(sql,)
    except Exception as e:
        print("学生一覧取得エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# 学生のmail一覧
def search_student_mail():
    conn = get_connection()
    cur = conn.cursor()

    sql = "select mail from student"

    try:
        cur.execute(sql,())
    except Exception as e:
        print("学生メール一覧",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# 学生進級一覧
def promotion_student_list():
    conn = get_connection()
    cur = conn.cursor()

    sql = "select stu_number,name,course_name from student \
        join course on (student.course_id=course.course_id) where \
            (((student.course_id='3' or student.course_id='10') and year=3) \
            or (student.course_id='4' and year=4) \
            or (student.course_id<>'3' and student.course_id<>'4' and student.course_id<>'10' and year=2))and student.delete_flag=false;"

    try:
        cur.execute(sql,)
    except Exception as e:
        print("学生進級一覧取得エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# 学生進級処理
def manager_promotion():
    conn = get_connection()
    cur = conn.cursor()

    sql = "update student set year = year + 1 where delete_flag=false"

    try:
        cur.execute(sql,())
    except Exception as e:
        print("UPDATEエラー", e)

    conn.commit()
    cur.close()
    conn.close()
    return True

# 進級処理で削除flagを変更
def manager_promotion_delete():
    conn = get_connection()
    cur = conn.cursor()

    sql = "update student set delete_flag=true \
        where (((student.course_id='3' or student.course_id='10') and year>3)\
        or (student.course_id='4' and year>4)\
        or (student.course_id<>'3' and student.course_id<>'4' and student.course_id<>'10' and year>2)) and delete_flag=false;"

    try:
        cur.execute(sql,())
    except Exception as e:
        print("進級フラグUPDATEエラー", e)

    conn.commit()
    cur.close()
    conn.close()
    return True

def promotion_history(mail):
    conn = get_connection()
    cur = conn.cursor()
    date = datetime.date.today()
    sql = "insert into promotion_history(promotion_day,manager_mail) values(%s,%s)"

    try:
        cur.execute(sql,(date,mail,))
    except Exception as e:
        print("進級履歴UPDATEエラー", e)

    conn.commit()
    cur.close()
    conn.close()
    return True

def update_student(mail, new_pw, new_salt):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update student set password=%s, salt=%s where mail=%s"

    try:
        cur.execute(sql,(new_pw,new_salt,mail))
    except Exception as e:
        print("UPDATEエラー", e)

    conn.commit()
    cur.close()
    conn.close()

def update_manager(mail, new_pw, new_salt):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update manager set password = %s, salt = %s where mail = %s"

    try:
        cur.execute(sql,(new_pw,new_salt,mail))
    except Exception as e:
        print("UPDATEエラー", e)

    conn.commit()
    cur.close()
    conn.close()

def search_temporary_password(mail):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select password from manager where mail=%s"

    try:
        cur.execute(sql,(mail,))
    except Exception as e:
        print(e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    print(result[0])
    return result[0]

def stu_search_temporary_password(mail):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select password from student where mail=%s"

    try:
        cur.execute(sql,(mail,))
    except Exception as e:
        print(e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

def password_update_student(mail,pw):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update student set password=%s, password_flag=%s where mail=%s"

    try:
        cur.execute(sql,(pw,"false",mail))
    except Exception as e:
        print("パスワードアップデートエラー",e)

    conn.commit()
    cur.close()
    conn.close()


def password_update_manager(mail,pw):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update manager set password=%s, password_flag=%s where mail=%s"

    try:
        cur.execute(sql,(pw,"false",mail))
    except Exception as e:
        print("パスワードアップデートエラー")

    conn.commit()
    cur.close()
    conn.close()

# 学生変更検索結果
def student_search_change(name):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select student.name, student.stu_number, course.course_name from student, course \
        where name like %s and student.delete_flag is false and student.course_id = course.course_id "
    name_like = "%"+name+"%"
    try:
        cur.execute(sql,(name_like,))
    except Exception as e:
        print(e)

    result = cur.fetchall()
    print("学生検索結果:", result)

    cur.close()
    conn.close()

    return result

# 学生詳細情報stu_numberで検索
def student_search_change_result(stu_number):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select student.mail,student.name,student.stu_number,\
        course.course_name,student.year,course.course_id from student \
            join course on (student.course_id = course.course_id) \
                where student.stu_number = %s and student.delete_flag is false"

    try:
        cur.execute(sql,(stu_number,))
    except Exception as e:
        print(e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result

# course_nameでmax_yearを検索
def search_max_year(course_id):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select max_year from course where course_id = %s"

    try:
        cur.execute(sql,(course_id,))
    except Exception as e:
        print(e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0]

# course_nameでcourse_idを検索
def search_course_id(course_name):
    conn = get_connection()
    cur = conn.cursor()

    sql = "select course_id from course where course_name=%s"

    try:
        cur.execute(sql,(course_name,))
    except Exception as e:
        print(e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0]

def stu_change_update(stu_number,name,mail,course_id,year):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update student set name=%s, mail=%s, course_id=%s, year=%s where stu_number=%s"
    try:
        cur.execute(sql,(name,mail,course_id,year,stu_number))
    except Exception as e:
        print("学生詳細アップデートエラー")

    conn.commit()
    cur.close()
    conn.close()
    return True

def delete_flag(stu_number):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update student set delete_flag=%s where stu_number=%s"
    try:
        cur.execute(sql,("true",stu_number))
    except Exception as e:
        print("学生削除フラグアップデートエラー")

    conn.commit()
    cur.close()
    conn.close()
    return True

# 管理者一覧
def select_manager_all():
    conn = get_connection()
    cur = conn.cursor()

    sql="select name,mail from manager where delete_flag is false"
    try:
        cur.execute(sql,)
    except Exception as e:
        print("管理者一覧エラー:",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result
    
def manager_delete_flag(mail):
    conn = get_connection()
    cur = conn.cursor()

    sql = "update manager set delete_flag=%s where mail=%s"
    try:
        cur.execute(sql,("true",mail))
    except Exception as e:
        print("管理者削除フラグアップデートエラー")

    conn.commit()
    cur.close()
    conn.close()
    return True


def book_review(review):
    conn = get_connection()
    cur = conn.cursor()

    sql = "insert into review values(%s,%s,%s,%s,%s)"

    try:
        cur.execute(sql,(review[0],review[1],review[2],review[3],review[4]))
        print("レビュー作成")
    except Exception as e:
        print("レビューエラー")

    conn.commit()
    cur.close()
    conn.close()

def book_review_star(review):
    conn = get_connection()
    cur = conn.cursor()

    sql = "insert into review(book_isbn,stu_number,review_star,name_flag) values(%s,%s,%s,%s)"

    try:
        cur.execute(sql,(review[0], review[1], review[2], review[3]))
        print("レビュー登録")
    except Exception as e:
        print("レビューエラー:",e)

    conn.commit()
    cur.close()
    conn.close()

# 最後の更新日をselect
def last_promotion_history():
    conn = get_connection()
    cur = conn.cursor()

    sql="select * from promotion_history,manager where mail=manager_mail order by promotion_day desc limit 1"
    try:
        cur.execute(sql,)
    except Exception as e:
        print("管理者一覧エラー:",e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

# DBとのコネクションを取得
def get_connection():
    url = urllib.parse.urlparse(os.environ['DATABASE_URL'])

    connection = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )

    return connection

def test():
    conn = get_connection()
    cur = conn.cursor()
    date = datetime.date.today()
    
    sql = "insert into promotion_history(promotion_day,manager_mail) values(%s,'b.ou.sys20@morijyobi.ac.jp')"
    try:
        cur.execute(sql,(date))
    except Exception as e:
        print("本の検索取得エラー",e)

    # result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
