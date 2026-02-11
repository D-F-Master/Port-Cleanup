import sys
import psutil
from PyQt5 import QtWidgets, QtCore
from port import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(800, 600)
        self.tableWidget.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.tableWidget.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        # 设置选择模式为整行选中
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # 设置选择模式为单选或多选
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # 单选
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)  # 多选

        # 绑定按钮点击事件
        self.pushButton.disconnect()
        self.pushButton.clicked.connect(self.on_pushButton_clicked)

        # 绑定清除按钮点击事件
        self.pushButton_2.clicked.connect(self.on_clear_button_clicked)

        # 设置表格列数和表头
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["PID", "名称", "状态", "内存(MB)", "CPU(%)", "路径"])

        # 初始化定时器
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_process_info)  # 定时器超时信号连接到更新函数

    def on_pushButton_clicked(self):
        port_text = self.lineEdit.text()
        try:
            port = int(port_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "错误", "请输入有效的端口号")
            return

        self.tableWidget.setRowCount(0)  # 清空表格
        processes = self.get_processes_by_port(port)

        if not processes:
            # 如果没有进程占用该端口，弹窗提示
            QtWidgets.QMessageBox.information(self, "提示", "无端口占用")
        else:
            # 否则正常显示进程信息
            for proc in processes:
                row_position = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_position)
                self.tableWidget.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(proc['pid'])))
                self.tableWidget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(proc['name']))
                self.tableWidget.setItem(row_position, 2, QtWidgets.QTableWidgetItem(proc['status']))
                self.tableWidget.setItem(row_position, 3, QtWidgets.QTableWidgetItem(f"{proc['memory']:.2f}"))
                self.tableWidget.setItem(row_position, 4, QtWidgets.QTableWidgetItem(f"{proc['cpu']:.2f}"))
                self.tableWidget.setItem(row_position, 5, QtWidgets.QTableWidgetItem(proc['path']))

    def on_clear_button_clicked(self):
        """清除按钮点击事件"""
        # 检查是否有选中的行
        selected_rows = set()
        for item in self.tableWidget.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择要删除的进程！")
            return

        # 弹窗确认是否删除
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认删除",
            "确定要终止选中的进程吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            # 遍历选中行并终止进程
            for row in sorted(selected_rows, reverse=True):  # 逆序删除避免索引错乱
                pid_item = self.tableWidget.item(row, 0)
                if pid_item and pid_item.text().isdigit():
                    pid = int(pid_item.text())
                    try:
                        proc = psutil.Process(pid)
                        proc.terminate()  # 终止进程
                        self.tableWidget.removeRow(row)  # 从表格中移除该行
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        QtWidgets.QMessageBox.critical(self, "错误", f"无法终止进程 PID={pid}: {e}")

            # 提示删除成功
            QtWidgets.QMessageBox.information(self, "成功", "选中的进程已终止！")

    def update_process_info(self):
        """定时更新进程信息"""
        for i, proc_info in enumerate(self.processes):
            try:
                proc = psutil.Process(proc_info['pid'])
                # 更新内存和 CPU 数据
                proc_info['memory'] = proc.memory_info().rss / 1024 / 1024
                proc_info['cpu'] = proc.cpu_percent(interval=0.1)
                # 刷新表格对应行的数据
                self.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(f"{proc_info['memory']:.2f}"))
                self.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(f"{proc_info['cpu']:.2f}"))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # 如果进程不存在或无权限访问，则从列表中移除
                del self.processes[i]
                self.tableWidget.removeRow(i)

    def update_table(self):
        """将进程信息填充到表格中"""
        for proc in self.processes:
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)
            self.tableWidget.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(proc['pid'])))
            self.tableWidget.setItem(row_position, 1, QtWidgets.QTableWidgetItem(proc['name']))
            self.tableWidget.setItem(row_position, 2, QtWidgets.QTableWidgetItem(proc['status']))
            self.tableWidget.setItem(row_position, 3, QtWidgets.QTableWidgetItem(f"{proc['memory']:.2f}"))
            self.tableWidget.setItem(row_position, 4, QtWidgets.QTableWidgetItem(f"{proc['cpu']:.2f}"))
            self.tableWidget.setItem(row_position, 5, QtWidgets.QTableWidgetItem(proc['path']))

    def get_processes_by_port(self, port):
        """根据端口号获取相关进程信息"""
        processes = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.pid is not None:
                try:
                    proc = psutil.Process(conn.pid)
                    processes.append({
                        'pid': proc.pid,
                        'name': proc.name(),
                        'status': proc.status(),
                        'memory': proc.memory_info().rss / 1024 / 1024,
                        'cpu': proc.cpu_percent(interval=0.1),
                        'path': proc.exe()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return processes

    def closeEvent(self, event):
        """窗口关闭时停止定时器"""
        self.timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
