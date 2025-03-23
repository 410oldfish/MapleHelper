from imports import *
from UIWidget.ImageDisplayWidget import *
from UIWidget.CaptureDisplayWidget import *


class ScreenCaptureApp(QWidget):
    def __init__(self):
        super().__init__()
        self.frame_rate = 30  # 初始化帧率属性，默认值为 30
        self.screenshot_folder = "UI/screenshots"  # 截图文件夹路径
        self.labels_folder = "UI/labels"  # 标签文件夹路径
        self.init_ui()
        self.selected_window = None
        self.sct = mss.mss()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_capture)  # 连接定时器到更新捕获的方法

    def init_ui(self):
        self.setWindowTitle("窗口捕获器")
        self.setGeometry(100, 100, 1200, 600)

        # 选择窗口的下拉菜单
        self.window_selector = QComboBox(self)
        self.update_window_list()  # 更新窗口列表
        # 刷新窗口列表
        self.refresh_button = QPushButton("刷新窗口列表", self)
        self.refresh_button.clicked.connect(self.update_window_list)
        # 开始和停止按钮
        self.capture_button = QPushButton("开始捕获", self)
        self.capture_button.clicked.connect(self.start_capture)
        self.stop_button = QPushButton("停止捕获", self)
        self.stop_button.clicked.connect(self.stop_capture)
        self.stop_button.setEnabled(False)

        # 新增截图按钮
        self.screenshot_button = QPushButton("截图", self)
        self.screenshot_button.clicked.connect(self.take_screenshot)

        # 新增帧率输入框
        self.frame_rate_input = QLineEdit(self)
        self.frame_rate_input.setFixedWidth(80)  # 设置输入框宽度，足够显示 3 位数
        self.frame_rate_input.setValidator(QIntValidator(0, 120))  # 限制输入范围为 0~120
        self.frame_rate_input.setText(str(self.frame_rate))  # 设置默认值

        # 新增“更改”按钮
        self.change_frame_rate_button = QPushButton("更改", self)
        self.change_frame_rate_button.clicked.connect(self.update_frame_rate)

        # 创建 QTabWidget 实现页签切换
        self.tab_widget = QTabWidget(self)

        # 捕获窗口的显示区域
        self.capture_display_widget = CaptureDisplayWidget(self)  # 捕获窗口
        self.image_display_widget = ImageDisplayWidget(self)  # 图片窗口

        # 将子窗口添加到页签中
        self.tab_widget.addTab(self.capture_display_widget, "捕获窗口")
        self.tab_widget.addTab(self.image_display_widget, "图片窗口")

        # 新增图片文件列表
        self.file_list = QListWidget(self)
        self.update_file_list()  # 初始化文件列表
        self.file_list.itemClicked.connect(self.display_selected_image)  # 绑定点击事件

        # 新增标签文件列表
        self.labels_list = QListWidget(self)
        self.update_labels_list()  # 初始化标签文件列表
        self.labels_list.itemClicked.connect(self.display_selected_label)  # 绑定点击事件

        # 使用 QSplitter 实现可拖拽调整大小的布局
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 创建一个垂直布局，用于放置文件列表和标签列表
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("图片文件列表"))
        left_layout.addWidget(self.file_list)
        left_layout.addWidget(QLabel("标签文件列表"))
        left_layout.addWidget(self.labels_list)

        # 创建一个 QWidget 用于放置左侧的布局
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        splitter.addWidget(left_widget)  # 添加文件列表到 QSplitter
        splitter.addWidget(self.tab_widget)  # 添加 QTabWidget
        splitter.setSizes([300, 800])  # 设置初始大小比例

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.window_selector)

        # 新增帧率输入框和“更改”按钮的布局
        frame_rate_layout = QHBoxLayout()
        frame_rate_layout.addWidget(QLabel("帧率 (0~120):"))  # 添加标签
        frame_rate_layout.addWidget(self.frame_rate_input)  # 添加输入框
        frame_rate_layout.addWidget(self.change_frame_rate_button)  # 添加“更改”按钮
        frame_rate_layout.addStretch()  # 添加拉伸，使布局更紧凑

        layout.addLayout(frame_rate_layout)  # 将帧率布局添加到主布局

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.capture_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.screenshot_button)

        layout.addLayout(button_layout)
        layout.addWidget(splitter)  # 添加 QSplitter 到主布局
        self.setLayout(layout)

    def update_window_list(self):
        """ 更新窗口列表 """
        self.window_selector.clear()  # 清空当前的窗口列表
        available_windows = self.get_available_windows()  # 获取可用窗口列表
        self.window_selector.addItems(available_windows)  # 将可用窗口添加到下拉菜单中

    def get_available_windows(self):
        """ 获取当前可用窗口的列表 """
        return [window.title for window in gw.getAllWindows() if window.title]

    def start_capture(self):
        """ 开始捕获 """
        try:
            self.selected_window = self.window_selector.currentText()  # 获取当前选中的窗口
            if self.selected_window:
                self.timer.start(1000 // self.frame_rate)  # 根据帧率启动定时器
                self.capture_button.setEnabled(False)
                self.stop_button.setEnabled(True)
        except Exception as e:
            print(f"Error starting capture: {e}")

    def stop_capture(self):
        """ 停止捕获 """
        self.timer.stop()
        self.capture_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_capture(self):
        """ 更新捕获内容 """
        if self.selected_window:
            # 获取选中的窗口的位置信息
            window = gw.getWindowsWithTitle(self.selected_window)[0]
            if window:
                # 获取窗口的坐标和大小
                left, top, width, height = window.left, window.top, window.width, window.height

                # 使用 mss 进行屏幕捕获
                screenshot = self.sct.grab({
                    'top': top,
                    'left': left,
                    'width': width,
                    'height': height
                })

                # 将捕获的图像转换为 QPixmap
                img = QImage(screenshot.rgb, screenshot.width, screenshot.height, QImage.Format.Format_RGB888)
                self.capture_display_widget.latest_pixmap = QPixmap.fromImage(img)  # 更新最新的捕获图像
                self.capture_display_widget.update_display()  # 更新显示

    def take_screenshot(self):
        """ 截图并保存 """
        if self.selected_window:
            try:
                # 获取选中的窗口的位置信息
                window = gw.getWindowsWithTitle(self.selected_window)[0]
                if window:
                    # 获取窗口的坐标和大小
                    left, top, width, height = window.left, window.top, window.width, window.height

                    # 使用 mss 进行屏幕捕获
                    screenshot = self.sct.grab({
                        'top': top,
                        'left': left,
                        'width': width,
                        'height': height
                    })

                    # 提示用户输入文件名
                    file_name, _ = QInputDialog.getText(self, "保存截图", "请输入文件名（不带扩展名）:")
                    if file_name:
                        # 确保文件名有效
                        file_name = file_name.strip()
                        if not file_name.endswith('.png'):
                            file_name += '.png'  # 默认保存为 PNG 格式

                        # 保存截图到指定路径
                        screenshot_path = os.path.join(self.screenshot_folder, file_name)
                        img = QImage(screenshot.rgb, screenshot.width, screenshot.height, QImage.Format.Format_RGB888)
                        img.save(screenshot_path)  # 保存图片

                        self.update_file_list()
                    else:
                        print("未输入文件名，截图未保存。")
            except Exception as e:
                print(f"Error taking screenshot: {e}")

    def update_frame_rate(self):
        """ 更新帧率 """
        try:
            self.frame_rate = int(self.frame_rate_input.text())
            if self.frame_rate < 1:
                self.frame_rate = 1
            self.timer.setInterval(1000 // self.frame_rate)  # 更新定时器间隔
        except ValueError:
            pass  # 如果输入无效，保持原来的帧率

    def update_file_list(self):
        """ 更新图片文件列表 """
        self.file_list.clear()  # 清空当前的文件列表
        print(f"Checking folder: {self.screenshot_folder}")  # 打印文件夹路径
        if os.path.exists(self.screenshot_folder):
            for filename in os.listdir(self.screenshot_folder):
                print(f"Found file: {filename}")  # 打印找到的文件名
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):  # 只添加图片文件
                    self.file_list.addItem(filename)  # 添加文件名到列表
        else:
            print("Folder does not exist.")

    def update_labels_list(self):
        """ 更新标签文件列表 """
        self.labels_list.clear()  # 清空当前的标签列表
        if os.path.exists(self.labels_folder):
            for filename in os.listdir(self.labels_folder):
                if filename.lower().endswith('.txt'):  # 只添加文本文件
                    self.labels_list.addItem(filename)  # 添加文件名到列表

    def display_selected_image(self, item):
        """ 显示选中的图片 """
        image_path = os.path.join(self.screenshot_folder, item.text())  # 获取完整路径
        pixmap = QPixmap(image_path)  # 加载图片
        self.image_display_widget.update_display(pixmap)  # 更新图片显示窗口

    def display_selected_label(self, item):
        """ 显示选中的标签 """
        label_path = os.path.join(self.labels_folder, item.text())  # 获取完整路径
        if os.path.exists(label_path):
            with open(label_path, 'r') as file:
                label_content = file.read()  # 读取标签文件内容
                # 假设有一个方法或控件来显示标签内容，例如一个文本框
                self.image_display_widget.update_display_label(label_content)  # 更新标签显示窗口

if __name__ == "__main__":
    target_folder = "screenshots"
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    app = QApplication(sys.argv)
    window = ScreenCaptureApp()
    window.show()
    sys.exit(app.exec())