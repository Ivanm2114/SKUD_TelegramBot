data = open('tuya card payload.txt')
for string in data:
    string = string.strip()
    print(list(bytearray(string, 'ascii')))
