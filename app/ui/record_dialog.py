from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDialog, QFormLayout, QLineEdit, QMessageBox, QSpinBox, QTextEdit, QVBoxLayout

from app.models.record import RecordCategory
from app.services.record_service import RecordService
from app.ui.widgets import AnimatedButton


class RecordDialog(QDialog):
    def __init__(self, record_service: RecordService, parent=None) -> None:
        super().__init__(parent)
        self.record_service = record_service
        self.setWindowTitle("Create PvP Record")
        self.setMinimumWidth(460)

        self.title_input = QLineEdit()
        self.rating = QSpinBox()
        self.rating.setRange(0, 100)
        self.category = QComboBox()
        for item in RecordCategory:
            self.category.addItem(item.value)
        self.content = QTextEdit()

        submit = AnimatedButton("Save")
        submit.clicked.connect(self.save_record)

        form = QFormLayout()
        form.addRow("Title (optional)", self.title_input)
        form.addRow("Category", self.category)
        form.addRow("Rating", self.rating)
        form.addRow("Content", self.content)

        root = QVBoxLayout()
        root.addLayout(form)
        root.addWidget(submit)
        self.setLayout(root)

    def save_record(self) -> None:
        content = self.content.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Validation", "Content is required.")
            return
        category = RecordCategory(self.category.currentText())
        self.record_service.create_record(
            category=category,
            rating=int(self.rating.value()),
            content=content,
            title=self.title_input.text(),
        )
        self.accept()
