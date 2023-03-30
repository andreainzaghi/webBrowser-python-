import os
import sys
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QAction, QVBoxLayout, QWidget, QToolBar, QStatusBar, QListWidget, QPushButton, QVBoxLayout, QDialog, QTabWidget, QLabel

from cryptography.fernet import Fernet
import base64

# Genera una chiave di crittografia e crea un oggetto Fernet
key = Fernet.generate_key()
cipher_suite = Fernet(key)


class HistoryWindow(QDialog):
    def __init__(self, history, *args, **kwargs):
        super(HistoryWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("Cronologia di ricerca")

        layout = QVBoxLayout()

        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        for item in history:
            decrypted_item = cipher_suite.decrypt(item).decode()
            self.history_list.addItem(decrypted_item)

        self.setLayout(layout)


class BrowserTab(QWidget):
    def __init__(self, *args, **kwargs):
        super(BrowserTab, self).__init__(*args, **kwargs)

        layout = QVBoxLayout()

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://www.google.com"))

        layout.addWidget(self.browser)

        self.setLayout(layout)


class SimpleBrowser(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(SimpleBrowser, self).__init__(*args, **kwargs)
        self.setWindowTitle("Simple Browser")

        # Imposta un tema scuro per l'applicazione
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

        self.tabs = QTabWidget()

        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)

        self.add_tab_btn = QAction(
            QIcon(os.path.join('qss_icons', 'add_tab.svg')), "New Tab", self)
        self.add_tab_btn.triggered.connect(self.add_tab)
        navtb.addAction(self.add_tab_btn)

        back_btn = QAction(
            QIcon(os.path.join('qss_icons', 'arrow_left.svg')), "Back", self)
        back_btn.triggered.connect(
            lambda: self.tabs.currentWidget().browser.back())
        navtb.addAction(back_btn)

        next_btn = QAction(
            QIcon(os.path.join('qss_icons', 'arrow_right.svg')), "Forward", self)
        next_btn.triggered.connect(
            lambda: self.tabs.currentWidget().browser.forward())
        navtb.addAction(next_btn)

        reload_btn = QAction(
            QIcon(os.path.join('qss_icons', 'refresh.svg')), "Reload", self)
        reload_btn.triggered.connect(
            lambda: self.tabs.currentWidget().browser.reload())
        navtb.addAction(reload_btn)

        home_btn = QAction(
            QIcon(os.path.join('qss_icons', 'home.svg')), "Home", self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        history_btn = QAction(
            QIcon(os.path.join('qss_icons', 'history.svg')), "Cronologia", self)
        history_btn.triggered.connect(self.show_history)
        navtb.addAction(history_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        navtb.addWidget(self.urlbar)

        self.history = []

        self.add_tab()

    def add_tab(self):
        new_tab = BrowserTab()
        i = self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentIndex(i)
        new_tab.browser.urlChanged.connect(
            lambda url, browser=new_tab.browser: self.update_urlbar(url, browser))
        new_tab.browser.loadFinished.connect(
            lambda _, i=i, browser=new_tab.browser: self.tabs.setTabText(i, browser.page().title()))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()

    def update_title(self, browser):
        title = browser.page().title()
        self.setWindowTitle("% s - Simple Browser" % title)

    def navigate_home(self):
        self.tabs.currentWidget().browser.setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")

        encrypted_url = cipher_suite.encrypt(self.urlbar.text().encode())
        self.history.append(encrypted_url)

        self.tabs.currentWidget().browser.setUrl(q)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget().browser:
            return

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def show_history(self):
        history_window = HistoryWindow(self.history)
        history_window.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Browser")
    app.setWindowIcon(QIcon(os.path.join('qss_icons', 'browser.svg')))
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec_())
