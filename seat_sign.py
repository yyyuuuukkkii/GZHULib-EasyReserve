import datetime
import threading

import pandas as pd
import requests

import config
import util


class SeatSign:
    def __init__(self, user):
        self.df = None
        self.username = user.get('username')
        self.password = user.get('password')
        self.session = requests.session()
        self.time = user.get('time')
        self.devSn = user.get('devSn')
        self.url = config.url

    def save_finish(self):
        beginDate = datetime.datetime.now()
        endDate = datetime.datetime.now() + datetime.timedelta(days=1)
        params = {
            'beginDate': beginDate.strftime('%Y-%m-%d'),
            'endDate': endDate.strftime('%Y-%m-%d'),
            'needStatus': '262',
            'page': '1',
            'pageNum': '10',
            'orderKey': 'gmt_create',
            'orderModel': 'desc'
        }
        response = self.session.get(self.url['resvInfo'], params=params).json().get('data')
        form = {
            'devName': [],
            'resvId': [],
            'devSn': [],
            'resvBeginTime': [],
            'resvEndTime': []

        }
        for i in response:
            resvDevInfoList = i.get('resvDevInfoList')
            form['devName'].append(resvDevInfoList[0].get('devName'))
            form['resvId'].append(resvDevInfoList[0].get('resvId'))
            form['devSn'].append(resvDevInfoList[0].get('devSn'))
            form['resvBeginTime'].append(i.get('resvBeginTime'))
            form['resvEndTime'].append(i.get('resvEndTime'))
        df = pd.DataFrame({
            'devName': form['devName'],
            'resvId': form['resvId'],
            'devSn': form['devSn'],
            'resvBeginTime': form['resvBeginTime'],
            'resvEndTime': form['resvEndTime']
        })
        df = df.sort_values(by='resvBeginTime')
        df = df.reset_index(drop=True)
        df['resvBeginTime'] = ((pd.to_datetime(df['resvBeginTime'] / 1000, unit='s')) + datetime.timedelta(hours=8))
        df['resvEndTime'] = ((pd.to_datetime(df['resvEndTime'] / 1000, unit='s')) + datetime.timedelta(hours=8))
        self.df = df

    def sign_seat(self):
        if self.df.size == 0:
            print(self.username + '没有预约座位\n', end='')
            return

        self.df['resvBeginTime'] = pd.to_datetime(self.df['resvBeginTime'], format='%Y-%m-%d %H:%M:%S')
        self.df['resvEndTime'] = pd.to_datetime(self.df['resvEndTime'], format='%Y-%m-%d %H:%M:%S')
        now = datetime.datetime.now()
        if not self.df['resvBeginTime'][0] <= now <= self.df['resvEndTime'][0]:
            print('未到签到时间\n', end='')
        else:
            print('正在签到......\n', end='')
        data = {
            "devSn": str(self.df['devSn'][0]),
            "type": "1",
            "bind": 0,
            "loginType": 2
        }
        self.session.post(url=self.url['userLogin'],
                          json=data).json()
        data = {
            'resvId': str(self.df['resvId'][0]),
        }
        response = self.session.post(url=self.url['seatSign'],
                                     json=data).json()
        print(self.username + "------" + response.get("message") + '\n', end='')

    def start(self):
        accNo = util.login(self.session, self.username, self.password)
        if accNo is None:
            return
        self.save_finish()

        try:
            self.sign_seat()
        except Exception as e:
            print(self.username + '签到失败\n', end='')
        finally:
            self.session.close()


if __name__ == '__main__':
    conn = util.get_sqlite_conn()
    userConfig = util.get_userConfig(conn.cursor())
    for user in userConfig:
        threading.Thread(target=SeatSign(user).start).start()
    conn.close()
