import sys
import time
import mss
import pygetwindow as gw
import numpy as np
import cv2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QComboBox, QHBoxLayout, QFrame,
    QFileDialog, QListWidget, QSplitter, QTabWidget, QLineEdit,QInputDialog
)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QIntValidator
from PyQt6.QtCore import QTimer, Qt, QPointF
from PyQt6.QtGui import QWheelEvent, QMouseEvent, QCursor, QPen, QBrush
import os
