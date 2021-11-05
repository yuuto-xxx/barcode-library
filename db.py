import psycopg2
import string
import random
import hashlib
import os

dbname="d146sdrtncr1rm" 
host = "ec2-23-23-199-57.compute-1.amazonaws.com"
port = 5432 
user = "sudfwfyugnjfdf"
password = "46a5575767a9c88ebcb1930e8afe9c557df8911a3b4021ce902a500ba47a4e8b"

DATABASE_URL = os.environ.get('postgres://sudfwfyugnjfdf:46a5575767a9c88ebcb1930e8afe9c557df8911a3b4021ce902a500ba47a4e8b@ec2-23-23-199-57.compute-1.amazonaws.com:5432/d146sdrtncr1rm')
url = "postgres://sudfwfyugnjfdf:46a5575767a9c88ebcb1930e8afe9c557df8911a3b4021ce902a500ba47a4e8b@ec2-23-23-199-57.compute-1.amazonaws.com:5432/d146sdrtncr1rm"

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
def student_register(mail,name,student_id,couse,grade,pw,salt):
    hashed_pw = hash_pw(pw,salt)
    print("mail",mail)
    print("name",name)
    print("student_id",student_id)
    print("hashed_pw",hashed_pw,len(hashed_pw))
    print("salt",salt,len(salt))
    print("course",couse)
    print("grade",grade)
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

    sql = "SELECT name from manager where mail=%s and password=%s"

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

    sql = "SELECT name FROM student where mail=%s and password=%s"

    try:
        cur.execute(sql,(mail,password))
    except Exception as e:
        print("search_student_account_error",e)

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result

#本の登録
def book_register(isbn,image,title,author,publisher,release_day,amount_max):
    conn = get_connection()
    cur = conn.cursor()

    sql = "insert into book values (%s,%s,%s,%s,%s,%s,%s)"

    try:
        cur.execute(sql,())
    except Exception as e:
        print("本の登録エラー", e)

    cur.close()
    conn.close()

def book_search():
    conn = get_connection()
    cur = conn.cursor()

    sql = "select * from book where "

    try:
        cur.execute(sql,())
    except Exception as e:
        print("図書検索エラー",e)

    result = cur.fetchall()

    cur.close()
    conn.close()

    return result


# DBとのコネクションを取得
def get_connection():
    connection = psycopg2.connect(
    database=dbname,
    user=user,
    password=password,
    host=host,
    port=5432 )
    return connection