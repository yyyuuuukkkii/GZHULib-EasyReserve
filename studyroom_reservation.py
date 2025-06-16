import datetime
import threading
from typing import List

import requests

import config
import util


class StudyRoom:
    def __init__(self, userInfo: dict):
        self.resvMember = None
        self.room_info = userInfo['room_info']
        self.username = userInfo['username']
        self.password = userInfo['password']
        self.accNo = None
        self.tasks = []
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50',
            'Referer': 'http://libbooking.gzhu.edu.cn/',
            'Host': 'libbooking.gzhu.edu.cn'
        })
        self.url = config.url
        self.lock = threading.Lock()

    def printMessage(self, postData: dict, message: str, roomName: str):
        print(
            f"[Thread-{threading.current_thread().name}] {self.username}------"
            f"{datetime.datetime.now()}------{roomName}------"
            f"{postData.get('resvBeginTime')}-{postData.get('resvEndTime')}: {message}\n",
            end=''
        )

    def PostReserve(self, postData: dict, roomName: str, event: threading.Event):
        retries = 0
        max_retries = 5  # 最大重试次数
        while retries < max_retries:
            try:
                with self.lock:
                    if event.is_set():  # 如果事件已被设置，退出当前线程
                        print(
                            f"[Thread-{threading.current_thread().name}] {self.username}事件已被设置---{roomName}预约终止---{postData.get('resvBeginTime')}-{postData.get('resvEndTime')}")
                        return
                    response = self.session.post(self.url['reserve'], json=postData, verify=False)
                    data = response.json()
                    message: str = data.get('message')
                    code = data.get("code")
                    if code == 300:
                        util.login(self.session, self.username, self.password)
                    elif code == 1:
                        self.printMessage(postData, message, roomName)
                        return
                    else:
                        self.printMessage(postData, message, roomName)
                        event.set()  # 设置事件，通知其他线程停止
                        return
            except requests.exceptions.RequestException as e:
                print(f"[Error-{threading.current_thread().name}] 网络错误: {e}")
            retries += 1
        print(f"[Thread-{threading.current_thread().name}] 超过最大重试次数，预约失败。")

    def prepare(self):
        self.accNo = util.login(self.session, self.username, self.password)
        self.resvMember = [self.accNo]
        if 'other_ids' in self.room_info:
            for other_id in self.room_info['other_ids']:
                self.resvMember.append(
                    self.session.get(f'http://libbooking.gzhu.edu.cn/ic-web/account/getMembers?key={other_id}&page=1'
                                     f'&pageNum=10').json().get('data')[0].get('accNo')
                )
        all_time = self.room_info['time']
        select_day = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
        week_index = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%A')
        select_time_list: List[str] = all_time[week_index]
        for select_time in select_time_list:
            resvBeginTime = select_day + " " + select_time.split('-')[0]
            resvEndTime = select_day + " " + select_time.split('-')[1]
            event = threading.Event()  # 创建事件
            for index, devId in enumerate(self.room_info['dev_ids']):
                postData = {
                    "sysKind": 1,
                    "appAccNo": self.accNo,
                    "memberKind": len(self.resvMember),
                    "resvBeginTime": resvBeginTime,
                    "resvEndTime": resvEndTime,
                    "testName": "学习",
                    "resvKind": 2, "resvProperty": 0, "appUrl": "",
                    "resvMember": self.resvMember, "resvDev": [devId],
                    "memo": "", "captcha": "", "addServices": [],
                }
                # 将共享的 event 传递给每个线程
                self.tasks.append(
                    threading.Thread(target=self.PostReserve,
                                     args=(postData, self.room_info['room_names'][index], event)))

    def AysnStart(self):
        [task.start() for task in self.tasks if not task.is_alive()]

    def startReserve(self, hour, minute):
        if hour is not None and minute is not None:
            util.wait_until(hour, minute - 2)
        print(self.username + "-" + datetime.datetime.now().__str__() + '\n', end='')
        self.prepare()
        if hour is not None and minute is not None:
            util.wait_until(hour, minute)
        self.AysnStart()
        print(datetime.datetime.now())
        self.session.close()


if __name__ == '__main__':
    conn = util.get_sqlite_conn()
    cursor = conn.cursor()
    userConfig = util.get_userConfig(cursor, False)
    thread_list = []
    for user in userConfig:
        thread_list.append(threading.Thread(target=StudyRoom(user).startReserve, args=(6, 30)))
    [thread.start() for thread in thread_list]
    [thread.join() for thread in thread_list]
    conn.close()
