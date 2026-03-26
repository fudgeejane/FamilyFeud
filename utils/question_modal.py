from typing import Callable, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QPushButton, QHBoxLayout, QWidget, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt


def open_question_modal(parent, on_create: Optional[Callable[[dict], None]] = None):
    dlg = QDialog(parent)
    dlg.setWindowModality(Qt.WindowModal)
    dlg.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
    dlg.setAttribute(Qt.WA_TranslucentBackground, True)

    outer = QVBoxLayout(dlg)
    outer.setContentsMargins(0, 0, 0, 0)

    # 🌫 Backdrop
    backdrop = QWidget(dlg)
    backdrop.setStyleSheet("background: rgba(2,6,23,0.65);")
    back_layout = QVBoxLayout(backdrop)
    back_layout.setContentsMargins(24, 24, 24, 24)

    # 🧾 Panel (Card UI)
    panel = QWidget(backdrop)
    panel.setStyleSheet("""
        background:#ffffff;
        border-radius:16px;
        padding:18px;
    """)
    panel_layout = QVBoxLayout(panel)
    panel_layout.setSpacing(12)
    panel_layout.setContentsMargins(16, 16, 16, 16)

    # ✨ Shadow
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(30)
    shadow.setXOffset(0)
    shadow.setYOffset(8)
    shadow.setColor(Qt.black)
    panel.setGraphicsEffect(shadow)

    # 🏷 Title
    title_lbl = QLabel("Create Question")
    title_lbl.setStyleSheet("""
        font-weight:700;
        font-size:16pt;
        color:#0f172a;
    """)
    panel_layout.addWidget(title_lbl)

    # Question
    lbl = QLabel("Question:")
    lbl.setStyleSheet("color:#374151; font-size:10.5pt; font-weight:600;")
    panel_layout.addWidget(lbl)

    q_entry = QTextEdit()
    q_entry.setFixedHeight(100)
    q_entry.setStyleSheet("""
        QTextEdit {
            border:1px solid #d1d5db;
            border-radius:10px;
            padding:10px;
            font-size:11pt;
            background:#f9fafb;
        }
        QTextEdit:focus {
            border:1px solid #0a84ff;
            background:#ffffff;
        }
    """)
    panel_layout.addWidget(q_entry)

    # Details
    lbl2 = QLabel("Details / Notes (optional):")
    lbl2.setStyleSheet("color:#374151; font-size:10.5pt; font-weight:600;")
    panel_layout.addWidget(lbl2)

    details = QTextEdit()
    details.setFixedHeight(140)
    details.setStyleSheet(q_entry.styleSheet())
    panel_layout.addWidget(details)

    # 🔘 Buttons
    btns = QHBoxLayout()
    btns.addStretch()

    cancel_btn = QPushButton("Cancel")
    create_btn = QPushButton("Create")

    cancel_btn.setCursor(Qt.PointingHandCursor)
    create_btn.setCursor(Qt.PointingHandCursor)

    cancel_btn.setStyleSheet("""
        QPushButton {
            background:#f3f4f6;
            color:#111827;
            border-radius:10px;
            padding:8px 16px;
            font-weight:500;
        }
        QPushButton:hover {
            background:#e5e7eb;
        }
    """)

    create_btn.setStyleSheet("""
        QPushButton {
            background:#0a84ff;
            color:white;
            border-radius:10px;
            padding:8px 16px;
            font-weight:600;
        }
        QPushButton:hover {
            background:#0969da;
        }
        QPushButton:pressed {
            background:#075ec2;
        }
    """)

    btns.addWidget(cancel_btn)
    btns.addWidget(create_btn)
    panel_layout.addLayout(btns)

    # Layout assembly
    back_layout.addStretch()
    back_layout.addWidget(panel, 0, Qt.AlignCenter)
    back_layout.addStretch()
    outer.addWidget(backdrop)

    # ✅ Logic
    def on_ok():
        q = q_entry.toPlainText().strip()
        d = details.toPlainText().strip()

        if not q:
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            err.setStyleSheet("""
                QDialog {
                    background:#ffffff;
                    border-radius:12px;
                }
                QLabel {
                    color:#111827;
                    font-size:10.5pt;
                }
                QPushButton {
                    background:#0a84ff;
                    color:white;
                    border-radius:8px;
                    padding:6px 12px;
                }
                QPushButton:hover {
                    background:#0969da;
                }
            """)

            l = QVBoxLayout(err)
            l.addWidget(QLabel("Please enter a question."))

            okb = QPushButton("OK")
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

    dlg.setMinimumSize(680, 420)

    try:
        center = parent.mapToGlobal(parent.rect().center())
        dlg.move(center.x() - dlg.width() // 2, center.y() - dlg.height() // 2)
    except Exception:
        pass

    dlg.exec()


# 🔴 CONFIRM MODAL (UPDATED)
def open_confirm_modal(parent, title: str, message: str,
                       confirm_text: str = "Delete",
                       cancel_text: str = "Cancel") -> bool:

    dlg = QDialog(parent)
    dlg.setWindowModality(Qt.WindowModal)
    dlg.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
    dlg.setAttribute(Qt.WA_TranslucentBackground, True)

    outer = QVBoxLayout(dlg)
    outer.setContentsMargins(0, 0, 0, 0)

    backdrop = QWidget(dlg)
    backdrop.setStyleSheet("background: rgba(2,6,23,0.65);")
    back_layout = QVBoxLayout(backdrop)
    back_layout.setContentsMargins(18, 18, 18, 18)

    panel = QWidget(backdrop)
    panel.setStyleSheet("""
        background: #020617;
        border-radius:14px;
        padding:14px;
    """)
    panel_layout = QVBoxLayout(panel)
    panel_layout.setSpacing(10)

    # Shadow
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(25)
    shadow.setYOffset(6)
    panel.setGraphicsEffect(shadow)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet("font-weight:700; font-size:13pt; color:#f8fafc;")
    panel_layout.addWidget(title_lbl)

    lbl = QLabel(message)
    lbl.setWordWrap(True)
    lbl.setStyleSheet("color:#cbd5f5; font-size:10.5pt;")
    panel_layout.addWidget(lbl)

    btns = QHBoxLayout()
    btns.addStretch()

    no = QPushButton(cancel_text)
    yes = QPushButton(confirm_text)

    no.setCursor(Qt.PointingHandCursor)
    yes.setCursor(Qt.PointingHandCursor)

    no.setStyleSheet("""
        QPushButton {
            background:#e5e7eb;
            color:#111827;
            border-radius:8px;
            padding:6px 14px;
        }
        QPushButton:hover {
            background:#d1d5db;
        }
    """)

    yes.setStyleSheet("""
        QPushButton {
            background:#ef4444;
            color:white;
            border-radius:8px;
            padding:6px 14px;
            font-weight:600;
        }
        QPushButton:hover {
            background:#dc2626;
        }
    """)

    btns.addWidget(no)
    btns.addWidget(yes)
    panel_layout.addLayout(btns)

    back_layout.addStretch()
    back_layout.addWidget(panel, 0, Qt.AlignCenter)
    back_layout.addStretch()
    outer.addWidget(backdrop)

    yes.clicked.connect(dlg.accept)
    no.clicked.connect(dlg.reject)

    dlg.setFixedWidth(360)
    dlg.adjustSize()
    dlg.setFixedSize(dlg.size())

    try:
        center = parent.mapToGlobal(parent.rect().center())
        dlg.move(center.x() - dlg.width() // 2, center.y() - dlg.height() // 2)
    except Exception:
        pass

    return dlg.exec() == QDialog.Accepted