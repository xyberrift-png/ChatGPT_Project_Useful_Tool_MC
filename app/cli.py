from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from app.services.mod_installer_service import ModInstallerService
from app.services.path_service import PathService
from app.services.profile_service import ProfileService

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minecraft PvP Hub CLI utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-profiles", help="List local profiles")

    scan = sub.add_parser("scan-mods", help="Scan files/folders for .jar mods")
    scan.add_argument("paths", nargs="+", help="Files or folders to scan")

    return parser


def list_profiles() -> int:
    service = ProfileService(PathService.default_app_profiles_dir())
    profiles = service.list_profiles()

    table = Table(title="Local Profiles")
    table.add_column("#", justify="right")
    table.add_column("Username")
    for idx, profile in enumerate(profiles, start=1):
        table.add_row(str(idx), profile)

    if not profiles:
        console.print("[yellow]No profiles found.[/yellow]")
    else:
        console.print(table)
    return 0


def scan_mods(raw_paths: list[str]) -> int:
    service = ModInstallerService()
    selections = [Path(p) for p in raw_paths]

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )
    task_id = progress.add_task("Scanning", total=100)

    def on_progress(current: int, total: int, text: str) -> None:
        percent = int((current / max(1, total)) * 100)
        progress.update(task_id, completed=percent, description=text)

    with progress:
        files = service.collect_mod_files(selections, progress=on_progress)

    table = Table(title="Detected Mod Files")
    table.add_column("Name")
    table.add_column("Path")
    for file in files:
        table.add_row(file.name, str(file))

    console.print(table)
    console.print(f"[green]Total mods:[/green] {len(files)}")
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list-profiles":
        return list_profiles()
    if args.command == "scan-mods":
        return scan_mods(args.paths)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
