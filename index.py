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
import pyautogui
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
    def execute (command: str, timeout: int = 10) -> tuple:
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
        # Đọc ảnh và template
        img = cv2.imread(image_path)
        template = cv2.imread(template_path)

        # Chuyển ảnh và template sang ảnh grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

        # Tìm kết quả khớp giữa template và ảnh sử dụng phương pháp so khớp (matching method)
        result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= confidence)

        # Tính tổng tọa độ của các điểm khớp
        total_x, total_y = np.sum(locations[1]), np.sum(locations[0])

        # Tính tọa độ trung bình
        avg_x = total_x / len(locations[1])
        avg_y = total_y / len(locations[0])

        # Tạo danh sách chứa tọa độ trung bình của các điểm khớp
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


class autoDeviceADBHelper:
    def __init__(self, deviceId: str = '') -> None:
        self.deviceId = deviceId
        self.objAdb = adbExec()
        self.deviceInfo = {}
        self.textDetection = textDetection()
        self.MathHelper = MathHelper()
        self.imageHandler = ImageHandler()
        self.pathOut = './'
    """
        reConnectServer: reconnect server
    """
    def reConnectServer (self) -> None:
        self.objAdb.execute(['adb', 'kill-server'])
        self.objAdb.execute(['adb', 'start-server'])

    
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
        imageName = self.randomString() + '.png'
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
    def clickElement (self, type: str, value: str, checkInLine=False, lowerMode=False, confidence: float = 0.9, indexClick=0, clickAll=False) -> bool:
        if type == 'text':
            try:
                # screen cap
                pathImage = self.screencap(self.pathOut)
                if pathImage:
                    data = self.textDetection.getTextInImage(pathImage)
                    self.rmImageScreencap(pathImage)
                    result = []
                 
                    for page in data['pages']:
                        for block in page['blocks']:
                            if block['blockType'] == "TEXT":
                                for paragraph in block['paragraphs']:
                                    lines = []
                                    for word in paragraph['words']:
                                        text = ''.join(symbol['text'] for symbol in word['symbols'])
                                        coordinates = self.MathHelper.calculateAverageCoordinates(word['boundingBox']['vertices'])
                                        lines.append({'text': text, 'coordinates': coordinates})

                                    full_text = ' '.join(line['text'] for line in lines)
                                    average_xy = self.MathHelper.calculateAverageCoordinates([line['coordinates'] for line in lines])
                                    result.append({'fullText': full_text, 'xy': average_xy})

                    print(result)
                    if lowerMode:
                        value = value.lower()
                        statusIsClick = False
                        indexCurrentElement = 0
                        for item in result:
                            if checkInLine:
                                
                                if value in item['fullText'].lower():
                                    if indexCurrentElement == indexClick:
                                        self.objAdb.execute([
                                            'adb', '-s', self.deviceId, 'shell', 'input', 'tap', str(item['xy']['x']), str(item['xy']['y'])
                                        ])
                                        statusIsClick = True
                                        if clickAll == False:
                                            return True
                                    if clickAll == False:
                                        indexCurrentElement += 1
                                if clickAll == False:
                                    return False
                                return statusIsClick
                            else:
                               
                                if value == item['fullText'].lower():
                                    if indexCurrentElement == indexClick:
                                        self.objAdb.execute([
                                            'adb', '-s', self.deviceId, 'shell', 'input', 'tap', str(item['xy']['x']), str(item['xy']['y'])
                                        ])
                                    
                                        statusIsClick = True
                                        if clickAll == False:
                                            return True
                                    if clickAll == False:
                                        indexCurrentElement += 1
                                if clickAll == False:
                                    return False
                                return statusIsClick
                    else:
                        statusIsClick = False
                        indexCurrentElement = 0
                        for item in result:
                            if checkInLine:
                                
                                if value in item['fullText']:
                                    statusIsClick = True
                                    if indexCurrentElement == indexClick:
                                        self.objAdb.execute([
                                            'adb', '-s', self.deviceId, 'shell', 'input', 'tap', str(item['xy']['x']), str(item['xy']['y'])
                                        ])
                                        if clickAll == False:
                                            return True
                                    if clickAll == False:
                                        indexCurrentElement += 1
                                if clickAll == False:
                                    return False
                                return statusIsClick
                            else:
                                if value == item['fullText']:
                                    statusIsClick = True
                                    if indexCurrentElement == indexClick:
                                        self.objAdb.execute([
                                            'adb', '-s', self.deviceId, 'shell', 'input', 'tap', str(item['xy']['x']), str(item['xy']['y'])
                                        ])
                                        if clickAll == False:
                                            return True
                                    if clickAll == False:
                                        indexCurrentElement += 1
                                if clickAll == False:
                                    return False
                                return statusIsClick
                                
                return False
            except Exception as e:
                raise handleException(f'An error occurred: {e}')
        elif type == 'image':
            try:
                pathImage = self.screencap(self.pathOut)
                if pathImage:
                    pathFind = value 
                    if not os.path.isfile(pathFind):
                        raise handleException('An error occurred: File not found')
                    
                    result = self.imageHandler.find_coordinates_on_image(pathImage, pathFind, confidence)
                    
                    self.rmImageScreencap(pathImage)
                    if result:
                        for condi in result:
                            x = str(condi['x'])
                            y = str(condi['y'])
                            self.objAdb.execute([
                                'adb', '-s', self.deviceId, 'shell', 'input', 'tap', x, y
                            ])
                            
                        return True
                    return False
                else:
                    raise handleException('An error occurred: Unable to take screenshot')
                    
            except Exception as e:
                raise handleException(f'An error occurred: {e}')
        else:
            raise handleException('Type not support')
    


    """
        sendKeys: send keys to device
        @param content: content send
        @param delay: delay send
        @return: bool
    """
    def sendKeys(self, content: str, delay: int=0) -> bool:
        try:
            char_to_keyevent_map = {
                ' ': '62'
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




obj = autoDeviceADBHelper()

allDevices = obj.getAllDevices()

obj.setDeviceId(allDevices[0]["deviceHost"])

if obj.findText('Galaxy Store', checkInLine=True, refind=5, timeout=5):
    print('Đã tìm thấy')
    obj.clickElement('text', 'Galaxy Store', checkInLine=False)
else:
    print('Không tìm thấy')

#obj.clickElement('image', r'D:\Downloads\khjkhkhjk\backup\project_py\adbPython\HuJxtbPDNd.png', confidence=0.9)
#print(obj.clickElement('text', 'genshin impact', lowerMode=True, checkInLine=True))
# find = obj.findText(
#     text='Galaxy Store',
#     refind=5,
#     pathTemp='./',
#     checkInLine=False,
#     ratio=90,
#     timeout=5
# )
# print(find)
# screenPath = obj.screencap('./')
# if screenPath:
#     print('Success: ' + screenPath)
#     #obj.rmImageScreencap(screenPath)


#test connect
# if obj.connect():
#     print('Connect: success')
# else:
#     print('Connect: failed')


# if obj.findDevice():
#     print('Device: find it')
# else:
#     print('Device: not found')


