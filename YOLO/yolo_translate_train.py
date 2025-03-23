from ultralytics import YOLO

def main():
    # 加载已经训练好的模型
    model = YOLO("./runs/detect/train46/weights/best.pt")  # 替换为你的模型路径

    # 修改模型的类别数量
    model.model.nc = 2  # 设置新的类别数量（蜗牛 + 角色）
    model.model.names = ['snail', 'player']  # 设置新的类别名称

    # 继续训练
    results = model.train(
        data="data.yaml",  # 新的数据配置文件
        epochs=50,  # 训练轮数
        batch=4,  # 批次大小
        imgsz=640,  # 图像尺寸
        pretrained=True,  # 使用预训练权重
        resume=False,  # 是否从上次的训练结果继续
        device=0,  # 使用GPU（0表示第一块GPU）
    )

    # 验证模型
    results = model.val()

if __name__ == '__main__':
    # 在 Windows 上使用多进程时需要调用 freeze_support()
    from multiprocessing import freeze_support
    freeze_support()
    main()