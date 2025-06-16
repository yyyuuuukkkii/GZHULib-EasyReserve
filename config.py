query = {
    'seat_dev_id_query': "SELECT dev_id FROM lib_seat WHERE name = ?",
    'room_dev_id_query': "SELECT dev_id FROM lib_room WHERE name IN ({placeholders})"
}
url = {
    'publicKey': 'http://libbooking.gzhu.edu.cn/ic-web/login/publicKey',
    'seatMenu': 'http://libbooking.gzhu.edu.cn/ic-web/seatMenu',
    'seatSign': 'http://libbooking.gzhu.edu.cn/ic-web/phoneSeatReserve/sign',
    'reserve': 'http://libbooking.gzhu.edu.cn/ic-web/reserve',
    'userInfo': 'http://libbooking.gzhu.edu.cn/ic-web/auth/userInfo',
    'roomMenu': 'http://libbooking.gzhu.edu.cn/ic-web/roomMenu',
    'roomSign': 'http://libbooking.gzhu.edu.cn/ic-web/pad/accountByQR',
    'resvInfo': 'http://libbooking.gzhu.edu.cn/ic-web/reserve/resvInfo',
    'userLogin': 'http://libbooking.gzhu.edu.cn/ic-web/phoneSeatReserve/login'
}
