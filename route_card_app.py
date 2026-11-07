"""Route Card Tool App: turn a Primary/Alternate KML pair into a printable sheet
of per-team-member route cards."""
import os
import sys

import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui_helpers import (  # noqa: E402
    BUTTON_FONT, LABEL_FONT, TITLE_FONT, SUBTITLE_FONT,
    make_drop_list, make_sidebar_button, show_status,
)

import route_card_excel

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk, TkinterDnD.DnDWrapper):
    """Main application window with drag-and-drop support."""

    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Route Card Tool")
        self.geometry("760x640")

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.sidebar, text="Route Card Tool", font=TITLE_FONT).pack(pady=(20, 30))

        tabs = [
            ("Home", self.show_home),
            ("Generate Route Cards", self.show_generate),
        ]
        for name, command in tabs:
            btn = make_sidebar_button(self.sidebar, name, command)
            btn.pack(fill="x", padx=15, pady=6)

        self.show_home()

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ---------- Home ----------
    def show_home(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Welcome to Route Card Tool", font=TITLE_FONT).pack(
            pady=(20, 10))
        ctk.CTkLabel(
            self.main_frame,
            text="Choose an option from the menu on the left to get started.",
            font=SUBTITLE_FONT,
        ).pack(pady=(0, 20))
        ctk.CTkLabel(
            self.main_frame,
            text="• Generate Route Cards — drop a Primary and Alternate KML "
                 "(exported from WinTAK) and build a printable sheet of route "
                 "cards, one per team member",
            font=LABEL_FONT, justify="left",
        ).pack(pady=10, padx=20, anchor="w")

    # ---------- Generate Route Cards ----------
    def show_generate(self):
        self.clear_main()
        ctk.CTkLabel(self.main_frame, text="Generate Route Cards", font=TITLE_FONT).pack(
            pady=(10, 5))

        lists_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        lists_frame.pack(fill="both", expand=True)
        lists_frame.grid_columnconfigure(0, weight=1)
        lists_frame.grid_columnconfigure(1, weight=1)

        primary_col = ctk.CTkFrame(lists_frame, fg_color="transparent")
        primary_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(primary_col, text="Primary Route KML", font=SUBTITLE_FONT).pack(anchor="w")
        primary_list = make_drop_list(self, primary_col, "KML", (".kml",))

        alt_col = ctk.CTkFrame(lists_frame, fg_color="transparent")
        alt_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(alt_col, text="Alternate Route KML", font=SUBTITLE_FONT).pack(anchor="w")
        alt_list = make_drop_list(self, alt_col, "KML", (".kml",))

        options = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        options.pack(pady=(5, 10))
        ctk.CTkLabel(options, text="Team Size", font=LABEL_FONT).grid(row=0, column=0, padx=5)
        team_size_entry = ctk.CTkEntry(options, font=LABEL_FONT, width=80)
        team_size_entry.insert(0, "12")
        team_size_entry.grid(row=0, column=1, padx=5)

        def generate_action():
            if len(primary_list) != 1:
                show_status(self.main_frame, "Drop exactly one Primary KML file.", is_error=True)
                return
            if len(alt_list) != 1:
                show_status(self.main_frame, "Drop exactly one Alternate KML file.", is_error=True)
                return
            try:
                team_size = int(team_size_entry.get().strip())
                if team_size < 1:
                    raise ValueError
            except ValueError:
                show_status(self.main_frame, "Team size must be a positive whole number.",
                            is_error=True)
                return
            try:
                output_path = route_card_excel.generate_route_cards_xlsx(
                    primary_list[0], alt_list[0], team_size)
                show_status(self.main_frame, f"Saved to {output_path}")
            except Exception as exc:
                show_status(self.main_frame, f"Error: {exc}", is_error=True)

        ctk.CTkButton(self.main_frame, text="Generate", font=BUTTON_FONT,
                      command=generate_action).pack(pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
