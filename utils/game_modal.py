from typing import Callable, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QPushButton, QHBoxLayout, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


# Shared dark modal style used by all game-related dialogs
STYLE = """
QDialog {
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    background: #071033;
}
QLabel {
    color: #e6eef8;
    font-size: 11pt;
}
QLabel#headerTitle {
    font-weight: 700;
    font-size: 12pt;
}
QLineEdit, QTextEdit {
    padding: 8px;
    border-radius: 8px;
    background: #ffffff;
    color: #071033;
    border: none;
}
QLineEdit:focus, QTextEdit:focus {
    border: 2px solid #0a84ff;
}
QPushButton {
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton#createBtn {
    background: #0b7d2a;
    color: white;
    font-weight: 600;
}
QPushButton#createBtn:hover {
    background: #0a6d24;
}
QPushButton#cancelBtn {
    background: #eef2f7;
    color: #0f172a;
}
QPushButton#dangerBtn {
    background: #b91c1c;
    color: white;
}
"""


def open_question_modal(parent, on_create: Optional[Callable[[dict], None]] = None):
    dlg = QDialog(parent)
    dlg.setWindowTitle("Create Question")
    dlg.setModal(True)

    # Remove buttons & frame (same as game modal)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
    dlg.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
    dlg.setWindowFlag(Qt.WindowCloseButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)

    # 🎨 SAME STYLE AS GAME MODAL
    dlg.setStyleSheet("""
    QDialog {
        border: 1px solid #ffffff;
        border-radius: 10px;
        background: #000e36;
    }
    QLabel {
        color: #ffffff;
        font-size: 11pt;
    }
    QLabel#headerTitle {
        font-weight: 700;
        font-size: 12pt;
    }
    QTextEdit {
        padding: 8px;
        border: 1px solid #e6e9ee;
        border-radius: 8px;
        background: #ffffff;
        color: #0f172a;
    }
    QTextEdit:focus {
        border: 2px solid #0a84ff;
    }
    QPushButton {
        background: transparent;
        color: #ffffff;
        border-radius: 6px;
        padding: 8px 12px;
        border: none;
    }
    QPushButton:hover {
        filter: brightness(0.95);
    }
    QPushButton:pressed {
        filter: brightness(0.9);
    }
    QPushButton#createBtn {
        background: #0b7d2a;
        color: white;
        font-weight: 600;
    }
    QPushButton#createBtn:hover {
        background: #0a6d24;
    }
    QPushButton#cancelBtn {
        background: #eef2f7;
        color: #0f172a;
    }
    QPushButton#cancelBtn:hover {
        background: #e6e9ee;
    }
    QPushButton#okBtn {
        background: #0a84ff;
        color: white;
        border-radius: 6px;
        padding: 6px 12px;
    }
    """)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(10)

    # 🏷 Header
    header = QHBoxLayout()
    title_label = QLabel("Create Question")
    title_label.setObjectName("headerTitle")

    font = QFont()
    font.setPointSize(12)
    font.setBold(True)
    title_label.setFont(font)

    header.addWidget(title_label)
    header.addStretch()
    layout.addLayout(header)

    # ❓ Question input
    lbl = QLabel("Question")
    layout.addWidget(lbl)

    q_entry = QTextEdit()
    q_entry.setFixedHeight(100)
    q_entry.setPlaceholderText("Enter your question here...")
    layout.addWidget(q_entry)

    # 📝 Details
    lbl2 = QLabel("Details (optional)")
    layout.addWidget(lbl2)

    details = QTextEdit()
    details.setFixedHeight(120)
    details.setPlaceholderText("Additional notes or hints...")
    layout.addWidget(details)

    # 🔘 Buttons
    btns = QHBoxLayout()

    cancel_btn = QPushButton("Cancel")
    create_btn = QPushButton("Create")

    cancel_btn.setObjectName("cancelBtn")
    create_btn.setObjectName("createBtn")

    cancel_btn.setCursor(Qt.PointingHandCursor)
    create_btn.setCursor(Qt.PointingHandCursor)

    # Disable until question has text
    create_btn.setEnabled(False)

    def _on_text_change():
        create_btn.setEnabled(bool(q_entry.toPlainText().strip()))

    q_entry.textChanged.connect(_on_text_change)

    btns.addWidget(cancel_btn)
    btns.addWidget(create_btn)
    layout.addLayout(btns)

    # ✅ Logic
    def on_ok():
        q = q_entry.toPlainText().strip()
        d = details.toPlainText().strip()

        if not q:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")

            l = QVBoxLayout(err)
            l.addWidget(QLabel("Please enter a question."))

            okb = QPushButton("OK")
            okb.setObjectName("okBtn")
            okb.clicked.connect(err.accept)

            l.addWidget(okb)
            err.exec()
            return

        payload = {"title": q, "details": d}
        dlg.accept()

        if on_create:
            on_create(payload)

    create_btn.clicked.connect(on_ok)
    cancel_btn.clicked.connect(dlg.reject)

    # 🖱 Draggable (same behavior)
    def _mousePressEvent(event):
        if event.button() == Qt.LeftButton:
            dlg._drag_pos = event.globalPosition().toPoint() - dlg.frameGeometry().topLeft()
            event.accept()

    def _mouseMoveEvent(event):
        if hasattr(dlg, "_drag_pos") and (event.buttons() & Qt.LeftButton):
            dlg.move(event.globalPosition().toPoint() - dlg._drag_pos)
            event.accept()

    dlg.mousePressEvent = _mousePressEvent
    dlg.mouseMoveEvent = _mouseMoveEvent

    # 📏 Size
    dlg.setFixedWidth(380)
    dlg.adjustSize()
    dlg.setFixedSize(dlg.size())

    q_entry.setFocus()
    dlg.exec()


def open_game_modal(parent, on_create: Optional[Callable[[dict], None]] = None):
    dlg = QDialog(parent)
    dlg.setWindowTitle("Create Game")
    dlg.setModal(True)

    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
    dlg.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
    dlg.setWindowFlag(Qt.WindowCloseButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)

    dlg.setStyleSheet(STYLE)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(10)

    header = QHBoxLayout()
    title_label = QLabel("Create Game")
    title_label.setObjectName("headerTitle")
    font = QFont()
    font.setPointSize(12)
    font.setBold(True)
    title_label.setFont(font)
    header.addWidget(title_label)
    header.addStretch()
    layout.addLayout(header)

    layout.addWidget(QLabel("Title"))
    title_entry = QLineEdit()
    title_entry.setPlaceholderText("Game title")
    layout.addWidget(title_entry)

    layout.addWidget(QLabel("Description (optional)"))
    desc = QTextEdit()
    desc.setFixedHeight(120)
    desc.setPlaceholderText("Short description...")
    layout.addWidget(desc)

    btns = QHBoxLayout()
    cancel_btn = QPushButton("Cancel")
    create_btn = QPushButton("Create")
    cancel_btn.setObjectName("cancelBtn")
    create_btn.setObjectName("createBtn")
    cancel_btn.setCursor(Qt.PointingHandCursor)
    create_btn.setCursor(Qt.PointingHandCursor)
    create_btn.setEnabled(False)

    def _on_text_change():
        create_btn.setEnabled(bool(title_entry.text().strip()))

    title_entry.textChanged.connect(_on_text_change)

    btns.addWidget(cancel_btn)
    btns.addWidget(create_btn)
    layout.addLayout(btns)

    def on_ok():
        t = title_entry.text().strip()
        d = desc.toPlainText().strip()
        if not t:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            l = QVBoxLayout(err)
            l.addWidget(QLabel("Please enter a title."))
            okb = QPushButton("OK")
            okb.setObjectName("okBtn")
            okb.clicked.connect(err.accept)
            l.addWidget(okb)
            err.exec()
            return
        payload = {"title": t, "description": d}
        dlg.accept()
        if on_create:
            on_create(payload)

    create_btn.clicked.connect(on_ok)
    cancel_btn.clicked.connect(dlg.reject)

    def _mousePressEvent(event):
        if event.button() == Qt.LeftButton:
            dlg._drag_pos = event.globalPosition().toPoint() - dlg.frameGeometry().topLeft()
            event.accept()

    def _mouseMoveEvent(event):
        if hasattr(dlg, "_drag_pos") and (event.buttons() & Qt.LeftButton):
            dlg.move(event.globalPosition().toPoint() - dlg._drag_pos)
            event.accept()

    dlg.mousePressEvent = _mousePressEvent
    dlg.mouseMoveEvent = _mouseMoveEvent

    dlg.setFixedWidth(420)
    dlg.adjustSize()
    dlg.setFixedSize(dlg.size())

    title_entry.setFocus()
    dlg.exec()


def open_edit_modal(parent, title: str, description: str, on_save: Optional[Callable[[dict], None]] = None):
    dlg = QDialog(parent)
    dlg.setWindowTitle("Edit Game")
    dlg.setModal(True)

    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)

    dlg.setStyleSheet(STYLE)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(12, 12, 12, 12)

    header = QHBoxLayout()
    title_lbl = QLabel("Edit Game")
    title_lbl.setObjectName("headerTitle")
    header.addWidget(title_lbl)
    header.addStretch()
    layout.addLayout(header)

    layout.addWidget(QLabel("Title"))
    title_entry = QLineEdit()
    title_entry.setText(title)
    layout.addWidget(title_entry)

    layout.addWidget(QLabel("Description (optional)"))
    desc = QTextEdit()
    desc.setPlainText(description or "")
    desc.setFixedHeight(120)
    layout.addWidget(desc)

    btns = QHBoxLayout()
    cancel_btn = QPushButton("Cancel")
    save_btn = QPushButton("Save")
    save_btn.setObjectName("createBtn")
    cancel_btn.setObjectName("cancelBtn")
    cancel_btn.setFixedHeight(30)
    save_btn.setFixedHeight(30)
    btns.addWidget(cancel_btn)
    btns.addWidget(save_btn)
    layout.addLayout(btns)

    def on_save_click():
        t = title_entry.text().strip()
        d = desc.toPlainText().strip()
        if not t:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            l = QVBoxLayout(err)
            l.addWidget(QLabel("Please enter a title."))
            okb = QPushButton("OK")
            okb.setObjectName("okBtn")
            okb.clicked.connect(err.accept)
            l.addWidget(okb)
            err.exec()
            return
        payload = {"title": t, "description": d}
        dlg.accept()
        if on_save:
            on_save(payload)

    save_btn.clicked.connect(on_save_click)
    cancel_btn.clicked.connect(dlg.reject)

    dlg.setFixedWidth(420)
    dlg.adjustSize()
    dlg.setFixedSize(dlg.size())
    dlg.exec()


def open_delete_confirm(parent, on_confirm: Optional[Callable[[], None]] = None):
    dlg = QDialog(parent)
    dlg.setWindowTitle("Delete Confirmation")
    dlg.setModal(True)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)

    dlg.setStyleSheet(STYLE)

    layout = QVBoxLayout(dlg)
    layout.setContentsMargins(16, 12, 16, 12)
    msg = QLabel("Are you sure you want to delete this game?")
    msg.setAlignment(Qt.AlignCenter)
    msg.setStyleSheet("color: #e6eef8; font-weight:600; padding:6px 12px;")
    layout.addWidget(msg)

    btns = QHBoxLayout()
    btns.setSpacing(10)
    cancel_btn = QPushButton("Cancel")
    del_btn = QPushButton("Delete")
    del_btn.setObjectName("dangerBtn")
    cancel_btn.setObjectName("cancelBtn")
    cancel_btn.setFixedHeight(32)
    del_btn.setFixedHeight(32)
    btns.addStretch()
    btns.addWidget(cancel_btn)
    btns.addWidget(del_btn)
    btns.addStretch()
    layout.addLayout(btns)

    def _on_del():
        dlg.accept()
        if on_confirm:
            on_confirm()

    del_btn.clicked.connect(_on_del)
    cancel_btn.clicked.connect(dlg.reject)

    dlg.setFixedWidth(360)
    dlg.adjustSize()
    dlg.setFixedSize(dlg.size())
    dlg.exec()