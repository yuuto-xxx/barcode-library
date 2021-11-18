import psycopg2
import string
import random
import hashlib
import os
import urllib.parse

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

    sql = "SELECT name, password_flag FROM student where mail=%s and password=%s"

    try:
        cur.execute(sql,(mail,password))
    except Exception as e:
        print("search_student_account_error",e)

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

def book_list():  #本の一覧表示
    conn = get_connection()
    cur = conn.cursor()

    sql = "select * from book"

    try:
        cur.execute(sql,())
    except Exception as e:
        print("図書一覧表示エラー",e)

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