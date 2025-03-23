import cv2
import numpy as np
import mss
import time
from ultralytics import YOLO

# 加载训练好的 YOLO 模型
model = YOLO("./runs/detect/train52/weights/best.pt")  # 训练后的模型

# 创建 mss 对象
sct = mss.mss()

# 获取窗口的坐标
def get_window_info(window_name):
    import pygetwindow as gw
    try:
        window = gw.getWindowsWithTitle(window_name)[0]
        return {
            'left': window.left,
            'top': window.top,
            'width': window.width,
            'height': window.height
        }
    except IndexError:
        print(f"Window '{window_name}' not found.")
        return None

# 获取 MapleStory 窗口信息
window_info = get_window_info("MapleStory")
if window_info is None:
    exit()

# 主循环
while True:
    # 截取窗口图像
    img = sct.grab(window_info)
    img_np = np.array(img)

    # 转换颜色格式，从 BGRA 转换为 BGR
    frame = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

    # YOLO 预测
    results = model(frame)

    # 解析检测结果
    for r in results:
        for box in r.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow("YOLO Detection", frame)

    # 按 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cv2.destroyAllWindows()
