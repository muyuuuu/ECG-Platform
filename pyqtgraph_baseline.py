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
import sys, qdarkstyle, wfdb
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGridLayout,
                             QWidget, QTextEdit, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QLabel, QStyledItemDelegate,
                             QGridLayout, QComboBox)
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
        self.data_com = QComboBox()
        delegate = QStyledItemDelegate()
        self.data_com.setItemDelegate(delegate)
        self.data_com.addItem("选择心电数据")
        self.data_com.setFixedSize(300, 40)
        self.data_com.setFont(font)
        set_btn = QPushButton("设置")
        help_btn = QPushButton("帮助")
        save_btn = QPushButton("存储")
        back_btn = QPushButton("回放")
        btn_list.append(set_btn)
        btn_list.append(help_btn)
        btn_list.append(save_btn)
        btn_list.append(back_btn)
        btn_layout.addWidget(self.data_com)
        btn_layout.addWidget(set_btn)
        btn_layout.addWidget(help_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(back_btn)
        pagelayout.addLayout(btn_layout)

        for btn in btn_list:
            btn.setFont(font)
            btn.setFixedSize(100, 40)

        for i in range (1, 10):
            self.data_com.addItem(str(100 + i))
        
        # 绘图函数区域
        win = pg.GraphicsLayoutWidget()
        self.p = win.addPlot()
        self.p.getAxis("bottom").tickFont = font
        self.p.getAxis("left").tickFont = font
        # 背景透明
        win.setBackground(background=None)
        pagelayout.addWidget(win)

        # 设置最终的窗口布局与控件-------------------------------------
        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # 计时器 当时间到了就出发绘图函数
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)

        # 记录当前用户
        self.people = ""
        # 当用户改变时出发函数 重新绘图
        self.data_com.currentIndexChanged.connect(self.show_)
        self.flag = 0

    def show_(self):
        # 捕获当前用户
        string = self.data_com.currentText()
        self.people = string
        self.p.clear()
        # 重置为 0 方可读取数据
        self.flag = 0

    def update(self):
        if self.people == "":
            pass
        else:
            # 第一次只读取 10000 数据
            if self.flag == 0:
                self.data = wfdb.rdrecord('MIT-BIH/mit-bih-database/' + self.people, sampfrom=0, sampto=10000, physical=False, channels=[0, ])
                # 先取这么多数据
                self.count = 250
                data = self.data.d_signal[:self.count].reshape(self.count)
                self.curve = self.p.plot(data)
                self.flag += 1
            # 第二次开始绘制，每次只绘制一个数据点
            else:
                self.count += 1
                # 每次多取一个数据
                data = self.data.d_signal[:self.count].reshape(self.count)
                # 删除第一个数据 新加一个数据
                data[:-1] = data[1:]
                data[-1] = self.data.d_signal[self.count]
                self.curve.setData(data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec_())

# ref
# https://github.com/conda-forge/pyqtgraph-feedstock/issues/10