import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QTextEdit, QShortcut, QDesktopWidget
)
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QKeySequence, QIcon
from src.workflow import Workflow

class Worker(QObject):
    finished = pyqtSignal(object, str)

    def __init__(self, workflow, query):
        super().__init__()
        self.workflow = workflow
        self.query = query

    def run(self):
        result = self.workflow.run(self.query)
        self.finished.emit(result, self.query)

class MainWindow(QMainWindow):
    log_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("favicon.ico"))
        self.setWindowTitle("Coding Agent Model - PyQt5 GUI")

        # Dynamically set window size to 60% of screen width and 70% of screen height
        screen = QDesktopWidget().screenGeometry()
        width = int(screen.width() * 0.6)
        height = int(screen.height() * 0.7)
        self.setGeometry(
            int((screen.width() - width) / 2),
            int((screen.height() - height) / 2),
            width,
            height
        )

        self.dark_mode = True

        main_layout = QVBoxLayout()
        title = QLabel("<h2>Coding Agent Model</h2>")
        main_layout.addWidget(title)

        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter your developer tools query...")
        self.input.returnPressed.connect(self.on_button_click)
        input_layout.addWidget(self.input)

        self.button = QPushButton("Search")
        self.button.clicked.connect(self.on_button_click)
        input_layout.addWidget(self.button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_results)
        input_layout.addWidget(self.clear_button)

        self.toggle_dark_button = QPushButton("Toggle Dark Mode")
        self.toggle_dark_button.clicked.connect(self.toggle_dark_mode)
        input_layout.addWidget(self.toggle_dark_button)

        main_layout.addLayout(input_layout)

        self.results = QTextEdit()
        self.results.setReadOnly(True)
        main_layout.addWidget(self.results)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Keyboard shortcut for quit
        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.quit_shortcut.activated.connect(self.close)

        # Logger for backend prints, using signal to ensure main thread update
        self.log_signal.connect(self.append_log)
        self.workflow = Workflow(logger=self.gui_logger)

        # Start in dark mode
        self.apply_dark_mode()

    def gui_logger(self, message):
        print(message)  # Also print to CLI
        self.log_signal.emit(message)

    def append_log(self, message):
        self.results.append(f'<span style="color:#00b894;">{message}</span>')

    def on_button_click(self):
        query = self.input.text().strip()
        if not query:
            self.results.setText("Please enter a query.")
            return
        self.results.setText("Searching... Please wait.")
        self.button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.thread = QThread()
        self.worker = Worker(self.workflow, query)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.display_results)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def display_results(self, result, query):
        output = f"<b></br>Results for: {query}</b><br>"
        for i, company in enumerate(result.companies, 1):
            output += f"<br><b>{i}. 🏢 {company.name}</b><br>"
            output += f"   🌐 <b>Website:</b> {company.website}<br>"
            output += f"   💰 <b>Pricing:</b> {company.pricing_model}<br>"
            output += f"   📖 <b>Open Source:</b> {company.is_open_source}<br>"
            if company.tech_stack:
                output += f"   🛠️  <b>Tech Stack:</b> {', '.join(company.tech_stack[:5])}<br>"
            if company.language_support:
                output += f"   💻 <b>Language Support:</b> {', '.join(company.language_support[:5])}<br>"
            if company.api_available is not None:
                api_status = "✅ Available" if company.api_available else "❌ Not Available"
                output += f"   🔌 <b>API:</b> {api_status}<br>"
            if company.integration_capabilities:
                output += f"   🔗 <b>Integrations:</b> {', '.join(company.integration_capabilities[:4])}<br>"
            if company.description and company.description != "Analysis failed":
                output += f"   📝 <b>Description:</b> {company.description}<br>"
            output += "<br>"
        if result.analysis:
            output += "<b>Developer Recommendations:</b><br>"
            output += "-"*40 + "<br>"
            output += result.analysis
        self.results.append(output)
        self.button.setEnabled(True)
        self.clear_button.setEnabled(True)

    def clear_results(self):
        self.input.clear()
        self.results.clear()

    def apply_dark_mode(self):
        self.setStyleSheet("""
            QMainWindow { background: #23272e; }
            QLabel { color: #f1f2f6; font-size: 18px; }
            QLineEdit {
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
                font-size: 16px;
                background: #2d3436;
                color: #f1f2f6;
            }
            QPushButton {
                background: #0984e3;
                color: #fff;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 16px;
            }
            QPushButton:disabled {
                background: #636e72;
                color: #b2bec3;
            }
            QTextEdit {
                background: #2d3436;
                border: 1px solid #444;
                border-radius: 6px;
                font-size: 15px;
                padding: 8px;
                color: #f1f2f6;
            }
        """)

    def apply_light_mode(self):
        self.setStyleSheet("""
            QMainWindow { background: #f5f6fa; }
            QLabel { color: #222f3e; font-size: 18px; }
            QLineEdit {
                border: 1px solid #b2bec3;
                border-radius: 6px;
                padding: 6px;
                font-size: 16px;
                background: #fff;
                color: #222f3e;
            }
            QPushButton {
                background: #0984e3;
                color: #fff;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 16px;
            }
            QPushButton:disabled {
                background: #b2bec3;
                color: #636e72;
            }
            QTextEdit {
                background: #fff;
                border: 1px solid #b2bec3;
                border-radius: 6px;
                font-size: 15px;
                padding: 8px;
                color: #222f3e;
            }
        """)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())