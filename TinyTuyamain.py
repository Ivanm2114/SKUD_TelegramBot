import tinytuya
import time

d = tinytuya.OutletDevice('bf45653c868eec068bawzu', '192.168.10.8', 'U_tn`Qb%*Rrm#/f_')
d.set_version(3.3)

STATUS_TIMER = 30
KEEPALIVE_TIMER = 12

print(" > Send Request for Status < ")
data = d.status()
print('Initial Status: %r' % data)
if data and 'Err' in data:
    print("Status request returned an error, is version %r and local key %r correct?" % (d.version, d.local_key))

print(" > Begin Monitor Loop <")
heartbeat_time = time.time() + KEEPALIVE_TIMER
status_time = None

# Uncomment if you want the monitor to constantly request status - otherwise you
# will only get updates when state changes
# status_time = time.time() + STATUS_TIMER

while (True):
    if status_time and time.time() >= status_time:
        # Uncomment if your device provides power monitoring data but it is not updating
        # Some devices require a UPDATEDPS command to force measurements of power.
        # print(" > Send DPS Update Request < ")
        # Most devices send power data on DPS indexes 18, 19 and 20
        # d.updatedps(['18','19','20'], nowait=True)
        # Some Tuya devices will not accept the DPS index values for UPDATEDPS - try:
        # payload = d.generate_payload(tinytuya.UPDATEDPS)
        # d.send(payload)

        # poll for status
        print(" > Send Request for Status < ")
        data = d.status()
        status_time = time.time() + STATUS_TIMER
        heartbeat_time = time.time() + KEEPALIVE_TIMER
    elif time.time() >= heartbeat_time:
        # send a keep-alive
        data = d.heartbeat(nowait=False)
        heartbeat_time = time.time() + KEEPALIVE_TIMER
    else:
        # no need to send anything, just listen for an asynchronous update
        data = d.receive()

    print('Received Payload: %r' % data)

    if data and 'Err' in data:
        print("Received error!")
        # rate limit retries so we don't hammer the device
        time.sleep(5)
