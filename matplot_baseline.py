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
Description: 因 wfdb 内置了 matplotlib 的方法，无法将对象展示到Qt内，所以放弃 matplotlib
'''
import sys, qdarkstyle
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGridLayout,
                             QWidget, QTextEdit, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QLabel, QStyledItemDelegate,
                             QGridLayout, QComboBox, QSizePolicy)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import numpy as np
from functools import partial
import wfdb


# 绘图的空白界面
class MymplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111) # 多界面绘图
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, 
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        FigureCanvas.updateGeometry(self)

    def static_plot(self):
        self.axes.clear()
        self.fig.suptitle("static FIG")
        t = np.linspace(1, 10, 10)
        s = np.sin(np.pi * t)
        self.axes.plot(t, s)
        self.axes.grid(True)
        self.draw()

    # 为何要加参数
    def dynamic_plot(self, *args, **kwargs):
        timer = QTimer(self)
        timer.timeout.connect(self.update_fig)
        timer.start(1000)

    def update_fig(self):
        self.axes.clear()
        self.fig.suptitle("dynamic FIG")
        l = np.random.randint(1, 10, 4)
        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.axes.grid(True)
        self.draw()

# 实现绘图类
class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)

        # 封装绘图类
        self.gridLayout = QGridLayout()
        self.mpl = MymplCanvas(self)
        # 添加工具栏
        self.mpl_tool = NavigationToolbar(self.mpl, self)
        self.setLayout(self.gridLayout)
        self.gridLayout.addWidget(self.mpl)
        self.gridLayout.addWidget(self.mpl_tool)

    def static(self):
        self.mpl.static_plot()

    def dynamic(self):
        self.mpl.dynamic_plot()

# 主窗口的类
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

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

        for i in range (1, 11):
            self.data_com.addItem(str(100 + i))

        # 绘图函数区域
        win = MatplotlibWidget()
        pagelayout.addWidget(win)

        # 设置最终的窗口布局与控件-------------------------------------
        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        self.data_com.currentIndexChanged.connect(self.show_)

    def show_(self):
        string = self.data_com.currentText()
        # 读取本地的100号记录，从0到25000，通道0
        record = wfdb.rdrecord('MIT-BIH/mit-bih-database/' + string, sampfrom=0, sampto=3600, physical=False, channels=[0, ])
        # 读取心电数据
        annotation = wfdb.rdann('MIT-BIH/mit-bih-database/' + string, 'atr', sampto=3600)

        wfdb.plot_wfdb(record=record, annotation=annotation,
                    title='Record 100 from MIT-BIH Arrhythmia Database', time_units='seconds')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    sys.exit(app.exec_())

# ref
# https://github.com/conda-forge/pyqtgraph-feedstock/issues/10