from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
)
from PySide6.QtCore import Qt


def open_modify_game(app, title: str, description: str):
    """Open a full-page Modify Game view inside the application's stack.

    The function will reuse an existing modify page if present, otherwise it
    constructs a new QWidget, adds it to `app.stack`, and switches to it.
    This view is static (placeholder) but provides Back and Save actions.
    """
    try:
        # Reuse existing modify page if previously created
        if hasattr(app, "modify_widget") and app.modify_widget is not None:
            app.modify_title_label.setText(title or "(Untitled Game)")
            try:
                app.modify_desc_edit.setPlainText(description or "")
            except Exception:
                pass
            app.stack.setCurrentWidget(app.modify_widget)
            return
    except Exception:
        pass

    # Build a scrollable page that resembles the screenshot: header with logo,
    # question cards (white rounded boxes), and a bottom-right "Back to Board" button.
    from PySide6.QtWidgets import QScrollArea, QFrame, QSizePolicy

    page = QWidget()
    page_layout = QVBoxLayout(page)
    page_layout.setContentsMargins(24, 20, 24, 20)
    page_layout.setSpacing(18)

    # Header: logo at top-left
    header = QWidget()
    h_layout = QHBoxLayout(header)
    h_layout.setContentsMargins(0, 0, 0, 0)
    logo_lbl = QLabel()
    try:
        from pathlib import Path

        assets_logo = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
        if assets_logo.exists():
            from PySide6.QtGui import QPixmap

            pix = QPixmap(str(assets_logo))
            if not pix.isNull():
                pix = pix.scaledToWidth(120, Qt.SmoothTransformation)
                logo_lbl.setPixmap(pix)
            else:
                logo_lbl.setText("TCC Feud")
                logo_lbl.setStyleSheet("font-size:20pt; color: #ffffff;")
        else:
            logo_lbl.setText("TCC Feud")
            logo_lbl.setStyleSheet("font-size:20pt; color: #ffffff;")
    except Exception:
        logo_lbl.setText("TCC Feud")
        logo_lbl.setStyleSheet("font-size:20pt; color: #ffffff;")

    h_layout.addWidget(logo_lbl, alignment=Qt.AlignLeft)
    h_layout.addStretch()
    page_layout.addWidget(header)

    # Scroll area for cards
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll_content = QWidget()
    sc_layout = QVBoxLayout(scroll_content)
    sc_layout.setContentsMargins(0, 0, 0, 0)
    sc_layout.setSpacing(20)

    total_questions = 2
    for idx in range(1, total_questions + 1):
        card_wrapper = QWidget()
        cw_layout = QHBoxLayout(card_wrapper)
        cw_layout.setContentsMargins(0, 0, 0, 0)

        # Left indicator (e.g., 1/2)
        indicator = QLabel(f"{idx}/{total_questions}")
        indicator.setStyleSheet("color:#ffffff; font-size:10pt;")
        indicator.setFixedWidth(36)
        cw_layout.addWidget(indicator, alignment=Qt.AlignTop)

        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("background:#ffffff; border-radius:8px;")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setFixedHeight(240)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(8)

        top_row = QWidget()
        tr_layout = QHBoxLayout(top_row)
        tr_layout.setContentsMargins(0, 0, 0, 0)
        title_lbl = QLabel(f"Question {idx}")
        title_lbl.setStyleSheet("font-weight:700; color:#111827;")
        tr_layout.addWidget(title_lbl)
        tr_layout.addStretch()

        # Example action button(s) on card
        if idx == 1:
            reset_btn = QPushButton("Reset Questions")
            reset_btn.setStyleSheet("background:#0a84ff; color:white; border-radius:6px; padding:6px 10px;")
            reset_btn.setCursor(Qt.PointingHandCursor)
            tr_layout.addWidget(reset_btn, alignment=Qt.AlignRight)
        else:
            add_fast = QPushButton("Add Fast Money")
            add_q = QPushButton("Add Question")
            add_fast.setStyleSheet("background:#0a84ff; color:white; border-radius:6px; padding:6px 10px;")
            add_q.setStyleSheet("background:#0a84ff; color:white; border-radius:6px; padding:6px 10px;")
            add_fast.setCursor(Qt.PointingHandCursor)
            add_q.setCursor(Qt.PointingHandCursor)
            tr_layout.addWidget(add_fast)
            tr_layout.addWidget(add_q)

        card_layout.addWidget(top_row)

        # Divider (visual line)
        hr = QFrame()
        hr.setFrameShape(QFrame.HLine)
        hr.setStyleSheet("color:#e5e7eb;")
        card_layout.addWidget(hr)

        # Answers area (placeholder boxes)
        answers = QWidget()
        a_layout = QHBoxLayout(answers)
        a_layout.setContentsMargins(0, 0, 0, 0)
        a_layout.setSpacing(12)

        def make_column():
            col = QWidget()
            col_l = QVBoxLayout(col)
            col_l.setContentsMargins(0, 0, 0, 0)
            for _ in range(4):
                b = QLabel()
                b.setFixedHeight(28)
                b.setStyleSheet("background:#eef2f7; border-radius:6px;")
                col_l.addWidget(b)
            return col

        a_layout.addWidget(make_column())
        # small points column
        pts = QWidget()
        pts_l = QVBoxLayout(pts)
        pts_l.setContentsMargins(0, 0, 0, 0)
        for _ in range(4):
            p = QLabel()
            p.setFixedSize(40, 28)
            p.setStyleSheet("background:#eef2f7; border-radius:6px;")
            pts_l.addWidget(p)
        a_layout.addWidget(pts)
        a_layout.addWidget(make_column())
        a_layout.addWidget(pts)

        card_layout.addWidget(answers)

        cw_layout.addWidget(card)
        sc_layout.addWidget(card_wrapper)

    sc_layout.addStretch()
    scroll.setWidget(scroll_content)
    page_layout.addWidget(scroll)

    # Bottom-right floating style Back button area
    bottom = QWidget()
    b_layout = QHBoxLayout(bottom)
    b_layout.setContentsMargins(0, 0, 0, 0)
    b_layout.addStretch()
    back_board = QPushButton("Back to Board")
    back_board.setStyleSheet("background:#0a84ff; color:white; border-radius:16px; padding:10px 18px;")
    back_board.setCursor(Qt.PointingHandCursor)
    back_board.clicked.connect(app.show_home)
    b_layout.addWidget(back_board, alignment=Qt.AlignRight)

    play_btn = QPushButton("Play Game")
    play_btn.setStyleSheet("background:#16a34a; color:white; border-radius:16px; padding:10px 18px;")
    play_btn.setCursor(Qt.PointingHandCursor)

    def _on_play(t=title, d=description):
        try:
            import importlib

            pg = importlib.import_module("modules.play_game")
            if hasattr(pg, "open_play_game"):
                pg.open_play_game(app, t, d)
                return
        except Exception:
            pass
        # fallback
        try:
            app.show_game(t, d)
        except Exception:
            pass

    play_btn.clicked.connect(_on_play)
    b_layout.addWidget(play_btn, alignment=Qt.AlignRight)

    page_layout.addWidget(bottom)

    # Store references and show
    app.modify_widget = page
    try:
        app.stack.addWidget(page)
        app.stack.setCurrentWidget(page)
    except Exception:
        try:
            app.show_static_modal(f"Modify {title}", "Modify page could not be opened.")
        except Exception:
            pass
