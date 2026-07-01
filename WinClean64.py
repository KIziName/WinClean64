# ==================== УНИВЕРСАЛЬНЫЙ GLOBAL МЬЮТЕКС ====================
import sys
import ctypes
import atexit
import os 

def _init_system_wide_mutex():
    kernel32 = ctypes.windll.kernel32
    clean_name = os.path.basename(sys.argv[0]).replace('.', '_').replace(' ', '_')
    mutex_name = f"Global\\AutoGuard_{clean_name}_Mutex"
    mutex_handle = kernel32.CreateMutexW(None, False, mutex_name)
    
    if kernel32.GetLastError() == 183:
        if mutex_handle:
            kernel32.CloseHandle(mutex_handle)
            
        try:
            is_russian = ctypes.windll.kernel32.GetUserDefaultUILanguage() == 1049
        except Exception:
            is_russian = True
            
        if is_russian:
            msg = "Приложение уже запущено!\nРазрешена только одна активная копия."
            title = "Защита от повторного запуска"
        else:
            msg = "The application is already running!\nOnly one active instance is allowed."
            title = "Already Running"
            
        ctypes.windll.user32.MessageBoxW(0, msg, title, 0x10 | 0x00)
        sys.exit(0)
        
    atexit.register(lambda: kernel32.CloseHandle(mutex_handle) if mutex_handle else None)

_init_system_wide_mutex()
# ======================================================================

import shutil
import tempfile
import webbrowser
import threading
from pathlib import Path
import tkinter as tk
import customtkinter as ctk

# Фикс отсутствия sys.stdin при --noconsole
if sys.stdin is None:
    class DummyStream:
        def read(self, *args, **kwargs):
            return ""
        def readline(self, *args, **kwargs):
            return ""
        def write(self, *args, **kwargs):
            pass
        def flush(self):
            pass
    sys.stdin = DummyStream()


class AboutWindow(ctk.CTkToplevel):
    """Окно 'О программе' с центрированием относительно родителя"""
    def __init__(self, parent, text_data, github_url, app_name, app_version):
        super().__init__(parent)
        self.title(text_data["about_title"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        width, height = 420, 340
        self.geometry(f"{width}x{height}")

        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        font_title = ("Segoe UI", 18, "bold")
        font_normal = ("Segoe UI", 13)
        font_link = ("Segoe UI", 13, "underline")

        self.card = ctk.CTkFrame(self, fg_color=("white", "#212121"), corner_radius=12)
        self.card.pack(expand=True, fill="both", padx=15, pady=15)

        self.lbl_title = ctk.CTkLabel(
            self.card, text=app_name.upper(), font=font_title,
            text_color=("#1f538d", "#3b8ed0")
        )
        self.lbl_title.pack(pady=(25, 15))

        self.lbl_author = ctk.CTkLabel(self.card, text=text_data["about_author"], font=font_normal)
        self.lbl_author.pack(pady=2)

        self.lbl_version = ctk.CTkLabel(
            self.card, text=f"{text_data['about_version_prefix']}: {app_version}",
            font=font_normal, text_color="gray"
        )
        self.lbl_version.pack(pady=2)

        self.lbl_desc = ctk.CTkLabel(
            self.card, text=text_data["about_desc"],
            font=font_normal, wraplength=340, justify="center"
        )
        self.lbl_desc.pack(pady=15, padx=20)

        self.lbl_link = ctk.CTkLabel(
            self.card, text="GitHub: KIziName/WinClean64",
            font=font_link, text_color=("#1f538d", "#1abc9c"), cursor="hand2"
        )
        self.lbl_link.pack(pady=5)
        self.lbl_link.bind("<Button-1>", lambda e: webbrowser.open(github_url))

        self.close_button = ctk.CTkButton(
            self.card, text=text_data["btn_close"], height=32, width=120,
            font=font_normal, corner_radius=8, command=self.destroy
        )
        self.close_button.pack(side="bottom", pady=20)


class WinClean64App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.APP_NAME = "WinClean64"
        self.APP_VERSION = "1.2"   # можно сменить на 1.3

        self.title(f"{self.APP_NAME} - {self.APP_VERSION}")
        self.geometry("550x600")
        self.resizable(False, False)
        self.current_lang = "ru"
        self.github_url = "https://github.com/KIziName/WinClean64"

        for i in range(100):
            color_name = f"gray{i:02d}"
            hex_val = f"#{int(i * 2.55):02x}{int(i * 2.55):02x}{int(i * 2.55):02x}"
            self.option_add(f"*{color_name}", hex_val)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.log_history = []
        self.clean_thread = None
        self.is_cleaning = False

        self.font_title = ("Segoe UI", 20, "bold")
        self.font_normal = ("Segoe UI", 13)
        self.font_bold = ("Segoe UI", 14, "bold")
        self.font_note = ("Segoe UI", 12, "normal")

        self.text_data = {
            "ru": {
                "title": "Очистка TEMP файлов",
                "btn_clean": "Очистить систему",
                "btn_about": "О программе",
                "btn_close": "Закрыть",
                "note": " Очистка безопасна и не затронет системные файлы Windows",
                "theme_lbl": "Тема:",
                "lang_lbl": "Язык:",
                "theme_dark": "Тёмная",
                "theme_light": "Светлая",
                "status_idle": "Система готова к анализу",
                "status_success": "Очистка завершена! Удалено: {}, Пропущено: {}, Освобождено: {:.2f} МБ",
                "about_title": "О программе",
                "about_author": "Автор: KiziName",
                "about_version_prefix": "Версия",
                "about_desc": "Современная утилита для безопасной очистки временных компонентов в Windows.",
                "log_start": "[СТАРТ] Анализ директории: {}",
                "log_error_access": "[ОШИБКА] Не удалось прочитать папку Temp: {}",
                "log_file_del": "[ФАЙЛ] Удален: {}",
                "log_dir_del": "[ПАПКА] Удалена пустая папка: {}",
                "log_finish": "\n[ФИНИШ] Очистка завершена. Удалено: {}, Пропущено: {}, Освобождено: {:.2f} МБ"
            },
            "en": {
                "title": "TEMP Files Cleaner",
                "btn_clean": "Clean System",
                "btn_about": "About",
                "btn_close": "Close",
                "note": " Cleaning is safe and will not affect Windows system files",
                "theme_lbl": "Theme:",
                "lang_lbl": "Language:",
                "theme_dark": "Dark",
                "theme_light": "Light",
                "status_idle": "System ready to clean",
                "status_success": "Cleaning finished! Deleted: {}, Skipped: {}, Freed: {:.2f} MB",
                "about_title": "About",
                "about_author": "Author: KiziName",
                "about_version_prefix": "Version",
                "about_desc": "Modern utility for safe cleaning of temporary components in Windows.",
                "log_start": "[START] Analyzing directory: {}",
                "log_error_access": "[ERROR] Could not read Temp folder: {}",
                "log_file_del": "[FILE] Deleted: {}",
                "log_dir_del": "[FOLDER] Deleted empty folder: {}",
                "log_finish": "\n[FINISH] Cleaning finished. Deleted: {}, Skipped: {}, Freed: {:.2f} MB"
            }
        }

        self.init_ui()
        self.update_interface_text()

    def init_ui(self):
        self.header_frame = ctk.CTkFrame(self, fg_color=("gray85", "#212121"), corner_radius=0, height=70)
        self.header_frame.pack(side="top", fill="x")
        self.header_frame.pack_propagate(False)

        self.main_label = ctk.CTkLabel(self.header_frame, text="", font=self.font_title)
        self.main_label.pack(side="left", padx=25, pady=15)

        self.about_button = ctk.CTkButton(
            self.header_frame, text="", height=28, width=110,
            fg_color=("gray75", "#181818"), hover_color=("gray65", "#252525"),
            text_color=("black", "white"), font=self.font_normal,
            corner_radius=6, command=self.open_about_window
        )
        self.about_button.pack(side="right", padx=25, pady=20)

        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.pack(expand=True, fill="both", padx=40, pady=10)

        self.icon_box = ctk.CTkButton(
            self.center_frame, text="🧹", font=("Segoe UI", 45),
            width=90, height=90, corner_radius=20,
            fg_color=("gray85", "gray16"), state="disabled",
            text_color_disabled=("gray20", "white")
        )
        self.icon_box.pack(pady=10)

        self.status_card = ctk.CTkFrame(self.center_frame, fg_color=("gray90", "gray11"), corner_radius=10, height=40)
        self.status_card.pack(fill="x", pady=5)
        self.status_card.pack_propagate(False)

        self.status_label = ctk.CTkLabel(self.status_card, text="", font=self.font_normal)
        self.status_label.pack(expand=True)

        self.log_textbox = ctk.CTkTextbox(
            self.center_frame, height=160, corner_radius=10,
            font=("Consolas", 11), fg_color=("#f3f3f3", "#141414"),
            text_color=("#333333", "#aaaaaa"), state="disabled"
        )
        self.log_textbox.pack(fill="both", expand=True, pady=10)

        self.clean_button = ctk.CTkButton(
            self.center_frame, text="", height=45, font=self.font_bold,
            corner_radius=10, command=self.start_clean_thread
        )
        self.clean_button.pack(fill="x", pady=10)

        self.note_label = ctk.CTkLabel(
            self.center_frame, text="", font=self.font_note,
            text_color=("gray40", "gray70"), wraplength=480, justify="center"
        )
        self.note_label.pack(pady=8)

        self.settings_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray11"), corner_radius=0, height=55)
        self.settings_frame.pack(side="bottom", fill="x")

        self.theme_label = ctk.CTkLabel(self.settings_frame, text="", font=self.font_normal)
        self.theme_label.pack(side="left", padx=(25, 5), pady=15)

        self.theme_switch = ctk.CTkComboBox(
            self.settings_frame, width=110, font=self.font_normal,
            corner_radius=6, values=[], command=self.change_theme
        )
        self.theme_switch.pack(side="left", padx=5, pady=15)

        self.lang_switch = ctk.CTkComboBox(
            self.settings_frame, width=80, font=self.font_normal,
            corner_radius=6, values=["RU", "EN"], command=self.change_language
        )
        self.lang_switch.pack(side="right", padx=25, pady=15)

        self.lang_label = ctk.CTkLabel(self.settings_frame, text="", font=self.font_normal)
        self.lang_label.pack(side="right", padx=5, pady=15)

    def update_interface_text(self):
        lang = self.current_lang
        data = self.text_data[lang]

        self.main_label.configure(text=data["title"])
        self.clean_button.configure(text=data["btn_clean"])
        self.about_button.configure(text=data["btn_about"])
        self.note_label.configure(text=data["note"])
        self.theme_label.configure(text=data["theme_lbl"])
        self.lang_label.configure(text=data["lang_lbl"])

        current_status = self.status_label.cget("text")
        import re
        if "Удалено:" in current_status or "Deleted:" in current_status:
            numbers = re.findall(r'\d+', current_status)
            # Ищем также число с плавающей точкой для MB
            mb_match = re.search(r'(\d+(?:\.\d+)?)\s*МБ', current_status) or re.search(r'(\d+(?:\.\d+)?)\s*MB', current_status)
            if len(numbers) >= 2:
                deleted = numbers[0]
                skipped = numbers[1]
                mb = float(mb_match.group(1)) if mb_match else 0.0
                self.status_label.configure(
                    text=data["status_success"].format(int(deleted), int(skipped), mb),
                    text_color=("#27ae60", "#2ecc71")
                )
            else:
                self.status_label.configure(text=data["status_idle"], text_color=("gray50", "gray70"))
        elif "Ошибка" in current_status or "Error" in current_status:
            self.status_label.configure(text="Ошибка" if lang == "ru" else "Error", text_color="#e74c3c")
        else:
            self.status_label.configure(text=data["status_idle"], text_color=("gray50", "gray70"))

        current_theme = data["theme_dark"] if ctk.get_appearance_mode() == "Dark" else data["theme_light"]
        self.theme_switch.configure(values=[data["theme_dark"], data["theme_light"]])
        self.theme_switch.set(current_theme)

        self.refresh_log_display()

    def change_theme(self, choice):
        lang = self.current_lang
        data = self.text_data[lang]
        if choice == data["theme_dark"]:
            ctk.set_appearance_mode("dark")
        elif choice == data["theme_light"]:
            ctk.set_appearance_mode("light")
        self.update_interface_text()

    def change_language(self, choice):
        self.current_lang = choice.lower()
        self.update_interface_text()

    def open_about_window(self):
        AboutWindow(self, self.text_data[self.current_lang], self.github_url, self.APP_NAME, self.APP_VERSION)

    def add_to_log(self, event_type, value=""):
        self.log_history.append((event_type, value))
        lang = self.current_lang
        text_template = self.text_data[lang].get(event_type, "{}")
        if "{}" in text_template:
            # Для log_finish value может быть кортежем (deleted, skipped, mb)
            if isinstance(value, tuple):
                formatted_msg = text_template.format(*value)
            else:
                formatted_msg = text_template.format(value)
        else:
            formatted_msg = text_template
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", formatted_msg + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def refresh_log_display(self):
        lang = self.current_lang
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        for event_type, value in self.log_history:
            text_template = self.text_data[lang].get(event_type, "{}")
            if "{}" in text_template:
                if isinstance(value, tuple):
                    formatted_msg = text_template.format(*value)
                else:
                    formatted_msg = text_template.format(value)
            else:
                formatted_msg = text_template
            self.log_textbox.insert("end", formatted_msg + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def start_clean_thread(self):
        if self.is_cleaning:
            return
        self.is_cleaning = True
        self.clean_button.configure(state="disabled", text="Очистка...")
        self.clean_thread = threading.Thread(target=self.clean_temp_files, daemon=True)
        self.clean_thread.start()

    def clean_temp_files(self):
        try:
            lang = self.current_lang
            data = self.text_data[lang]

            base_temp_dir = Path(tempfile.gettempdir()).resolve()
            deleted_objects = 0
            skipped_objects = 0
            deleted_bytes = 0   # <-- новый счётчик байт

            self.after(0, lambda: self.log_history.clear())
            self.after(0, lambda: self.add_to_log("log_start", str(base_temp_dir)))

            if not os.access(base_temp_dir, os.R_OK):
                self.after(0, lambda: self.add_to_log("log_error_access", "Нет прав на чтение"))
                self.after(0, lambda: self.status_label.configure(text="Ошибка доступа", text_color="#e74c3c"))
                return

            temp_extensions = {'.tmp', '.temp', '.log', '.cache', '.old', '.bak'}
            temp_patterns = ['~$', '~']

            try:
                items = list(base_temp_dir.iterdir())
            except Exception as e:
                self.after(0, lambda: self.add_to_log("log_error_access", str(e)))
                self.after(0, lambda: self.status_label.configure(text="Ошибка доступа", text_color="#e74c3c"))
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

                        # Получаем размер до удаления
                        file_size = real_path.stat().st_size
                        real_path.unlink()
                        deleted_objects += 1
                        deleted_bytes += file_size
                        self.after(0, lambda n=real_path.name: self.add_to_log("log_file_del", n))

                    elif real_path.is_dir():
                        try:
                            if not any(real_path.iterdir()):
                                real_path.rmdir()
                                deleted_objects += 1
                                # Размер пустой папки = 0, ничего не добавляем
                                self.after(0, lambda n=real_path.name: self.add_to_log("log_dir_del", n))
                            else:
                                skipped_objects += 1
                        except OSError:
                            skipped_objects += 1
                except Exception:
                    skipped_objects += 1

            freed_mb = deleted_bytes / (1024 * 1024)
            success_text = data["status_success"].format(deleted_objects, skipped_objects, freed_mb)
            self.after(0, lambda: self.status_label.configure(text=success_text, text_color=("#27ae60", "#2ecc71")))
            self.after(0, lambda: self.add_to_log("log_finish", (deleted_objects, skipped_objects, freed_mb)))
        except Exception as e:
            self.after(0, lambda: self.add_to_log("log_error_access", str(e)))
            self.after(0, lambda: self.status_label.configure(text="Критическая ошибка", text_color="#e74c3c"))
        finally:
            self.after(0, self._finish_cleanup)

    def _finish_cleanup(self):
        self.is_cleaning = False
        self.clean_button.configure(state="normal", text=self.text_data[self.current_lang]["btn_clean"])

    def on_closing(self):
        self.destroy()
        
        sys.exit(0)


if __name__ == "__main__":
    app = WinClean64App()
    app.mainloop()
