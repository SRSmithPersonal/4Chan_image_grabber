import scripts.crawl_scrape_4chan as c4
import threading
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget,\
    QPushButton, QHBoxLayout, QLineEdit, QLabel, QComboBox, QListWidget, QListWidgetItem, QAbstractItemView


# #Create the Gui
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget(self)
        self.ret = 'b'
        self.topic = ''
        self.thread = []
        self.listBoards = c4.getBoards()
        self.listGrabs = []
        # #create layout
        hbox1 = QHBoxLayout()
        hbox1.addStretch(1)
        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox3 = QHBoxLayout()
        hbox3.addStretch(1)
        hbox4 = QHBoxLayout()
        hbox4.addStretch(1)
        hbox5 = QHBoxLayout()
        hbox5.addStretch(1)
        vbox1 = QVBoxLayout()
        vbox1.addStretch(1)

        # #create run button
        self.btn1 = QPushButton('Start', self)
        self.btn1.clicked.connect(self.start)
        self.btn1.resize(self.btn1.sizeHint())
        self.btn1.setToolTip('Perform a single scrapping based on given search list')

        # #create add button
        self.btn2 = QPushButton('Add', self)
        self.btn2.clicked.connect(self.add)
        self.btn2.resize(self.btn1.sizeHint())
        self.btn2.setToolTip('Add item to search list')

        # #create auto button
        self.btn3 = QPushButton('Auto', self)
        self.btn3.clicked.connect(self.auto)
        self.btn3.resize(self.btn1.sizeHint())
        self.btn3.setToolTip('Perform scrapping based on given search list every hour')

        # #create stop button
        self.btn4 = QPushButton('Stop', self)
        self.btn4.clicked.connect(self.stop)
        self.btn4.resize(self.btn1.sizeHint())
        self.btn4.setToolTip('Stop current operation')

        # #create delete button
        self.btn5 = QPushButton('Delete', self)
        self.btn5.clicked.connect(self.delete)
        self.btn5.resize(self.btn1.sizeHint())
        self.btn5.setToolTip('Delete selected items from list')

        # #create boards dropdown box
        self.lbl1 = QLabel()
        self.lbl1.setText('Board')
        self.combo = QComboBox(self)
        for board in self.listBoards:
            self.combo.addItem(board[0])
        self.combo.activated[str].connect(self.choice)

        # #create search topic box
        self.lbl2 = QLabel()
        self.lbl2.setText('Search Topic')
        self.top = QLineEdit(self)
        self.top.textChanged[str].connect(self.on_changed)

        # #create list box for search results
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # #feed widgets into layout
        hbox2.addWidget(self.lbl1)
        hbox2.addWidget(self.combo)
        hbox3.addWidget(self.lbl2)
        hbox3.addWidget(self.top)
        vbox1.addLayout(hbox2)
        vbox1.addLayout(hbox3)
        hbox4.addWidget(self.btn1)
        hbox4.addWidget(self.btn2)
        hbox4.addWidget(self.btn3)
        hbox4.addWidget(self.btn4)
        hbox5.addWidget(self.btn5)
        vbox1.addLayout(hbox4)
        vbox1.addLayout(hbox5)
        vbox1.addWidget(self.list)
        hbox1.addLayout(vbox1)

        self.main_widget.setLayout(hbox1)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.initui()

    def initui(self):
        self.setWindowTitle('4Chan Image scrapper')
        self.show()

    # #Function for 'run' button
    def start(self):
        if not c4.Active:
            c4.set_active()
            self.thread = threading.Thread(target=c4.starter, args=(self.listGrabs,))
            self.thread.daemon = True
            self.thread.start()

    # #Function for 'add' button
    def add(self):
        self.listGrabs.append((self.ret, self.topic))
        item = QListWidgetItem(self.ret + ', ' + self.topic)
        self.list.addItem(item)

    # #Function for 'auto' button
    def auto(self):
        if not c4.Active:
            c4.set_active()
            self.thread = threading.Thread(target=c4.astarter, args=(self.listGrabs,))
            self.thread.daemon = True
            self.thread.start()

    # #Function for 'stop' button
    def stop(self):
        c4.set_stop()

    # #Function for 'delete' button
    def delete(self):
        listit = self.list.selectedItems()
        for item in listit:
            temp = item.text().split(', ')
            tup = (temp[0], temp[1])
            self.listGrabs.remove(tup)
            self.list.takeItem(self.list.row(item))

    # #Function for 'boards' drop down menu
    def choice(self, text):
        for board in self.listBoards:
            if text == board[0]:
                self.ret = board[1]
                break

    # #Function for reading in topic when edited
    def on_changed(self, text):
        self.topic = text