import requests
from datetime import datetime
from pytz import timezone


def get_user_access_by_email(email, lock_id):
    body = {'email': 'test@ex.com', 'password': '123'}

    r = requests.post("http://172.18.198.34:8000/api/v1/token/auth/", json=body)

    token = r.json()['access']

    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get("http://172.18.198.34:8000/api/v1/api/v1/users/", headers=headers)

    people = r.json()['results']

    u_id = -1

    for person in people:
        if person['email'] == email:
            u_id = person['u_id']

    r = requests.get(f"http://172.18.198.34:8000/api/v1/accesses?u_id={u_id}&lock={lock_id}", headers=headers)
    accesses = r.json()['results']
    print(accesses)
    for access in accesses:
        access_start = datetime.fromisoformat(access['access_start'])
        access_stop = datetime.fromisoformat(access['access_stop'])
        access_start.astimezone(timezone('Europe/Moscow'))
        access_stop.astimezone(timezone('Europe/Moscow'))

        if access_start < datetime.now().astimezone(timezone('Europe/Moscow')) < access_stop:
            return True
    return False


def get_user_access_by_tg(tg, lock_id):
    body = {'email': 'test@ex.com', 'password': '123'}

    r = requests.post("http://172.18.198.34:8000/api/v1/token/auth/", json=body)

    token = r.json()['access']

    headers = {"Authorization": f"Bearer {token}"}

    r = requests.get(f"http://172.18.198.34:8000/api/v1/api/v1/users/?telegram_login={tg}", headers=headers)
    if len(r.json()['results']):
        person_id = r.json()['results'][0]['u_id']
    else:
        return False

    u_id = -1

    r = requests.get(f"http://172.18.198.34:8000/api/v1/users/{person_id}/accesses/", headers=headers)
    accesses = r.json()
    for access in accesses:
        access_start = datetime.fromisoformat(access['access_start'])
        access_stop = datetime.fromisoformat(access['access_stop'])
        access_start.astimezone(timezone('Europe/Moscow'))
        access_stop.astimezone(timezone('Europe/Moscow'))

        if lock_id == access['lock'] and access_start < datetime.now().astimezone(
                timezone('Europe/Moscow')) < access_stop:
            return True
    return False

# email = 'dabrameshin@miem.hse.ru'
# print(get_user_access_by_email(email, 1))
