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
                             QGridLayout, QComboBox, QFrame, QSplitter,
                             QStackedLayout, QRadioButton)
import pyqtgraph as pg 
import pyqtgraph.exporters
import datetime
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
        top = QFrame(self)
        top.setFrameShape(QFrame.StyledPanel)
        btn_layout = QHBoxLayout(top)
        self.data_com = QComboBox()
        delegate = QStyledItemDelegate()
        self.data_com.setItemDelegate(delegate)
        self.data_com.addItem("选择心电数据")
        self.data_com.setFixedSize(200, 40)
        self.data_com.setFont(font)
        set_btn = QPushButton("设置")
        help_btn = QPushButton("帮助")
        save_btn = QPushButton("存储")
        back_btn = QPushButton("回放")
        fig_btn = QPushButton("截图")
        self.stop_btn = QPushButton("暂停")
        btn_list.append(set_btn)
        btn_list.append(help_btn)
        btn_list.append(save_btn)
        btn_list.append(back_btn)
        btn_list.append(self.stop_btn)
        btn_list.append(fig_btn)
        btn_layout.addWidget(self.data_com)
        btn_layout.addWidget(set_btn)
        btn_layout.addWidget(help_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(fig_btn)

        for btn in btn_list:
            btn.setFont(font)
            btn.setFixedSize(100, 40)

        for i in range (1, 10):
            self.data_com.addItem(str(100 + i))
        
        # 底层布局
        bottom = QFrame(self)
        bottom.setFrameShape(QFrame.StyledPanel)
        self.bottom_layout = QStackedLayout(bottom)

        # 1. 绘图区域
        plot_widget = QWidget(bottom)
        plot_layout = QHBoxLayout()
        win = pg.GraphicsLayoutWidget()
        self.p = win.addPlot()
        self.p.getAxis("bottom").tickFont = font
        self.p.getAxis("left").tickFont = font
        # 背景透明
        win.setBackground(background=None)
        plot_layout.addWidget(win)
        plot_widget.setLayout(plot_layout)
        self.bottom_layout.addWidget(plot_widget)

        # 2. 帮助文档
        help_widget = QWidget(bottom)
        help_layout = QHBoxLayout()
        self.help_text = QTextEdit()
        self.help_text.setReadOnly(True)
        help_layout.addWidget(self.help_text)
        help_widget.setLayout(help_layout)
        self.bottom_layout.addWidget(help_widget)
        help_btn.clicked.connect(self.show_help)

        # 3. 设置
        set_widget = QWidget(bottom)
        set_layout = QHBoxLayout()
        self.theme_white_radio = QRadioButton("白色主题")
        self.theme_black_radio = QRadioButton("黑色主题")
        set_layout.addWidget(self.theme_white_radio)
        set_layout.addWidget(self.theme_black_radio)
        set_widget.setLayout(set_layout)
        self.bottom_layout.addWidget(set_widget)
        self.theme_white_radio.toggled.connect(self.change_status)
        self.theme_black_radio.toggled.connect(self.change_status)
        set_btn.clicked.connect(self.set_)

        # 暂停与启动的切换
        self.stop_btn.clicked.connect(self.stop_)

        # 截图功能
        fig_btn.clicked.connect(self.save_fig)

        # 设置最终的窗口布局与控件-------------------------------------
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(top)
        splitter.addWidget(bottom)

        widget = QWidget()
        pagelayout.addWidget(splitter)
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)
        
        # 计时器 当时间到了就出发绘图函数
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)

        # 记录当前用户
        self.people = ""
        # 当用户改变时出发函数 重新绘图
        self.data_com.currentIndexChanged.connect(self.show_ecg)
        # 读取数据的标志
        self.flag = 0
        # 帮助文档的标志
        self.help = 0
        # 暂停的标志
        self.stop = 0

    def save_fig(self):
        exporter = pg.exporters.ImageExporter(self.p)
        exporter.parameters()['width'] = 1080
        file_name = str(datetime.datetime.now())
        file_name = file_name.replace(" ", "-")
        file_name = file_name.replace(".", "-")
        file_name = file_name.replace(":", "-")
        file_name = file_name + ".png"
        exporter.export(file_name)
        

    def stop_(self):
        print(self.stop)
        if self.stop == 0:
            self.stop = 1
            self.stop_btn.setText("启动")
        else:
            self.stop = 0
            self.stop_btn.setText("暂停")
        
    def set_(self):
        self.bottom_layout.setCurrentIndex(2)

    def change_status(self):
        if self.theme_white_radio.isChecked():
            self.setStyleSheet("")
        else:
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def show_help(self):
        self.bottom_layout.setCurrentIndex(1)
        if (self.help == 0):
            self.help += 1
            with open ("help.txt", "r") as f:
                text = f.readlines()
                for line in text:
                    self.help_text.append(line)

    def show_ecg(self):
        # 捕获当前用户
        self.bottom_layout.setCurrentIndex(0)
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
                self.data = wfdb.rdrecord('MIT-BIH/mit-bih-database/' + self.people, 
                                    sampfrom=0, 
                                    sampto=10000, 
                                    physical=False, 
                                    channels=[0, ])
                # 先取这么多数据
                self.count = 250
                data = self.data.d_signal[:self.count].reshape(self.count)
                self.curve = self.p.plot(data)
                self.flag += 1
            # 第二次开始绘制，每次只绘制一个数据点
            else:
                if self.stop != 1:
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
# https://github.com/pyqtgraph/pyqtgraph/issues/538
# http://www.pyqtgraph.org/documentation/exporting.html