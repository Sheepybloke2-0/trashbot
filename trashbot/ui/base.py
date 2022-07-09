from PyQt5 import QtWidgets as qw
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


class BaseLayout(qw.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        button1 = qw.QPushButton("Up")
        button2 = qw.QPushButton("Update")
        button3 = qw.QPushButton("Remove")
        button4 = qw.QPushButton("Down")

        label1 = qw.QLabel()
        label1.setText("This is a reminder")
        label1.adjustSize()

        label2 = qw.QLabel()
        label2.setText("This is also a reminder")
        label2.adjustSize()

        label3 = qw.QLabel()
        label3.setText("This is also a reminder")
        label3.adjustSize()

        grid = qw.QGridLayout()
        grid.addWidget(button1, 1, 0)
        grid.addWidget(button2, 2, 0)
        grid.addWidget(button3, 3, 0)
        grid.addWidget(button4, 4, 0)

        grid.addWidget(label1, 0, 2, 3, 1)
        grid.addWidget(label2, 1, 2, 3, 1)
        grid.addWidget(label3, 2, 2, 3, 1)

        self.setLayout(grid)
        self.setGeometry(0, 0, 400, 300)
        self.setWindowTitle("Wow - Owen Wilson")

        self.show()


def main():
    app = QApplication(sys.argv)
    ex = BaseLayout()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
