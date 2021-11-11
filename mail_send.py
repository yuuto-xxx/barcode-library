from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP


def mail(mail2,pw):
    # SMTP認証情報
    account = "morijyobi.library.apprication@gmail.com"
    password = "morijyobi"
    
    # 送受信先
    to_email = mail2
    from_email = account
    
    # MIMEの作成
    subject = "仮パスワードの送信"
    message = f"新しいパスワード；＿＿{pw}"
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

def mail(mail2,pw,student_flg):
    # SMTP認証情報
    account = "#"
    password = "#"
    
    # 送受信先
    to_email = mail2
    from_email = "#"
    
    email = "?mail="+mail2+"?student_flg="+student_flg
    # MIMEの作成
    subject = "仮パスワードの送信"
    message = f"新しいパスワード；＿＿{pw}__http://127.0.0.1/pw_reset{email}"
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
    print("ok")
    return True