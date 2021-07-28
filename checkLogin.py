# coding:utf-8
import socket
import re
import requests
import json
import time
import datetime
import random
from requests.cookies import RequestsCookieJar
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
HOST, PORT = '', 9999

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT)

random_str = ''
base_str = '0123456789'
length = len(base_str) - 1
for i in range(40):
    random_str += base_str[random.randint(0, length)]

jd_ua = 'jdapp;android;10.0.2;9;'+random_str+';network/wifi;model/MI 8;addressid/138087843;aid/0a4fc8ec9548a7f9;oaid/3ac46dd4d42fa41c;osVer/28;appBuild/${UANumber};partner/jingdong;eufv/1;jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 9; MI 8 Build/PKQ1.180729.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045715 Mobile Safari/537.36'
print("生成ua为:" + jd_ua)

while True:

    try:
        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(102400)

        reqDec = request.decode("utf-8")
        reqDec = reqDec.splitlines()
        reqDec = reqDec[len(reqDec) - 1]

        reqJson = json.loads(reqDec)
        user = reqJson['user']

        cookies = user['cookies']

        lang = cookies['lang']
        lsid = cookies['lsid']
        lstoken = cookies['lstoken']
        guid = cookies['guid']

        ck = "lang=" + str(lang)
        ck += ";lsid=" + str(lsid)
        ck += ";lstoken=" + str(lstoken)
        ck += ";guid=" + str(guid) + ";"
        print("ck:" + ck)

        domain = "plogin.m.jd.com"
        path = "/"

        requestsCookieJar = requests.cookies.RequestsCookieJar()
        requestsCookieJar.set('guid', guid, domain=domain)
        requestsCookieJar.set('lang', lang, domain=domain)
        requestsCookieJar.set('lsid', lsid, domain=domain)
        requestsCookieJar.set('lstoken', lstoken, domain=domain)

        okl_token = user['okl_token']

        token = user['token']

        if ((token != "") & (okl_token != "")):
            t = round(time.time() * 1000)
            loginUrl = "https://plogin.m.jd.com/cgi-bin/mm/new_login_entrance?lang=chs&appid=300&returnurl=https://wq.jd.com/passport/LoginRedirect?state={0}&returnurl=https://home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action&source=wq_passport".format(
                t)
            headers = {
                "Connection": "Keep-Alive",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-cn",
                "Cookie": ck,
                'User-Agent': jd_ua,
                'Referer': loginUrl,
                'Content-Type': 'application/x-www-form-urlencoded; Charset=UTF-8'
            }
            url = 'https://plogin.m.jd.com/cgi-bin/m/tmauthchecktoken?&token={0}&ou_state=0&okl_token={1}'.format(token,
                                                                                                                  okl_token)
            data = {
                'lang': 'chs',
                'appid': 300,
                'returnurl': 'https://wqlogin2.jd.com/passport/LoginRedirect?state={0}&returnurl=//home.m.jd.com/myJd/newhome.action?sceneval=2&ufc=&/myJd/home.action'.format(
                    t),
                'source': 'wq_passport',
            }
            session = requests.session()
            session.cookies.update(requestsCookieJar)
            res = session.post(url=url, headers=headers, data=data, verify=False)
            check = json.loads(res.text)

            print("check：" + json.dumps(check))

            code = check['errcode']
            message = check['message']
            while code == 0:
                jd_ck = session.cookies.get_dict()
                print(jd_ck)
                pt_key = 'pt_key=' + jd_ck['pt_key']
                pt_pin = 'pt_pin=' + jd_ck['pt_pin']
                ck = str(pt_key) + ';' + str(pt_pin) + ';'

                # 更新ck到后台
                rep = requests.get("http://127.0.0.1:8888/?" + ck)
                print(rep)

                response = "HTTP/1.1 " + str(rep.status_code) + " OK\r\n"
                response += "\r\n"  # header与body之间必须隔一行
                client_connection.sendall(response.encode("utf-8"))

                responseData = {
                    'err': "0",
                    'msg': "更新成功"
                }
                responseStr = json.dumps(responseData)
                responseStr = responseStr.encode("utf-8")
                client_connection.send(responseStr)

                client_connection.close()
                break
            else:
                response = "HTTP/1.1 " + str(res.status_code) + " OK\r\n"
                response += "\r\n"  # header与body之间必须隔一行
                client_connection.sendall(response.encode("utf-8"))

                responseData = {
                    'err': str(res.status_code),
                    'msg': message
                }
                responseStr = json.dumps(responseData)
                responseStr = responseStr.encode("utf-8")
                client_connection.send(responseStr)
                client_connection.close()
    except Exception as e:
        print(e)





