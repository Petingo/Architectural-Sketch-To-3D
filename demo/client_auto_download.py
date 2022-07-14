# import json
# import socket

# HOST = "127.0.0.1"  # The server's hostname or IP address
# PORT = 5000  # The port used by the server

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b'link_uid {"old_uid": 123, "new_uid": 456}')
#     data = s.recv(1024)

# print(f"Received {data!r}")

import json
import socketio
import logging
import requests
import time
import sys

print("Start with ID: ", sys.argv[1])
print("URL: ", sys.argv[2])

new_uid = sys.argv[1]

sio = socketio.Client()

@sio.on('assign_id')
def handle_assign_id(data):
    uid = data['uid']
    sketch_id = data['sketch_id']
    logging.warning('uid & sketch id', uid, sketch_id)
    flag = True
    while flag:
        try:
            sio.emit('link_uid', data=json.dumps({"old_uid": uid, "new_uid": str(new_uid)}))
            flag = False
        except:
            pass

@sio.on('update_3d')
def handle_update_3d(data):
    sketch_id = data['sketch_id']
    url = os.path.join(sys.argv[2], f'/objs/{sketch_id}.obj')
    logging.warning('update 3d: url', url)
    file = requests.get(url)
    print(file.text)
    print(time.time())
    open('/mnt/c/Users/Petingo/Downloads/obj_temp/test.obj', 'wb').write(file.content)

# sio.on('assign_id', handler=handle_assign_id)
# sio.on('update_3d', handler=handle_update_3d)

sio.connect(sys.argv[2], wait=True, wait_timeout=1, namespaces=['/'])
