from typing import Callable, Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


def open_game_modal(parent, on_create: Optional[Callable[[dict], None]] = None):
    dlg = QDialog(parent)
    dlg.setWindowTitle("Create Game")
    dlg.setModal(True)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
    # Remove minimize, maximize and close buttons
    dlg.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
    dlg.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
    dlg.setWindowFlag(Qt.WindowCloseButtonHint, False)
    # Remove the title bar / frame entirely
    dlg.setWindowFlag(Qt.FramelessWindowHint, True)
    
    # Style the dialog itself: rounded corners and background (no visible border)
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
    QLineEdit, QTextEdit {
        padding: 8px;
        border: 1px solid #e6e9ee;
        border-radius: 8px;
        background: #ffffff;
        color: #0f172a;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 2px solid #0a84ff;
        outline: none;
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
    QPushButton:disabled {
        background: #f1f5f9;
        color: #94a3b8;
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
    QPushButton#closeBtn {
        background: transparent;
        color: #cbd5e1;
        font-size: 14px;
        border: none;
    }
    QPushButton#closeBtn:hover {
        color: #ffffff;
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

    # Header with title and close button
    header = QHBoxLayout()
    title_label = QLabel("Create Game")
    title_font = QFont()
    title_font.setPointSize(12)
    title_font.setBold(True)
    title_label.setFont(title_font)
    title_label.setStyleSheet("")
    title_label.setObjectName("headerTitle")
    header.addWidget(title_label)
    header.addStretch()
    close_btn = QPushButton("✕")
    close_btn.setFixedSize(28, 28)
    close_btn.setObjectName("closeBtn")
    close_btn.setCursor(Qt.PointingHandCursor)
    close_btn.clicked.connect(dlg.reject)
    header.addWidget(close_btn)
    layout.addLayout(header)

    # Title input (single-line) with placeholder
    lbl = QLabel("Game Title")
    layout.addWidget(lbl)
    title_entry = QLineEdit()
    title_entry.setPlaceholderText("Enter a title for your game")
    title_entry.setFixedHeight(36)
    title_entry.setStyleSheet("padding:6px; border:1px solid #e6e9ee; border-radius:6px;")
    layout.addWidget(title_entry)

    # Description field
    lbl2 = QLabel("Description (optional)")
    layout.addWidget(lbl2)
    details = QTextEdit()
    details.setFixedHeight(140)
    details.setStyleSheet("padding:8px; border:1px solid #e6e9ee; border-radius:6px;")
    layout.addWidget(details)

    btns = QHBoxLayout()
    cancel_btn = QPushButton("Cancel")
    create_btn = QPushButton("Create")
    # Object names used by dialog stylesheet for consistent styling
    create_btn.setObjectName("createBtn")
    cancel_btn.setObjectName("cancelBtn")
    cancel_btn.setCursor(Qt.PointingHandCursor)
    create_btn.setCursor(Qt.PointingHandCursor)

    # Create disabled until title entered
    create_btn.setEnabled(False)
    def _on_title_change(text: str):
        create_btn.setEnabled(bool(text.strip()))
    title_entry.textChanged.connect(_on_title_change)
    # Allow Enter to submit when focused on title
    title_entry.returnPressed.connect(lambda: on_ok())

    btns.addWidget(cancel_btn)
    btns.addWidget(create_btn)
    layout.addLayout(btns)

    def on_ok():
        title = title_entry.text().strip()
        d = details.toPlainText().strip()
        if not title:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            l = QVBoxLayout(err)
            l.addWidget(QLabel("Please enter a game title."))
            okb = QPushButton("OK")
            okb.setObjectName("okBtn")
            okb.clicked.connect(err.accept)
            l.addWidget(okb)
            err.exec()
            return
        payload = {"title": title, "description": d}
        dlg.accept()
        if on_create:
            on_create(payload)

    create_btn.clicked.connect(on_ok)
    cancel_btn.clicked.connect(dlg.reject)

    # Make dialog draggable since it's frameless
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

    # Final sizing: prefer a fixed width and adapt height
    dlg.setFixedWidth(380)
    dlg.adjustSize()
    dlg.setFixedSize(dlg.size())

    title_entry.setFocus()

    dlg.exec()
