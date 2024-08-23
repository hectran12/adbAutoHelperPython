## GIỚI THIỆU
- Một thư viện hỗ trợ auto adb đơn giản, được tôi phát triển từ lớp 9 nhưng chưa hoàn hảo. Nên vào năm nay tôi đã fix và viết thêm document cho nó :D


## CÀI ĐẶT
- Cứ ném file này vào project của bạn là xong:D

## THƯ VIỆN CẦN THIẾT
```pip install requests opencv-python numpy easyocr```

## HƯỚNG DẪN SỬ DỤNG
1. Khởi tạo đối tượng
```python
import adb2

adb2.DEFAULT_LANGUAGE = 'vi' # set ngôn ngữ mặc định là 
adb2.GPU_SUPPORT = True # set hỗ trợ GPU (nhầm mục đích text recognition nhanh hơn)
adb2.SERVICE_OCR = 'easyocr' # pytesseract or easyocr (recommend: easyocr)
objAdb = adb2.autoDeviceADBHelper() # khởi tạo object
```

2. Thiết lập ban đầu
```python
objAdb.setDeviceId('emulator-5554') # set serial number của device
objAdb.skipConnect(True) # nếu trường hợp emulator không có port thì nên skip connect
```

3. Lấy toàn bộ máy hiện đang kết nối với máy tính
```python
allDevices = objAdb.getAllDevices() # output: [{'deviceHost': 'emulator-5554', 'status': 'device'}]
objAdb.setDeviceId(allDevices[0]['deviceHost'])
objAdb.skipConnect(True) 
```

4. Lấy text từ màn hình của máy
```python
extractText = objAdb.getTextInScreen() # lấy text từ màn hình
print(extractText)
```

5. Kiểm tra văn bản xem có trên màn hình không
```python
findText = objAdb.findText("Tìm kiếm cài đặt")
print(findText)
```

6. Click element (gồm 2 loại là hình ảnh và văn bản)
```python
if objAdb.clickElement(type="text", value="Thiết bị đã kết nối"):
    print('Click success')
else:
    print('Click failed')


# confidence: độ chính xác của việc click, giá trị càng cao thì càng chính xác
if objAdb.clickElement(type="image", value="./Screenshot_109.png", confidence=0.6):
    print('Click success')
else:
    print('Click failed')
```

7. Scroll đến khi tìm thấy văn bản
```python
if objAdb.scrollUntilFindText(text='về máy tính', checkInLine=True, roundOut=60):
    print('Scroll success')
else:
    print('Scroll failed')
```

- Ngoài ra còn nhiều tính năng nữa, hãy tự mở source và đọc, tôi đã chú thích vào đây. Có thể bạn không hiểu, xin lỗi vì trình độ tiếng anh hạn hẹp;)
- Một số tính năng bạn có thể tìm hiểu thêm:
```cài đặt APK, XAPK, swipe, scroll,..```
