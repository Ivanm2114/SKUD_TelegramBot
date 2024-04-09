import tinytuya
import time
# Connect to the device - replace with real values
d = tinytuya.OutletDevice('bf45653c868eec068bawzu', '192.168.10.8', 'U_tn`Qb%*Rrm#/f_')
d.set_version(3.3)

# Generate the payload to send - add all the DPS values you want to change here


# Optionally you can set separate gwId, devId and uid values
# payload=d.generate_payload(tinytuya.CONTROL, data={'1': True, '2': 50}, gwId=DEVICEID, devId=DEVICEID, uid=DEVICEID)

# Send the payload to the device
payload=d.generate_payload(tinytuya.CONTROL, {'1': 'AwAAAAMAAAMAAAE='})
print(payload)
d._send_receive(payload)