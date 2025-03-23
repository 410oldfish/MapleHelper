from UI.imports import *

class ImageDisplayWidget(QFrame):
    """ 子窗口：用于显示用户从文件夹中选中的图片，支持以鼠标位置为中心的缩放 """
    # 信号
    labels_updated = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.Box)  # 加个边框，方便拖拽识别
        self.setMinimumSize(200, 150)  # 设置最小大小
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setScaledContents(False)  # 不直接拉伸，手动缩放
        self.latest_pixmap = None  # 存储最新图片
        self.original_pixmap = None  # 存储原始图片
        self.scale_factor = 1.0  # 当前缩放比例
        self.mouse_pos = QPointF()  # 记录鼠标位置
        self.setStyleSheet("background-color: black;")  # 设置背景黑色
        self.setMouseTracking(True)  # 启用鼠标跟踪
        self.crosshair_visible = True  # 是否显示十字光标
        self.initial_scale_factor = 1.0  # 新增初始缩放比例变量
        self.image_name = None
        self.showing_label = False  # 新增标志位，指示是否正在显示标签
        #
        self.selection_start = QPointF()  # 框选开始位置
        self.selection_end = QPointF()  # 框选结束位置
        self.selecting = False  # 是否正在框选

        # 新增变量以支持拖拽
        self.dragging = False  # 是否正在拖拽
        self.drag_start_pos = QPointF()  # 拖拽开始时的鼠标位置
        self.image_offset = QPointF(0, 0)  # 图片的偏移量

        # 新增 QLabel 用于显示文本内容
        self.text_label = QLabel(self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.text_label.setStyleSheet("color: white;")  # 设置文本颜色为白色
        self.text_label.setWordWrap(False)  # 允许文本换行
        self.text_label.hide()  # 初始隐藏文本标签

    def update_display(self, pixmap, img_name):
        """ 更新显示的图片 """
        if pixmap is None:
            return

        self.showing_label = False
        self.image_name,_ = os.path.splitext(img_name)

        self.original_pixmap = pixmap
        self.latest_pixmap = pixmap

        # 计算初始缩放比例（保持比例且不超出窗口）
        window_width = self.width()
        window_height = self.height()
        img_width = self.original_pixmap.width()
        img_height = self.original_pixmap.height()

        # 计算适应窗口的最大比例
        scale_w = window_width / img_width
        scale_h = window_height / img_height
        self.initial_scale_factor = min(scale_w, scale_h)
        self.scale_factor = self.initial_scale_factor  # 使用适应窗口的比例作为初始值

        self.image_offset = QPointF(0, 0)  # 重置偏移量
        self.text_label.clear()
        self.text_label.hide()
        self.image_label.show()
        self._apply_scale()

    def update_display_label(self, label_content):
        self.showing_label = True  # 新增标志位，指示是否正在显示标签
        """ 更新显示的标签内容 """
        self.text_label.setText(label_content)  # 设置标签内容
        self.text_label.adjustSize()  # 调整大小以适应文本内容
        self.text_label.show()  # 显示文本标签

        # 隐藏图片
        self.image_label.clear()  # 清空图片显示
        self.image_label.hide()  # 隐藏图片

    def mousePressEvent(self, event: QMouseEvent):
        """ 记录鼠标按下位置 """
        if event.button() == Qt.MouseButton.RightButton:
            self.dragging = True
            self.drag_start_pos = event.position()  # 记录拖拽开始时的鼠标位置

        """ 记录鼠标按下位置 """
        if not self.showing_label and event.button() == Qt.MouseButton.LeftButton:
            self.selecting = True
            self.selection_start = event.position()  # 记录框选开始位置

    def mouseMoveEvent(self, event: QMouseEvent):
        """ 监听鼠标移动事件，更新鼠标位置 """
        self.mouse_pos = event.position()
        self.crosshair_visible = True  # 显示十字光标

        if self.selecting:
            self.selection_end = event.position()  # 更新框选结束位置

        if self.dragging:
            # 计算拖拽的偏移量
            delta = event.position() - self.drag_start_pos
            self.image_offset += delta  # 更新图片偏移量
            self.drag_start_pos = event.position()  # 更新拖拽开始位置

        self._apply_scale()  # 更新显示

    def _apply_scale(self):
        """ 根据当前缩放比例和鼠标位置重新绘制图片 """
        if self.latest_pixmap is None:
            return

        label_width = self.width()
        label_height = self.height()

        # 创建黑色背景的 QPixmap
        result_pixmap = QPixmap(label_width, label_height)
        result_pixmap.fill(QColor(0, 0, 0))  # 黑色填充

        # 计算缩放后的图片大小
        scaled_pixmap = self.original_pixmap.scaled(
            int(self.original_pixmap.width() * self.scale_factor),
            int(self.original_pixmap.height() * self.scale_factor),
            Qt.AspectRatioMode.KeepAspectRatio
        )

        # 计算图片的偏移量，使其居中显示
        x_offset = (label_width - scaled_pixmap.width()) // 2 + int(self.image_offset.x())
        y_offset = (label_height - scaled_pixmap.height()) // 2 + int(self.image_offset.y())

        # 将偏移量转换为整数
        x_offset = int(x_offset)
        y_offset = int(y_offset)

        painter = QPainter(result_pixmap)
        painter.drawPixmap(x_offset, y_offset, scaled_pixmap)

        # 绘制框选区域
        if self.selecting:
            selection_rect = QRectF(self.selection_start, self.selection_end).normalized()
            pen = QPen(QColor(0, 255, 0), 2)  # 绿色边框
            painter.setPen(pen)
            painter.drawRect(selection_rect)  # 绘制框选区域

        # 绘制十字光标
        if self.crosshair_visible:
            pen = QPen(QColor(255, 0, 0))  # 红色十字
            pen.setWidth(2)
            painter.setPen(pen)

            crosshair_length = 15
            painter.drawLine(int(self.mouse_pos.x()), int(self.mouse_pos.y() - crosshair_length),
                             int(self.mouse_pos.x()), int(self.mouse_pos.y() + crosshair_length))  # 垂直线
            painter.drawLine(int(self.mouse_pos.x() - crosshair_length), int(self.mouse_pos.y()),
                             int(self.mouse_pos.x() + crosshair_length), int(self.mouse_pos.y()))  # 水平线

        painter.end()

        self.image_label.setPixmap(result_pixmap)
        self.image_label.setGeometry(0, 0, label_width, label_height)  # 让 QLabel 覆盖整个子窗口

        # 确保文本标签在图片上方显示
        self.text_label.raise_()  # 将文本标签提升到最上层

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ 处理鼠标释放事件，结束框选并弹出输入框 """
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.selecting = False
            self.selection_end = event.position()  # 更新框选结束位置
            self._show_label_input()  # 弹出输入框

        """ 处理鼠标释放事件，结束拖拽 """
        if event.button() == Qt.MouseButton.RightButton:
            self.dragging = False

    def leaveEvent(self, event):
        """ 监听鼠标离开事件，隐藏十字光标 """
        pass

    def resizeEvent(self, event):
        """ 窗口大小变化时自动调整初始缩放 """
        if self.latest_pixmap:
            # 仅在保持初始缩放时自动调整
            if self.scale_factor == self.initial_scale_factor:
                # 重新计算适应新窗口的比例
                window_width = self.width()
                window_height = self.height()
                img_width = self.original_pixmap.width()
                img_height = self.original_pixmap.height()

                scale_w = window_width / img_width
                scale_h = window_height / img_height
                self.initial_scale_factor = min(scale_w, scale_h)
                self.scale_factor = self.initial_scale_factor

            self._apply_scale()

    def wheelEvent(self, event: QWheelEvent):
        """ 允许缩放超出初始比例 """
        if self.original_pixmap is None:
            return

        self.mouse_pos = event.position()
        delta = event.angleDelta().y()

        # 计算缩放后的新比例
        new_scale = self.scale_factor * 1.1 if delta > 0 else self.scale_factor * 0.9

        # 允许自由缩放（移除下限限制）
        self.scale_factor = new_scale  # 允许缩小到任意比例

        self._apply_scale()

    def _show_label_input(self):
        label, ok = QInputDialog.getText(self, '输入标签', '请输入标签名称:')
        if ok and label:
            # 处理标签和框选区域
            self._save_label(label)

    def _save_label(self, label):
        # 计算框选区域在原始图片上的位置
        selection_rect = QRectF(self.selection_start, self.selection_end).normalized()
        scaled_width = self.original_pixmap.width() * self.scale_factor
        scaled_height = self.original_pixmap.height() * self.scale_factor

        # 计算相对于原始图片的坐标
        x_center = (selection_rect.x() + selection_rect.width() / 2) / scaled_width
        y_center = (selection_rect.y() + selection_rect.height() / 2) / scaled_height
        width = selection_rect.width() / scaled_width
        height = selection_rect.height() / scaled_height

        # 假设标签ID为0（可以根据已有标签生成ID）
        label_id = 0  # 这里可以根据已有标签生成ID

        # 保存到txt文件
        label_file_path = os.path.join(labels_path, f"{self.image_name}.txt")
        with open(label_file_path, 'a') as f:
            f.write(f"{label_id} {x_center} {y_center} {width} {height}\n")

        #通知framework更新文件列表
        self.labels_updated.emit()


# def display_selected_label(self, item):
#     """ 显示选中的标签 """
#     label_path = os.path.join(self.labels_folder, item.text())  # 获取完整路径
#     if os.path.exists(label_path):
#         with open(label_path, 'r') as file:
#             label_content = file.read()  # 读取标签文件内容
#             # 假设有一个方法或控件来显示标签内容，例如一个文本框
#             self.image_display_widget.update_display_label(label_content)  # 更新标签显示窗口