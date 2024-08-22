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
objAdb = adb2.autoDeviceADBHelper()
```
