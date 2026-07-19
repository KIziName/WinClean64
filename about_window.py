import webbrowser
import customtkinter as ctk

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
