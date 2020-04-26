'''
File: view.py
Project: ECG-Platform
File Created: Saturday, 25th April 2020 11:46:06 am
Author: lanling (https://github.com/muyuuuu)
-----------
Last Modified: Saturday, 25th April 2020 11:47:25 am
Modified By: lanling (https://github.com/muyuuuu)
Copyright 2020 - 2020 NCST, NCST
-----------
@ 佛祖保佑，永无BUG--
'''
import sys, qdarkstyle
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGridLayout, QFrame,
                             QSplitter, QWidget, QTextEdit, QVBoxLayout,
                             QPushButton, QHBoxLayout, QLabel,QStyledItemDelegate,
                             QLineEdit, QGridLayout, QComboBox)
import pyqtgraph as pg 
import numpy as np
from functools import partial


# 主窗口的类
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # 在初始化之前设置pg，因为初始化会写死配置，无法在更改
        # pg.setConfigOption('foreground', 'd')
        # 使曲线看起来光滑
        pg.setConfigOptions(antialias = True)
        # 设置文字的字体
        font = QFont()
        font.setFamily("Microsoft Yahei")
        font.setPointSize(11)

        self.setFixedSize(900, 650)

        # 统一设置按钮的字体
        btn_list = []

        # 设置题目和状态栏
        self.setWindowTitle("心电平台检测")

        # 设置状态栏
        self.status = self.statusBar()
        self.status.showMessage("检测~")

        # 整体布局
        pagelayout = QVBoxLayout()

        # 顶层按钮布局
        btn_layout = QHBoxLayout()
        data_com = QComboBox()
        delegate = QStyledItemDelegate()
        data_com.setItemDelegate(delegate)
        data_com.addItem("选择心电数据")
        data_com.setFixedSize(300, 40)
        data_com.setFont(font)
        set_btn = QPushButton("设置")
        help_btn = QPushButton("帮助")
        save_btn = QPushButton("存储")
        back_btn = QPushButton("回放")
        btn_list.append(set_btn)
        btn_list.append(help_btn)
        btn_list.append(save_btn)
        btn_list.append(back_btn)
        btn_layout.addWidget(data_com)
        btn_layout.addWidget(set_btn)
        btn_layout.addWidget(help_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(back_btn)
        pagelayout.addLayout(btn_layout)

        for btn in btn_list:
            btn.setFont(font)
            btn.setFixedSize(100, 40)

        # 绘图函数区域
        win = pg.GraphicsLayoutWidget()
        p = win.addPlot()
        p.getAxis("bottom").tickFont = font
        p.getAxis("left").tickFont = font
        # 背景透明
        win.setBackground(background=None)
        self.data = np.random.normal(size=300)
        self.curve = p.plot(self.data)
        pagelayout.addWidget(win)

        # 设置最终的窗口布局与控件-------------------------------------
        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):
        self.data[:-1] = self.data[1:]
        self.data[-1] = np.random.normal()
        self.curve.setData(self.data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec_())

# ref
# https://github.com/conda-forge/pyqtgraph-feedstock/issues/10