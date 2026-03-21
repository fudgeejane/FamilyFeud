from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt


def open_play_game(app, title: str, description: str):
    """Open the Play Game page in the app.stack. This builds a static
    representation matching the provided screenshot: side score boxes, central
    question board, answer slots, and control buttons.
    """
    try:
        if hasattr(app, "play_widget") and app.play_widget is not None:
            app.stack.setCurrentWidget(app.play_widget)
            return
    except Exception:
        pass

    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)

    # Top area: horizontal layout with left score, center board, right score
    top = QWidget()
    t_layout = QHBoxLayout(top)
    t_layout.setContentsMargins(0, 0, 0, 0)

    def score_panel(team_name="Team"):
        p = QFrame()
        p.setStyleSheet("background:transparent;")
        pl = QVBoxLayout(p)
        lbl = QLabel(team_name)
        lbl.setStyleSheet("font-weight:700; color:#ffffff;")
        score = QLabel("0")
        score.setFixedSize(64, 64)
        score.setAlignment(Qt.AlignCenter)
        score.setStyleSheet("background:#3b82f6; border-radius:8px; font-size:20pt; color:white;")
        strike = QPushButton("Strike")
        strike.setStyleSheet("background:#0a84ff; color:white; border-radius:8px; padding:6px 10px;")
        strike.setCursor(Qt.PointingHandCursor)
        pl.addWidget(lbl, alignment=Qt.AlignLeft)
        pl.addWidget(score)
        pl.addWidget(strike)
        return p

    t_layout.addWidget(score_panel("Team A"), stretch=1)

    # Center question board
    board = QFrame()
    board.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0b3b8c, stop:1 #04203a); border-radius:12px; padding:16px; border:4px solid #2b8fd6;")
    board.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    b_layout = QVBoxLayout(board)

    header = QLabel(title or "QUESTION")
    header.setStyleSheet("background:#193b8c; color:white; padding:8px 16px; font-size:18pt; border-radius:6px;")
    header.setAlignment(Qt.AlignCenter)
    b_layout.addWidget(header, alignment=Qt.AlignTop)

    # Answers grid: two columns of four answers with points on the side
    answers = QWidget()
    a_layout = QHBoxLayout(answers)
    a_layout.setContentsMargins(12, 12, 12, 12)
    a_layout.setSpacing(12)

    def answer_column():
        col = QVBoxLayout()
        for _ in range(4):
            row = QWidget()
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(0, 0, 0, 0)
            ans_lbl = QLabel("ANSWER")
            ans_lbl.setStyleSheet("background:transparent; color:white; font-weight:700; padding:8px;")
            circle = QLabel()
            circle.setFixedSize(36, 36)
            circle.setStyleSheet("background:#f59e0b; border-radius:18px;")
            r_layout.addWidget(ans_lbl)
            r_layout.addStretch()
            r_layout.addWidget(circle)
            col.addWidget(row)
        return col

    left_col = QWidget()
    left_col.setLayout(answer_column())
    right_col = QWidget()
    right_col.setLayout(answer_column())

    a_layout.addWidget(left_col)
    a_layout.addWidget(right_col)
    b_layout.addWidget(answers)

    t_layout.addWidget(board, stretch=4)
    t_layout.addWidget(score_panel("Team B"), stretch=1)

    layout.addWidget(top)

    # Control buttons row
    controls = QWidget()
    c_layout = QHBoxLayout(controls)
    c_layout.setContentsMargins(0, 0, 0, 0)
    c_layout.addStretch()
    for label in ("Award Points", "Start Round", "Next Round"):
        btn = QPushButton(label)
        btn.setStyleSheet("background:#0a84ff; color:white; border-radius:8px; padding:8px 14px;")
        btn.setCursor(Qt.PointingHandCursor)
        c_layout.addWidget(btn)
    c_layout.addStretch()
    layout.addWidget(controls)

    # Bottom action row: Steal Points, Add/Edit Q&A, Fast Money
    bottom = QWidget()
    b_layout2 = QHBoxLayout(bottom)
    b_layout2.setContentsMargins(0, 0, 0, 0)
    steal = QPushButton("Steal Points")
    fast = QPushButton("Fast Money")
    steal.setStyleSheet("background:#0a84ff; color:white; border-radius:8px; padding:8px 14px;")
    fast.setStyleSheet("background:#0a84ff; color:white; border-radius:8px; padding:8px 14px;")
    b_layout2.addWidget(steal)
    b_layout2.addStretch()
    add_edit = QPushButton("Add/Edit Q&A")
    add_edit.setStyleSheet("background:transparent; color:#ffffff; border:none;")
    b_layout2.addWidget(add_edit, alignment=Qt.AlignCenter)
    b_layout2.addStretch()
    b_layout2.addWidget(fast)
    layout.addWidget(bottom)

    # Navigation row: Back to Board and Play (right-aligned)
    nav = QWidget()
    n_layout = QHBoxLayout(nav)
    n_layout.setContentsMargins(0, 0, 0, 0)
    n_layout.addStretch()
    back_btn = QPushButton("Back to Board")
    back_btn.setStyleSheet("background:#0a84ff; color:white; border-radius:16px; padding:10px 18px;")
    back_btn.setCursor(Qt.PointingHandCursor)
    back_btn.clicked.connect(app.show_home)
    play_btn = QPushButton("Play")
    play_btn.setStyleSheet("background:#16a34a; color:white; border-radius:16px; padding:10px 18px;")
    play_btn.setCursor(Qt.PointingHandCursor)
    play_btn.clicked.connect(lambda t=title, d=description: app.show_game(t or "", d or ""))
    n_layout.addWidget(back_btn)
    n_layout.addWidget(play_btn)
    layout.addWidget(nav)

    app.play_widget = page
    try:
        app.stack.addWidget(page)
        app.stack.setCurrentWidget(page)
    except Exception:
        try:
            app.show_static_modal("Play", "Could not open play page.")
        except Exception:
            pass
