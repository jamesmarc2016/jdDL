# coding:utf-8
import socket
import requests
import json
import time
import random
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

        random_str = ''
        base_str = '0123456789'
        length = len(base_str) - 1
        for i in range(40):
            random_str += base_str[random.randint(0, length)]

        jd_ua = 'jdapp;android;10.0.2;9;'+random_str+';network/wifi;model/MI 8;addressid/138087843;aid/0a4fc8ec9548a7f9;oaid/3ac46dd4d42fa41c;osVer/28;appBuild/${UANumber};partner/jingdong;eufv/1;jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 9; MI 8 Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045715 Mobile Safari/537.36'

        print("生成ua为:" + jd_ua)

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
























