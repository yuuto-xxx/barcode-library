import psycopg2
import string
import random
import hashlib

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
  database='d6cp6dkkvdfkd1',        # データベース名
  user='cxhmqrtrdemxbm',            # ユーザ名
  password='bc491716a7dd69ab726a155c1928ddc06165ff87965dee628297ac73c03edfbb', # パスワード
  host='ec2-44-198-100-81.compute-1.amazonaws.com', # ホスト名
  port=5432 ) # ポート番号
    return connection

