import os
import tempfile
import threading
from pathlib import Path

def clean_temp_files_backend(on_start, on_log, on_success, on_error, on_finish):
    """
    Выполняет очистку папки Temp.
    Принимает колбэки для синхронизации с GUI.
    """
    try:
        base_temp_dir = Path(tempfile.gettempdir()).resolve()
        deleted_objects = 0
        skipped_objects = 0
        deleted_bytes = 0

        on_start(str(base_temp_dir))

        if not os.access(base_temp_dir, os.R_OK):
            on_log("log_error_access", "Нет прав на чтение")
            on_error("access_error")
            return

        temp_extensions = {'.tmp', '.temp', '.log', '.cache', '.old', '.bak'}
        temp_patterns = ['~$', '~']

        try:
            items = list(base_temp_dir.iterdir())
        except Exception as e:
            on_log("log_error_access", str(e))
            on_error("access_error")
            return

        for item in items:
            try:
                real_path = item.resolve(strict=True)
                if not real_path.is_relative_to(base_temp_dir):
                    skipped_objects += 1
                    continue

                if real_path.is_file() or real_path.is_symlink():
                    name = real_path.name.lower()
                    is_temp = (real_path.suffix.lower() in temp_extensions or
                               any(name.startswith(p) for p in temp_patterns))
                    if not is_temp:
                        skipped_objects += 1
                        continue

                    file_size = real_path.stat().st_size
                    real_path.unlink()
                    deleted_objects += 1
                    deleted_bytes += file_size
                    on_log("log_file_del", real_path.name)

                elif real_path.is_dir():
                    try:
                        if not any(real_path.iterdir()):
                            real_path.rmdir()
                            deleted_objects += 1
                            on_log("log_dir_del", real_path.name)
                        else:
                            skipped_objects += 1
                    except OSError:
                        skipped_objects += 1
            except Exception:
                skipped_objects += 1

        freed_mb = deleted_bytes / (1024 * 1024)
        on_success(deleted_objects, skipped_objects, freed_mb)
        on_log("log_finish", (deleted_objects, skipped_objects, freed_mb))
        
    except Exception as e:
        on_log("log_error_access", str(e))
        on_error("critical_error")
    finally:
        on_finish()
