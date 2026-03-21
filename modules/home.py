from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path
import importlib


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
    layout.setContentsMargins(60, 30, 60, 40)
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

    # Short inline green button
    try:
        qm = importlib.import_module("utils.game_modal")

        def on_game_created(payload):
            app.show_static_modal("Game Created", payload.get("title", "(no title)"))

        qbtn = QPushButton("New Game")
        qbtn.setFixedSize(96, 34)
        qbtn.setStyleSheet("""
        QPushButton {
            background-color: #0038d9;
            color: white;
            border-radius: 6px;
            font-weight: 600;
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

    # Static game cards (three cards side-by-side)
    cards_area = QWidget()
    cards_layout = QHBoxLayout(cards_area)
    cards_layout.setSpacing(20)
    cards_layout.setContentsMargins(0, 8, 0, 20)
    # align cards to the left/top inside the cards area
    cards_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    # keep the cards area compact so it doesn't center vertically
    cards_area.setFixedHeight(200)

    for i, title_text in enumerate(["Game 1", "Game 2", "Game 3"], start=1):
        card = QWidget()
        card.setStyleSheet("background:#789aff; border-radius:8px;")
        card.setFixedSize(300, 180)
        card.setCursor(Qt.PointingHandCursor)

        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(12, 12, 12, 12)

        # Top row: title and three-dot menu
        top = QWidget()
        top_l = QHBoxLayout(top)
        top_l.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(title_text)
        title_lbl.setStyleSheet("font-weight:700; color:#111827;")
        top_l.addWidget(title_lbl)
        top_l.addStretch()

        menu_btn = QPushButton("⋮")
        menu_btn.setFixedSize(28, 28)
        menu_btn.setCursor(Qt.PointingHandCursor)
        menu = QMenu(menu_btn)
        # Edit action — open a simple modal for now
        menu.addAction("Edit", lambda t=title_text: app.show_static_modal("Edit", f"Edit {t}"))
        # Delete action — remove the card from layout
        def _make_delete(c=card):
            def _del():
                c.setParent(None)
                c.deleteLater()
            return _del
        menu.addAction("Delete", _make_delete())
        menu_btn.setMenu(menu)
        top_l.addWidget(menu_btn)

        c_layout.addWidget(top)

        # Description
        desc = QLabel(f"This is a short description for {title_text}.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#6b7280;")
        c_layout.addWidget(desc)

        c_layout.addStretch()

        # Informational text only (no dropdown or click actions)
        info = QLabel("Click to view, modify or play the game")
 
        info.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(info)

        # Clicking the card opens the modify UI (modules.modify_game.open_modify_game)
        def _on_card_click(event, t=title_text, d=desc.text()):
            try:
                mg = importlib.import_module("modules.modify_game")
                if hasattr(mg, "open_modify_game"):
                    mg.open_modify_game(app, t, d)
                    return
            except Exception:
                pass
            # Fallback: show a static modal
            try:
                app.show_static_modal(f"Modify {t}", "Static modify UI not available.")
            except Exception:
                pass

        card.mousePressEvent = _on_card_click
        cards_layout.addWidget(card)

    layout.addWidget(cards_area, alignment=Qt.AlignLeft | Qt.AlignTop)