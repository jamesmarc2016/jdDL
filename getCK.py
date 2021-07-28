# coding:utf-8
import socket
import re
import requests
import json
import time
import datetime
import logging
requests.packages.urllib3.disable_warnings()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

HOST, PORT = '', 7777

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT)

while True:
    try:
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        reqDec = request.decode("utf-8")

        jd_ua = 'jdltapp;iPhone;3.1.0;14.4;;network/wifi;hasUPPay/0;pushNoticeIsOpen/0;lang/zh_CN;model/iPhone11,6;hasOCPay/0;appBuild/1017;supportBestPay/0;addressid/2813715704;pv/67.38;apprpd/MyJD_Main;ref/https%3A%2F%2Fh5.m.jd.com%2FbabelDiy%2FZeus%2F2ynE8QDtc2svd36VowmYWBzzDdK6%2Findex.html%3Flng%3D103.957532%26lat%3D30.626962%26sid%3D4fe8ef4283b24723a7bb30ee87c18b2w%26un_area%3D22_1930_49324_52512;psq/4;ads/;psn/5aef178f95931bdbbde849ea9e2fc62b18bc5829|127;jdv/0|direct|-|none|-|1612588090667|1613822580;adk/;app_device/IOS;pap/JA2020_3112531|3.1.0|IOS 14.4;Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'

        session = requests.session()

        # 获取s_token
        t = round(time.time())
        headers = {
            'User-Agent': jd_ua,
            'referer': 'https://plogin.m.jd.com/cgi-bin/mm/new_login_entrance?lang=chs&appid=300&returnurl=https://wq.jd.com/passport/LoginRedirect?state={0}&returnurl=https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(
                t)
        }
        t = round(time.time())
        url = 'https://plogin.m.jd.com/cgi-bin/mm/new_login_entrance?lang=chs&appid=300&returnurl=https://wq.jd.com/passport/LoginRedirect?state={0}&returnurl=https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(
            t)

        res = session.get(url=url, headers=headers, verify=False)
        res_json = json.loads(res.text)
        s_token = res_json['s_token']

        print("s_token:" + s_token)

        # 获取okl_token token
        t = round(time.time() * 1000)
        headers = {
            "Connection": "Keep-Alive",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-cn",
            'User-Agent': jd_ua,
            'referer': 'https://plogin.m.jd.com/login/login?appid=300&returnurl=https://wqlogin2.jd.com/passport/LoginRedirect?state={0}&returnurl=//home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(
                t),
            'Content-Type': 'application/x-www-form-urlencoded; Charset=UTF-8',
            "Host": "plogin.m.jd.com"
        }
        url = 'https://plogin.m.jd.com/cgi-bin/m/tmauthreflogurl?s_token={0}&v={1}&remember=true'.format(s_token, t)

        data = {
            'lang': 'chs',
            'appid': 300,
            'returnurl': 'https://wqlogin2.jd.com/passport/LoginRedirect?state={0}returnurl=//home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport'.format(
                t)
        }

        res = session.post(url, data, None, headers=headers)
        print(res.text)
        res_json = json.loads(res.text)
        token = res_json['token']
        print("token:", token)
        c = session.cookies.get_dict()
        okl_token = c['okl_token']
        print("okl_token:", okl_token)
        qrurl = 'https://plogin.m.jd.com/cgi-bin/m/tmauth?client_type=m&appid=300&token={0}'.format(token)

        #  准备发送的header
        response = "HTTP/1.1 200 OK\r\n"
        response += "\r\n"  # header与body之间必须隔一行
        client_connection.sendall(response.encode("utf-8"))

        responseData = {
            'err': 0,
            'qrcode': qrurl,
            'user': {
                's_token': s_token,
                'cookies': session.cookies.get_dict(),
                'qrCodeUrl': qrurl,
                'okl_token': okl_token,
                'token': token
            },
            'jdCode': ''
        }
        responseStr = json.dumps(responseData)
        responseStr = responseStr.encode("utf-8")
        client_connection.send(responseStr)
        client_connection.close()
    except Exception as e:
        print(e)
























