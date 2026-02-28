from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.services.mod_installer_service import ModInstallerService
from app.services.profile_service import ProfileService
from app.services.record_service import RecordService
from app.ui.mod_installer_dialog import ModInstallerDialog
from app.ui.record_dialog import RecordDialog
from app.ui.widgets import AnimatedButton


class MainWindow(QMainWindow):
    def __init__(self, username: str, profile_service: ProfileService, parent=None) -> None:
        super().__init__(parent)
        self.username = username
        self.profile_service = profile_service
        self.profile_dir = self.profile_service.base_dir / username
        self.record_service = RecordService(self.profile_dir)
        self.setWindowTitle(f"Minecraft PvP Hub - {username}")
        self.resize(900, 600)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by date/title")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Date (Newest)", "Rating (Highest)"])

        self.latest_list = QListWidget()
        self.all_list = QListWidget()
        self.detail = QTextEdit()
        self.detail.setReadOnly(True)

        add_record = AnimatedButton("New Record")
        more_btn = AnimatedButton("More")
        mod_installer_btn = AnimatedButton("Mod Installer")
        export_btn = AnimatedButton("Export Profile")
        import_btn = AnimatedButton("Import Profile")

        add_record.clicked.connect(self.open_new_record)
        more_btn.clicked.connect(self.refresh_all)
        mod_installer_btn.clicked.connect(self.open_mod_installer)
        export_btn.clicked.connect(self.export_profile)
        import_btn.clicked.connect(self.import_profile)
        self.search_input.textChanged.connect(self.refresh_all)
        self.sort_combo.currentIndexChanged.connect(self.refresh_all)
        self.latest_list.itemClicked.connect(self.show_detail_from_item)
        self.all_list.itemClicked.connect(self.show_detail_from_item)

        top = QHBoxLayout()
        top.addWidget(QLabel("Search"))
        top.addWidget(self.search_input)
        top.addWidget(self.sort_combo)

        button_row = QHBoxLayout()
        for btn in [add_record, more_btn, mod_installer_btn, export_btn, import_btn]:
            button_row.addWidget(btn)

        lists = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel("Latest 3 Records"))
        left.addWidget(self.latest_list)
        left.addWidget(QLabel("All Records"))
        left.addWidget(self.all_list)
        lists.addLayout(left, 2)
        lists.addWidget(self.detail, 3)

        root = QVBoxLayout()
        root.addLayout(top)
        root.addLayout(button_row)
        root.addLayout(lists)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self.refresh_latest()
        self.refresh_all()

    def refresh_latest(self) -> None:
        self.latest_list.clear()
        for record in self.record_service.latest(3):
            item = QListWidgetItem(f"{record.created_at:%Y-%m-%d} | {record.title} | ⭐{record.rating}")
            item.setData(32, record.id)
            self.latest_list.addItem(item)

    def refresh_all(self) -> None:
        query = self.search_input.text().strip()
        self.all_list.clear()
        if query:
            records = self.record_service.search(query)
        else:
            mode = "rating" if self.sort_combo.currentIndex() == 1 else "date"
            records = self.record_service.list_records(mode)

        for record in records:
            item = QListWidgetItem(f"[{record.category.value}] {record.created_at:%Y-%m-%d} - {record.title} (⭐{record.rating})")
            item.setData(32, record.id)
            self.all_list.addItem(item)

    def show_detail_from_item(self, item: QListWidgetItem) -> None:
        record_id = item.data(32)
        record = self.record_service.get_record(record_id)
        if not record:
            self.detail.clear()
            return
        self.detail.setText(
            f"Title: {record.title}\n"
            f"Category: {record.category.value}\n"
            f"Rating: {record.rating}\n"
            f"Date: {record.created_at:%Y-%m-%d %H:%M:%S}\n"
            f"File: {record.storage_filename}\n\n"
            f"{record.content}"
        )

    def open_new_record(self) -> None:
        dialog = RecordDialog(self.record_service, self)
        if dialog.exec():
            self.refresh_latest()
            self.refresh_all()

    def open_mod_installer(self) -> None:
        dialog = ModInstallerDialog(ModInstallerService(), self)
        dialog.exec()

    def export_profile(self) -> None:
        username, ok = QInputDialog.getText(self, "Export", "Username")
        if not ok:
            return
        password, ok = QInputDialog.getText(self, "Export", "Password", QLineEdit.Password)
        if not ok:
            return
        parent = QFileDialog.getExistingDirectory(self, "Select Export Destination")
        if not parent:
            return

        progress = QProgressDialog("Exporting profile...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        def on_progress(current: int, total: int, text: str) -> None:
            if progress.wasCanceled():
                return
            progress.setLabelText(text)
            progress.setValue(int((current / max(1, total)) * 100))

        try:
            path = self.profile_service.export_profile(username.strip(), password, Path(parent), progress=on_progress)
            progress.setValue(100)
            QMessageBox.information(self, "Export", f"Exported to:\n{path}")
        except ValueError as exc:
            QMessageBox.warning(self, "Export Failed", str(exc))

    def import_profile(self) -> None:
        source = QFileDialog.getExistingDirectory(self, "Select Profile Folder to Import")
        if not source:
            return

        progress = QProgressDialog("Importing profile...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)

        def on_progress(current: int, total: int, text: str) -> None:
            if progress.wasCanceled():
                return
            progress.setLabelText(text)
            progress.setValue(int((current / max(1, total)) * 100))

        try:
            username = self.profile_service.import_profile(Path(source), progress=on_progress)
            progress.setValue(100)
            QMessageBox.information(self, "Import", f"Imported profile: {username}")
        except ValueError as exc:
            QMessageBox.warning(self, "Import Failed", str(exc))
