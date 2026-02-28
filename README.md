# Minecraft PvP Desktop Hub (PySide6)

A production-ready local desktop app with clean architecture for:

- Local profile login (bcrypt password hashing)
- PvP record management with SQLite
- Profile export/import validation
- Minecraft mod installer with append/overwrite modes
- Rich CLI utilities with progress indicators

## Project Structure

```text
app/
  data/
    db.py
    record_repository.py
  models/
    record.py
  services/
    security.py
    path_service.py
    profile_service.py
    record_service.py
    mod_installer_service.py
  ui/
    theme.py
    widgets.py
    login_dialog.py
    record_dialog.py
    mod_installer_dialog.py
    main_window.py
  cli.py
  main.py
requirements.txt
```

## Run (Desktop)

1. Create virtual environment (recommended)
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start app:

```bash
python -m app.main
```

## Run (CLI)

```bash
python -m app.cli list-profiles
python -m app.cli scan-mods "C:\\mods" "C:\\Downloads\\some_mod.jar"
```

## Notes

- Profiles are stored under `%APPDATA%\\MinecraftPvPHub\\profiles` on Windows.
- If `%APPDATA%` is unavailable, storage falls back to `local_data/profiles/<username>/`.
- Each profile includes:
  - `credentials.json` (username + bcrypt hash)
  - `records.db` (SQLite records DB)
  - `record_contents/` text files with timestamped filenames
- Windows default `.minecraft` path is prefilled as `%APPDATA%\\.minecraft`.
- Import/export and mod scanning/installing now show progress indicators.
