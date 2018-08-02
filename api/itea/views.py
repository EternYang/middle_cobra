from random import Random

import requests
import re
import json
# Create your views here.
from django.shortcuts import render
from django.views import View
from django.core.mail import send_mail
from rest_framework import status, generics

from rest_framework.response import Response
from django.http import JsonResponse

from app01.models import EmailVerifyRecord, Member, LoginSession, Wallet
from .utils import send_register_email, random_str

URL = ""


class RegisterView(generics.GenericAPIView):
    """
    注册register，
    @:param username 用户名，必须是邮箱格式，不可重复
    @:param mobile_no 手机号，不可重复
    @:param password 密码
    @:param dob 会员生日
    """

    def post(self, request):
        dic = request.data
        mobile_no = dic.get("mobile_no", "")
        email = dic.get("email", "")
        password = dic.get("password", "")
        dob = dic.get("dob", "")
        nick_name = dic.get("nick_name", "")
        data = {
            "email": email,
            "password": password,
            "dob": dob,
            "mobile_no": mobile_no,
            "nick_name": nick_name
        }
        # 四个必需参数，有一个为空，则返回错误请求信息
        for key, value in data.items():
            if not value:
                return Response({"msg": "param {0} is not exist, please confirm  and Retry".format(key)},
                            status=status.HTTP_400_BAD_REQUEST)

        # 正则表达式验证邮箱
        if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
            return Response({"msg": "username is not an email or Wrongful, please confirm  and Retry"},
                            status=status.HTTP_400_BAD_REQUEST)

        # 正则表达式验证密码
        if not re.match(r'^[0-9a-zA-Z_]{6,15}$', password):
            return Response({"msg": "password is Wrongful, only be composed of English letters and numbers. "
                                    "The length is greater than 6 bits and less than 15 bits. "
                                    "Please confirm and Retry."},
                            status=status.HTTP_400_BAD_REQUEST)

        # 正则表达式验证手机
        if not re.match(r"^[0-9]{8}$", mobile_no):
            return Response({"msg": "phone Number is Wrongful, please confirm  and Retry"},
                                status=status.HTTP_400_BAD_REQUEST)

        url = "v1/member/registerbyemail/"
        r = requestCRM("POST", url, data, None)
        if r.status_code == 201:
            send_register_email(email, "register")
            return Response({'msg': "Instructions sent to email"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"msg": r.text}, status=r.status_code)


class ActiveUserView(generics.GenericAPIView):
    def get(self, request, active_code):
        # 用code在数据库中过滤处信息
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                # 通过邮箱查找到对应的用户
                user = Member.objects.get(email=email)
                # 激活用户
                user.is_active = 1
                user.save()
                EmailVerifyRecord.objects.filter(id=record.id).delete()
                return render(request, "result.html",
                              {"msg": "Activation is successful, please return to app login", "status": "success"})
        else:
            return render(request, "result.html",
                          {"msg": "Activate failure, please return to the mailbox and click again", "status": "error"})


class ForgetPasswordView(generics.GenericAPIView):

    def post(self, request):
        dic = request.data
        email = dic.get("email", "")
        # 验证参数是否存在
        if not email:
            return Response({"msg": "username is not exist, please confirm  and Retry"},
                            status=status.HTTP_400_BAD_REQUEST)

        # 正则表达式验证邮箱
        if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
            return Response({"msg": "username is not an email or Wrongful, please confirm  and Retry"},
                            status=status.HTTP_400_BAD_REQUEST)
        # 查询用户
        users = Member.objects.filter(email=email)
        if users and users[0]:
            # 存在发送邮件
            send_register_email(email, "forget")
            return Response({'msg': "Instructions sent to email"}, status=status.HTTP_200_OK)
        # 不存在返回错误
        return Response({'msg': 'User is not exist, please check your email and retry'},
                        status=status.HTTP_201_CREATED)


class ForgetView(generics.GenericAPIView):

    def get(self, request, code):
        all_records = EmailVerifyRecord.objects.filter(code=code)
        if all_records:
            for record in all_records:
                email = record.email
                # 通过邮箱查找到对应的用户
                user = Member.objects.filter(email=email)
                if user:
                    # EmailVerifyRecord.objects.filter(id=record.id).delete()
                    # 确认邮箱，返回充值密码页面
                    return render(request, "resetpassword.html", {"email": email})
        else:
            return Response({"msg": "Request invalid or verify connection failure, please try again"},
                            status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(generics.GenericAPIView):
    def post(self, request):
        dic = request.data
        email = dic.get("email", "")
        password = dic.get("password", "")
        # 正则表达式验证密码
        if not re.match(r'^[0-9a-zA-Z_]{6,15}$', password):
            return Response({"msg": "password is Wrongful, only be composed of English letters and numbers. "
                                    "The length is greater than 6 bits and less than 15 bits. "
                                    "Please confirm and Retry."},
                            status=status.HTTP_400_BAD_REQUEST)
        # 获取用户
        users = Member.objects.filter(email=email)
        if users and users[0]:
            user = users[0]
            # 用户不活跃，返回错误，先激活
            if not user.is_active:
                return Response({"msg": "User is not activated, please activate first and retry"},
                                status=status.HTTP_403_FORBIDDEN)
            # 密码相同，返回错误，不必修改
            if password == user.password:
                return Response({"msg": "The new password is the same as the original password"},
                                status=status.HTTP_403_FORBIDDEN)
            print(user)
            user.set_password(password)
            print(user)
            user.save()
            EmailVerifyRecord.objects.filter(email=user.email).delete()
            # 成功修改，返回信息
            return Response({"msg": "password is renew, please back to APP "
                                    "and log in again"},
                            status=status.HTTP_200_OK)
        else:
            return Response({"msg": "User is not exist, please check your email and retry"},
                            status=status.HTTP_403_FORBIDDEN)


class LoginView(generics.GenericAPIView):
    def post(self, request):
        dic = request.data
        email = dic.get("email", "")
        password = dic.get("password", "")
        data = {
            "username": email,
            "password": password
        }
        user = Member.objects.filter(email=email)
        if not user:
            user = Member.objects.filter(username=email)
        print("-------------{0}".format(email))
        if not user[0].is_active:
            return Response({'msg': "the user is not active, please go to the mailbox first, "
                                    "click the confirmation activation and retry."}, status=status.HTTP_403_FORBIDDEN)
        else:
            url = "v1/member/login/"
            r = requestCRM("POST", url, data, None)
            if r.status_code == 200:
                login_session = LoginSession.objects.filter(pk=email)
                ls = LoginSession()
                if login_session:
                    ls = login_session[0]
                else:
                    ls.email = email
                token = random_str(randomlength=32)
                print(token)
                ls.session = token
                ls.save()
                msg = {"Authorization": "Token {0}".format(json.loads(r.text)['token']), "token": token}
                return Response(msg, status=r.status_code)
            else:
                return Response({"msg": r.text}, r.status_code)


class RechargeConsumptionView(generics.GenericAPIView):
    """
    充值消费
    """
    def post(self, request):
        dic = request.data
        print(dic)
        meta = request.META
        print(meta)
        perm_token = meta.get("HTTP_AUTHORIZATION", "")
        login_token = dic.get("token", "")
        mon = dic.get("money", "")
        email = dic.get("email", "")
        if email:
            # 有emai,说明是app，需要校验登录状态，无email，是pos请求，直接扣款
            response = checktoken(token=login_token, email=email)
            if not response.status_code == 200:
                return response
        else:
            #是pos请求，根据token查询email
            email = LoginSession.objects.get(session=login_token).email
        member = Member.objects.get(email=email)
        wallet = member.wallet
        wal_id = wallet.id
        data = {
            "wallet": wal_id,
            "money": mon
        }
        r = requestCRM("POST", "v1/wallet/recharge-record/", data, perm_token)
        if r.status_code == 201:
            balance = Wallet.objects.get(pk=wal_id).balance
            return Response({"msg": "success", "balance": balance}, status=status.HTTP_200_OK)
        return Response({"msg": r.text}, status=r.status_code)


def requestCRM(method, url, data, perm_token):
    request_url = "http://localhost:8000/api/{url_name}".format(url_name=url)
    header_dict = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
                   "Content-Type": "application/json"}
    if perm_token:
        header_dict["Authorization"] = perm_token
    print(header_dict)
    return requests.request(method, request_url, data=json.dumps(data), headers=header_dict)


def checktoken(token="", email=""):
    if not token:
        return Response({"msg": "Token does not exist"}, status=status.HTTP_403_FORBIDDEN)
    login_session = LoginSession.objects.filter(pk=email)
    if login_session and login_session[0]:
        ls = login_session[0]
        if ls.session == token:
            return Response({"msg": "Token pass"}, status=status.HTTP_200_OK)
        else:
            return Response({"msg": "Token expires, please log in again"}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({"msg": "User is not login,please login first"}, status=status.HTTP_403_FORBIDDEN)


class ClosureView(generics.GenericAPIView):
    pass
