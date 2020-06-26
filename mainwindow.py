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

import sys, qdarkstyle, wfdb, os, datetime, pyqtgraph.exporters
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGridLayout,
                             QWidget, QTextEdit, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QLabel, QStyledItemDelegate,
                             QGridLayout, QComboBox, QFrame, QSplitter,
                             QStackedLayout, QRadioButton, QSpinBox, 
                             QMessageBox, QLineEdit, QFileDialog, QTableWidget,
                             QHeaderView, QTableWidgetItem)
import pyqtgraph as pg 
import numpy as np
import pandas as pd

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

        self.setMinimumHeight(750)
        self.setMinimumWidth(1000)
        # self.setFixedSize(1000, 750)

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
        patient_table_btn = QPushButton("病例表")
        self.stop_btn = QPushButton("暂停")
        btn_list.append(set_btn)
        btn_list.append(help_btn)
        btn_list.append(save_btn)
        btn_list.append(back_btn)
        btn_list.append(self.stop_btn)
        btn_list.append(fig_btn)
        btn_list.append(patient_table_btn)
        btn_layout.addWidget(self.data_com)
        btn_layout.addWidget(set_btn)
        btn_layout.addWidget(help_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(back_btn)
        btn_layout.addWidget(fig_btn)
        btn_layout.addWidget(patient_table_btn)

        for btn in btn_list:
            btn.setFont(font)
            btn.setFixedSize(100, 40)

        # 以此统计病人数量
        self.patient = 0
        for i in range (0, 10):
            self.patient += 1
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
        set_layout = QVBoxLayout()
        theme_layout = QHBoxLayout()
        self.theme_white_radio = QRadioButton("白色主题")
        self.theme_white_radio.setFixedWidth(120)
        self.theme_black_radio = QRadioButton("黑色主题")
        theme_label = QLabel("主题颜色选择")
        theme_label.setFixedWidth(120)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_white_radio)
        theme_layout.addWidget(self.theme_black_radio)
        line_width_layout = QHBoxLayout()
        line_width = QLabel("设置线宽(范围1-4)")
        line_width.setFixedWidth(150)
        line_width_layout.addWidget(line_width)
        self.line_width_spin = QSpinBox()
        self.line_width_spin.setMinimum(1)
        self.line_width_spin.setMaximum(4)
        line_width_layout.addWidget(self.line_width_spin)
        set_layout.addLayout(theme_layout)
        set_layout.addLayout(line_width_layout)
        set_widget.setLayout(set_layout)
        self.bottom_layout.addWidget(set_widget)
        self.theme_white_radio.toggled.connect(self.change_status)
        self.theme_black_radio.toggled.connect(self.change_status)
        set_btn.clicked.connect(self.set_)

        # 暂停与启动的切换
        self.stop_btn.clicked.connect(self.stop_)

        # 截图功能
        fig_btn.clicked.connect(self.save_fig)

        # 回放功能
        back_btn.clicked.connect(self.back_show)

        # 保存数据功能
        save_widget = QWidget(bottom)
        save_layout = QHBoxLayout()
        save_label = QLabel("请选择保存数据的区间")
        save_label.setFixedHeight(40)
        self.left_interval = QLineEdit()
        self.left_interval.setFixedHeight(40)
        self.left_interval.setPlaceholderText("起始点,左区间")
        self.right_interval = QLineEdit()
        self.right_interval.setFixedHeight(40)
        self.right_interval.setPlaceholderText("终止点,右区间")
        save_confirm_btn = QPushButton("确认")
        save_confirm_btn.setFixedHeight(40)
        save_layout.addWidget(save_label)
        save_layout.addWidget(self.left_interval)
        save_layout.addWidget(self.right_interval)
        save_layout.addWidget(save_confirm_btn)
        save_widget.setLayout(save_layout)
        save_btn.clicked.connect(self.save_widget_)
        save_confirm_btn.clicked.connect(self.save_data)
        self.bottom_layout.addWidget(save_widget)

        # 病例表的填写
        table_widget = QWidget(bottom)
        table_layout = QHBoxLayout()
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(9)
        self.patient_table.setRowCount(self.patient)
        self.patient_table.setHorizontalHeaderLabels([
            '标号', '年龄', '性别', '用药', '房性早博', '室性早博', '心室融合心博', '右束支传导阻塞心博', '左束支传导阻塞心博'
        ])
        # self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.patient_table.resizeColumnsToContents()
        self.patient_table.verticalHeader().setVisible(False)
        table_layout.addWidget(self.patient_table)
        table_widget.setLayout(table_layout)
        self.bottom_layout.addWidget(table_widget)
        patient_table_btn.clicked.connect(self.show_table)

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
        
        # 记录当前用户
        self.people = ""
        # 当用户改变时出发函数 重新绘图
        self.data_com.currentIndexChanged.connect(self.show_ecg1)
        self.data_com.view().pressed.connect(self.show_ecg)
        # 读取数据的标志
        self.flag = 0
        # 帮助文档的标志
        self.help = 0
        # 暂停的标志
        self.stop = 0

    def show_table(self):
        # 这么多行
        self.timer.stop()
        self.bottom_layout.setCurrentIndex(4)
        rows = self.patient
        for row in range(0, rows):
            item = QTableWidgetItem(str(100 + row))
            self.patient_table.setItem(row, 0, item)
            head = wfdb.rdheader('MIT-BIH/mit-bih-database/' + str(100 + row))
            age, gender, _, _, _ = head.comments[0].split(" ")
            item = QTableWidgetItem(str(age))
            self.patient_table.setItem(row, 1, item)
            item = QTableWidgetItem(str(gender))
            self.patient_table.setItem(row, 2, item)
            drugs = head.comments[1]
            item = QTableWidgetItem(str(drugs))
            self.patient_table.setItem(row, 3, item)
            record = wfdb.rdann('MIT-BIH/mit-bih-database/' + str(100 + row), 
                        "atr", 
                        sampfrom=0, 
                        sampto=650000)
            A, V, F, R, L = 0, 0, 0, 0, 0
            for index in record.symbol:
                if index == 'A':
                    A += 1
                if index == "V":
                    V += 1
                if index == "F":
                    F += 1
                if index == "R":
                    R += 1
                if index == "L":
                    L += 1
            item = QTableWidgetItem(str(A))
            self.patient_table.setItem(row, 4, item)
            item = QTableWidgetItem(str(V))
            self.patient_table.setItem(row, 5, item)
            item = QTableWidgetItem(str(F))
            self.patient_table.setItem(row, 6, item)
            item = QTableWidgetItem(str(R))
            self.patient_table.setItem(row, 7, item)
            item = QTableWidgetItem(str(L))
            self.patient_table.setItem(row, 8, item)
            self.patient_table.resizeColumnsToContents()

    # 选择区间断和数据，保存即可
    def save_data(self):
        left = int(self.left_interval.text())
        right = int(self.right_interval.text())
        print(self.people)
        record = wfdb.rdrecord('MIT-BIH/mit-bih-database/' + self.people, physical=False, sampto=100000)
        data = record.d_signal
        data = data[left : right]
        channels = data.shape[1]
        # print(data)
        columns = ["channel_" + str(i) for i in range(channels)]
        df = pd.DataFrame(data, columns=columns, index=range(left, right))
        filename, _ = QFileDialog.getSaveFileName(self,  "文件保存",  os.getcwd(), "Text Files (*.csv)")
        if filename == "":
            return
        df.to_csv(filename)

    # 只是打开保存的页面
    def save_widget_(self):
        self.timer.stop()
        self.bottom_layout.setCurrentIndex(3)

    def timer_(self):
        self.timer.start(20)

    def back_show(self):
        self.p.clear()
        self.flag = 0
        self.stop = 0
        self.stop_btn.setText("暂停")
        self.timer_()

    def save_fig(self):
        exporter = pg.exporters.ImageExporter(self.p)
        exporter.parameters()['width'] = 1080
        file_name = str(datetime.datetime.now())
        file_name = file_name.replace(" ", "-")
        file_name = file_name.replace(".", "-")
        file_name = file_name.replace(":", "-")
        file_name = file_name + ".png"
        exporter.export(file_name)
        QMessageBox.information(None, ("友情提示"), ("保存完毕"),
                        QMessageBox.Cancel)

    # 停止时关闭计时器
    def stop_(self):
        if self.stop == 0:
            self.stop = 1
            self.stop_btn.setText("启动")
            self.timer.stop()
        else:
            self.stop = 0
            self.timer.start()
            self.stop_btn.setText("暂停")
        
    # 设置时停止计时器
    def set_(self):
        self.timer.stop()
        self.bottom_layout.setCurrentIndex(2)

    def change_status(self):
        self.timer.stop()
        if self.theme_white_radio.isChecked():
            self.setStyleSheet("")
        else:
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    def show_help(self):
        self.timer.stop()
        self.bottom_layout.setCurrentIndex(1)
        if (self.help == 0):
            self.help += 1
            with open ("help.txt", "r") as f:
                text = f.readlines()
                for line in text:
                    self.help_text.append(line)

    def show_ecg1(self):
        string = self.data_com.currentText()
        self.people = string
        self.p.clear()
        # 重置为 0 方可读取数据
        self.flag = 0
        self.timer_()

    def show_ecg(self):
        # 捕获当前用户
        self.bottom_layout.setCurrentIndex(0)

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
                self.curve = self.p.plot(data, pen=pg.mkPen(width=self.line_width_spin.value()))
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
# http://www.pyqtgraph.org/documentation/functions.html