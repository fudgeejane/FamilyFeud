from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PySide6.QtWidgets import QInputDialog, QMessageBox, QDialog, QLineEdit
from PySide6.QtWidgets import QStackedLayout
from PySide6.QtCore import Qt, QSize, QEvent, QObject
from PySide6.QtGui import QPixmap, QFont, QColor, QIntValidator
import utils.game_modal as game_modal
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup
import modules.display_game as display_game
import database.db as db


def open_play_game(app, title: str, description: str, load_db_first: bool = False):
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

    def make_shadow(w, blur=20, color=QColor(0, 150, 255, 160)):
        shadow = QGraphicsDropShadowEffect(w)
        shadow.setBlurRadius(blur)
        shadow.setOffset(0, 6)
        shadow.setColor(color)
        w.setGraphicsEffect(shadow)
        return shadow

    def score_panel(team_name="Team"):
        p = QFrame()
        p.setStyleSheet("background:transparent;")
        pl = QVBoxLayout(p)
        # Team name as a button so users can rename the team
        name_btn = QPushButton(team_name)
        name_btn.setFlat(True)
        name_btn.setStyleSheet("font-weight:700; color:#ffffff; text-align:left; margin-bottom:8px;")
        name_btn.setFont(QFont(name_btn.font().family(), 12))
        score = QLabel("0")
        score.setFixedSize(84, 84)
        score.setAlignment(Qt.AlignCenter)
        score.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #6ee7b7, stop:1 #3b82f6);"
            "border-radius:14px; font-size:22pt; color:white; font-weight:700;"
        )
        make_shadow(score, blur=28, color=QColor(59,130,246,160))
        strike = QPushButton("Strike")
        strike.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #60a5fa, stop:1 #0a84ff);"
            "color:white; border-radius:12px; padding:8px 12px; font-weight:600;"
        )
        strike.setCursor(Qt.PointingHandCursor)

        # Strike indicators (up to 3)
        strikes_widget = QWidget()
        s_layout = QHBoxLayout(strikes_widget)
        s_layout.setContentsMargins(0, 0, 0, 0)
        strike_labels = []
        for _ in range(3):
            sx = QLabel("X")
            sx.setFixedSize(22, 22)
            sx.setAlignment(Qt.AlignCenter)
            sx.setStyleSheet("color:#fff; border:2px solid #ff4d4d; border-radius:4px; background:transparent; font-weight:800;")
            sx.setVisible(False)
            strike_labels.append(sx)
            s_layout.addWidget(sx)

        pl.addWidget(name_btn, alignment=Qt.AlignLeft)
        pl.addWidget(score)
        pl.addWidget(strike)
        pl.addWidget(strikes_widget)
        pl.addStretch()

        # expose for wiring (caller will set behaviour)
        p._name_btn = name_btn
        p._score_lbl = score
        p._strike_btn = strike
        p._strike_labels = strike_labels
        return p

    team_a_panel = score_panel("Team A")
    team_b_panel = score_panel("Team B")
    t_layout.addWidget(team_a_panel, stretch=1)

    # Center question board
    board = QFrame()
    board.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    board.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #071432, stop:0.6 #0b3b8c, stop:1 #041628);"
        "border-radius:14px; padding:12px;"
    )
    make_shadow(board, blur=36, color=QColor(10,132,255,150))
    b_layout = QVBoxLayout(board)

    header = QLabel(title or "QUESTION")
    header.setAlignment(Qt.AlignCenter)
    header.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #2b6cf6, stop:1 #6b46ff);"
        "color:white; padding:12px 18px; font-size:20pt; font-weight:800; border-radius:8px;"
    )
    b_layout.addWidget(header, alignment=Qt.AlignTop)

    # Answers grid and game state
    answers = QWidget()
    a_layout = QHBoxLayout(answers)
    a_layout.setContentsMargins(12, 12, 12, 12)
    a_layout.setSpacing(14)

    # sample ComSci rounds
    sample_rounds = [
        {
            'question': 'Name a common data structure taught in CS courses:',
            'answers': [('Array', 30), ('Linked List', 20), ('Stack', 15), ('Queue', 10), ('Hash Table', 8), ('Tree', 7), ('Graph', 6), ('Heap', 4)],
        },
        {
            'question': 'Name a programming language commonly used for teaching:',
            'answers': [('Python', 40), ('Java', 25), ('C++', 15), ('JavaScript', 8), ('C', 6), ('Ruby', 3), ('Haskell', 2), ('MATLAB', 1)],
        },
    ]

    

    page.game_state = {
        'teams': [{'name': 'Team A', 'score': 0, 'strikes': 0}, {'name': 'Team B', 'score': 0, 'strikes': 0}],
        'current_round': None,
        'game_idx': 0,
        'question_idx': 0,
        'answers_widgets': [],
    }

    def build_answer_boxes():
        # clear any previous widgets in answers area
        for w in page.game_state.get('answers_widgets', []):
            try:
                w.setParent(None)
            except Exception:
                pass
        page.game_state['answers_widgets'] = []

        left = QWidget()
        left_l = QVBoxLayout(left)
        left_l.setSpacing(12)
        right = QWidget()
        right_l = QVBoxLayout(right)
        right_l.setSpacing(12)

        answers_data = page.game_state['current_round']['answers']
        total_slots = 8

        # Flashcard widget: full-card clickable area, crossfade reveal animation
        class FlashCard(QWidget):
            def __init__(self, text: str, pts: int, active: bool = True):
                super().__init__()
                self._answer_text = text or ''
                self._answer_pts = pts or 0
                self._revealed = False
                self._active = bool(active)
                self._reveal_anim = None
                self.setFixedHeight(56)
                self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                if self._active:
                    self.setStyleSheet(
                        'background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #062244, stop:1 #0b2a5a);'
                        'border-radius:14px;'
                    )
                else:
                    self.setStyleSheet(
                        'background: #2f3946;'
                        'border:2px dashed #4b5563;'
                        'border-radius:14px;'
                    )

                hl = QHBoxLayout(self)
                hl.setContentsMargins(12, 0, 12, 0)
                hl.setSpacing(10)

                self._content = QWidget()
                self._content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self._stack = QStackedLayout(self._content)
                self._stack.setContentsMargins(0, 0, 0, 0)

                # front (hidden content) and back (revealed content)
                self.front = QLabel('')
                self.front.setStyleSheet(
                    'background: transparent;'
                    'border: none;'
                    'color: rgba(255,255,255,0);'
                    'font-weight:800;'
                    'font-size:14pt;'
                )
                self.front.setAlignment(Qt.AlignCenter)

                self.back = QLabel(self._answer_text)
                self.back.setStyleSheet(
                    'background: transparent;'
                    'border: none;'
                    'color: white;'
                    'font-weight:800;'
                    'font-size:14pt;'
                )
                self.back.setAlignment(Qt.AlignCenter)
                self.back.setWordWrap(True)

                self._stack.addWidget(self.front)
                self._stack.addWidget(self.back)
                self._stack.setCurrentWidget(self.front)

                # (No opacity effects here) — using a width-based flip animation instead.

                # pts label
                self._pts_lbl = QLabel(str(self._answer_pts))
                self._pts_lbl.setStyleSheet(
                    'background: qradialgradient(cx:0.3, cy:0.3, radius:1, fx:0.3, fy:0.3, stop:0 #ffd27a, stop:1 #f59e0b);'
                    'border-radius:16px; padding:6px; color:#000; font-weight:800; margin-right:12px; font-size:18pt;'
                )
                self._pts_lbl.setFixedSize(56, 36)
                self._pts_lbl.setVisible(False)

                hl.addWidget(self._content, stretch=1)
                hl.addWidget(self._pts_lbl)

                if not self._active:
                    # disable interaction; show placeholder marker
                    self.front.setStyleSheet(
                        'background: transparent;'
                        'border: none;'
                        'color:#9ca3af;'
                        'font-weight:700;'
                        'font-size:18pt;'
                    )
                    self.front.setText('—')
                    self.front.setAlignment(Qt.AlignCenter)
                    self.setEnabled(False)
                    self.setCursor(Qt.ArrowCursor)
                else:
                    self.setCursor(Qt.PointingHandCursor)

            def mousePressEvent(self, event):
                if not self._active or self._revealed:
                    return
                self.reveal()

            def ensure_revealed_visible(self):
                """Force the revealed side to be visible.

                This prevents a mid-animation state from leaving the card blank
                after alt-tab/window deactivation.
                """
                if not self._revealed:
                    return
                try:
                    if self._reveal_anim is not None:
                        self._reveal_anim.stop()
                except Exception:
                    pass
                self._stack.setCurrentWidget(self.back)
                self._content.setMaximumWidth(16777215)
                self._pts_lbl.setVisible(True)
                self._reveal_anim = None

            def reveal(self, award: bool = True, animate: bool = True):
                if self._revealed or not self._active:
                    return
                self._revealed = True

                if not animate:
                    self._stack.setCurrentWidget(self.back)
                    self._pts_lbl.setVisible(True)
                    self._content.setMaximumWidth(16777215)
                else:
                    # Flip animation: shrink -> swap -> expand
                    try:
                        if self._reveal_anim is not None:
                            self._reveal_anim.stop()
                    except Exception:
                        pass

                    full_w = max(self._content.width(), self._content.sizeHint().width(), 1)
                    self._content.setMaximumWidth(full_w)

                    shrink = QPropertyAnimation(self._content, b"maximumWidth", self)
                    shrink.setDuration(140)
                    shrink.setStartValue(full_w)
                    shrink.setEndValue(0)
                    shrink.setEasingCurve(QEasingCurve.InOutCubic)

                    expand = QPropertyAnimation(self._content, b"maximumWidth", self)
                    expand.setDuration(160)
                    expand.setStartValue(0)
                    expand.setEndValue(full_w)
                    expand.setEasingCurve(QEasingCurve.InOutCubic)

                    group = QSequentialAnimationGroup(self)
                    group.addAnimation(shrink)

                    def _swap():
                        self._stack.setCurrentWidget(self.back)
                        self._pts_lbl.setVisible(True)

                    shrink.finished.connect(_swap)
                    group.addAnimation(expand)

                    def _finish():
                        self._content.setMaximumWidth(16777215)
                        self._reveal_anim = None

                    group.finished.connect(_finish)
                    self._reveal_anim = group
                    group.start()

                if award:
                    try:
                        award_to_team_dialog(self._answer_pts)
                    except Exception:
                        pass

        # Stabilize revealed cards on alt-tab/window activation.
        class _RevealStabilizer(QObject):
            def eventFilter(self, obj, event):
                try:
                    if event.type() in (QEvent.WindowActivate, QEvent.ApplicationActivate):
                        for card in page.game_state.get('answers_widgets', []):
                            if hasattr(card, 'ensure_revealed_visible'):
                                card.ensure_revealed_visible()
                except Exception:
                    pass
                return False

        if not hasattr(page, '_reveal_stabilizer'):
            page._reveal_stabilizer = _RevealStabilizer(page)
            try:
                app.installEventFilter(page._reveal_stabilizer)
            except Exception:
                try:
                    page.installEventFilter(page._reveal_stabilizer)
                except Exception:
                    pass

        for i in range(total_slots):
            if i < len(answers_data):
                text, pts = answers_data[i]
                is_empty = (not str(text).strip()) and (int(pts or 0) == 0)
                card = FlashCard(text, pts, active=(not is_empty))
                container = QWidget()
                hl = QHBoxLayout(container)
                hl.setContentsMargins(0, 0, 0, 0)
                hl.addWidget(card)
            else:
                card = FlashCard('', 0, active=False)
                container = QWidget()
                hl = QHBoxLayout(container)
                hl.setContentsMargins(0, 0, 0, 0)
                hl.addWidget(card)

            if i < 4:
                left_l.addWidget(container)
            else:
                right_l.addWidget(container)

            page.game_state['answers_widgets'].append(card)

        a_layout.addWidget(left)
        a_layout.addWidget(right)
        b_layout.addWidget(answers)

    def load_round(round_data, from_db=False):
        page.game_state['current_round'] = round_data
        # reset team scores/strikes
        page.game_state['teams'][0]['score'] = 0
        page.game_state['teams'][1]['score'] = 0
        page.game_state['teams'][0]['strikes'] = 0
        page.game_state['teams'][1]['strikes'] = 0
        page.game_state['from_db'] = bool(from_db)
        header.setText(round_data['question'])
        update_team_panels()
        build_answer_boxes()
        try:
            update_next_button_state()
        except Exception:
            pass
    def get_db_round(game_idx=0, question_idx=0):
        games = db.load_games()
        if not games:
            return None
        if game_idx < 0 or game_idx >= len(games):
            return None
        game = games[game_idx]
        questions = game.get('questions', [])
        if question_idx < 0 or question_idx >= len(questions):
            return None
        q = questions[question_idx]
        # map to internal format
        answers = []
        for a in q.get('answers', []):
            text = a.get('text', '') or ''
            score = a.get('score', 0) or 0
            answers.append((text, score))
        return {'question': q.get('question', ''), 'answers': answers}

    def load_first_db_round():
        r = get_db_round(game_idx=0, question_idx=0)
        if r is None:
            QMessageBox.warning(page, 'No Games', 'No game found in database/games.json')
            return
        page.game_state['game_idx'] = 0
        page.game_state['question_idx'] = 0
        load_round(r, from_db=True)

    def load_next_db_round():
        gi = page.game_state.get('game_idx', 0)
        qi = page.game_state.get('question_idx', 0) + 1
        r = get_db_round(game_idx=gi, question_idx=qi)
        if r is None:
            QMessageBox.information(page, 'End', 'No more questions in this game.')
            return
        page.game_state['question_idx'] = qi
        load_round(r, from_db=True)

    def reveal_answer(obj):
        # backward-compatible helper: accepts old QPushButton-style or new FlashCard
        if getattr(obj, '_revealed', False):
            return
        if hasattr(obj, 'reveal'):
            try:
                obj.reveal()
            except Exception:
                pass
            return
        # fallback for legacy objects
        try:
            obj._revealed = True
            obj.setText(obj._answer_text)
            obj.setStyleSheet(obj.styleSheet().replace('color:transparent;', 'color:white;'))
            obj._pts_lbl.setVisible(True)
            award_to_team_dialog(obj._answer_pts)
        except Exception:
            return

    def award_to_team_dialog(points: int):
        msg = QMessageBox(page)
        msg.setWindowTitle('Award Points')
        msg.setText(f'Which team receives {points} points?')
        ta = msg.addButton(page.game_state['teams'][0]['name'], QMessageBox.AcceptRole)
        tb = msg.addButton(page.game_state['teams'][1]['name'], QMessageBox.AcceptRole)
        msg.addButton('Cancel', QMessageBox.RejectRole)
        msg.exec()
        chosen = msg.clickedButton()
        if chosen == ta:
            page.game_state['teams'][0]['score'] += points
        elif chosen == tb:
            page.game_state['teams'][1]['score'] += points
        update_team_panels()

    def update_team_panels():
        team_a_panel._score_lbl.setText(str(page.game_state['teams'][0]['score']))
        team_b_panel._score_lbl.setText(str(page.game_state['teams'][1]['score']))
        team_a_panel._name_btn.setText(page.game_state['teams'][0]['name'])
        team_b_panel._name_btn.setText(page.game_state['teams'][1]['name'])
        for i, sx in enumerate(team_a_panel._strike_labels):
            sx.setVisible(i < page.game_state['teams'][0]['strikes'])
        for i, sx in enumerate(team_b_panel._strike_labels):
            sx.setVisible(i < page.game_state['teams'][1]['strikes'])

    def rename_team(idx):
        text, ok = QInputDialog.getText(page, 'Rename Team', 'Team name:', text=page.game_state['teams'][idx]['name'])
        if ok and text:
            page.game_state['teams'][idx]['name'] = text
            update_team_panels()

    def increment_strike(idx):
        page.game_state['teams'][idx]['strikes'] += 1
        if page.game_state['teams'][idx]['strikes'] > 3:
            page.game_state['teams'][idx]['strikes'] = 3
        update_team_panels()
        if page.game_state['teams'][idx]['strikes'] >= 3:
            # mark which team is eligible to attempt a steal instead of
            # immediately popping a modal input dialog
            page.game_state['steal_pending'] = 1 - idx

    def steal_attempt(team_idx):
        text, ok = QInputDialog.getText(page, 'Steal Attempt', f"{page.game_state['teams'][team_idx]['name']}, enter your steal answer:")
        if not ok or not text:
            return
        unrevealed = []
        for card in page.game_state['answers_widgets']:
            try:
                if not getattr(card, '_revealed', True) and getattr(card, '_active', True):
                    unrevealed.append(card)
            except Exception:
                pass
        matched = None
        for card in unrevealed:
            if card._answer_text.strip().lower() == text.strip().lower():
                matched = card
                break
        if matched:
            total = sum(c._answer_pts for c in unrevealed)
            opponent_idx = 1 - team_idx
            opponent_score = page.game_state['teams'][opponent_idx]['score']
            if total > opponent_score:
                QMessageBox.information(page, 'Steal', 'Cannot steal more points than the opposing team currently has.')
                return
            page.game_state['teams'][team_idx]['score'] += total
            page.game_state['teams'][opponent_idx]['score'] -= total
            for c in unrevealed:
                try:
                    c.reveal(award=False, animate=False)
                except Exception:
                    pass
            update_team_panels()
            QMessageBox.information(page, 'Steal', f'Correct! {page.game_state["teams"][team_idx]["name"]} steals {total} points.')
        else:
            QMessageBox.information(page, 'Steal', 'Incorrect steal attempt.')

    # wire renaming and strike buttons
    # will reference team panels created earlier
    # hook after both panels exist
    team_a_panel._name_btn.clicked.connect(lambda: rename_team(0))
    team_b_panel._name_btn.clicked.connect(lambda: rename_team(1))
    team_a_panel._strike_btn.clicked.connect(lambda: increment_strike(0))
    team_b_panel._strike_btn.clicked.connect(lambda: increment_strike(1))

    t_layout.addWidget(board, stretch=4)
    t_layout.addWidget(team_b_panel, stretch=1)

    layout.addWidget(top)

    # Control buttons row
    controls = QWidget()
    c_layout = QHBoxLayout(controls)
    c_layout.setContentsMargins(0, 0, 0, 0)
    c_layout.addStretch()
    control_buttons = {}
    for label in ("Next Round",):
        btn = QPushButton(label)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #4f46e5, stop:1 #0ea5e9);"
            "color:white; border-radius:22px; padding:12px 24px; font-weight:700;"
        )
        make_shadow(btn, blur=18, color=QColor(79,70,229,130))
        control_buttons[label] = btn
        c_layout.addWidget(btn)
    c_layout.addStretch()
    layout.addWidget(controls)

    # wire control buttons
    # helper: enable/disable Next Round depending on whether another question exists
    def update_next_button_state():
        next_btn = control_buttons.get('Next Round')
        if not next_btn:
            return
        if page.game_state.get('from_db'):
            gi = page.game_state.get('game_idx', 0)
            qi = page.game_state.get('question_idx', 0)
            # enable if a next DB question exists
            has_next = get_db_round(game_idx=gi, question_idx=qi + 1) is not None
            next_btn.setEnabled(bool(has_next))
        else:
            qi = page.game_state.get('question_idx', 0)
            has_next = (qi + 1) < len(sample_rounds)
            next_btn.setEnabled(bool(has_next))

    def next_round_action():
        if page.game_state.get('from_db'):
            # attempt to load next DB question
            gi = page.game_state.get('game_idx', 0)
            qi = page.game_state.get('question_idx', 0) + 1
            r = get_db_round(game_idx=gi, question_idx=qi)
            if r is None:
                control_buttons['Next Round'].setEnabled(False)
                QMessageBox.information(page, 'End', 'No more questions in this game.')
                return
            page.game_state['question_idx'] = qi
            load_round(r, from_db=True)
        else:
            qi = page.game_state.get('question_idx', 0) + 1
            if qi < len(sample_rounds):
                page.game_state['question_idx'] = qi
                load_round(sample_rounds[qi], from_db=False)
            else:
                control_buttons['Next Round'].setEnabled(False)

    control_buttons['Next Round'].clicked.connect(next_round_action)
    

    # Bottom action row: Steal Points, Add/Edit Q&A, Fast Money
    bottom = QWidget()
    b_layout2 = QHBoxLayout(bottom)
    b_layout2.setContentsMargins(0, 0, 0, 0)
    steal = QPushButton("Steal Points")
    steal.setCursor(Qt.PointingHandCursor)
    steal.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #60a5fa, stop:1 #0a84ff);"
        "color:white; border-radius:20px; padding:10px 18px; font-weight:700;"
    )
    make_shadow(steal, blur=16, color=QColor(10,132,255,120))
    b_layout2.addWidget(steal)
    b_layout2.addStretch()
    add_edit = QPushButton("Add/Edit Q&A")
    add_edit.setStyleSheet("background:transparent; color:#ffffff; border:none; font-weight:600;")
    b_layout2.addWidget(add_edit, alignment=Qt.AlignCenter)
    b_layout2.addStretch()
    # Fast Money removed per user request
    layout.addWidget(bottom)

    # wire bottom steal button: ask which team will try to steal
    def steal_from_bottom():
        dlg = QDialog(page)
        dlg.setModal(True)
        dlg.setWindowTitle("Steal Points")
        dlg.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        dlg.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        dlg.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        dlg.setWindowFlag(Qt.WindowCloseButtonHint, False)
        dlg.setWindowFlag(Qt.FramelessWindowHint, True)
        dlg.setStyleSheet(game_modal.STYLE)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title_label = QLabel("Steal Points")
        title_label.setObjectName("headerTitle")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)

        layout.addWidget(QLabel("Points to award:"))
        points_input = QLineEdit()
        points_input.setPlaceholderText("Enter number of points")
        points_input.setValidator(QIntValidator(0, 100000, points_input))
        layout.addWidget(points_input)

        btns = QHBoxLayout()
        ta_btn = QPushButton(page.game_state['teams'][0]['name'])
        tb_btn = QPushButton(page.game_state['teams'][1]['name'])
        cancel_btn = QPushButton("Cancel")

        ta_btn.setCursor(Qt.PointingHandCursor)
        tb_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setCursor(Qt.PointingHandCursor)

        btns.addStretch()
        btns.addWidget(ta_btn)
        btns.addWidget(tb_btn)
        btns.addWidget(cancel_btn)
        btns.addStretch()
        layout.addLayout(btns)

        def _award_to(team_idx: int):
            txt = points_input.text().strip()
            if not txt:
                QMessageBox.information(dlg, 'Invalid', 'Please enter a number of points to award.')
                return
            try:
                pts = int(txt)
            except Exception:
                QMessageBox.information(dlg, 'Invalid', 'Please enter a valid integer.')
                return
            opponent_idx = 1 - team_idx
            opponent_score = page.game_state['teams'][opponent_idx]['score']
            if pts > opponent_score:
                QMessageBox.information(dlg, 'Invalid', 'Cannot steal more points than the opposing team currently has.')
                return
            page.game_state['teams'][team_idx]['score'] += pts
            page.game_state['teams'][opponent_idx]['score'] -= pts
            update_team_panels()
            dlg.accept()

        ta_btn.clicked.connect(lambda: _award_to(0))
        tb_btn.clicked.connect(lambda: _award_to(1))
        cancel_btn.clicked.connect(dlg.reject)

        dlg.setFixedWidth(360)
        dlg.adjustSize()
        dlg.setFixedSize(dlg.size())
        points_input.setFocus()
        dlg.exec()

    steal.clicked.connect(steal_from_bottom)

    # Navigation row: Back to Board and Play (right-aligned)
    nav = QWidget()
    n_layout = QHBoxLayout(nav)
    n_layout.setContentsMargins(0, 0, 0, 0)
    n_layout.addStretch()
    back_btn = QPushButton("Back to Board")
    back_btn.setCursor(Qt.PointingHandCursor)
    back_btn.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #4f46e5, stop:1 #0ea5e9);"
        "color:white; border-radius:20px; padding:12px 22px; font-weight:700;"
    )
    back_btn.clicked.connect(app.show_home)
    play_btn = QPushButton("Display Game")
    play_btn.setCursor(Qt.PointingHandCursor)
    play_btn.setStyleSheet(
        "background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #34d399, stop:1 #10b981);"
        "color:white; border-radius:20px; padding:12px 22px; font-weight:800;"
    )
    # Open the separate display window that shows the audience/board view
    play_btn.clicked.connect(lambda t=title, d=description: display_game.open_display_game(app, t or "", d or ""))
    n_layout.addWidget(back_btn)
    n_layout.addWidget(play_btn)
    layout.addWidget(nav)

    app.play_widget = page
    if load_db_first:
        try:
            load_first_db_round()
        except Exception:
            pass
    # expose helper to get current round (question + answers) from this page
    def _get_current_round_data():
        return page.game_state.get('current_round')

    page.get_current_round_data = _get_current_round_data

    # module-level helper to fetch current round from the app if needed
    def get_opened_game_round(app_ref):
        try:
            pw = getattr(app_ref, 'play_widget', None)
            if pw and hasattr(pw, 'game_state'):
                return pw.game_state.get('current_round')
        except Exception:
            pass
        return None

    try:
        app.stack.addWidget(page)
        app.stack.setCurrentWidget(page)
    except Exception:
        try:
            app.show_static_modal("Play", "Could not open play page.")
        except Exception:
            pass
