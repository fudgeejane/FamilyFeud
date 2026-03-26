from PySide6.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect


def make_shadow(w, blur=18, color=QColor(255, 200, 50, 140)):
    sh = QGraphicsDropShadowEffect(w)
    sh.setBlurRadius(blur)
    sh.setOffset(0, 6)
    sh.setColor(color)
    w.setGraphicsEffect(sh)
    return sh


def open_display_game(app, title: str = "", description: str = ""):
    """Create a top-level QMainWindow (non-modal) that visually matches the audience display image.
    This window is independent from the main stack and can be shown/hidden freely.
    """
    try:
        if hasattr(app, "display_window") and app.display_window is not None:
            # refresh existing window if possible
            try:
                if hasattr(app.display_window, "_refresh_display"):
                    app.display_window._refresh_display()
            except Exception:
                pass
            app.display_window.show()
            app.display_window.raise_()
            return
    except Exception:
        pass

    win = QMainWindow()
    win.setWindowTitle("Display Game")
    win.setWindowFlag(Qt.Window, True)
    win.setWindowModality(Qt.NonModal)
    central = QWidget()
    win.setCentralWidget(central)
    central.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0b1730, stop:0.4 #071a3a, stop:1 #06203a);"
    )
    win.setMinimumSize(1000, 700)

    layout = QVBoxLayout(central)
    layout.setContentsMargins(20, 20, 20, 20)
    layout.setSpacing(12)

    # Top scores row (left, center small score, right)
    top = QWidget()
    tlay = QHBoxLayout(top)
    tlay.setContentsMargins(0, 0, 0, 0)

    def score_block(val="0"):
        f = QFrame()
        f.setFixedSize(96, 96)
        f.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #7c3aed, stop:1 #0ea5e9);"
            "color:white; border-radius:8px; border:6px solid rgba(255,255,255,0.06); font-size:36pt; font-weight:800;"
        )
        lbl = QLabel(val, f)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color:white; font-weight:900; font-size:42pt;")
        make_shadow(f, blur=28, color=QColor(60, 160, 255, 160))
        return f

    tlay.addWidget(score_block("0"), alignment=Qt.AlignLeft)
    # center placeholder small score
    center_small = QFrame()
    center_small.setFixedSize(140, 88)
    center_small.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #3b82f6, stop:1 #6b46ff);"
        "border:4px solid #f59e0b; border-radius:8px;"
    )
    cs_lbl = QLabel("0", center_small)
    cs_lbl.setAlignment(Qt.AlignCenter)
    cs_lbl.setStyleSheet("color:white; font-weight:900; font-size:34pt;")
    tlay.addStretch()
    tlay.addWidget(center_small, alignment=Qt.AlignHCenter)
    tlay.addStretch()
    tlay.addWidget(score_block("0"), alignment=Qt.AlignRight)

    layout.addWidget(top)

    # Main board area - approximate arched board with gold border
    board_container = QFrame()
    board_container.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #071b3a, stop:1 #0b2a5a);"
        "border-radius:30px; padding:20px; border:6px solid #f59e0b;"
    )
    board_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    make_shadow(board_container, blur=40, color=QColor(255, 180, 70, 140))

    b_layout = QVBoxLayout(board_container)
    b_layout.setContentsMargins(14, 14, 14, 14)
    b_layout.setSpacing(18)

    # big header bar (question area)
    header = QFrame()
    header.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0f2a57, stop:1 #162e63); border-radius:6px; border:4px solid rgba(255,255,255,0.06);"
    )
    header_layout = QVBoxLayout(header)
    header_layout.setContentsMargins(12, 6, 12, 6)
    header_label = QLabel("")
    header_label.setStyleSheet("color:white; font-weight:800; font-size:18pt;")
    header_label.setAlignment(Qt.AlignCenter)
    header_label.setWordWrap(True)
    header_layout.addWidget(header_label)
    b_layout.addWidget(header)

    # Answers grid
    grid = QWidget()
    gl = QHBoxLayout(grid)
    gl.setContentsMargins(8, 8, 8, 8)
    gl.setSpacing(14)

    # build answer columns and keep references for dynamic updates
    answer_widgets = []  # list of (text_label, score_label, frame)
    def grid_column():
        w = QWidget()
        col = QVBoxLayout(w)
        col.setSpacing(12)
        for i in range(4):
            item = QFrame()
            item.setStyleSheet(
                "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0b3b8c, stop:1 #09245a);"
                "border:4px solid #f59e0b; border-radius:8px;"
            )
            il = QHBoxLayout(item)
            il.setContentsMargins(10, 6, 10, 6)
            txt = QLabel("")
            txt.setStyleSheet("color:white; font-weight:800; font-size:16pt; padding-left:8px;")
            txt.setWordWrap(True)
            txt.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            score_badge = QLabel("")
            score_badge.setFixedSize(56, 40)
            score_badge.setStyleSheet(
                "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0ea5e9, stop:1 #2563eb); color:white;"
                "border-radius:8px; font-weight:800; font-size:14pt; padding:4px;"
            )
            il.addWidget(txt)
            il.addStretch()
            il.addWidget(score_badge)
            make_shadow(item, blur=18, color=QColor(245,158,11,120))
            col.addWidget(item)
            answer_widgets.append((txt, score_badge, item))
        return w

    left = grid_column()
    right = grid_column()
    gl.addWidget(left)
    gl.addWidget(right)

    b_layout.addWidget(grid)

    # update function to populate header and answers from current round
    def _refresh_display():
        # try to get round from app.play_widget if available
        rd = None
        try:
            pw = getattr(app, 'play_widget', None)
            if pw and hasattr(pw, 'get_current_round_data'):
                rd = pw.get_current_round_data()
            elif pw and hasattr(pw, 'game_state'):
                rd = pw.game_state.get('current_round')
        except Exception:
            rd = None

        if rd is None:
            header_label.setText(title or "")
            # clear answers
            for i, (t_lbl, s_lbl, fr) in enumerate(answer_widgets):
                t_lbl.setText("")
                s_lbl.setText("")
            return

        header_label.setText(rd.get('question', ''))
        answers = rd.get('answers', [])
        # populate up to available answer slots (8)
        for i in range(len(answer_widgets)):
            t_lbl, s_lbl, fr = answer_widgets[i]
            if i < len(answers):
                text, pts = answers[i]
                t_lbl.setText(text or "")
                s_lbl.setText(str(pts or 0))
            else:
                t_lbl.setText("")
                s_lbl.setText("")

    # attach refresh function to window so future opens can refresh
    win._refresh_display = _refresh_display

    layout.addWidget(board_container, stretch=1)

    # Bottom placeholders (left score, center add/edit label, right fast money)
    bottom = QWidget()
    bl = QHBoxLayout(bottom)
    bl.setContentsMargins(10, 6, 10, 6)
    steal = QPushButton("Steal Points")
    steal.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #60a5fa, stop:1 #0a84ff);"
        "color:white; border-radius:20px; padding:10px 18px; font-weight:700;"
    )
    fast = QPushButton("Fast Money")
    fast.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #60a5fa, stop:1 #0a84ff);"
        "color:white; border-radius:20px; padding:10px 18px; font-weight:700;"
    )
    add_edit = QLabel("Add/Edit Q&A")
    add_edit.setStyleSheet("color:#f3f4f6; font-weight:600;")
    bl.addWidget(steal, alignment=Qt.AlignLeft)
    bl.addStretch()
    bl.addWidget(add_edit, alignment=Qt.AlignCenter)
    bl.addStretch()
    bl.addWidget(fast, alignment=Qt.AlignRight)

    layout.addWidget(bottom)

    # show as standalone window
    app.display_window = win
    win.show()
    return win
