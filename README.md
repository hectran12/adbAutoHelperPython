# adbAutoHelperPython
Hỗ trợ ADB Python
# Repo này mình lười viết demo , docs các bạn chịu khó mò nha. Mình viết cái này lúc đang cần phục vụ cho công việc, sau không cần nữa nên mình up vui vui thui.
<pre>
from adb import autoDeviceADBHelper


obj = autoDeviceADBHelper()
device = obj.getAllDevices()[0]['deviceHost']
obj.setDeviceId(device)
obj.skipConnect(True)

if obj.connect():
    print('[', device, '] Connected')

    infoDevice = obj.getInfoDevice()
    for key in infoDevice:
        print(key, ':', infoDevice[key])

    speedInternet = obj.getNetworkSpeed()
    print('Speed Internet: ' + str(speedInternet) + 'Mbps')
    apps = obj.getPackageInstalled()
    print(apps)
</pre>
