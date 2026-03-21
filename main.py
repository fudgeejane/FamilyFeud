from importlib import import_module
import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QStackedLayout,
    QDialog,
)
from PySide6.QtCore import Qt, Slot

# Button styles
APP_STYLE = """
QWidget{background: #000e36; color: #ffffff; font-family: 'Segoe UI', Roboto, Arial, sans-serif;}
QLabel{color: #111827}
QLineEdit, QTextEdit {background: #ffffff; color: #111827; border: 1px solid #e5e7eb; border-radius:6px; padding:6px}
QDialog {background: #ffffff}
"""

PRIMARY_BTN = "background:#0a84ff; color:white; border-radius:8px; padding:8px 14px; font-weight:600;"
SUCCESS_BTN = "background:#16a34a; color:white; border-radius:8px; padding:8px 14px; font-weight:600;"
CANCEL_BTN = "background:#f3f4f6; color:#111827; border-radius:8px; padding:8px 14px;"


class TCCFeudApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCC Feud")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        self.stack_widget = QWidget()
        self.stack = QStackedLayout(self.stack_widget)
        main_layout.addWidget(self.stack_widget)

        self.home_widget = QWidget()
        self.game_widget = QWidget()
        self.stack.addWidget(self.home_widget)
        self.stack.addWidget(self.game_widget)

        # Try to delegate home building to modules.home.build_home
        try:
            mod = import_module("modules.home")
            if hasattr(mod, "build_home"):
                mod.build_home(self.home_widget, self)
            else:
                self._default_build_home()
        except Exception:
            self._default_build_home()

        self._build_game()

        self.showFullScreen()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
        # Removed F11 fullscreen toggle to keep fixed non-resizable window

    def _default_build_home(self):
        f = self.home_widget
        layout = QVBoxLayout(f)
        layout.setContentsMargins(60, 60, 60, 40)

        title = QLabel("Welcome")
        title.setStyleSheet("font-size:40pt; color: #111827;")
        layout.addWidget(title, alignment=Qt.AlignTop)

        subtitle = QLabel("TCC Feud — Create a new game")
        subtitle.setStyleSheet("font-size:12pt; color: #6b7280;")
        layout.addWidget(subtitle)

        form = QWidget()
        form_layout = QVBoxLayout(form)

        form_layout.addWidget(QLabel("Game Title:"))
        self.title_entry = QLineEdit()
        self.title_entry.setFixedHeight(34)
        form_layout.addWidget(self.title_entry)

        form_layout.addWidget(QLabel("Description:"))
        self.desc_text = QTextEdit()
        self.desc_text.setFixedHeight(140)
        form_layout.addWidget(self.desc_text)

        layout.addWidget(form)

        create_btn = QPushButton("Create Game")
        create_btn.setFixedHeight(48)
        create_btn.setStyleSheet(PRIMARY_BTN)
        create_btn.clicked.connect(self.on_create_game)
        create_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(create_btn)

        # Try to wire Create Game button if utils.game_modal exists
        try:
            gm = import_module("utils.game_modal")

            def on_game_created(payload):
                self.show_static_modal("Game Created", payload.get("title", "(no title)"))

            gbtn = QPushButton("Create Game")
            gbtn.setStyleSheet(SUCCESS_BTN)
            gbtn.clicked.connect(lambda: gm.open_game_modal(self, on_create=on_game_created))
            gbtn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(gbtn)
        except Exception:
            pass

        spacer = QWidget()
        spacer.setMinimumHeight(20)
        layout.addWidget(spacer)

    def _build_game(self):
        f = self.game_widget
        layout = QVBoxLayout(f)
        header = QHBoxLayout()
        back = QPushButton("← Home")
        back.setStyleSheet(CANCEL_BTN)
        back.clicked.connect(self.show_home)
        back.setCursor(Qt.PointingHandCursor)
        header.addWidget(back)
        layout.addLayout(header)

        self.game_title_label = QLabel("")
        self.game_title_label.setStyleSheet("font-size:28pt; color: #111827;")
        layout.addWidget(self.game_title_label)

        self.game_desc_label = QLabel("")
        self.game_desc_label.setWordWrap(True)
        self.game_desc_label.setStyleSheet("font-size:12pt; color: #6b7280;")
        layout.addWidget(self.game_desc_label)

    @Slot()
    def show_home(self):
        self.stack.setCurrentWidget(self.home_widget)

    def show_game(self, title: str, description: str):
        # clear inputs if present
        try:
            self.title_entry.clear()
            self.desc_text.clear()
        except Exception:
            pass
        self.game_title_label.setText(title or "(Untitled Game)")
        self.game_desc_label.setText(description or "(No description provided)")
        self.stack.setCurrentWidget(self.game_widget)

    def on_create_game(self):
        title = getattr(self, "title_entry", QLineEdit()).text().strip()
        description = getattr(self, "desc_text", QTextEdit()).toPlainText().strip()

        def after():
            self.show_game(title, description)

        self.show_static_modal("Creating game...", "Your game is being created. This is a static modal display.", after)

    def show_static_modal(self, header: str, body: str, on_close=None):
        dlg = QDialog(self)
        dlg.setWindowTitle(header)
        dlg.setModal(True)
        dlg_layout = QVBoxLayout(dlg)
        lbl = QLabel(body)
        lbl.setWordWrap(True)
        dlg_layout.addWidget(lbl)
        placeholder = QLabel("[static display]")
        placeholder.setStyleSheet("background:#f3f4f6; color:#374151; padding:20px; border-radius:6px;")
        dlg_layout.addWidget(placeholder, alignment=Qt.AlignCenter)
        btn = QPushButton("OK")
        btn.setStyleSheet(PRIMARY_BTN)
        btn.clicked.connect(lambda: (dlg.accept(), on_close() if on_close else None))
        btn.setCursor(Qt.PointingHandCursor)
        dlg_layout.addWidget(btn, alignment=Qt.AlignCenter)
        dlg.exec()


def main():
    app = QApplication(sys.argv)
    try:
        app.setStyleSheet(APP_STYLE)
    except Exception:
        pass
    window = TCCFeudApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
