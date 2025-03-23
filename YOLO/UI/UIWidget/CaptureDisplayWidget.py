from UI.imports import *

class CaptureDisplayWidget(QFrame):
    """ 子窗口：用于显示捕获内容，可以自由拖拽大小 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Box)  # 加个边框，方便拖拽识别
        self.setMinimumSize(200, 150)  # 设置最小大小
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)  # 不直接拉伸，手动缩放
        self.latest_pixmap = None  # 存储最新截图
        self.setStyleSheet("background-color: black;")  # 设置背景黑色

    def update_display(self):
        """ 调整缩放并填充黑色背景 """
        if self.latest_pixmap is None:
            return

        label_width = self.width()
        label_height = self.height()

        img_width = self.latest_pixmap.width()
        img_height = self.latest_pixmap.height()

        # 计算缩放比例
        scale = min(label_width / img_width, label_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        # 创建黑色背景的 QPixmap
        result_pixmap = QPixmap(label_width, label_height)
        result_pixmap.fill(QColor(0, 0, 0))  # 黑色填充

        # 在黑色背景上居中绘制缩放后的图片
        scaled_pixmap = self.latest_pixmap.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio)
        painter = QPainter(result_pixmap)
        x_offset = (label_width - new_width) // 2
        y_offset = (label_height - new_height) // 2
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        painter.end()

        self.image_label.setPixmap(result_pixmap)
        self.image_label.setGeometry(0, 0, label_width, label_height)  # 让 QLabel 覆盖整个子窗口

    def resizeEvent(self, event):
        """ 监听窗口大小变化，重新绘制图像 """
        self.update_display()