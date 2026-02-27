from __future__ import annotations

import shutil
from pathlib import Path


class ModInstallerService:
    @staticmethod
    def default_minecraft_dir() -> Path:
        return Path.home() / "AppData" / "Roaming" / ".minecraft"

    @staticmethod
    def collect_mod_files(selection: list[Path]) -> list[Path]:
        mod_files: list[Path] = []
        for item in selection:
            if item.is_file() and item.suffix.lower() == ".jar":
                mod_files.append(item)
            elif item.is_dir():
                mod_files.extend([p for p in item.glob("*.jar") if p.is_file()])
        return mod_files

    def install(self, selected_files: list[Path], minecraft_dir: Path, mode: str, replace_duplicates: bool) -> list[str]:
        mods_dir = minecraft_dir / "mods"
        mods_dir.mkdir(parents=True, exist_ok=True)
        installed: list[str] = []

        if mode == "overwrite":
            for existing in mods_dir.glob("*.jar"):
                existing.unlink()

        for source in selected_files:
            target = mods_dir / source.name
            if target.exists():
                if replace_duplicates:
                    target.unlink()
                else:
                    continue
            shutil.copy2(source, target)
            installed.append(source.name)

        return installed

    @staticmethod
    def files_to_delete_on_overwrite(minecraft_dir: Path) -> list[str]:
        mods_dir = minecraft_dir / "mods"
        if not mods_dir.exists():
            return []
        return sorted([p.name for p in mods_dir.glob("*.jar")])
