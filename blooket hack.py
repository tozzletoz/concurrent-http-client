import aiohttp
import asyncio
import time
import sys
import ast
import random
import traceback
from PySide6.QtWidgets import *


def errorhandling(exc_type, exc_value, exc_tb):
    window.exeption(type=exc_type, value=exc_value)

async def sent(session, i, method= str, url= str, headers=dict, payload=dict, amount=float | int):
    global fails, completes, window
    if payload == {}:
        payload = None
    fails = 0
    completes = 0
    if method == "POST":
        async with session.post(url, headers=headers, json=payload) as response:
            response_data = await response.text()
            status = response.status

    if method == "GET":
        async with session.get(url, headers=headers, json=payload) as response:
            response_data = await response.text()
            status = response.status
    
    if method == "PATCH":
        async with session.patch(url, headers=headers, json=payload) as response:
            response_data = await response.text()
            status = response.status

    if method == "DELETE":
        async with session.delete(url, headers=headers, json=payload) as response:
            response_data = await response.text()
            status = response.status

    if method == "HEAD":
        async with session.head(url, headers=headers, json=payload) as response:
            response_data = await response.text()
            status = response.status

    if method == "OPTIONS":
        async with session.options(url, headers=headers, json=payload) as response:
            response_data = await response.text()
            status = response.status

    if method == "PUT":
        async with session.put(url, headers=headers, json=payload) as response:
            response_data = await response.text()
            status = response.status


    completes+=1
    print(completes, amount)
    window.testing(value=completes, max_val=amount)
    return status, response_data


async def main(method, amount, url, headers, payload="{}"):
    global responses, response
    time1 = time.time()

    if payload != "":
        formatted = ast.literal_eval(payload)
    else:
        formatted = {}

    async with aiohttp.ClientSession() as session:
        tasks = [sent(session, x, method, url, headers, payload=formatted, amount=amount) for x in range(0, int(amount))]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            response = response[1]

        timed = time.time()-time1
        window.showresp(timed=timed)

#asyncio.run(main())

#GUI

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Concurrent HTTP Client")
        self.adjustSize()
        self.setFixedWidth(318)

        self.add = QPushButton("Add header")
        self.add.clicked.connect(self.addheader)

        self.btn_start = QPushButton("Execute")
        self.btn_start.clicked.connect(self.execute)
        self.amount = QLineEdit()
        self.amount.setPlaceholderText("Amount...")
        self.amount.setText("1")
        self.url = QLineEdit()
        self.url.setPlaceholderText("URL...")

        self.copytocb = QPushButton("Copy response to clipboard")
        self.copytocb.clicked.connect(self.copy)
        self.timetaken = QLabel("")
        self.timetaken.setContentsMargins(0, 0, 0, 0)
        

        self.url.setText("https://region1.google-analytics.com/g/")

        self.methods = QComboBox()

        self.methods.addItems(("GET", "POST", "PATCH", "PUT", "HEAD", "DELETE", "OPTIONS"))

        self.vlayout = QVBoxLayout()
        self.header_holder = QVBoxLayout()
        self.payload = QTextEdit()
        self.payload.setPlaceholderText("Payload (JSON format)...")
        self.payload.setMaximumHeight(100)

        self.payload.setTabStopDistance(4 * self.payload.fontMetrics().horizontalAdvance(' '))

        self.respcontainer = QTextEdit()
        self.respcontainer.setMaximumHeight(100)
        self.respcontainer.setPlaceholderText("Response...")
        self.respcontainer.setReadOnly(True)

        self.progress = QProgressBar()
        self.progress.setValue(0)

        self.vlayout.addWidget(self.add)
        self.vlayout.addLayout(self.header_holder)
        self.vlayout.addWidget(self.payload)
        self.vlayout.addWidget(self.methods)
        self.vlayout.addWidget(self.url)
        self.vlayout.addWidget(self.amount)
        self.vlayout.addWidget(self.btn_start)
        self.vlayout.addWidget(self.progress)
        self.vlayout.addWidget(self.respcontainer)
        self.vlayout.addWidget(self.copytocb)
        self.vlayout.addWidget(self.timetaken)

        self.setLayout(self.vlayout)

        self.headers = {}
        self.formattedheaders = {}
        self.container = {}

        #STYLES:
        self.btn_start.setStyleSheet("background-color:rgb(19, 61, 134)")

    def exeption(self, type, value):
        self.timetaken.setText(f"An exeption occurred: {type}")

    def testing(self, value, max_val):
        self.progress.setRange(0, max_val)
        self.progress.setValue(float(value))
        print(self.progress.value(), int(max_val))
        QApplication.processEvents()

    def copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.respcontainer.toPlainText())

    def showresp(self, timed):
        self.respcontainer.clear()
        self.respcontainer.setPlainText(str(response))
        self.timetaken.setText(f"Time taken: {round(float(timed), 2)}s")

    def addheader(self):
        self.hlayout = QHBoxLayout()
        inpkey = QLineEdit()
        inpkey.setPlaceholderText("header name")
        inpvalue = QLineEdit()
        inpvalue.setPlaceholderText("value name")
        remove = QPushButton("X")
        remove.clicked.connect(self.removeheader)
        remove.setStyleSheet("background-color:rgb(134, 19, 19)")
        remove.setFixedWidth(25)
        self.headers[inpkey] = inpvalue
        self.hlayout.addWidget(inpkey)
        self.hlayout.addWidget(inpvalue)
        self.hlayout.addWidget(remove)

        self.container[remove] = inpkey

        self.header_holder.setContentsMargins(0, 0, 0, 0)
        self.header_holder.setSpacing(3)
        self.header_holder.addLayout(self.hlayout)
        self.vlayout.addLayout(self.header_holder)

    def removeheader(self):
        clicked = self.sender()
        value = self.container[clicked]
        inp1 = self.headers[value]
        inp2 = value
        self.container.pop(clicked)
        self.headers.pop(inp2)
        
        inp1.deleteLater()
        inp2.deleteLater()
        clicked.deleteLater()
        self.adjustSize()
        try:
            self.formattedheaders.pop(value.text())
        except:
            pass

    def execute(self):
        self.progress.setValue(0)
        self.respcontainer.clear()
        self.timetaken.clear()
        QApplication.processEvents()
        self.get_headers()
        method = self.methods.currentText()
        if self.payload.toPlainText() != "":
            asyncio.run(main(method=method, amount=float(self.amount.text()), url=str(self.url.text()), headers=self.formattedheaders, payload=str(self.payload.toPlainText())))
        else:
            asyncio.run(main(method=method, amount=float(self.amount.text()), url=str(self.url.text()), headers=self.formattedheaders))


    def get_headers(self):
        for x in self.headers.keys():
            value = self.headers[x]
            self.formattedheaders[x.text()] = value.text()


app = QApplication(sys.argv)
window = Window()
window.show()

sys.excepthook = errorhandling
sys.exit(app.exec())