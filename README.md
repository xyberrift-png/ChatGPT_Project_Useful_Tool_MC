# Minecraft PvP Desktop Hub (PySide6)

A local desktop app with clean architecture for:

- Profile login (bcrypt password hashing)
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
    bootstrap_service.py
    dependency_service.py
    log_service.py
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

## First-Run Bootstrap

On first run, the app automatically:

- creates required folders under app root (`data/`, `data/profiles/`, `logs/`)
- initializes SQLite DB files as needed
- creates default user:
  - username: `admin`
  - password: `admin`

## Run (Desktop)

```bash
python -m app.main
```

## Run (CLI)

```bash
python -m app.cli list-profiles
python -m app.cli create-user myuser mypassword
python -m app.cli scan-mods "C:\\mods" "C:\\Downloads\\some_mod.jar"
```

## Logging & Error Handling

- Log file: `logs/app.log`
- Logged events include startup, DB initialization, login events, and unhandled crashes.
- Unhandled exceptions are logged with full traceback and shown in a GUI error dialog.

## Packaging

Path resolution is compatible with both:

- normal Python execution
- PyInstaller frozen execution

via `PathService.get_app_root()`.
