# user_config.json总体结构
```json
[
  //第一个用户
  {
    "username": "...",
    "password": "...",
    "seat_info": { ... },
    "room_info": { ... }
  }, 
  //第n个用户
  {
    "username": "...",
    "password": "...",
    "seat_info": { ... },
    "room_info": { ... }
  }

]

```
## `username`
个人学号
## `password`
个人融合门户密码
## `seat_info`
预约座位信息
```json
"seat_info": {
  "seat_name": "座位号（例101-001）",
  "time": { ... }
}
```
+ `seat_name`：用户指定的座位编号

+ `time`：每天的预约时间段，按星期划分。
  + `key`：星期名（Monday、Tuesday、...、Sunday）
  + `value`：该天预约的时间段列表。每个时间段为字符串，格式为 "开始时间-结束时间"，时间格式为 `HH:MM:SS`。
```json
"time": {
  "Monday": [
    "9:30:00-13:30:00",
    "13:30:00-17:30:00",
    "17:30:00-21:30:00"
  ],
  ...
}
```
## `room_info`
预约研讨室信息
```json
"room_info": {
  "room_names": [ ... ],
  "time": { ... },
  "other_ids":[...](可选，一些研讨室需要多人预约)
}
```
+ `room_names`：房间名称列表，可选多个研讨间。例如：
```json
"room_names": [
  "研讨间A(例子)",
  "研讨间B(例子)"
]
```
+ `time`：与 `seat_info` 的 `time` 结构一致，按星期分，每天可能有多个预约时间段。
+ `other_ids`：其他用户的学号列表，可选项，一些研讨室需要多人预约。例如：
```json
"other_ids": [
  "2021000001",
  "2021000002"
]
```