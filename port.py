from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)

        # 中央部件
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # 顶部输入区域（水平布局）
        top_layout = QtWidgets.QHBoxLayout()
        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setPlaceholderText("请输入端口号")
        self.pushButton = QtWidgets.QPushButton("查找")
        top_layout.addWidget(self.lineEdit)
        top_layout.addWidget(self.pushButton)
        top_layout.addStretch()  # 增加弹性空间
        main_layout.addLayout(top_layout)

        # 表格控件
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["PID", "名称", "状态", "内存(MB)", "CPU(%)", "路径"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)  # 自动拉伸最后一列
        main_layout.addWidget(self.tableWidget)

        # 底部按钮区域（水平布局）
        bottom_layout = QtWidgets.QHBoxLayout()
        bottom_layout.addStretch()  # 左侧弹性空间
        self.pushButton_2 = QtWidgets.QPushButton("清理占用")
        bottom_layout.addWidget(self.pushButton_2)
        main_layout.addLayout(bottom_layout)

        # 设置中央部件
        MainWindow.setCentralWidget(self.centralwidget)

        # 翻译文本
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "端口占用查询工具"))
