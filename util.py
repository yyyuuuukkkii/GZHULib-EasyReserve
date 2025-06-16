import base64
import datetime
import sqlite3
import time
from sqlite3 import Connection, Cursor
from typing import List, Dict, Any, Optional

import requests
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pksc1_v1_5
from Crypto.PublicKey import RSA

import config


def wait_until(hour: int, minute: int, second: int = 0, microsecond: int = 0) -> None:
    now: datetime.datetime = datetime.datetime.now()
    target_time: datetime.datetime = now.replace(hour=hour, minute=minute, second=second, microsecond=microsecond)
    if target_time < now:
        return
    wait_time: float = (target_time - now).total_seconds()
    time.sleep(wait_time)


def encrypt(password: str, public_key: str) -> str:
    rsakey: RSA.RsaKey = RSA.importKey(public_key)
    cipher: Cipher_pksc1_v1_5 = Cipher_pksc1_v1_5.new(rsakey)
    cipher_text: bytes = base64.b64encode(cipher.encrypt(password.encode()))
    return cipher_text.decode()


def get_userConfig(cursor: Cursor, isSeat=True) -> List[Dict[str, Any]]:
    import json
    with open('user_config_example.json', 'r', encoding='utf-8') as f:
        userConfig: List[Dict[str, Any]] = json.load(f)
    valid_userConfig = []
    for user in userConfig:
        seatInfo: Optional[dict] = user.get('seat_info')
        roomInfo: Optional[dict] = user.get('room_info')
        if isSeat and seatInfo is not None:
            seatName: str = seatInfo['seat_name']
            devId: int = cursor.execute(config.query['seat_dev_id_query'], (seatName,)).fetchone()[0]
            seatInfo.update({'seat_name': seatName, 'dev_id': devId})
            valid_userConfig.append(user)

        elif not isSeat and roomInfo is not None:
            roomNames: str = roomInfo['room_names']
            placeholders = ','.join(['?'] * len(roomNames))  # 根据列表长度生成占位符
            room_dev_id_query = config.query['room_dev_id_query'].format(placeholders=placeholders)
            devIds: List[int] = [devId[0] for devId in cursor.execute(room_dev_id_query, roomNames).fetchall()]
            if roomInfo.get('is_reverse', False):
                devIds.reverse()
                roomNames.reverse()
            roomInfo.update({'room_names': roomNames, 'dev_ids': devIds})
            valid_userConfig.append(user)
    return valid_userConfig


def getSearchURL(resvDates: str, page: int, pageSize: int, labIds: str) -> str:
    return 'http://libbooking.gzhu.edu.cn/ic-web/reserve?sysKind=1&resvDates={}&page={}&pageSize={}&labIds={}&kindId='.format(
        resvDates, page, pageSize, labIds)


def login(session: requests.Session, username: str, password: str) -> Optional[int]:
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50',
        'Referer': 'http://libbooking.gzhu.edu.cn/',
        'Host': 'libbooking.gzhu.edu.cn'})
    r1: Dict[str, Any] = session.get(config.url['publicKey'], verify=False).json()
    key: Dict[str, str] = r1.get('data')
    publicKey: str = key['publicKey']
    nonceStr: str = key['nonceStr']
    psd: str = '{};{}'.format(password, nonceStr)
    public_key: str = '-----BEGIN PUBLIC KEY-----\n' + publicKey + '\n-----END PUBLIC KEY-----'
    password = encrypt(psd, public_key)
    login_data: Dict[str, Any] = {
        "bind": 0,
        "logonName": username,
        "password": password,
        "type": "",
        "unionId": ""
    }
    res: requests.Response = session.post(config.url['userLogin'],
                                          json=login_data, verify=False)
    data: Dict[str, Any] = session.get(url=config.url['userInfo'], verify=False).json()
    if data['message'] == '查询成功':
        session.headers.update({
            'token': data['data']['token']
        })
        print(username + '自习室系统登录成功\n', end='')
        return data['data']['accNo']
    else:
        print(username + '自习室系统登录失败\n', end='')
        print(data['message'])
        return None


def get_sqlite_conn(db_name: str = 'campus.db') -> Connection:
    conn = sqlite3.connect(db_name)
    return conn
