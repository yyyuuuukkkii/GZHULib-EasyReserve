import datetime
import random
import threading
import time

import requests

import config
import util


class Seat:
    def __init__(self, user):
        self.seatInfo = user.get('seat_info')
        self.username = user.get('username')
        self.password = user.get('password')
        self.session = requests.session()
        self.time = self.seatInfo.get('time')
        self.devId = self.seatInfo.get('dev_id')
        self.url = config.url

    def get_seat(self, accNo):
        payload = {"sysKind": 8, "appAccNo": accNo, "memberKind": 1, "resvMember": [accNo], "resvBeginTime": "",
                   "resvEndTime": "", "testName": "", "captcha": "", "resvProperty": 0, "memo": "",
                   'resvDev': [self.devId]}
        # 选择座位
        # 选择日期
        day_time = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        # 获取星期的下标
        week_index = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%A')
        # 选择时间
        if not self.time[week_index]:
            return print(self.username + '没有设置时间\n' + '\n', end='')
        for select_time in self.time[week_index]:
            # 选择开始时间
            payload['resvBeginTime'] = day_time + ' ' + select_time.split('-')[0]
            # 选择结束时间
            payload['resvEndTime'] = day_time + ' ' + select_time.split('-')[1]
            self.post(self.url['reserve'], payload)

    def post(self, url, payload):
        response = self.session.post(url, json=payload).json()
        message = response.get('message')
        code = response.get('code')
        if code == 300:
            util.login(self.session, self.username, self.password)
            self.post(url, payload)
        elif code != 500 and "请稍后" in message:
            time.sleep(random.uniform(0, 0.2))
            self.post(url, payload)
        else:
            print(self.username + "---" + str() + "---" + message + '\n', end='')

    def start(self):
        accNo = util.login(self.session, self.username, self.password)
        if accNo is None:
            return
        # 预约座位
        try:
            self.get_seat(accNo)
        except Exception as e:
            print(self.username + e + '\n', end='')
        finally:
            self.session.close()


if __name__ == '__main__':
    conn = util.get_sqlite_conn()
    cursor = conn.cursor()

    userConfig = util.get_userConfig(cursor)
    util.wait_until(6, 20)
    print(datetime.datetime.now())
    for user in userConfig:
        if user.get('seat_info') is None:
            continue
        threading.Thread(target=Seat(user).start).start()
    conn.close()
