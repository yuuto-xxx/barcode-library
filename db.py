import psycopg2
import string
import random
import hashlib
import os
import psycopg2
from flask_sqlalchemy import SQLAlchemy

dbname=d146sdrtncr1rm 
host = "ec2-23-23-199-57.compute-1.amazonaws.com "
port = 5432 
user = "sudfwfyugnjfdf "
password = "46a5575767a9c88ebcb1930e8afe9c557df8911a3b4021ce902a500ba47a4e8b"

DATABASE_URL = os.environ.get('postgres://sudfwfyugnjfdf:46a5575767a9c88ebcb1930e8afe9c557df8911a3b4021ce902a500ba47a4e8b@ec2-23-23-199-57.compute-1.amazonaws.com:5432/d146sdrtncr1rm')

# 管理者の新規登録
def manager_insert(mail,name,pw,salt):
    # conn = get_connection()
    # cur = conn.cursor()
    # sql = """INSERT INTO manger(mail,name,pw,salt) VALUES(%s,%s,%s,%s)"""
    hashed_pw = hash_pw(pw,salt)
    # try:
    #     cur.execute(sql,(mail,name,hashed_pw,salt))
    # except Exception as e:
    #     print("SQL実行に失敗：", e)
    
    # conn.commit()
    # cur.close()
    # conn.close()
    
    print(mail)
    print(name)
    print(hashed_pw)
    print(salt)
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

# DBとのコネクションを取得
def get_connection():
    connection = psycopg2.connect(
  database=dbname,
  user=user,            # ユーザ名
  password=password, # パスワード
  host=host, # ホスト名
  port=5432 ) # ポート番号
    return connection



def test():
    conn = psycopg2.connect(DATABASE_URL, user=user, password=password)
    cur = conn.cursor()
    print("DBアクセス")
    cur.execute("select * from course")
    result = cur.fetchall()
    print("リザルト表示:" + result)
    cur.close()
    conn.close()
