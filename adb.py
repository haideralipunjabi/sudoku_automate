from ppadb.client import Client

def connect_device():
    adb = Client(host='127.0.0.1',port=5037)
    devices = adb.devices()

    if len(devices) == 0:
        print("No Devices Attached")
        quit()
    return devices[0]

def take_screenshot(device):
    image = device.screencap()
    with open('screen.png', 'wb') as f:
        f.write(image)