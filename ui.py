import sys
import threading
import re
import webbrowser
import customtkinter as ctk
import config as cfg

from cleaner import clean_temp_files_backend

class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent, text_data, github_url, app_name, app_version):
        super().__init__(parent)
        self.title(text_data["about_title"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        width, height = cfg.ABOUT_WINDOW_WIDTH, cfg.ABOUT_WINDOW_HEIGHT
        self.geometry(f"{width}x{height}")

        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.card = ctk.CTkFrame(self, fg_color=("white", "#212121"), corner_radius=12)
        self.card.pack(expand=True, fill="both", padx=15, pady=15)

        self.lbl_title = ctk.CTkLabel(
            self.card, text=app_name.upper(), font=cfg.FONT_ABOUT_TITLE,
            text_color=cfg.COLOR_ABOUT_TITLE
        )
        self.lbl_title.pack(pady=(25, 15))

        self.lbl_author = ctk.CTkLabel(self.card, text=text_data["about_author"], font=cfg.FONT_ABOUT_NORMAL)
        self.lbl_author.pack(pady=2)

        self.lbl_version = ctk.CTkLabel(
            self.card, text=f"{text_data['about_version_prefix']}: {app_version}",
            font=cfg.FONT_ABOUT_NORMAL, text_color="gray"
        )
        self.lbl_version.pack(pady=2)

        self.lbl_desc = ctk.CTkLabel(
            self.card, text=text_data["about_desc"],
            font=cfg.FONT_ABOUT_NORMAL, wraplength=340, justify="center"
        )
        self.lbl_desc.pack(pady=15, padx=20)

        self.lbl_link = ctk.CTkLabel(
            self.card, text="GitHub: KIziName/WinClean64",
            font=cfg.FONT_ABOUT_LINK, text_color=cfg.COLOR_ABOUT_LINK, cursor="hand2"
        )
        self.lbl_link.pack(pady=5)
        self.lbl_link.bind("<Button-1>", lambda e: webbrowser.open(github_url))

        self.close_button = ctk.CTkButton(
            self.card, text=text_data["btn_close"], height=32, width=120,
            font=cfg.FONT_ABOUT_NORMAL, corner_radius=8, command=self.destroy
        )
        self.close_button.pack(side="bottom", pady=20)

class UIManager:
    def __init__(self, app):
        self.app = app
        self.lang = "en"
        
    def get_text(self, key):
        return cfg.TEXT_DATA[self.lang].get(key, "")

    def update_all_texts(self):
        data = cfg.TEXT_DATA[self.lang]

        self.app.main_label.configure(text=data["title"])
        self.app.clean_button.configure(text=data["btn_clean"])
        self.app.about_button.configure(text=data["btn_about"])
        self.app.note_label.configure(text=data["note"])
        self.app.theme_label.configure(text=data["theme_lbl"])

        self.refresh_status()
        current_theme = data["theme_dark"] if ctk.get_appearance_mode() == cfg.THEME_DARK_NAME else data["theme_light"]
        self.app.theme_switch.configure(values=[data["theme_dark"], data["theme_light"]])
        self.app.theme_switch.set(current_theme)

        self.refresh_log()

    def refresh_status(self):
        current_status = self.app.status_label.cget("text")
        data = cfg.TEXT_DATA[self.lang]

        if "Deleted:" in current_status:
            numbers = re.findall(r'\d+', current_status)
            mb_match = re.search(r'(\d+(?:\.\d+)?)\s*MB', current_status)
            if len(numbers) >= 2:
                deleted, skipped = int(numbers[0]), int(numbers[1])
                mb = float(mb_match.group(1)) if mb_match else 0.0
                self.app.status_label.configure(
                    text=data["status_success"].format(deleted, skipped, mb),
                    text_color=cfg.COLOR_SUCCESS
                )
                return
        elif "Error" in current_status:
            self.app.status_label.configure(text="Access Error", text_color=cfg.COLOR_ERROR)
            return

        self.app.status_label.configure(text=data["status_idle"], text_color=cfg.COLOR_IDLE)

    def refresh_log(self):
        log_textbox = self.app.log_textbox
        log_history = self.app.log_history
        log_textbox.configure(state="normal")
        log_textbox.delete("1.0", "end")
        for event_type, value in log_history:
            template = cfg.TEXT_DATA[self.lang].get(event_type, "{}")
            if "{}" in template:
                if isinstance(value, tuple):
                    msg = template.format(*value)
                else:
                    msg = template.format(value)
            else:
                msg = template
            log_textbox.insert("end", msg + "\n")
        log_textbox.see("end")
        log_textbox.configure(state="disabled")

    def add_log(self, event_type, value=""):
        self.app.log_history.append((event_type, value))
        template = cfg.TEXT_DATA[self.lang].get(event_type, "{}")
        if "{}" in template:
            if isinstance(value, tuple):
                msg = template.format(*value)
            else:
                msg = template.format(value)
        else:
            msg = template
        log_textbox = self.app.log_textbox
        log_textbox.configure(state="normal")
        log_textbox.insert("end", msg + "\n")
        log_textbox.see("end")
        log_textbox.configure(state="disabled")

    def change_theme(self, choice):
        data = cfg.TEXT_DATA[self.lang]
        if choice == data["theme_dark"]:
            ctk.set_appearance_mode(cfg.THEME_DARK_NAME)
        elif choice == data["theme_light"]:
            ctk.set_appearance_mode(cfg.THEME_LIGHT_NAME)
        self.update_all_texts()

class CleanupController:
    def __init__(self, app):
        self.app = app
        self.clean_thread = None
        self.is_cleaning = False

    def start_cleanup(self):
        if self.is_cleaning:
            return
        self.is_cleaning = True
        self.app.clean_button.configure(state="disabled", text="Cleaning...")

        self.clean_thread = threading.Thread(
            target=clean_temp_files_backend,
            args=(
                self._on_start,
                self._on_log,
                self._on_success,
                self._on_error,
                self._on_finish
            ),
            daemon=True
        )
        self.clean_thread.start()

    def _on_start(self, path):
        self.app.after(0, lambda: (self.app.log_history.clear(), self.app.ui.add_log("log_start", path)))

    def _on_log(self, event_type, value):
        self.app.after(0, lambda: self.app.ui.add_log(event_type, value))

    def _on_success(self, deleted, skipped, freed_mb):
        self.app.after(0, lambda: self.app.status_label.configure(
            text=cfg.TEXT_DATA[self.app.ui.lang]["status_success"].format(deleted, skipped, freed_mb),
            text_color=cfg.COLOR_SUCCESS
        ))

    def _on_error(self, err_type):
        self.app.after(0, lambda: self.app.status_label.configure(
            text="Error",
            text_color=cfg.COLOR_ERROR
        ))

    def _on_finish(self):
        self.app.after(0, self._finish_cleanup)

    def _finish_cleanup(self):
        self.is_cleaning = False
        self.app.clean_button.configure(state="normal", text=cfg.TEXT_DATA[self.app.ui.lang]["btn_clean"])

def build_ui(app):
    app.header_frame = ctk.CTkFrame(app, fg_color=cfg.COLOR_HEADER_FG, corner_radius=0, height=70)
    app.header_frame.pack(side="top", fill="x")
    app.header_frame.pack_propagate(False)

    app.main_label = ctk.CTkLabel(app.header_frame, text="", font=cfg.FONT_TITLE)
    app.main_label.pack(side="left", padx=25, pady=15)

    app.about_button = ctk.CTkButton(
        app.header_frame, text="", height=28, width=110,
        fg_color=cfg.COLOR_ABOUT_BUTTON_FG, hover_color=cfg.COLOR_ABOUT_BUTTON_HOVER,
        text_color=("black", "white"), font=cfg.FONT_NORMAL,
        corner_radius=6, command=app.open_about_window
    )
    app.about_button.pack(side="right", padx=25, pady=20)

    app.center_frame = ctk.CTkFrame(app, fg_color="transparent")
    app.center_frame.pack(expand=True, fill="both", padx=40, pady=10)

    app.icon_box = ctk.CTkButton(
        app.center_frame, text="🧹", font=cfg.FONT_ICON,
        width=90, height=90, corner_radius=20,
        fg_color=cfg.COLOR_ICON_BUTTON_FG, state="disabled",
        text_color_disabled=cfg.COLOR_ICON_TEXT_DISABLED
    )
    app.icon_box.pack(pady=10)

    app.status_card = ctk.CTkFrame(app.center_frame, fg_color=cfg.COLOR_STATUS_CARD_FG, corner_radius=10, height=40)
    app.status_card.pack(fill="x", pady=5)
    app.status_card.pack_propagate(False)

    app.status_label = ctk.CTkLabel(app.status_card, text="", font=cfg.FONT_NORMAL)
    app.status_label.pack(expand=True)

    app.log_textbox = ctk.CTkTextbox(
        app.center_frame, height=160, corner_radius=10,
        font=cfg.FONT_LOG, fg_color=cfg.COLOR_LOG_TEXTBOX_FG,
        text_color=cfg.COLOR_LOG_TEXTBOX_TEXT, state="disabled"
    )
    app.log_textbox.pack(fill="both", expand=True, pady=10)

    app.clean_button = ctk.CTkButton(
        app.center_frame, text="", height=45, font=cfg.FONT_BOLD,
        corner_radius=10, command=app.start_clean_thread
    )
    app.clean_button.pack(fill="x", pady=10)

    app.note_label = ctk.CTkLabel(
        app.center_frame, text="", font=cfg.FONT_NOTE,
        text_color=cfg.COLOR_IDLE, wraplength=480, justify="center"
    )
    app.note_label.pack(pady=8)

    app.settings_frame = ctk.CTkFrame(app, fg_color=cfg.COLOR_SETTINGS_FRAME_FG, corner_radius=0, height=55)
    app.settings_frame.pack(side="bottom", fill="x")

    app.theme_label = ctk.CTkLabel(app.settings_frame, text="", font=cfg.FONT_NORMAL)
    app.theme_label.pack(side="left", padx=(25, 5), pady=15)

    app.theme_switch = ctk.CTkComboBox(
        app.settings_frame, width=110, font=cfg.FONT_NORMAL,
        corner_radius=6, values=[], command=app.ui.change_theme
    )
    app.theme_switch.pack(side="left", padx=5, pady=15)

class WinClean64App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.APP_NAME = cfg.APP_NAME
        self.APP_VERSION = cfg.APP_VERSION
        self.github_url = cfg.GITHUB_URL

        self.title(cfg.APP_NAME)
        self.geometry(f"{cfg.MAIN_WINDOW_WIDTH}x{cfg.MAIN_WINDOW_HEIGHT}")
        self.resizable(False, False)

        for i in range(100):
            color_name = f"gray{i:02d}"
            hex_val = f"#{int(i * 2.55):02x}{int(i * 2.55):02x}{int(i * 2.55):02x}"
            self.option_add(f"*{color_name}", hex_val)

        ctk.set_appearance_mode(cfg.THEME_DARK_NAME)
        ctk.set_default_color_theme("blue")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.log_history = []
        self.clean_thread = None
        self.is_cleaning = False

        self.ui = UIManager(self)
        self.cleanup = CleanupController(self)

        build_ui(self)
        self.ui.update_all_texts()

    def open_about_window(self):
        AboutWindow(self, cfg.TEXT_DATA[self.ui.lang], self.github_url, self.APP_NAME, self.APP_VERSION)

    def start_clean_thread(self):
        self.cleanup.start_cleanup()

    def on_closing(self):
        self.destroy()
        sys.exit(0)
