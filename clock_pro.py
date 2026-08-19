import sys
import json
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QDialog, QFormLayout, QSpinBox, QSlider, QColorDialog, QFontComboBox,
    QCheckBox, QComboBox, QDialogButtonBox
)

APP_DIR = Path.home() / ".clock_pro_minimal"
APP_DIR.mkdir(exist_ok=True)
CONFIG = APP_DIR / "settings.json"

DEFAULT = {
    "x": 80, "y": 80,
    "locked": False,
    "topmost": True,
    "hour24": True,
    "show_seconds": True,
    "show_date": True,
    "clock_font": "Segoe UI",
    "clock_size": 48,
    "date_font": "Segoe UI",
    "date_size": 13,
    "clock_color": "#FFFFFF",
    "date_color": "#B8BDC5",
    "background": "#202329",
    "opacity": 96,
    "width": 430,
    "height": 220
}

def load():
    try:
        return {**DEFAULT, **json.loads(CONFIG.read_text(encoding="utf-8"))}
    except Exception:
        return DEFAULT.copy()

cfg = load()

def save():
    try:
        CONFIG.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception:
        pass


class Settings(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Clock Customization")
        self.setMinimumWidth(430)

        self.setStyleSheet("""
            QDialog { background:#181B20; color:white; }
            QLabel, QCheckBox { color:#E9EAEC; }
            QSpinBox, QComboBox, QFontComboBox {
                background:#292D34; color:white; padding:5px;
                border:1px solid #424852; border-radius:4px;
            }
            QPushButton {
                background:#292D34; color:white; padding:7px 10px;
                border:0; border-radius:5px;
            }
            QPushButton:hover { background:#3A404A; }
        """)

        form = QFormLayout(self)

        self.clock_font = QFontComboBox()
        self.clock_font.setCurrentFont(QFont(cfg["clock_font"]))
        form.addRow("Time font:", self.clock_font)

        self.clock_size = QSpinBox()
        self.clock_size.setRange(18, 120)
        self.clock_size.setValue(cfg["clock_size"])
        form.addRow("Time font size:", self.clock_size)

        self.date_font = QFontComboBox()
        self.date_font.setCurrentFont(QFont(cfg["date_font"]))
        form.addRow("Date font:", self.date_font)

        self.date_size = QSpinBox()
        self.date_size.setRange(8, 50)
        self.date_size.setValue(cfg["date_size"])
        form.addRow("Date font size:", self.date_size)

        self.format = QComboBox()
        self.format.addItems(["24-hour", "12-hour"])
        self.format.setCurrentIndex(0 if cfg["hour24"] else 1)
        form.addRow("Time format:", self.format)

        self.seconds = QCheckBox("Show seconds")
        self.seconds.setChecked(cfg["show_seconds"])
        form.addRow("", self.seconds)

        self.date = QCheckBox("Show date")
        self.date.setChecked(cfg["show_date"])
        form.addRow("", self.date)

        time_color = QPushButton("Choose time color")
        time_color.clicked.connect(self.choose_time_color)
        form.addRow("Time color:", time_color)

        date_color = QPushButton("Choose date color")
        date_color.clicked.connect(self.choose_date_color)
        form.addRow("Date color:", date_color)

        bg = QPushButton("Choose background")
        bg.clicked.connect(self.choose_bg)
        form.addRow("Background:", bg)

        self.opacity = QSlider(Qt.Orientation.Horizontal)
        self.opacity.setRange(30, 100)
        self.opacity.setValue(cfg["opacity"])
        form.addRow("Opacity:", self.opacity)

        self.width = QSpinBox()
        self.width.setRange(260, 1000)
        self.width.setValue(cfg["width"])
        form.addRow("Widget width:", self.width)

        self.height = QSpinBox()
        self.height.setRange(150, 600)
        self.height.setValue(cfg["height"])
        form.addRow("Widget height:", self.height)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.apply)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def choose_time_color(self):
        c = QColorDialog.getColor(QColor(cfg["clock_color"]), self)
        if c.isValid():
            cfg["clock_color"] = c.name()

    def choose_date_color(self):
        c = QColorDialog.getColor(QColor(cfg["date_color"]), self)
        if c.isValid():
            cfg["date_color"] = c.name()

    def choose_bg(self):
        c = QColorDialog.getColor(QColor(cfg["background"]), self)
        if c.isValid():
            cfg["background"] = c.name()

    def apply(self):
        cfg["clock_font"] = self.clock_font.currentFont().family()
        cfg["clock_size"] = self.clock_size.value()
        cfg["date_font"] = self.date_font.currentFont().family()
        cfg["date_size"] = self.date_size.value()
        cfg["hour24"] = self.format.currentIndex() == 0
        cfg["show_seconds"] = self.seconds.isChecked()
        cfg["show_date"] = self.date.isChecked()
        cfg["opacity"] = self.opacity.value()
        cfg["width"] = self.width.value()
        cfg["height"] = self.height.value()

        save()
        self.parent.apply_style()
        self.accept()


class Clock(QWidget):
    def __init__(self):
        super().__init__()

        self.drag_offset = QPoint()

        self.setWindowTitle("Clock Pro")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.apply_flags()
        self.build()
        self.apply_style()

        self.move(cfg["x"], cfg["y"])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(250)

        self.tick()

    def apply_flags(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool

        if cfg["topmost"]:
            flags |= Qt.WindowType.WindowStaysOnTopHint

        self.setWindowFlags(flags)

    def build(self):
        self.card = QWidget(self)
        self.card.setObjectName("card")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.card)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(14, 10, 14, 16)

        top = QHBoxLayout()

        self.title = QLabel("CLOCK PRO")
        self.title.setStyleSheet(
            "color:#A9AFB8;font-size:9pt;font-weight:bold;"
        )

        top.addWidget(self.title)
        top.addStretch()

        self.lock_btn = QPushButton()
        self.lock_btn.clicked.connect(self.toggle_lock)

        self.pin_btn = QPushButton()
        self.pin_btn.clicked.connect(self.toggle_pin)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setToolTip("Customize")
        self.settings_btn.clicked.connect(self.open_settings)

        # IMPORTANT: don't call this button "self.close".
        # QWidget already has a close() method.
        self.close_btn = QPushButton("×")
        self.close_btn.clicked.connect(self.close_app)

        for button in (
            self.lock_btn,
            self.pin_btn,
            self.settings_btn,
            self.close_btn
        ):
            button.setFixedSize(38, 32)
            top.addWidget(button)

        layout.addLayout(top)
        layout.addStretch()

        self.time = QLabel()
        self.time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time)

        self.date = QLabel()
        self.date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.date)

        layout.addStretch()

        self.update_buttons()

    def apply_style(self):
        self.resize(cfg["width"], cfg["height"])

        c = QColor(cfg["background"])

        self.card.setStyleSheet(f"""
            QWidget#card {{
                background: rgba(
                    {c.red()},
                    {c.green()},
                    {c.blue()},
                    245
                );
                border: 1px solid #454B55;
                border-radius: 18px;
            }}

            QPushButton {{
                background: #2A2F38;
                color: white;
                border: 0;
                border-radius: 7px;
                font-size: 11pt;
            }}

            QPushButton:hover {{
                background: #3A414C;
            }}
        """)

        self.time.setStyleSheet(
            f"color:{cfg['clock_color']};"
            f"font-family:'{cfg['clock_font']}';"
            f"font-size:{cfg['clock_size']}pt;"
            f"font-weight:bold;"
        )

        self.date.setStyleSheet(
            f"color:{cfg['date_color']};"
            f"font-family:'{cfg['date_font']}';"
            f"font-size:{cfg['date_size']}pt;"
        )

        self.setWindowOpacity(cfg["opacity"] / 100)
        self.date.setVisible(cfg["show_date"])

    def tick(self):
        now = datetime.now()

        if cfg["hour24"]:
            fmt = "%H:%M:%S" if cfg["show_seconds"] else "%H:%M"
        else:
            fmt = "%I:%M:%S %p" if cfg["show_seconds"] else "%I:%M %p"

        self.time.setText(now.strftime(fmt))
        self.date.setText(now.strftime("%A • %d %B %Y"))

    def toggle_lock(self):
        cfg["locked"] = not cfg["locked"]
        save()
        self.update_buttons()

    def toggle_pin(self):
        cfg["topmost"] = not cfg["topmost"]

        # Save the current position before recreating the native window.
        cfg["x"], cfg["y"] = self.x(), self.y()

        self.apply_flags()
        self.show()
        self.move(cfg["x"], cfg["y"])

        save()
        self.update_buttons()

    def update_buttons(self):
        self.lock_btn.setText("🔒" if cfg["locked"] else "🔓")
        self.lock_btn.setToolTip(
            "Unlock position" if cfg["locked"] else "Lock position"
        )

        self.pin_btn.setText("📌" if cfg["topmost"] else "📍")
        self.pin_btn.setToolTip(
            "Disable always on top"
            if cfg["topmost"]
            else "Enable always on top"
        )

    def open_settings(self):
        Settings(self).exec()

    def close_app(self):
        cfg["x"], cfg["y"] = self.x(), self.y()
        save()
        QApplication.quit()

    def mousePressEvent(self, event):
        if (
            not cfg["locked"]
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self.drag_offset = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if (
            not cfg["locked"]
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(
                event.globalPosition().toPoint() - self.drag_offset
            )

            cfg["x"], cfg["y"] = self.x(), self.y()
            event.accept()

    def mouseReleaseEvent(self, event):
        cfg["x"], cfg["y"] = self.x(), self.y()
        save()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    clock = Clock()
    clock.show()
    clock.raise_()

    sys.exit(app.exec())
