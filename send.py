import tinytuya
import time
# Connect to the device - replace with real values
d = tinytuya.OutletDevice('bfc2362c23fa6fe8a32qxv', '192.168.137.68', '?mcc<FabE]py;ViN')
d.set_version(3.3)

# Generate the payload to send - add all the DPS values you want to change here


# Optionally you can set separate gwId, devId and uid values
# payload=d.generate_payload(tinytuya.CONTROL, data={'1': True, '2': 50}, gwId=DEVICEID, devId=DEVICEID, uid=DEVICEID)

# Send the payload to the device
payload=d.generate_payload(tinytuya.CONTROL, {'1': 'AgAAAAYAAAEAAG8='})
print(payload)
d._send_receive(payload)