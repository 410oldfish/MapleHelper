from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO("YOLOv8s.yaml")  # 你可以换成 yolov8n.yaml  (nano 版本更轻量)
    model.train(data="data.yaml",  # 数据集配置文件
    epochs=50,  # 增加epoch数量
    batch=4,  # 根据硬件调整批次大小
    imgsz=(704,704),  # 图像尺寸
    device=0,  # 使用GPU
    augment=True,  # 启用数据增强
    val=True,  # 启用验证集
    amp=True  # 启用混合精度训练
    )
