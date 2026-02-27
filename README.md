# Minecraft PvP Desktop Hub (PySide6)

A production-ready local desktop app with clean architecture for:

- Local profile login (bcrypt password hashing)
- PvP record management with SQLite
- Profile export/import validation
- Minecraft mod installer with append/overwrite modes

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
  main.py
requirements.txt
```

## Run

1. Create virtual environment (recommended)
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start app:

```bash
python -m app.main
```

## Notes

- Profiles are stored under `local_data/profiles/<username>/`
- Each profile includes:
  - `credentials.json` (username + bcrypt hash)
  - `records.db` (SQLite records DB)
  - `record_contents/` text files with timestamped filenames
- Windows default `.minecraft` path is prefilled as `%USERPROFILE%\\AppData\\Roaming\\.minecraft`
