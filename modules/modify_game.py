from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
import uuid


def open_modify_game(app, title: str, description: str, game_id: str | None = None):
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
    # page background to match app theme
    try:
        page.setStyleSheet("background: #071437;")
    except Exception:
        pass
    page_layout = QVBoxLayout(page)
    page_layout.setContentsMargins(60, 30, 60, 40)
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
                pix = pix.scaledToWidth(300, Qt.SmoothTransformation)
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

    # Header action buttons: Back to Board and Play Game
    back_board = QPushButton("Back to Board")
    back_board.setStyleSheet("background:#0a84ff; color:white; border-radius:16px; padding:8px 14px;")
    back_board.setCursor(Qt.PointingHandCursor)
    back_board.clicked.connect(app.show_home)

    play_btn = QPushButton("Play Game")
    play_btn.setStyleSheet("background:#16a34a; color:white; border-radius:16px; padding:8px 14px;")
    play_btn.setCursor(Qt.PointingHandCursor)

    def _on_play(t=title, d=description):
        try:
            import importlib

            pg = importlib.import_module("modules.play_game")
            if hasattr(pg, "open_play_game"):
                # open Play view and load the first question from the DB for this game
                try:
                    pg.open_play_game(app, t, d, load_db_first=True)
                except TypeError:
                    # fallback if older signature
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

    h_layout.addWidget(back_board, alignment=Qt.AlignRight)
    h_layout.addWidget(play_btn, alignment=Qt.AlignRight)

    page_layout.addWidget(header)

    # Toolbar under header: Add Question button
    from PySide6.QtWidgets import QScrollArea, QFrame, QSizePolicy, QLineEdit, QSpinBox, QCheckBox, QAbstractSpinBox, QMessageBox

    # optional DB persistence helper
    try:
        import database.db as db
    except Exception:
        db = None

    toolbar = QWidget()
    tb_layout = QHBoxLayout(toolbar)
    tb_layout.setContentsMargins(0, 0, 0, 0)
    tb_layout.addStretch()
    add_question_btn = QPushButton("Add Question")
    add_question_btn.setStyleSheet("background:#0a84ff; color:white; border-radius:8px; padding:8px 12px;")
    add_question_btn.setCursor(Qt.PointingHandCursor)
    tb_layout.addWidget(add_question_btn, alignment=Qt.AlignRight)
    page_layout.addWidget(toolbar)

    # store current game id on the app for UI-only association
    try:
        if game_id is not None:
            app.current_game_id = game_id
    except Exception:
        pass

    # Scroll area for dynamic question cards
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll_content = QWidget()
    sc_layout = QVBoxLayout(scroll_content)
    sc_layout.setContentsMargins(0, 0, 0, 0)
    sc_layout.setSpacing(14)

    # Container where question cards will be added
    questions_container = QWidget()
    questions_layout = QVBoxLayout(questions_container)
    questions_layout.setContentsMargins(0, 0, 0, 0)
    questions_layout.setSpacing(12)

    # Helper to renumber question titles
    def renumber_questions():
        for i in range(questions_layout.count()):
            item = questions_layout.itemAt(i).widget()
            if item is None:
                continue
            title_lbl = item.findChild(QLabel, "_q_title")
            if title_lbl:
                title_lbl.setText(f"Question {i+1}")

    # Function to create and add a new question card
    def add_question(initial: dict | None = None):
        card = QWidget()
        card.setObjectName("question_card")
        # subtle shadow for card to lift it from the background
        try:
            from PySide6.QtWidgets import QGraphicsDropShadowEffect
            from PySide6.QtGui import QColor

            sh = QGraphicsDropShadowEffect(card)
            sh.setBlurRadius(18)
            sh.setXOffset(0)
            sh.setYOffset(6)
            sh.setColor(QColor(6, 11, 28, 120))
            card.setGraphicsEffect(sh)
        except Exception:
            pass
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)
        card.setStyleSheet("background:#ffffff; border-radius:8px;")

        # Top row: title, fast-money toggle, reset, delete
        top = QWidget()
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(0, 0, 0, 0)
        title_lbl = QLabel("Question")
        title_lbl.setObjectName("_q_title")
        title_lbl.setStyleSheet("font-weight:700; color:#111827;")
        top_l.addWidget(title_lbl)
        top_l.addStretch()

        fast_cb = QCheckBox("Fast Money")
        fast_cb.setCursor(Qt.PointingHandCursor)
        top_l.addWidget(fast_cb)

        reset_btn = QPushButton("Reset")
        reset_btn.setStyleSheet("background:#ef4444; color:white; border-radius:6px; padding:6px 10px;")
        reset_btn.setCursor(Qt.PointingHandCursor)
        top_l.addWidget(reset_btn)

        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background:#6b7280; color:white; border-radius:6px; padding:6px 10px;")
        del_btn.setCursor(Qt.PointingHandCursor)
        top_l.addWidget(del_btn)

        card_layout.addWidget(top)

        # Question input
        q_input = QLineEdit()
        q_input.setPlaceholderText("Enter question text...")
        q_input.setMinimumHeight(32)
        card_layout.addWidget(q_input)

        # Answers: two columns, four answers each (1-4 left, 5-8 right)
        answers_area = QWidget()
        answers_layout = QHBoxLayout(answers_area)
        answers_layout.setContentsMargins(0, 0, 0, 0)
        answers_layout.setSpacing(12)

        # We'll collect score inputs and answer edits per card so we can compute a running total
        score_inputs = []
        answer_inputs = []

        # First column (answers 1-4)
        col1 = QWidget()
        col1_l = QVBoxLayout(col1)
        col1_l.setContentsMargins(0, 0, 0, 0)
        col1_l.setSpacing(8)
        for a_i in range(4):
            row = QWidget()
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(0, 0, 0, 0)
            r_layout.setSpacing(8)
            ans_input = QLineEdit()
            ans_input.setPlaceholderText(f"Answer {a_i+1}")
            ans_input.setMinimumHeight(32)
            ans_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            ans_input.setStyleSheet("background:#fbfdff; border:1px solid #e6eef6; border-radius:6px; padding:8px;")
            score_input = QSpinBox()
            score_input.setRange(0, 1000000)
            score_input.setFixedWidth(92)
            score_input.setMinimumHeight(32)
            score_input.setStyleSheet(
                "background: #ffffff;"
                "color: #0b1220;"
                "border: 1px solid #94a3b8;"
                "border-radius: 6px;"
                "padding: 4px;"
                "font-size: 11pt;"
                "font-weight: 600;"
            )
            score_input.setAlignment(Qt.AlignCenter)
            score_input.setToolTip("Points awarded for this answer")
            try:
                score_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
            except Exception:
                pass
            answer_inputs.append(ans_input)
            score_inputs.append(score_input)
            r_layout.addWidget(ans_input)
            r_layout.addWidget(score_input, alignment=Qt.AlignRight)
            col1_l.addWidget(row)

        # Second column (answers 5-8)
        col2 = QWidget()
        col2_l = QVBoxLayout(col2)
        col2_l.setContentsMargins(0, 0, 0, 0)
        col2_l.setSpacing(8)
        for a_i in range(4, 8):
            row = QWidget()
            r_layout = QHBoxLayout(row)
            r_layout.setContentsMargins(0, 0, 0, 0)
            r_layout.setSpacing(8)
            ans_input = QLineEdit()
            ans_input.setPlaceholderText(f"Answer {a_i+1}")
            ans_input.setMinimumHeight(32)
            ans_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            ans_input.setStyleSheet("background:#fbfdff; border:1px solid #e6eef6; border-radius:6px; padding:8px;")
            score_input = QSpinBox()
            score_input.setRange(0, 1000000)
            score_input.setFixedWidth(92)
            score_input.setMinimumHeight(32)
            score_input.setStyleSheet(
                "background: #ffffff;"
                "color: #0b1220;"
                "border: 1px solid #94a3b8;"
                "border-radius: 6px;"
                "padding: 4px;"
                "font-size: 11pt;"
                "font-weight: 600;"
            )
            score_input.setAlignment(Qt.AlignCenter)
            score_input.setToolTip("Points awarded for this answer")
            try:
                score_input.setButtonSymbols(QAbstractSpinBox.NoButtons)
            except Exception:
                pass
            answer_inputs.append(ans_input)
            score_inputs.append(score_input)
            r_layout.addWidget(ans_input)
            r_layout.addWidget(score_input, alignment=Qt.AlignRight)
            col2_l.addWidget(row)

        answers_layout.addWidget(col1)
        answers_layout.addWidget(col2)
        card_layout.addWidget(answers_area)

        # Total score display for this question card with Save button
        total_row = QWidget()
        total_l = QHBoxLayout(total_row)
        total_l.setContentsMargins(0, 6, 0, 0)

        total_l.addStretch()  # pushes everything to the right

        total_label = QLabel("Total: 0 pts")
        total_label.setStyleSheet("font-weight:700; color:#0b1220;")

        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("background:#00d627; font-size:12px; color:white; border-radius:8px; padding:6px 18px; margin-left:12px;")

        total_l.addWidget(total_label)
        total_l.addWidget(save_btn)

        card_layout.addWidget(total_row)

        def update_total():
            s = sum(si.value() for si in score_inputs)
            total_label.setText(f"Total: {s} pts")

        # mark card unsaved when user edits any input so Save button re-enables
        def mark_unsaved():
            try:
                if getattr(card, "_saved", False):
                    card._saved = False
                    save_btn.setText("Save")
                    save_btn.setEnabled(True)
                    update_add_button_state()
            except Exception:
                pass

        for si in score_inputs:
            # update total when score changes
            si.valueChanged.connect(lambda v, fn=update_total: fn())
            # mark card as unsaved when score changes
            si.valueChanged.connect(lambda v, fn=mark_unsaved: fn())

        # mark unsaved when text inputs change (question and answers)
        try:
            q_input.textChanged.connect(lambda *_: mark_unsaved())
        except Exception:
            pass
        for ai in answer_inputs:
            try:
                ai.textChanged.connect(lambda *_: mark_unsaved())
            except Exception:
                pass

        # if initial data provided, pre-fill fields and mark saved
        if initial:
            try:
                q_input.setText(initial.get("question", ""))
                ans_list = initial.get("answers", [])
                # fill answers and scores in order
                for i, line in enumerate(answer_inputs):
                    if i < len(ans_list):
                        line.setText(ans_list[i].get("text", ""))
                for i, si in enumerate(score_inputs):
                    if i < len(ans_list):
                        try:
                            si.setValue(int(ans_list[i].get("score", 0)))
                        except Exception:
                            si.setValue(0)
                # compute total display
                update_total()
                # mark saved state
                card._saved = True
                card.saved_payload = initial
                save_btn.setText("Saved")
                save_btn.setEnabled(False)
            except Exception:
                pass

        # mark card as unsaved initially (unless pre-filled)
        if not initial:
            card._saved = False

        def set_card_saved(payload: dict):
            card._saved = True
            card.saved_payload = payload
            save_btn.setText("Saved")
            save_btn.setEnabled(False)
            # after saving, enable Add Question if no unsaved cards
            update_add_button_state()

        def save_question():
            # basic validation: question text required
            qtext = q_input.text().strip()
            if not qtext:
                mb = QMessageBox(card)
                mb.setWindowTitle("Validation")
                mb.setText("Please enter the question text before saving.")
                mb.exec()
                return
            answers = []
            for col in (col1, col2):
                for i in range(col.layout().count()):
                    roww = col.layout().itemAt(i).widget()
                    if roww is None:
                        continue
                    line = roww.findChild(QLineEdit)
                    spin = roww.findChild(QSpinBox)
                    answers.append({
                        "text": line.text().strip() if line else "",
                        "score": spin.value() if spin else 0,
                    })
            payload = {
                "question": qtext,
                "answers": answers,
                "total": sum(a["score"] for a in answers),
                "game_id": getattr(app, "current_game_id", None),
            }
            # ensure a stable id for updates
            try:
                if hasattr(card, "saved_payload") and isinstance(card.saved_payload, dict) and card.saved_payload.get("id"):
                    payload["id"] = card.saved_payload.get("id")
                else:
                    payload["id"] = uuid.uuid4().hex
            except Exception:
                payload["id"] = uuid.uuid4().hex
            # associate with app.games under the matching game id or title when possible
            try:
                if not hasattr(app, "games") or not isinstance(app.games, list):
                    app.games = []

                gid = payload.get("game_id") or getattr(app, "current_game_id", None)
                target_game = None

                # prefer matching by explicit id
                if gid:
                    for g in app.games:
                        if g.get("id") == gid:
                            target_game = g
                            break

                # fallback to matching by title
                if not target_game:
                    for g in app.games:
                        if g.get("title") == title:
                            target_game = g
                            break

                # if still not found, create a new game entry and append it
                if not target_game:
                    new_game = {"title": title or "(Untitled Game)", "description": description or "", "id": gid or uuid.uuid4().hex, "questions": []}
                    app.games.append(new_game)
                    target_game = new_game

                qs = target_game.setdefault("questions", [])
                # Prefer updating the card's saved_payload object directly if available
                saved_ref = None
                try:
                    if hasattr(card, "saved_payload") and isinstance(card.saved_payload, dict):
                        # update the saved_payload dict in-place
                        card.saved_payload.clear()
                        card.saved_payload.update(payload)
                        saved_ref = card.saved_payload
                        # ensure it's present in the questions list
                        if card.saved_payload not in qs:
                            # try to replace by id if an old entry exists
                            replaced = False
                            for i, q in enumerate(qs):
                                if isinstance(q, dict) and q.get("id") == payload.get("id"):
                                    qs[i] = card.saved_payload
                                    replaced = True
                                    break
                            if not replaced:
                                qs.append(card.saved_payload)
                    else:
                        # fallback: try replace existing question by id (update in-place)
                        replaced = False
                        for i, q in enumerate(qs):
                            if isinstance(q, dict) and q.get("id") == payload.get("id"):
                                q.clear()
                                q.update(payload)
                                saved_ref = q
                                replaced = True
                                break
                        if not replaced:
                            qs.append(payload)
                            saved_ref = payload
                except Exception:
                    # as a last resort, append the payload
                    try:
                        qs.append(payload)
                        saved_ref = payload
                    except Exception:
                        saved_ref = payload

                # persist to DB if available (raise or log on failure)
                if db:
                    ok = False
                    try:
                        ok = db.save_games(app.games)
                    except Exception:
                        ok = False
                    if not ok:
                        try:
                            mb = QMessageBox(card)
                            mb.setWindowTitle("Save Failed")
                            mb.setText("Could not save changes to disk. Your changes are kept in memory.")
                            mb.exec()
                        except Exception:
                            pass

                # refresh home view if available so changes are visible immediately
                try:
                    if hasattr(app, "render_home_cards"):
                        app.render_home_cards()
                except Exception:
                    pass
            except Exception:
                try:
                    mb = QMessageBox(card)
                    mb.setWindowTitle("Error")
                    mb.setText("An error occurred while saving the question.")
                    mb.exec()
                except Exception:
                    pass
            # use saved_ref when available to keep consistent object reference
            try:
                set_card_saved(saved_ref if 'saved_ref' in locals() and saved_ref is not None else payload)
            except Exception:
                set_card_saved(payload)

        save_btn.clicked.connect(save_question)

        # Reset behavior for this card
        def _reset_card():
            q_input.clear()
            fast_cb.setChecked(False)
            for i in range(card_layout.count()):
                w = card_layout.itemAt(i).widget()
                if isinstance(w, QWidget):
                    # find QLineEdit and QSpinBox children
                    for child in w.findChildren(QLineEdit):
                        child.clear()
                    for child in w.findChildren(QSpinBox):
                        child.setValue(0)
                # resetting makes the card unsaved
                try:
                    card._saved = False
                    save_btn.setText("Save")
                    save_btn.setEnabled(True)
                    update_add_button_state()
                except Exception:
                    pass

        reset_btn.clicked.connect(_reset_card)

        # Delete behavior
        def _delete_card():
            # show a parented modal dialog (overlay-style) to confirm deletion
            try:
                from utils.question_modal import open_confirm_modal

                confirmed = open_confirm_modal(
                    page,
                    "Delete Question",
                    "Are you sure you want to delete this question? This action cannot be undone.",
                )
                if not confirmed:
                    return
            except Exception:
                # fallback to simple QMessageBox if dialog creation fails
                try:
                    resp = QMessageBox.question(
                        card,
                        "Delete Question",
                        "Are you sure you want to delete this question? This action cannot be undone.",
                        QMessageBox.Yes | QMessageBox.No,
                    )
                except Exception:
                    return
                if resp not in (QMessageBox.Yes, QMessageBox.StandardButton(QMessageBox.Yes)):
                    return

            # remove from data model if this card was previously saved
            try:
                if hasattr(app, "games") and isinstance(app.games, list):
                    gid = getattr(app, "current_game_id", None)
                    target_game = None
                    if gid:
                        for g in app.games:
                            if g.get("id") == gid or g.get("title") == title:
                                target_game = g
                                break
                    if not target_game:
                        for g in app.games:
                            if g.get("title") == title:
                                target_game = g
                                break
                    if target_game and isinstance(target_game.get("questions"), list):
                        try:
                            if hasattr(card, "saved_payload") and isinstance(card.saved_payload, dict):
                                sp = card.saved_payload
                                # remove by identity or by id
                                for i, q in enumerate(list(target_game.get("questions", []))):
                                    try:
                                        if q is sp or (isinstance(q, dict) and sp.get("id") and q.get("id") == sp.get("id")):
                                            del target_game["questions"][i]
                                            break
                                    except Exception:
                                        continue
                        except Exception:
                            pass
                    # persist changes
                    if db:
                        try:
                            db.save_games(app.games)
                        except Exception:
                            pass
            except Exception:
                pass

            # remove UI
            try:
                card.setParent(None)
                card.deleteLater()
            except Exception:
                pass
            renumber_questions()
            # if deleted, ensure Add Question button state updates
            try:
                update_add_button_state()
            except Exception:
                pass
            try:
                if hasattr(app, "render_home_cards"):
                    app.render_home_cards()
            except Exception:
                pass

        del_btn.clicked.connect(_delete_card)

        questions_layout.addWidget(card)
        renumber_questions()

    # Wire add_question_btn
    def any_unsaved():
        for i in range(questions_layout.count()):
            w = questions_layout.itemAt(i).widget()
            if w and getattr(w, "_saved", False) is False:
                return True
        return False

    def update_add_button_state():
        try:
            add_question_btn.setEnabled(not any_unsaved())
        except Exception:
            add_question_btn.setEnabled(True)

    add_question_btn.clicked.connect(lambda: add_question(None) if not any_unsaved() else None)

    # Populate existing saved questions for this game (if any), otherwise start with one blank
    try:
        populated = False
        if hasattr(app, "games"):
            gid = getattr(app, "current_game_id", None)
            target_game = None
            if gid:
                for g in app.games:
                    if g.get("id") == gid or g.get("title") == title:
                        target_game = g
                        break
            if not target_game:
                for g in app.games:
                    if g.get("title") == title:
                        target_game = g
                        break
            if target_game and isinstance(target_game.get("questions"), list):
                for q in target_game.get("questions", []):
                    add_question(q)
                populated = True
        if not populated:
            add_question(None)
    except Exception:
        add_question(None)
    # ensure Add Question button state reflects any unsaved items
    try:
        update_add_button_state()
    except Exception:
        pass

    sc_layout.addWidget(questions_container)
    sc_layout.addStretch()
    scroll.setWidget(scroll_content)
    page_layout.addWidget(scroll)

    

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
