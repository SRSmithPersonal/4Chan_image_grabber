import sys
import requests
import os.path
import threading
import time
from os import listdir
from io import open as iopen
from os import makedirs
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget,\
    QPushButton, QHBoxLayout, QLineEdit, QLabel, QComboBox, QListWidget, QListWidgetItem, QAbstractItemView

listBoards = []
listGrabs = []
Stop = True
Active = False


# #Function to grab a list of all current 4Chan boards and their aliases, returns a list of tuples
def getBoards():
    adr = 'https://a.4cdn.org/boards.json'

    try:
        r = requests.get(adr)
        res = r.json()
    except Exception as e:
        print(e)

    boards = []

    for board in res["boards"]:
        boards.append((board["title"], board["board"]))

    return boards


# #Function that finds all threads on a board that have the given term/ phrase in there OP, then downloads all images
# #from those threads
def crawler(board, topic):
    print("Start Scrapping")
    adr = 'https://a.4cdn.org/{}/catalog.json'.format(board)

    # #Collect JSON data for board from 4chan API
    try:
        r = requests.get(adr)
        res = r.json()
    except Exception as e:
        print(e)

    # # make a list of threads that have the given term in their OP
    threadsy = []

    for page in res:
        for thread in page["threads"]:
            if "com" in thread:
                if topic in thread["com"]:
                    threadsy.append(thread["no"])
                elif "sub" in thread:
                    if topic in thread["sub"]:
                        threadsy.append(thread["no"])
            elif "sub" in thread:
                if topic in thread["sub"]:
                    threadsy.append(thread["no"])

    print("Number of threads found: ", len(threadsy))

    # #Set path to save image files and create the directory if needed
    dir_path = os.path.dirname(os.path.realpath(__file__))
    save_path = os.path.join(dir_path, "4chan/{}".format(topic))
    if not os.path.isdir(save_path):
        makedirs(save_path)

    # #List of files in directory
    files = listdir(save_path)

    # #For each thread found, the JSON data of that thread is collected, the each post is checked for attachments, which
    # #are then downloaded
    for thread in threadsy:
        if not Stop:
            jsonurl = "http://api.4chan.org/{}/res/{}.json".format(board, thread)

            try:
                r = requests.get(jsonurl)
                res = r.json()
            except Exception as e:
                print(e)

            for post in res["posts"]:
                if not Stop:
                    if ("filename" in post) and ("filedeleted" not in post):
                        file_name = "{}{}".format(post["tim"], post["ext"])
                        file_url = "http://i.4cdn.org/{}/{}".format(board, file_name)
                        # prevent grabbing the same post's image more than once
                        if file_name not in files:
                            re = requests.get(file_url)
                            complete_name = os.path.join(save_path, file_name)
                            with iopen(complete_name, 'wb') as file:
                                file.write(re.content)
                                file.close()

    print("Scrapping completed")


# #Function that performs a single scrapping run
def starter():
    global Active
    for search in listGrabs:
        if not Stop:
            crawler(search[0], search[1])
        else:
            print("stopping")
            break
    Active = False


# #Function that performs a scrapping run once every hour
def astarter():
    global Active
    while not Stop:
        for search in listGrabs:
            if not Stop:
                crawler(search[0], search[1])
            else:
                break

        for i in range(3600):
            if not Stop:
                time.sleep(1)
            else:
                print("stopping")
                break
    Active = False


# #Create the Gui
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget(self)
        self.ret = 'b'
        self.topic = ''
        self.thread = []
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
        for board in listBoards:
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
        global Stop, Active
        if not Active:
            Active = True
            Stop = False
            self.thread = threading.Thread(target=starter, args=())
            self.thread.daemon = True
            self.thread.start()

    # #Function for 'add' button
    def add(self):
        global listGrabs
        listGrabs.append((self.ret, self.topic))
        item = QListWidgetItem(self.ret + ', ' + self.topic)
        self.list.addItem(item)

    # #Function for 'auto' button
    def auto(self):
        global Stop, Active
        if not Active:
            Active = True
            Stop = False
            self.thread = threading.Thread(target=astarter, args=())
            self.thread.daemon = True
            self.thread.start()

    # #Function for 'stop' button
    def stop(self):
        global Stop
        Stop = True

    # #Function for 'delete' button
    def delete(self):
        global listGrabs
        listit = self.list.selectedItems()
        for item in listit:
            temp = item.text().split(', ')
            tup = (temp[0], temp[1])
            listGrabs.remove(tup)
            self.list.takeItem(self.list.row(item))

    # #Function for 'boards' drop down menu
    def choice(self, text):
        for board in listBoards:
            if text == board[0]:
                self.ret = board[1]
                break

    # #Function for reading in topic when edited
    def on_changed(self, text):
        self.topic = text


if __name__ == '__main__':
    listBoards = getBoards()
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
