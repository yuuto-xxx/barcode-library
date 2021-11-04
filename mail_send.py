from email.mime.text import MIMEText
import smtplib


def mail(mail2,pw):
    # SMTP認証情報
    account = "#"
    password = "#"
    
    # 送受信先
    to_email = mail2
    from_email = "#"
    
    # MIMEの作成
    subject = "仮パスワードの送信"
    message = f"新しいパスワード；＿＿{pw}"
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
