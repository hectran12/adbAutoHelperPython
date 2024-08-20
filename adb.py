import subprocess
import random
import string
import os
import requests
import base64
import json
import time
import cv2
import numpy as np
class adbExec:
    def __init__(self) -> None:
        return
    """
        execute: execute command
        command: command
        timeout: timeout
        return: tuple (on stdout, on stderr)

    """
    @staticmethod
    def execute (command: str, timeout: int = 100) -> tuple:
        try:
            # exec
            result = subprocess.run(command, 
                                    capture_output=True,
                                    text=True,
                                    check=True,
                                    timeout=timeout
                                    )
            
            return result.stdout.strip(), result.stderr.strip()
        
        except subprocess.CalledProcessError as e:
            return None, e.stderr.strip()
    
    @staticmethod
    def execute_powershell (script: str, timeout:int=10) -> tuple:
        try:
            result = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True)

            return result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            return None, e.stderr.strip()
        

class textDetection:
    def __init__(self) -> None:
        return
    """
        getTextInImage: get text in image
        file_path: file path
        return: dict (on text, on vertices)
    """
    @staticmethod
    def getTextInImage (file_path: str) -> dict:
        try:
            with open(file_path, "rb") as image_file:
                data_image = image_file.read()
                base64_image = base64.urlsafe_b64encode(data_image).decode()

            response = requests.post('https://ahexcommunity.com/api/gettext.php', data={"data": base64_image})
            result_data = response.json()

            return result_data

        except Exception as e:
            return str(e)
    

class ImageHandler:
    def __init__(self) -> None:
        return
    """
        findCoordinatesOnImageUsingPic: find coordinates on image using pic
        image: image
        template: template
        return: dict

    """
    @staticmethod
    def find_coordinates_on_image(image_path: str, template_path: str, confidence: float = 0.9) -> list:
        img = cv2.imread(image_path)
        template = cv2.imread(template_path)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= confidence)
        total_x, total_y = np.sum(locations[1]), np.sum(locations[0])
        avg_x = total_x / len(locations[1])
        avg_y = total_y / len(locations[0])
        coordinates = [{'x': avg_x, 'y': avg_y}]
        return coordinates

class MathHelper:
    def __init__ (self) -> None:
        return
    """
        calculateSimilarity: calculate similarity
        str1: string 1
        str2: string 2
        retrun: float
    """
    @staticmethod
    def calculateSimilarity (str1: str, str2: str) -> float:
        common_chars = sum(
            1 for ch1, ch2 in zip(str1, str2) if ch1 == ch2
        )
        total_chars = max(len(str1), len(str2))
        similarity_ratio = (common_chars / total_chars) * 100
        return similarity_ratio
    
    @staticmethod
    def calculateAverageCoordinates (vertices: list) -> dict:
        sumX = sum(v['x'] for v in vertices)
        sumY = sum(v['y'] for v in vertices)
        AvgX = sumX / len(vertices)
        AvgY = sumY / len(vertices)
        return {
            'x': AvgX,
            'y': AvgY
        }

class handleException (Exception):
    def __init__ (self, message) -> None:
        super().__init__(message)


class XAPKHelper:
    """
        WARNING: IS CLEAR OUT FOLDER PROCESS AFTER EXTRACT XAPK
    """
    def __init__ (self, pathXAPK: str = '', outFolderProcess: str = './', deviceId: str = '') -> None:
        self.pathXAPK = pathXAPK  
        self.outFolderProcess = outFolderProcess
        self.deviceId = deviceId
        self.objAdb = autoDeviceADBHelper()
        self.objAdb.setDeviceId(deviceId)
        self.objAdb.skipConnect(True)

    def clearFile (self) -> None:
        for file in os.listdir(self.outFolderProcess):
            os.remove(self.outFolderProcess + file)
            
    def extractXAPK (self) -> bool:
        try:
            with zipfile.ZipFile(self.pathXAPK, 'r') as zip_ref:
                zip_ref.extractall(self.outFolderProcess)

            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
        
    def copyObb (self, obbFolder: str, packageName: str) -> None:
        try:
            obbDestPath = f'/sdcard/Android/obb/{packageName}/'
            self.objAdb.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'mkdir', '-p', obbDestPath])
            for file in os.listdir(obbFolder):
                filePath = os.path.join(obbFolder, file)
                self.objAdb.objAdb.execute(['adb', '-s', self.deviceId, 'push', filePath, obbDestPath])
            
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    
    def actionInstall (self) -> bool:
        try:
            self.clearFile()
            self.extractXAPK()


            listAPKFiles = []
            listObbFolders = []

            for root, dirs, files in os.walk(self.outFolderProcess):
                for file in files:
                    if file.endswith('.apk'):
                        apkFile = os.path.join(root, file)
                        listAPKFiles.append(apkFile)
                    if file.endswith('.obb'):
                        obbFolder = os.path.join(root, file)
                        packageName = file.split('.')[0]
                        listObbFolders.append({
                            'obbFolder': obbFolder,
                            'packageName': packageName
                        })

            if len(listAPKFiles) == 0:
                raise handleException('An error occurred: No APK file found')
            
            for apkFile in listAPKFiles:
                self.objAdb.installApk(apkFile)

            for obb in listObbFolders:
                self.copyObb(obb['obbFolder'], obb['packageName'])


        
        except Exception as e:
            raise handleException(f'An error occurred: {e}')


class autoDeviceADBHelper:
    def __init__(self, deviceId: str = '') -> None:
        self.deviceId = deviceId
        self.objAdb = adbExec()
        self.deviceInfo = {}
        self.textDetection = textDetection()
        self.MathHelper = MathHelper()
        self.imageHandler = ImageHandler()
        self.skipConnectADB = False
        self.systemPackageAlawaysActive = ["com.android.systemui", "com.android.settings", "com.android.systemui.recents"
                                      ,"com.google.android.packageinstaller", "com.sec.android.app.launcher.activities.LauncherActivity",
                                      'com.android.settings.FallbackHome', 'com.samsung.rtlassistant']
        self.pathOut = './'

    """
        skipConnect: skip connect
        @param status: status
    """
    def skipConnect (self, status: bool) -> None:
        self.skipConnectADB = status

    """
        reConnectServer: reconnect server
    """
    def reConnectServer (self) -> None:
        self.objAdb.execute(['adb', 'kill-server'])
        self.objAdb.execute(['adb', 'start-server'])
    """
        checkInstallADB: check install adb
    """
    def checkInstallADB (self) -> bool:
        result, err = self.objAdb.execute(['adb', 'version'])
        if err:
            return False
        else:
            return True
    """
        getAllDevices: get all devices
    """
    def getAllDevices (self) -> list:
        result, err = self.objAdb.execute(
            ['adb', 'devices']
        )
        if err:
            raise handleException('An error occurred: maybe adb isn\'t working')
        else:
            result = result.replace('List of devices attached\n', '')
            if result == 'List of devices attached': return []
            allDevices = []
            for device in result.split("\n"):
                if device != "":
                    device = device.replace('\t', ' ')

                 
                    deviceHost = device.split(' ')[0]
                    deviceStatus = device.split(' ')[1]
                    allDevices.append({
                        'deviceHost': deviceHost,
                        'status': deviceStatus
                    })
            return allDevices
    """
        setDeviceId: set device id
    """
    def setDeviceId (self, deviceId) -> None:
        self.deviceId = deviceId
    """
        setPathOut: set path out
    """
    def setPathOut (self, pathOut) -> None:
        self.pathOut = pathOut

    """
        findDevice: find device
    """
    def findDevice (self) -> bool:
        if self.deviceId == '':
            raise handleException('An error occurred: no device specified to search')
        devices = self.getAllDevices()
        for device in devices:
        
            if self.deviceId in device['deviceHost']:
                return True 
        return False
    """
        connect: connect to device
    """
    def connect (self) -> bool:
        if self.skipConnectADB:
            return True
        
        try:
            port = self.deviceId.split(':')[1]
            if port.isdigit() == False:
                raise handleException('An error occurred: port case is not a number, so it cannot be connected')
            conn, err = self.objAdb.execute([
                'adb', 'forward', f'tcp:{port}', f'tcp:{port}'
            ])
            if err:
                raise handleException(f'An error occurred: An error occurred during command execution {err}')
            
            if (conn == ''):
                return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')

        return False
    
    """
        getInfoDevice: get information of device
        @return: dict

    """
    def getInfoDevice (self) -> dict:
        if self.connect() == False:
            raise handleException('An error has occurred: Unable to connect to the device to get information')
        
        androidVersion, err = self.objAdb.execute([
            'adb', '-s', self.deviceId,  'shell', 'getprop', 'ro.build.version.release'
        ])
        if err:
            raise handleException('An error occurred: Unable to get Android version information')
        
        androidName, err = self.objAdb.execute([
            'adb', '-s', self.deviceId, 'shell', 'getprop', 'ro.product.model'
        ])

        if err:
            raise handleException('An error occurred: Could not get phone name information')
        
        androidManufacturer, err = self.objAdb.execute([
            'adb', '-s', self.deviceId, 'shell', 'getprop', 'ro.product.manufacturer'
        ])

        if err:
            raise handleException('An error occurred: Unable to get manufacturer information')
        
        androidSerial, err = self.objAdb.execute([
            'adb', '-s', self.deviceId, 'shell', 'getprop', 'ro.serialno'
        ])

        if err:
            raise handleException('An error occurred: Unable to get the serial number')
        
        androidBuildNumber, err = self.objAdb.execute([
            'adb', '-s', self.deviceId, 'shell', 'getprop', 'ro.build.display.id'
        ])

        if err:
            raise handleException('An error occurred: Could not get build number')
        

        self.deviceInfo['androidVersion'] = androidVersion
        self.deviceInfo['androidName'] = androidName
        self.deviceInfo['androidManufacturer'] = androidManufacturer
        self.deviceInfo['androidSerial'] = androidSerial
        self.deviceInfo['androidBuildNumber'] = androidBuildNumber
        
        return self.deviceInfo
    """
        randomString: generate random string
    """
    def randomString (self, length: int = 10) -> str:
        return ''.join(random.choice(string.ascii_letters) for i in range(length))
    """
        screencap: take screenshot
        @param pathOut: path to save image
        @return: bool
    """

    def screencap (self, pathOut: str) -> bool:
        imageName = self.randomString() + '-temphexnguyenadb.png'
        pathOut = pathOut + imageName
        result, err = self.objAdb.execute([
            'adb', '-s', self.deviceId, 'shell', 'screencap', '-p', '/sdcard/' + imageName
        ])
        if err:
            raise handleException('An error occurred: Unable to take screenshot')
        
        result, err = self.objAdb.execute([
            'adb', '-s', self.deviceId, 'pull', '/sdcard/' + imageName, pathOut
        ])

        # remove in device
        result, err = self.objAdb.execute([
            'adb', '-s', self.deviceId, 'shell', 'rm', '/sdcard/' + imageName
        ])
        if err:
            raise handleException('An error occurred: Unable to take screenshot')
        
        return pathOut

    """
        rmImageScreencap: remove image screencap
    """
    def rmImageScreencap (self, path) -> None:
        os.remove(path)

    """
        findText: find text in image
        @param text: text to find
        @param refind: number of times to find
        @param timeout: timeout (delay = timeout/refind)
        @param pathTemp: path to save image
        @param ratio: ratio to find text in image (default = 100, ratio calc per line in image)
        @return: bool
    """
    def findText (self, text: str, refind: int = 10, timeout: int = 30, pathTemp: str = './', ratio=100, checkInLine=False) -> bool:
        delayFind = round(timeout/refind)
        for i in range(refind):
            try:
                # screenshot
                pathImage = self.screencap(pathTemp)
                if pathImage:
                    textInImage = self.textDetection.getTextInImage(pathImage)
                    textInImage = textInImage['text']
                    
                    self.rmImageScreencap(pathImage)
                    if checkInLine:
                        if text in textInImage:
                            return True
                        
                    if ratio == 100:
                        if text == textInImage:
                            return True
                        
                    # calc ratio
                    for line in textInImage.split('\n'):
                        if line != '': 
                            calcRatio = self.MathHelper.calculateSimilarity(text, line)
                            if calcRatio >= ratio:
                                return True
                  
            except Exception as e:
                pass 

            time.sleep(delayFind)

        return False
    """
        clickElement: click element in image
        @param type: type of element (text, image)
        @param value: value of element (text, path image)
        @param checkInLine: check text in line
        @param lowerMode: lower mode
        @return: bool
    """
    def clickElement (self, type: str, value: str, confidence: float = 0.9) -> bool:
        if type == 'text':
            try:
                # screen cap
                pathImage = self.screencap(self.pathOut)
                if pathImage:
                    # get all text
                    textInImage = self.textDetection.getTextInImage(pathImage)
                    self.deleteAllFileTemp()
                    target_vertices = []

                    for page in textInImage["pages"]:
                        for block in page["blocks"]:
                            for paragraph in block["paragraphs"]:
                                text = ""
                                for word in paragraph["words"]:
                                    for symbol in word["symbols"]:
                                        text += symbol["text"]
                                    text += " "
                            
                                if value in text:
                                    target_vertices.append(paragraph["boundingBox"]["vertices"])
                    
                    if len(target_vertices) > 0:
                        for vertices in target_vertices:
                            coordinates = self.MathHelper.calculateAverageCoordinates(vertices)
                            # click tap
                            self.objAdb.execute([
                                'adb', '-s', self.deviceId, 'shell', 'input', 'tap', str(coordinates['x']), str(coordinates['y'])
                            ])
                        return True
                    
                    else:
                        return False
            except Exception as e:
                raise handleException(f'An error occurred: {e}')
        elif type == 'image':
            try:
                # screen cap
                pathImage = self.screencap(self.pathOut)
                if pathImage:
                    # find coordinates
                    coordinates = self.imageHandler.find_coordinates_on_image(pathImage, value, confidence)
                    
                    if len(coordinates) > 0:
                        # click tap
                        self.objAdb.execute([
                            'adb', '-s', self.deviceId, 'shell', 'input', 'tap', str(coordinates[0]['x']), str(coordinates[0]['y'])
                        ])
                        self.deleteAllFileTemp()
                        return True
                    else:
                        self.deleteAllFileTemp
                        return False
            except Exception as e:
                raise handleException(f'An error occurred: {e}')


    """
        sendKeys: send keys to device
        @param content: content send
        @param delay: delay send
        @return: bool
    """
    def sendKeys(self, content: str, delay: int=0) -> bool:
        try:
            char_to_keyevent_map = {
                ' ': '62',
                '\n': '66'
            }

            for char in content:
                keyevent = char_to_keyevent_map.get(char.lower())
                if keyevent:
                    self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'keyevent', keyevent])
                else:
                    self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'text', char])
                time.sleep(delay)
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        installApk: install apk
        @param path: path apk
        @return: bool
    """
    def installApk (self, path: str, timeout=2000) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'install', path], timeout=timeout)
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
        

    """
        uninstallApk: uninstall apk
        @param packageName: package name
        @return: bool
    """
    def uninstallApp (self, packageName: str) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'uninstall', packageName])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
        
    """
        getPackageInstalled: get package installed
        @return: list

    """

    def getPackageInstalled (self) -> list:
        try:
            result, err = self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'pm', 'list', 'packages'])
            if err:
                raise handleException(f'An error occurred: {err}')
            else:
                packages = []
                for pack in result.split('\n'):
                    if pack != '':
                        # remove index
                        pack = pack.replace('package:', '')
                        packages.append(pack)
                return packages
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        openApp: open app
        @param packageName: package name
        @return: bool
    """
    def openApp (self, packageName) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'monkey', '-p', packageName, '-c', 'android.intent.category.LAUNCHER', '2'])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        dumpXML: dump xml
        @return: str
    """
    def dumpXML (self) -> str:
        try:
            name_file = self.randomString() + '.xml'
            result, err = self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'uiautomator', 'dump'])
            if err:
                raise handleException(f'An error occurred: {err}')
            else:
                result, err = self.objAdb.execute(['adb', '-s', self.deviceId, 'pull', '/sdcard/window_dump.xml', self.pathOut + name_file])
                if err:
                    raise handleException(f'An error occurred: {err}')
                else:
                    # read data and remove
                    with open(self.pathOut + name_file, 'r') as f:
                        data = f.read()
                    os.remove(self.pathOut + name_file)
                    return data
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        tap: tap
        @param x: x
        @param y: y

    """
    def tap (self, x: int, y: int) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'tap', str(x), str(y)])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        swipe: swipe
        @param x1: x1
        @param y1: y1
    """
    def rotateScreen(self) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'content', 'insert', '--uri', 'content://settings/system', '--bind', 'name:s:user_rotation', '--bind', 'value:i:1'])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        swipe: swipe
        @param x1: x1
        @param y1: y1
        @param x2: x2
        @param y2: y2
        @param timeScroll: time scroll
        (timeScroll - milliseconds)
    """
    def scroll(self, x1: int = 100, y1: int = 500, x2: int = 100, y2: int = 300, timeScroll: int = 500) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(timeScroll)])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        scrollUntilFindText: scroll until find text
        @param x1: x1
        @param y1: y1
        @param x2: x2
        @param y2: y2
        @param timeScroll: time scroll
        @param text: text

    """
    def scrollUntilFindText (self,
                            x1: int = 100,
                            y1: int = 500,
                            x2: int = 100,
                            y2: int = 300,
                            timeScroll: int = 500,
                            text=''
                             ):
        try:
            while True:
                if self.findText(text=text, refind=1, timeout=1):
                    return True
                else:
                    self.scroll(x1, y1, x2, y2, timeScroll)
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
        
    """
        setPin: set pin
        @param pin: pin
        @return: bool
    """
    def setPin (self, pin: str) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'locksettings', 'set-pin', pin])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        closeApp: close app
        @param packageName: package name
        @return: bool
    """
    def closeApp (self, packageName: str) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'am', 'force-stop', packageName])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        getAllAppCurrentActive: get all app current active
        @return: list
    """
    def getAllAppCurrentActive (self) -> list:
        try:
            result, err = self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'dumpsys', 'activity', 'activities'])
            if err:
                raise handleException(f'An error occurred: {err}')
            else:
                packages = []
                for pack in result.split('\n'):
                    if pack != '':
                        # remove index
                        pack = pack.replace('package:', '')
                        packages.append(pack)
                return packages
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        closeAllTabsCurrentActive: close all tabs current active
        @return: bool
    """ 
    def closeAllTabsCurrentActive (self) -> bool:
        for app in self.getAllAppCurrentActive():
            self.closeApp(app)
        return True
    """
        unlockPhone: unlock phone
        @param pin: pin
        @return: bool
    """
    def unlockPhone (self, pin: str) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'text', pin])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        btnHomeClick: click button home
        @return: bool
    """
    def btnHomeClick (self) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'keyevent', '3'])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        btnBackClick: click button back
        @return: bool
    """
    def btnBackClick (self) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'keyevent', '4'])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        btnRecentClick: click button recent
        @return: bool
    """   
    def btnRecentClick (self) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'keyevent', '187'])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        setTimeOpenScreenContinuous: set time open screen continuous
        @return: bool
    """
    def setTimeOpenScreenContinuous (self, time: int = 130000) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'settings', 'put', 'system', 'screen_off_timeout', str(time)])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        setModeSleep: set mode sleep
        @param mode: mode
        @return: bool
    """ 
    def setModeSleep (self, mode: int = 3) -> bool:
       
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'settings', 'put', 'global', 'stay_on_while_plugged_in', str(mode)])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        setScreenBrightness: set screen brightness
        @param brightness: brightness
        @return: bool
    """
    def setScreenBrightness (self, brightness: int = 255) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'settings', 'put', 'system', 'screen_brightness', str(brightness)])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')


    """
        getNetworkSpeed: get network speed
        @return: int
    """
    def getNetworkSpeed (self) -> int:
        try:
            result, err = self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'dumpsys', 'wifi'])
            if 'Link speed:' in result:
                result = result.split('Link speed:')[1].split('Mbps')[0].strip()
                return int(result)
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    

    """
        getMemoryInfo: get memory info
        @return: int
    """
    def getMemoryInfo (self) -> int:
        try:
            result, err = self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'cat', '/proc/meminfo'])
            if err:
                raise handleException(f'An error occurred: {err}')
            self.ramInfo = {}
            for x in result.split('\n'):
                name = x.split(':')[0].strip()
                value = x.split(':')[1].strip().split(' ')[0]
                self.ramInfo[name] = value

            return self.ramInfo
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        getMultiTasking: get multi tasking
        @return: list
    """
    def getMultiTasking (self) -> list:
        powershellScript = """
            $recents = (adb shell dumpsys activity recents)
            $recents | Select-String "Recent #" | ForEach-Object { "[{0}]" -f $_.ToString() }
            $recents | Select-String "packageName=" | ForEach-Object { $_.ToString() -replace "packageName=", "" }
        """
        try:
            result, err = self.objAdb.execute_powershell(powershellScript)
            
            if err:
                raise handleException(f'An error occurred: {err}')
            else:
                recentCount = len(result.split('Recent #'))-1
                data = {}
                data['recentCount'] = recentCount
                data['infoTask'] = []
                for task in result.split('\n'):
                    obj = {}
                    try:
                        obj['type'] = task.split('type=')[1].split(' ')[0]
                    except:
                        pass

                    try:
                        obj['A'] = task.split('A=')[1].split(':')[0]
                    except:
                        pass
                    
                    try:
                        obj['packageName'] = 'com.' + task.split(':com.')[1].split(' ')[0]
                    except:
                        pass
                    
                    try:
                        obj['mode'] = task.split('mode=')[1].split(' ')[0]
                    except:
                        pass

                    try:
                        obj['U'] = task.split('U=')[1].split(' ')[0]
                    except:
                        pass

                    try:
                        obj['translucent'] = task.split('translucent=')[1].split(' ')[0]
                    except:
                        pass

                    try:
                        obj['sz'] = task.split('sz=')[1].split(' ')[0]
                    except:
                        pass


                    try:
                        obj['visible'] = task.split('visible=')[1].split(' ')[0]
                    except:
                        pass
                    data['infoTask'].append(obj)


                return data
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
        
    """
        checkOnlyPackageNameActive: check only package name active
        @param packageName: package name
    """
    def checkOnlyPackageNameActive (self, packageName: str) -> bool:
        multiTasks = self.getMultiTasking()
        taskInfo = multiTasks['infoTask']
        acceptPackageNames = self.systemPackageAlawaysActive.copy()
        acceptPackageNames.append(packageName)
        for task in taskInfo:
            if task['packageName'] not in acceptPackageNames:
                return False
    """
        onPhone: on phone
        @return: bool
    """
    def onPhone (self) -> bool:
        try:
            result, err = self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'dumpsys', 'power'])
            if err:
                raise handleException(f'An error occurred: {err}')
            else:
                if 'Display Power: state=OFF' in result:
                    return False
                else:
                    return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        sendActivePhone: send active phone
        @return: bool
    """
    def sendActivePhone (self) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'keyevent', '26'])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
        
    """
        swipeToOpen: swipe to open
        @return: bool
    """
    def swipeToOpen (self) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'swipe', '500', '1000', '500', '100'])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        getTextInScreen: get text in screen
        @return: bool
    """
    def getTextInScreen (self) -> bool:
        try:
            # screen cap
            pathImage = self.screencap(self.pathOut)
            if pathImage:
                # get all text
                textInImage = self.textDetection.getTextInImage(pathImage)
                return textInImage['text']
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        checkScreenIsOn: check screen is on
        @return: bool
    """
    def checkScreenIsOn (self) -> bool:
        try:
            self.getTextInScreen()
            self.deleteAllFileTemp()
            return True
        except Exception as e:
            return False
    """
        deleteAllFileTemp: delete all file temp
    """
    def deleteAllFileTemp (self) -> None:
        endWith = '-temphexnguyenadb.png'
        for file in os.listdir(self.pathOut):
            if file.endswith(endWith):
                os.remove(self.pathOut + file)


    """
        findCoordinatesByText: find coordinates by text 
    """
    def findCoordinatesByText (self, textFind, checkInLine=True) -> dict:
        try:
            # screen cap
            pathImage = self.screencap(self.pathOut)
            if pathImage:
                # get all text
                textInImage = self.textDetection.getTextInImage(pathImage)
                print(textInImage)
                self.deleteAllFileTemp()
                target_vertices = []

                for page in textInImage["pages"]:
                    for block in page["blocks"]:
                        for paragraph in block["paragraphs"]:
                            text = ""
                            for word in paragraph["words"]:
                                for symbol in word["symbols"]:
                                    text += symbol["text"]
                                text += " "
                            if checkInLine:
                                if textFind in text or textFind == text:
                                    target_vertices.append(paragraph["boundingBox"]["vertices"])
                            else:
                                print(textFind, text)
                                if textFind.strip() == text.strip():
                                    target_vertices.append(paragraph["boundingBox"]["vertices"])
                if len(target_vertices) > 0:
                    for vertices in target_vertices:
                        coordinates = self.MathHelper.calculateAverageCoordinates(vertices)
                        return coordinates
                    
                else:
                    return None
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    
    """
        sendKeyevent: send keyevent
        @param keyCode: key code
        @return: bool
    """
    def sendKeyevent (self, keyCode) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'input', 'keyevent', str(keyCode)])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')

    """
        closeAllMultiTasking: close all multi tasking
        @return: bool
    """
    def closeAllMultiTasking (self) -> bool:
        self.sendKeyevent("KEYCODE_APP_SWITCH")
        if self.findText('Close all', timeout=3, refind=3):
            self.clickElement('text', 'Close all')
            return True
        else:
            return False

    """
        push: push file to android  
        @param pathImageComputer: path image computer
        @param pathToAndroid: path to android
        @return: bool
    """
    def push(self, pathImageComputer: str, pathToAndroid: str) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'push', pathImageComputer, pathToAndroid])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
    """
        openLink: open link
        @param link: link
        @return: bool
    """
    def openLink (self, link: str) -> bool:
        try:
            self.objAdb.execute(['adb', '-s', self.deviceId, 'shell', 'am', 'start', '-a', 'android.intent.action.VIEW', '-d', link])
            return True
        except Exception as e:
            raise handleException(f'An error occurred: {e}')
