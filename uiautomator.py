import time
import datetime
import random
import uiautomator2 as u2

# d = u2.connect('872QEDU82***')  # usb连接
d = u2.connect('172.18.229.168:5555') # wifi连接
d.app_start('com.duolingo')