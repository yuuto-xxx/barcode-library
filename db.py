import os
import psycopg2
from flask_sqlalchemy import SQLAlchemy
import random
import hashlib
import string

#dbname=d146sdrtncr1rm 
host = "ec2-23-23-199-57.compute-1.amazonaws.com "
port = 5432 
user = "sudfwfyugnjfdf "
password = "46a5575767a9c88ebcb1930e8afe9c557df8911a3b4021ce902a500ba47a4e8b "
sslmode = "require"

DATABASE_URL = os.environ.get('postgres://sudfwfyugnjfdf:46a5575767a9c88ebcb1930e8afe9c557df8911a3b4021ce902a500ba47a4e8b@ec2-23-23-199-57.compute-1.amazonaws.com:5432/d146sdrtncr1rm')

def test():
    conn = psycopg2.connect(DATABASE_URL, user=user, password=password)
    cur = conn.cursor()
    print("DBアクセス")
    cur.execute("select * from course")
    result = cur.fetchall()
    print("リザルト表示:" + result)
    cur.close()
    conn.close()