# Список контейнеров

Выводит информацию обо всех контейнерах.

**URL** : `/api/containers`

**Method** : `GET`

**Auth required** : YES

**Permissions required** : None

**Data constraints** : `{}`

## Success Responses

**Code** : `200 OK`

**Content** : `{[]}`

```json
[
    {
        "id": 2,
        "kind": 1,
        "mass": 10,
        "building": {
            "id": 1,
            "address": "Кронверкский 49"
        },
        "building_part": {
            "id": 1,
            "num": 1
        },
        "floor": 3,
        "room": "1303",
        "description": "У окна",
        "is_full": true,
        "status": 2,
        "requested_activation": false,
        "email": "",
        "phone": "",
        "cur_fill_time": null,
        "cur_takeout_wait_time": "1124324.785517",
        "avg_fill_time": null,
        "avg_takeout_wait_time": null
    },
    {
        "id": 7,
        "kind": 1,
        "mass": 10,
        "building": {
            "id": 1,
            "address": "Кронверкский 49"
        },
        "building_part": {
            "id": 1,
            "num": 1
        },
        "floor": 3,
        "room": "",
        "description": "",
        "is_full": false,
        "status": 2,
        "requested_activation": false,
        "email": "test@test.com",
        "phone": "89999999999",
        "cur_fill_time": "925435.254573",
        "cur_takeout_wait_time": null,
        "avg_fill_time": null,
        "avg_takeout_wait_time": null
    },
    {
        "id": 1,
        "kind": 1,
        "mass": 10,
        "building": {
            "id": 1,
            "address": "Кронверкский 49"
        },
        "building_part": {
            "id": 1,
            "num": 1
        },
        "floor": 6,
        "room": "1600",
        "description": "",
        "is_full": true,
        "status": 2,
        "requested_activation": false,
        "email": "",
        "phone": "",
        "cur_fill_time": null,
        "cur_takeout_wait_time": "925301.341255",
        "avg_fill_time": "00:03:46.836039",
        "avg_takeout_wait_time": "17:47:14.078495"
    },
    {
        "id": 42,
        "kind": 2,
        "mass": 15,
        "building": {
            "id": 1,
            "address": "Кронверкский 49"
        },
        "building_part": {
            "id": 2,
            "num": 2
        },
        "floor": 3,
        "room": "2301",
        "description": "в центре аудитории",
        "is_full": false,
        "status": 2,
        "requested_activation": false,
        "email": "test@test.com",
        "phone": "89999999999",
        "cur_fill_time": "1031360.422812",
        "cur_takeout_wait_time": null,
        "avg_fill_time": null,
        "avg_takeout_wait_time": null
    }
]
```
