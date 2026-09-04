APP_NAME = "WinClean64"
APP_VERSION = "1.2"
GITHUB_URL = "https://github.com/KIziName/WinClean64"

# Размеры окон
MAIN_WINDOW_WIDTH = 550
MAIN_WINDOW_HEIGHT = 600
ABOUT_WINDOW_WIDTH = 420
ABOUT_WINDOW_HEIGHT = 340

# Шрифты
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_NORMAL = ("Segoe UI", 13)
FONT_BOLD = ("Segoe UI", 14, "bold")
FONT_NOTE = ("Segoe UI", 12, "normal")
FONT_ABOUT_TITLE = ("Segoe UI", 18, "bold")
FONT_ABOUT_NORMAL = ("Segoe UI", 13)
FONT_ABOUT_LINK = ("Segoe UI", 13, "underline")
FONT_LOG = ("Consolas", 11)
FONT_ICON = ("Segoe UI", 45)

# Цвета
COLOR_HEADER_FG = ("gray85", "#212121")
COLOR_ABOUT_BUTTON_FG = ("gray75", "#181818")
COLOR_ABOUT_BUTTON_HOVER = ("gray65", "#252525")
COLOR_STATUS_CARD_FG = ("gray90", "gray11")
COLOR_LOG_TEXTBOX_FG = ("#f3f3f3", "#141414")
COLOR_LOG_TEXTBOX_TEXT = ("#333333", "#aaaaaa")
COLOR_SETTINGS_FRAME_FG = ("gray90", "gray11")
COLOR_ICON_BUTTON_FG = ("gray85", "gray16")
COLOR_ICON_TEXT_DISABLED = ("gray20", "white")
COLOR_SUCCESS = ("#27ae60", "#2ecc71")
COLOR_ERROR = "#e74c3c"
COLOR_IDLE = ("gray50", "gray70")
COLOR_ABOUT_LINK = ("#1f538d", "#1abc9c")
COLOR_ABOUT_TITLE = ("#1f538d", "#3b8ed0")

# Тематические имена
THEME_DARK_NAME = "dark"
THEME_LIGHT_NAME = "light"

# Настройки очистки
TEMP_EXTENSIONS = {'.tmp', '.temp', '.log', '.cache', '.old', '.bak'}
TEMP_PATTERNS = ['~$', '~']

# Локализация
TEXT_DATA = {
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
