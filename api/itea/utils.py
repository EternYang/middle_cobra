import sched
import smtplib
import threading
import time
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from email.header import Header
from random import Random  # 用于生成随机码
from django.core.mail import send_mail  # 发送邮件模块

from app01.models import EmailVerifyRecord  # 邮箱验证model

from api.settings import EMAIL_FROM, EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD  # setting.py添加的的配置信息



"""
生成随机字符串
@:param randomlength 长度
@:return str 生成的随机字符串
"""
def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def send_register_email(email, send_type="register"):
    email_record = EmailVerifyRecord()
    # 将给用户发的信息保存在数据库中
    code = random_str(16)
    print(code)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    # 定时，60秒后删除
    # MyThread(code).start()
    # server = smtplib.SMTP_SSL(host=EMAIL_HOST, port=EMAIL_PORT)
    # 如果为注册类型
    try:
        to_mail = smtplib.SMTP_SSL()
        to_mail.connect(EMAIL_HOST, EMAIL_PORT)
        to_mail.set_debuglevel(1)
        to_mail.ehlo()  # 向Gamil发送SMTP 'ehlo' 命令
        to_mail.starttls()
        to_mail.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        if send_type == "register":
            email_title = "Hello and Welcome to ITEA"
            email_body = "please click this Registration activation link to active your email:\n" \
                         "http://localhost:8000/itea/active/{0}".format(code)
            msg = MIMEText(email_body)
            msg['From'] = '%s <%s>' % (Header('itea'.decode('utf-8')).encode(), EMAIL_FROM)     # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = email            # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = Header(email_title.decode('utf-8')).encode()
            to_mail.sendmail(EMAIL_FROM, email, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        else:
            email_title = "CHANGE PASSWORD"
            email_body = "Hello, you are applying for resetting your password. " \
                         "If this is not your own operation, please ignore it. " \
                         "Please click the link below to complete the reset operation:\n" \
                         "http://localhost:8000/itea/forgetpassword/{0}".format(code)
            msg = MIMEText(email_body)
            msg['From'] = '%s <%s>' % (Header('itea'.decode('utf-8')).encode(), EMAIL_FROM)  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
            msg['To'] = email  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
            msg['Subject'] = Header(email_title.decode('utf-8')).encode()
            to_mail.sendmail(EMAIL_FROM, email, msg.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        to_mail.quit()  # 关闭连接
    except smtplib.SMTPConnectError as e:
        print('email send failed 1，connect failed:{code},{error}', e.smtp_code, e.smtp_error)
    except smtplib.SMTPAuthenticationError as e:
        print('email send failed 2，Authentication failure:', e.smtp_code, e.smtp_error)
    except smtplib.SMTPSenderRefused as e:
        print('email send failed 3，sender denied:', e.smtp_code, e.smtp_error)
    except smtplib.SMTPRecipientsRefused as e:
        print('email send failed 4，The recipient was rejected:', e.smtp_code, e.smtp_error)
    except smtplib.SMTPDataError as e:
        print('email send failed 5，Data reception is rejected:', e.smtp_code, e.smtp_error)
    except smtplib.SMTPException as e:
        print('email send failed 6, ', e)
    except Exception as e:
        print('email send failed 7', str(e))


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def delete_code(code):
    print("删除被执行啦")
    if EmailVerifyRecord.objects.filter(code=code):
        EmailVerifyRecord.objects.filter(code=code).delete()

"""
class MyThread(threading.Thread):
    def __init__(self, code):
        threading.Thread.__init__(self)
        self.code = code

    def run(self):  # 定义每个线程要运行的函数
        schedule = sched.scheduler(time.time, time.sleep)
        schedule.enter(60, 0, delete_code, self.code)
        schedule.run()
        """

