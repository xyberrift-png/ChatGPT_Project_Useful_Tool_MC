from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QRadioButton,
    QVBoxLayout,
    QDialog,
)

from app.services.mod_installer_service import ModInstallerService
from app.ui.widgets import AnimatedButton


class ModInstallerDialog(QDialog):
    def __init__(self, service: ModInstallerService, parent=None) -> None:
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Minecraft Mod Installer")
        self.resize(560, 420)

        self.selected_paths: list[Path] = []

        self.minecraft_dir = QLineEdit(str(self.service.default_minecraft_dir()))
        self.file_list = QListWidget()
        self.append_mode = QRadioButton("Append")
        self.overwrite_mode = QRadioButton("Overwrite")
        self.append_mode.setChecked(True)

        browse_mc = AnimatedButton("Browse .minecraft")
        browse_items = AnimatedButton("Select .jar files/folders")
        install_btn = AnimatedButton("Install")

        browse_mc.clicked.connect(self.browse_minecraft_dir)
        browse_items.clicked.connect(self.browse_mod_items)
        install_btn.clicked.connect(self.install)

        top = QHBoxLayout()
        top.addWidget(QLabel("Minecraft Dir"))
        top.addWidget(self.minecraft_dir)
        top.addWidget(browse_mc)

        root = QVBoxLayout()
        root.addLayout(top)
        root.addWidget(browse_items)
        root.addWidget(self.file_list)
        root.addWidget(self.append_mode)
        root.addWidget(self.overwrite_mode)
        root.addWidget(install_btn)
        self.setLayout(root)

    def browse_minecraft_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select .minecraft directory")
        if directory:
            self.minecraft_dir.setText(directory)

    def browse_mod_items(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Select Jar Files", filter="Jar files (*.jar)")
        folder = QFileDialog.getExistingDirectory(self, "Select Modpack Folder (optional)")
        selections = [Path(f) for f in files]
        if folder:
            selections.append(Path(folder))
        self.selected_paths = self.service.collect_mod_files(selections)
        self.file_list.clear()
        self.file_list.addItems([str(p) for p in self.selected_paths])

    def install(self) -> None:
        if not self.selected_paths:
            QMessageBox.warning(self, "Installer", "No compatible .jar files selected.")
            return
        minecraft_dir = Path(self.minecraft_dir.text().strip())
        mode = "overwrite" if self.overwrite_mode.isChecked() else "append"

        if mode == "overwrite":
            deletions = self.service.files_to_delete_on_overwrite(minecraft_dir)
            text = "Files to delete:\n" + "\n".join(deletions or ["(none)"])
            response = QMessageBox.warning(
                self,
                "Overwrite Warning",
                text,
                QMessageBox.Ok | QMessageBox.Cancel,
            )
            if response != QMessageBox.Ok:
                return

        replace = QMessageBox.question(
            self,
            "Duplicate Handling",
            "If duplicate filenames are found, replace existing files?",
            QMessageBox.Yes | QMessageBox.No,
        )
        replace_duplicates = replace == QMessageBox.Yes
        installed = self.service.install(self.selected_paths, minecraft_dir, mode, replace_duplicates)
        QMessageBox.information(self, "Install Complete", f"Installed {len(installed)} mods.")
        self.accept()
