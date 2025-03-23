from ultralytics import YOLO
import cv2

# 加载训练好的 YOLO 模型
model = YOLO('./runs/detect/train52/weights/best.pt')  # 替换为你的模型路径

# 读取要推理的图像
image_path = "./datasets/train/images/Maple_250321_091229.jpg"  # 替换为你的图片路径
image = cv2.imread(image_path)

# 进行目标检测
results = model(image)

# 定义类别颜色（可以根据需要修改）
class_colors = {
    0: (0, 255, 0),  # 类别 0 的颜色（例如蜗牛，绿色）
    1: (0, 0, 255),  # 类别 1 的颜色（例如角色，红色）
}

# 遍历检测结果并绘制边界框
for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # 获取边界框坐标
        conf = box.conf[0].item()  # 置信度
        class_id = int(box.cls[0])  # 类别 ID
        label = result.names[class_id]  # 类别标签

        # 根据类别 ID 选择颜色
        color = class_colors.get(class_id, (255, 255, 255))  # 默认白色

        # 画框
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, f'{label} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# 显示图像
cv2.imshow('YOLO Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()