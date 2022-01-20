from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib

def mail(address,pw):
    #検証用
    print(address)
    print(pw)

    # SMTP認証情報
    account = "morijyobi.library.application@gmail.com"
    password = "ebitlukbrhhognds"
    
    # 送受信先
    to_email = address
    from_email = account
    
    # MIMEの作成
    subject = "仮パスワードの送信"
    message = f"新しいパスワード；{pw}"
    msg = MIMEText(message, "html")
    msg["Subject"] = subject
    msg["To"] = to_email
    msg["From"] = from_email
    
    # メール送信処理
    server = SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(account, password)
    server.send_message(msg)
    server.quit()
    print("ok")
    return True

def forget_pw_mail(address,pw,student_flg,new_salt):
    # SMTP認証情報
    account = "morijyobi.library.application@gmail.com"
    password = "ebitlukbrhhognds"
    
    # 送受信先
    to_email = address
    from_email = account
    
    email = "?mail="+address+"?student_flg="+str(student_flg)+"?salt="+new_salt
    # MIMEの作成
    subject = "仮パスワードの送信"
    message = f"新しいパスワード；{pw}"
    msg = MIMEText(message, "html")
    msg["Subject"] = subject
    msg["To"] = to_email
    msg["From"] = from_email
    
    # メール送信処理
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(account, password)
    server.send_message(msg)
    server.quit()
    return True