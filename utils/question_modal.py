from typing import Callable, Optional
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt


def open_question_modal(parent, on_create: Optional[Callable[[dict], None]] = None):
    dlg = QDialog(parent)
    dlg.setWindowTitle("Create Question")
    dlg.setModal(True)
    dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

    layout = QVBoxLayout(dlg)

    lbl = QLabel("Question:")
    layout.addWidget(lbl)
    q_entry = QTextEdit()
    q_entry.setFixedHeight(100)
    layout.addWidget(q_entry)

    lbl2 = QLabel("Details / Notes (optional):")
    layout.addWidget(lbl2)
    details = QTextEdit()
    details.setFixedHeight(140)
    layout.addWidget(details)

    btns = QHBoxLayout()
    create_btn = QPushButton("Create")
    cancel_btn = QPushButton("Cancel")
    create_btn.setStyleSheet("background:#0a84ff; color:white; border-radius:6px; padding:8px 12px;")
    cancel_btn.setStyleSheet("background:#e5e7eb; color:#111; border-radius:6px; padding:8px 12px;")
    btns.addWidget(create_btn)
    btns.addWidget(cancel_btn)
    layout.addLayout(btns)

    def on_ok():
        q = q_entry.toPlainText().strip()
        d = details.toPlainText().strip()
        if not q:
            # simple inline validation
            err = QDialog(dlg)
            err.setWindowTitle("Validation")
            l = QVBoxLayout(err)
            l.addWidget(QLabel("Please enter a question."))
            okb = QPushButton("OK")
            okb.setStyleSheet("background:#0a84ff; color:white; border-radius:6px; padding:6px 12px;")
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

    dlg.exec()
