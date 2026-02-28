from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.services.bootstrap_service import BootstrapService
from app.services.dependency_service import DependencyService
from app.services.mod_installer_service import ModInstallerService
from app.services.path_service import PathService
from app.services.profile_service import ProfileService


def _load_rich() -> tuple[object, object, object, object, object, object, object]:
    try:
        from rich.console import Console
        from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
        from rich.table import Table
    except ModuleNotFoundError:
        print("Please run: pip install -r requirements.txt")
        raise SystemExit(1)
    return Console, Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, Table


Console, Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, Table = _load_rich()
console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minecraft PvP Hub CLI utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-profiles", help="List local profiles")

    create_user = sub.add_parser("create-user", help="Create a local profile user")
    create_user.add_argument("username", help="New username")
    create_user.add_argument("password", help="New password")

    scan = sub.add_parser("scan-mods", help="Scan files/folders for .jar mods")
    scan.add_argument("paths", nargs="+", help="Files or folders to scan")

    return parser


def list_profiles(service: ProfileService) -> int:
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


def create_user(service: ProfileService, username: str, password: str) -> int:
    try:
        service.create_profile(username, password)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        return 1
    console.print(f"[green]Created user:[/green] {username}")
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
    missing = DependencyService.missing_runtime_modules()
    if missing and not getattr(sys, "frozen", False):
        print("Please run: pip install -r requirements.txt")
        return 1

    BootstrapService.ensure_directories()
    profile_service = ProfileService(PathService.default_app_profiles_dir())
    BootstrapService(profile_service).initialize_database_and_default_user()

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list-profiles":
        return list_profiles(profile_service)
    if args.command == "create-user":
        return create_user(profile_service, args.username, args.password)
    if args.command == "scan-mods":
        return scan_mods(args.paths)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
