import json
import tinytuya


class Lock:
    def __init__(self, room, room_id, device_id, address, local_key):
        self.room = room
        self.device_id = device_id
        self.address = address
        self.local_key = local_key
        self.room_id = room_id
        self.users = {}
        self.d = tinytuya.OutletDevice(self.device_id,
                                       self.address,
                                       self.local_key)
        self.d.set_version(3.3)
        print(f" > Send Request for Status of Lock {self.room} < ")
        data = self.d.status()
        print(f'Initial Status of Lock {self.room}: %r' % data)

    def sync_users(self):
        with open('users.json') as f:
            users = json.load(f)
            if self.room in users.keys():
                self.users = users[self.room]

    def add_user(self, user_id):
        self.users[str(user_id)] = {}

    def add_fingerprint(self, user):
        payload = self.d.generate_payload(tinytuya.CONTROL, {'1': 'AwABAAEAAAMAAAE='})
        self.d._send_receive(payload)
        counter = 0
        while counter < 3:
            data = self.d.receive()
            if data:
                if 'dps' in data.keys():
                    if '1' in data['dps'].keys():
                        if 'A/w' in data['dps']['1']:
                            counter += 1
                        elif 'A/0' in data['dps']['1']:
                            break
        data = self.d.receive()
        if 'A/8' in data['dps']['1']:
            self.users[str(user)]['fingerprint'] = data['dps']['1'][8:10]
            return True
        return False

    def get_user(self, user):
        return self.users[str(user)]

    def delete_user(self, user):
        self.delete_card(user)
        self.delete_fingerprint(user)
        del self.users[str(user)]

    def add_card(self, user):
        payload = self.d.generate_payload(tinytuya.CONTROL, {'1': 'AgABAAEAZAEAAAE='})
        self.d._send_receive(payload)
        data = self.d.receive()
        if 'Av8' in data['dps']['1']:
            self.users[str(user)]['card'] = data['dps']['1'][8:10]
            return True
        return False

    def delete_fingerprint(self, user):
        if "fingerprint" in self.users[str(user)]:
            payload = self.d.generate_payload(tinytuya.CONTROL,
                                              {'2': f'AwAAAAMA{self.users[str(user)]["fingerprint"]}H/'})
            self.d._send_receive(payload)
            del self.users[str(user)]['fingerprint']

    def delete_card(self, user):
        if "card" in self.users[str(user)].keys():
            payload = self.d.generate_payload(tinytuya.CONTROL,
                                              {'2': f'AgAAAAMA{self.users[str(user)]["card"]}H/'})
            self.d._send_receive(payload)
            del self.users[str(user)]['card']

    def get_users(self):
        return self.users

    def get_room(self):
        return self.room
