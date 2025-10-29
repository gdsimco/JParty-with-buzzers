from PyQt6.QtWidgets import QStyle, QCommonStyle
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

import json
import logging

from jparty.utils import DynamicLabel, add_shadow, resource_path


class JPartyStyle(QCommonStyle):
    PM_dict = {
        QStyle.PixelMetric.PM_LayoutBottomMargin: 0,
        QStyle.PixelMetric.PM_LayoutLeftMargin: 0,
        QStyle.PixelMetric.PM_LayoutRightMargin: 0,
        QStyle.PixelMetric.PM_LayoutTopMargin: 0,
        QStyle.PixelMetric.PM_LayoutHorizontalSpacing: 0,
        QStyle.PixelMetric.PM_LayoutVerticalSpacing: 0,
    }
    SH_dict = {
        QStyle.StyleHint.SH_Button_FocusPolicy: 0,
    }

    def pixelMetric(self, key, *args, **kwargs):
        return JPartyStyle.PM_dict.get(key, super().pixelMetric(key, *args, **kwargs))

    def styleHint(self, key, *args, **kwargs):
        return JPartyStyle.SH_dict.get(key, super().styleHint(key, *args, **kwargs))


class MyLabel(DynamicLabel):
    def __init__(self, text, initialSize, parent=None):
        super().__init__(text, initialSize, parent)
        self.font().setBold(True)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        add_shadow(self)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))
        self.setPalette(palette)

        self.show()


WINDOWPAL = QPalette()
WINDOWPAL.setColor(QPalette.ColorRole.Base, QColor("white"))
WINDOWPAL.setColor(QPalette.ColorRole.WindowText, QColor("black"))
WINDOWPAL.setColor(QPalette.ColorRole.Text, QColor("black"))
WINDOWPAL.setColor(QPalette.ColorRole.Window, QColor("#fefefe"))
WINDOWPAL.setColor(QPalette.ColorRole.Button, QColor("#e6e6e6"))
WINDOWPAL.setColor(QPalette.ColorRole.Button, QColor("#e6e6e6"))
WINDOWPAL.setColor(QPalette.ColorRole.ButtonText, QColor("black"))
WINDOWPAL.setColor(
    QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor("#d0d0d0")
)

# Try to load theme colors from theme_config.json so styles match Game's theme.
# theme_config.json is expected to contain hex strings for 'boardTileColor' and
# 'boardTileHighlightedColor'.
try:
    with open(resource_path('theme_config.json'), 'r') as _f:
        _theme = json.load(_f)
except Exception:
    _theme = {}

_colors = _theme.get('colors', _theme)

def _ensure_hash(s):
    if s is None:
        return None
    if isinstance(s, str) and s.startswith('#'):
        return s
    if isinstance(s, str):
        return f'#{s}'
    return None

_board_tile_hex = _ensure_hash(_colors.get('boardTileColor')) or '#1010a1'
_board_tile_highlighted_hex = _ensure_hash(_colors.get('boardTileHighlightedColor')) or '#0b0b74'
_board_text_hex = _ensure_hash(_colors.get('boardTextColor')) or '#ffcc00'

# Provide both constant-style names and snake_case names so callers can use either.
BOARD_TILE_COLOR = QColor(_board_tile_hex)
BOARD_TILE_HIGHLIGHTED_COLOR = QColor(_board_tile_highlighted_hex)

# Board text color used for money / clue text on the board
BOARD_TEXT_COLOR = QColor(_board_text_hex)

# Convenience lowercase names requested: board_tile_color, board_tile_highlighted_color
board_text_color = BOARD_TEXT_COLOR

# Convenience lowercase names requested: board_tile_color, board_tile_highlighted_color
board_tile_color = BOARD_TILE_COLOR
board_tile_highlighted_color = BOARD_TILE_HIGHLIGHTED_COLOR

CARDPAL = QPalette()
CARDPAL.setColor(QPalette.ColorRole.Window, BOARD_TILE_COLOR)
CARDPAL.setColor(QPalette.ColorRole.WindowText, QColor('#ffffff'))
logging.info(f"Style colors - BOARD_TILE_COLOR: {_board_tile_hex}, BOARD_TILE_HIGHLIGHTED_COLOR: {_board_tile_highlighted_hex}, BOARD_TEXT_COLOR: {_board_text_hex}")
