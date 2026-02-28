from __future__ import annotations

from PySide6.QtCore import QEasingCurve, Property, QPropertyAnimation, QSize
from PySide6.QtWidgets import QPushButton


class AnimatedButton(QPushButton):
    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self._scale = 1.0
        self._anim = QPropertyAnimation(self, b"scale")
        self._anim.setDuration(120)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event) -> None:  # noqa: N802
        self._animate_to(1.03)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self._animate_to(1.0)
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        self._animate_to(0.97)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._animate_to(1.03)
        super().mouseReleaseEvent(event)

    def _animate_to(self, value: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._scale)
        self._anim.setEndValue(value)
        self._anim.start()

    def get_scale(self) -> float:
        return self._scale

    def set_scale(self, value: float) -> None:
        self._scale = value
        base_size = QSize(120, 36)
        self.setMinimumSize(base_size * value)

    scale = Property(float, get_scale, set_scale)
