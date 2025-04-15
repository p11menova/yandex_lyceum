import sys
import os
import _csv
import datetime as dt

from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image, ImageDraw


class Calendar(QMainWindow):
    def __init__(self, directory):
        super().__init__()
        uic.loadUi('start.ui', self)

        self.setWindowTitle('Календарь')

        self.calendar = self.calendarWidget
        self.directory = directory

        self.forphoto = self.label
        self.csvstrings = []
        self.namefile = f'{self.directory}/readyworks.csv'

        self.memories = []
        self.counter = 0

        self.photobutton.clicked.connect(self.add_photo)
        self.graffitibutton.clicked.connect(self.add_paint)
        self.galereabutton.clicked.connect(self.watch_my_gallery)
        self.csvbutton.clicked.connect(self.add_csvtable)

    def write_in_csv(self):
        with open(self.namefile, 'w', newline='', encoding='utf-8') as csvfile:
            writer = _csv.writer(csvfile, delimiter=';', quotechar='"', quoting=_csv.QUOTE_MINIMAL)
            for i in self.csvstrings:
                writer.writerow(i)

    def add_photo(self):
        self.label_empty.clear()
        self.widgetforpfotos = NewPhoto(self.forphoto, self.directory, self.memories)
        self.csvstrings.append([f'{dt.datetime.now().time()}', 'Новая фотография', self.choose_date()])
        self.write_in_csv()

        self.widgetforpfotos.show()

    def add_paint(self):
        self.label_empty.clear()

        self.w = QWidget()
        self.csvstrings.append([f'{dt.datetime.now().time()}', 'Новое граффити', self.choose_date()])
        self.write_in_csv()

        self.newdrawing = Drawer(self.forphoto, self.w, self.memories)

        buttonsave = QPushButton()
        buttonsave.setText('Сохранить изображение')

        buttoncolor = QPushButton()
        buttoncolor.setText('Изменить цвет')

        buttondelete = QPushButton()
        buttondelete.setText('Перерисовать')

        self.w.setLayout(QVBoxLayout())
        self.w.layout().addWidget(buttonsave)
        self.w.layout().addWidget(buttoncolor)
        self.w.layout().addWidget(buttondelete)
        self.w.layout().addWidget(self.newdrawing)

        buttonsave.clicked.connect(lambda: self.newdrawing.saveImage(f'{self.directory}/' + f'{self.counter}'
                                                                     + self.choose_date() + '.jpg', "JPG"))
        buttondelete.clicked.connect(self.newdrawing.clearImage)
        buttoncolor.clicked.connect(self.newdrawing.change_color)

        self.w.show()

    def choose_date(self):
        data = self.calendar.selectedDate()
        self.counter += 1
        self.data = f'{data.getDate()}'
        return self.data

    def watch_my_gallery(self):
        if os.listdir(self.directory):
            self.widget = QWidget()
            self.setWindowTitle('Галерея')
            uic.loadUi('galery.ui', self.widget)
            labels = [self.widget.label, self.widget.label_1, self.widget.label_2,
                      self.widget.label_3, self.widget.label_4, self.widget.label_5]
            indexlabel = -1
            if len(self.memories) >= 6:
                self.memories = self.memories[-6:]
            for im in reversed(self.memories):
                indexlabel += 1
                image_for_label = Image.open(im)
                x, y = image_for_label.size
                otn = 120 / max([x, y])
                x *= otn
                y *= otn

                image_for_label_corrsize = image_for_label.resize((int(x), int(y)))
                image_for_label_corrsize.save('correct_size.jpg')

                pixmap = QPixmap('correct_size.jpg')

                labels[indexlabel].setPixmap(pixmap)
                os.remove('correct_size.jpg')
            self.widget.show()
        else:
            self.label_empty.setText('Галерея еще пуста!')

    def add_csvtable(self):
        if not os.path.exists(self.namefile):
            self.label_empty.setText('Еще нет воспоминаний!')
        else:
            self.w = QWidget()
            self.csvtable = CsvTable(self.namefile, self.w)
            buttonclose = QPushButton('OK')

            self.w.setLayout(QVBoxLayout())
            self.w.layout().addWidget(self.csvtable)
            self.w.layout().addWidget(buttonclose)

            buttonclose.clicked.connect(self.csvtable.hidewidget)
            self.w.show()


class NewPhoto(QWidget):
    def __init__(self, label, directory, memories):

        super().__init__()
        self.memory = memories
        self.setFixedSize(370, 380)
        self.setWindowTitle('Новое изображение')
        self.directory = directory

        self.bttn = QPushButton(self)
        self.bttn.setText('Ок')
        self.bttn.move(100, 345)
        self.bttn.clicked.connect(self.ready)

        self.deletebutton = QPushButton(self)
        self.deletebutton.move(200, 345)
        self.deletebutton.setText('Удалить фотографию')
        self.deletebutton.clicked.connect(self.deletephoto)

        self.label = QLabel(self)
        self.label.resize(300, 300)
        self.label.move(25, 25)

        self.w_b = False

        self.filename = self.dialog()

        self.label.setPixmap(self.make_pixmap())
        self.add_differences()

        self.labelforphoto = label

    def dialog(self):
        self.file = QFileDialog.getOpenFileName(self, 'Выбрать картинку',
                                                 '', 'Картинка (*.jpg);;Картинка (*.jpg);;Все файлы (*)')[0]

        return self.file

    def make_pixmap(self):
        if self.w_b:
            image = Image.open(f'{self.directory}/{self.filename.split("/")[-1]}')
        else:
            image = Image.open(self.filename)
        fname = self.filename.split('/')[-1]
        image.save(f'{self.directory}/{fname}')
        if f'{self.directory}/{fname}' not in self.memory:
            self.memory.append(f'{self.directory}/{fname}')

        x, y = image.size
        otn = 300 / max([x, y])
        x *= otn
        y *= otn
        image1 = image.resize((int(x), int(y)))
        image1.save('correct_size.jpg')
        self.pixmap = QPixmap('correct_size.jpg')
        os.remove('correct_size.jpg')

        return self.pixmap

    def add_differences(self):
        if self.filters() == 'white_black':
            self.white_black()
            self.label.setPixmap(self.make_pixmap())

    def filters(self):
        answer, ok_pressed = QInputDialog.getItem(self, "Фильтр", "Добавить фильтр?",
                                                  ("Нет", "Черно-белое изображение"), 1, False)
        if ok_pressed:
            if answer == 'Черно-белое изображение':
                return 'white_black'

    def white_black(self):
        im = Image.open(self.filename)
        draw = ImageDraw.Draw(im)
        width, height = im.size
        pix = im.load()
        for i in range(width):
            for j in range(height):
                a = pix[i, j][0]
                b = pix[i, j][1]
                c = pix[i, j][2]
                S = (a + b + c) // 3
                draw.point((i, j), (S, S, S))
        im.save(f'{self.directory}/{self.filename.split("/")[-1]}')
        self.w_b = True

    def ready(self):
        self.hide()
        self.labelforphoto.setPixmap(self.pixmap)

    def deletephoto(self):
        self.label.clear()
        self.hide()


class Drawer(QWidget):
    def __init__(self, label, widget, memories, parent=None):
        QWidget.__init__(self, parent)
        self.setAttribute(Qt.WA_StaticContents)

        self.setWindowTitle('Новое граффити')

        self.myPenWidth = 5
        self.myPenColor = QColor(0, 0, 0)
        self.image = QImage(300, 300, QImage.Format_RGB32)
        self.path = QPainterPath()
        self.clearImage()
        self.memory = memories

        self.labelforgraffiti = label
        self.widget_to_close = widget

    def setPenColor(self, newColor):
        self.myPenColor = newColor

    def setPenWidth(self, newWidth):
        self.myPenWidth = newWidth

    def clearImage(self):
        self.path = QPainterPath()
        self.image.fill(Qt.white)
        self.update()

    def saveImage(self, fileName, fileFormat):
        self.image.save(fileName, fileFormat)
        self.memory.append(fileName)
        self.pixmap = QPixmap().fromImage(self.image)
        self.hide()
        self.widget_to_close.hide()
        self.labelforgraffiti.setPixmap(self.pixmap)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(event.rect(), self.image, self.rect())

    def mousePressEvent(self, event):
        self.path.moveTo(event.pos())

    def mouseMoveEvent(self, event):
        self.path.lineTo(event.pos())
        p = QPainter(self.image)
        p.setPen(QPen(self.myPenColor, self.myPenWidth, Qt.SolidLine, Qt.RoundCap,
                      Qt.RoundJoin))
        p.drawPath(self.path)
        p.end()
        self.update()

    def sizeHint(self):
        return QSize(300, 300)

    def change_color(self):
        self.color = QColorDialog.getColor()
        if self.color.isValid():
            self.setPenColor(self.color)


class CsvTable(QWidget):
    def __init__(self, table_name, widget):
        super().__init__()

        self.setFixedSize(300, 300)
        self.setWindowTitle('Готовые работы')
        self.tableWidget = QTableWidget(self)
        self.tableWidget.resize(290, 300)
        self.tableWidget.move(0, 0)

        self.table_name = table_name
        self.loadTable(self.table_name)

        self.w = widget

    def loadTable(self, table_name):
        with open(table_name, encoding='utf-8') as csvfile:
            reader = _csv.reader(csvfile, delimiter=';', quotechar='"')

            self.tableWidget.setColumnCount(3)
            self.tableWidget.setHorizontalHeaderLabels(['Time', 'Type of memory', 'Date'])
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(reader):
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(elem))
        self.tableWidget.resizeColumnsToContents()

    def hidewidget(self):
        self.w.hide()
        self.hide()


def find_directory():
    ok = False
    while not ok:
        path = input('Введите директорию для создания в ней Галереи:')
        try:
            os.mkdir(path)
        except OSError:
            print("Создать директорию %s не удалось" % path)
        else:
            ok = True
            print("Успешно создана директория %s " % path)
            return path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Calendar(find_directory())
    ex.show()
    sys.exit(app.exec())

