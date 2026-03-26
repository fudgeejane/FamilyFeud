from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap
from pathlib import Path
import importlib

# optional DB persistence
try:
    import database.db as db
except Exception:
    db = None


def build_home(parent: QWidget, app):
    """Construct the home UI inside `parent` for a PySide6-based UI.

    Sets `app.title_entry` and `app.desc_text`.
    """
    # clear layout/widgets
    try:
        layout = parent.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                if w:
                    w.setParent(None)
    except Exception:
        pass

    layout = QVBoxLayout(parent)
    # reduce the top margin so cards sit closer under the header
    layout.setContentsMargins(120, 30, 120, 40)
    # keep widgets aligned to the top so cards appear below the header
    layout.setAlignment(Qt.AlignTop)

    # Header: title on the left, short green button inline at the right
    from PySide6.QtWidgets import QHBoxLayout, QWidget, QMenu

    header = QWidget()
    h_layout = QHBoxLayout(header)
    h_layout.setContentsMargins(0, 0, 0, 0)

    # Header logo: prefer `assets/logo.png` if present, otherwise fall back to text
    assets_logo = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
    if assets_logo.exists():
        logo_lbl = QLabel()
        pix = QPixmap(str(assets_logo))
        if not pix.isNull():
            # scale to a reasonable width while preserving aspect ratio
            pix = pix.scaledToWidth(300, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        else:
            logo_lbl.setText("TCC Feud")
            logo_lbl.setStyleSheet("font-size:40pt; color: #ffffff;")
        h_layout.addWidget(logo_lbl, alignment=Qt.AlignLeft)
    else:
        title = QLabel("TCC Feud")
        title.setStyleSheet("font-size:40pt; color: #ffffff;")
        h_layout.addWidget(title, alignment=Qt.AlignLeft)

    h_layout.addStretch()
    h_layout.addStretch()

    # Try import game modal for edit/delete functionality
    try:
        qm = importlib.import_module("utils.game_modal")
    except Exception:
        qm = None

    # Short inline green button
    try:
        qm = importlib.import_module("utils.game_modal")

        def on_game_created(payload):
            # append to in-memory model and refresh cards
            try:
                if not hasattr(app, "games"):
                    app.games = []
                app.games.append({"title": payload.get("title", "(no title)"), "description": payload.get("description", "")})
                try:
                    if db:
                        db.save_games(app.games)
                except Exception:
                    pass
                if hasattr(app, "render_home_cards"):
                    app.render_home_cards()
                elif hasattr(app, "render_cards"):
                    app.render_cards()
            except Exception:
                try:
                    app.show_static_modal("Game Created", payload.get("title", "(no title)"))
                except Exception:
                    pass

        qbtn = QPushButton("Create Game")
        qbtn.setFixedSize(96, 42)
        qbtn.setStyleSheet("""
        QPushButton {
            background-color: #0038d9;
            color: white;
            border-radius: 6px;
            font-weight: 600;
                           font-size: 14px;
        }
        QPushButton:hover {
            background-color: #0050ff;
        }
        """)
        qbtn.clicked.connect(lambda: qm.open_game_modal(app, on_create=on_game_created))
        qbtn.setCursor(Qt.PointingHandCursor)
        h_layout.addWidget(qbtn, alignment=Qt.AlignRight)
    except Exception:
        pass

    layout.addWidget(header, alignment=Qt.AlignTop)

    # Dynamic game cards area backed by `app.games` list
    cards_area = QWidget()
    cards_layout = QHBoxLayout(cards_area)
    cards_layout.setSpacing(20)
    cards_layout.setContentsMargins(0, 8, 0, 20)
    cards_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    cards_area.setFixedHeight(220)

    # ensure an in-memory games list exists on the app; prefer DB if available
    if not hasattr(app, "games"):
        if db:
            try:
                loaded = db.load_games()
                # if DB exists but empty, use empty list (display placeholder)
                app.games = loaded if isinstance(loaded, list) else []
            except Exception:
                app.games = []
        else:
            # start with empty list when no DB persistence is available
            app.games = []

    def render_cards():
        # clear existing widgets
        while cards_layout.count():
            item = cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        if not app.games:
            placeholder = QLabel("No games created yet.")
            placeholder.setStyleSheet("color:#cbd5e1; font-size:12pt; padding:12px;")
            placeholder.setAlignment(Qt.AlignCenter)
            cards_layout.addWidget(placeholder)
            return

        for idx, game in enumerate(app.games):
            title_text = game.get("title", "(no title)")
            desc_text = game.get("description", "")

            card = QWidget()
            card.setStyleSheet("background:#789aff; border-radius:8px;")
            card.setFixedSize(300, 180)
            card.setCursor(Qt.PointingHandCursor)

            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(12, 12, 12, 12)

            top = QWidget()
            top_l = QHBoxLayout(top)
            top_l.setContentsMargins(0, 0, 0, 0)

            title_lbl = QLabel(title_text)
            title_lbl.setStyleSheet("font-weight:700; font-size:16px; color:white;")
            top_l.addWidget(title_lbl)
            top_l.addStretch()

            # Improved menu button styling and controlled popup for better UX
            menu_btn = QPushButton("⋮")
            menu_btn.setFixedSize(40, 40)
            menu_btn.setCursor(Qt.PointingHandCursor)
            menu_btn.setFocusPolicy(Qt.NoFocus)
            menu_btn.setToolTip("More actions")
            menu_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #ffffff;
                    border-radius: 8px;
                    font-size: 18px;
                    padding: 4px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.06);
                }
                QPushButton:pressed {
                    background: rgba(255,255,255,0.10);
                }
            """)

            # Create a styled QMenu and open it explicitly so positioning is consistent
            menu = QMenu()
            menu.setWindowFlags(menu.windowFlags() | Qt.NoDropShadowWindowHint)
            menu.setStyleSheet("""
                QMenu {
                    background: #071033;
                    color: #e6eef8;
                    border: 1px solid rgba(255,255,255,0.06);
                    border-radius: 8px;
                    padding: 6px 0px;
                }
                QMenu::item {
                    padding: 8px 20px;
                    spacing: 8px;
                }
                QMenu::item:selected {
                    background: rgba(255,255,255,0.04);
                }
            """)

            # Actions
            edit_action = menu.addAction("Edit")
            delete_action = menu.addAction("Delete")
            # style delete action text color by wrapping in HTML on triggered handler (QAction styling limited)

            def on_edit_triggered(checked=False, i=idx):
                try:
                    if qm and hasattr(qm, "open_edit_modal"):
                        def _on_save(payload):
                            app.games[i]["title"] = payload.get("title", app.games[i]["title"]) 
                            app.games[i]["description"] = payload.get("description", app.games[i].get("description", ""))
                            try:
                                if db:
                                    db.save_games(app.games)
                            except Exception:
                                pass
                            render_cards()
                        qm.open_edit_modal(app, app.games[i].get("title", ""), app.games[i].get("description", ""), on_save=_on_save)
                        return
                except Exception:
                    pass
                app.show_static_modal("Edit", f"Edit {app.games[i].get('title', '')}")

            def on_delete_triggered(checked=False, i=idx):
                try:
                    if qm and hasattr(qm, "open_delete_confirm"):
                        def _on_confirm():
                            try:
                                del app.games[i]
                            except Exception:
                                pass
                            try:
                                if db:
                                    db.save_games(app.games)
                            except Exception:
                                pass
                            render_cards()
                        qm.open_delete_confirm(app, on_confirm=_on_confirm)
                        return
                except Exception:
                    pass
                try:
                    del app.games[i]
                except Exception:
                    pass
                try:
                    if db:
                        db.save_games(app.games)
                except Exception:
                    pass
                render_cards()

            edit_action.triggered.connect(on_edit_triggered)
            delete_action.triggered.connect(on_delete_triggered)

            # open menu on click with precise placement
            def _open_menu():
                pos = menu_btn.mapToGlobal(QPoint(menu_btn.width() - menu.sizeHint().width(), menu_btn.height()))
                menu.exec(pos)

            menu_btn.clicked.connect(_open_menu)
            top_l.addWidget(menu_btn)

            c_layout.addWidget(top)

            desc = QLabel(desc_text)
            desc.setWordWrap(True)
            desc.setStyleSheet("color:white;")
            c_layout.addWidget(desc)

            c_layout.addStretch()

            info = QLabel("Click to view, modify or play the game")
            info.setStyleSheet("color:#002866; font-size:12px;")
            info.setAlignment(Qt.AlignCenter)
            c_layout.addWidget(info)

            def _on_card_click(event, i=idx):
                try:
                    mg = importlib.import_module("modules.modify_game")
                    if hasattr(mg, "open_modify_game"):
                        mg.open_modify_game(app, app.games[i].get("title", ""), app.games[i].get("description", ""))
                        return
                except Exception:
                    pass
                try:
                    app.show_static_modal(f"Modify {app.games[i].get('title', '')}", "Static modify UI not available.")
                except Exception:
                    pass

            card.mousePressEvent = _on_card_click
            cards_layout.addWidget(card)

    # expose renderer so other callbacks (create modal) can refresh the UI
    try:
        app.render_home_cards = render_cards
    except Exception:
        pass
    render_cards()
    layout.addWidget(cards_area, alignment=Qt.AlignLeft | Qt.AlignTop)