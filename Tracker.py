import tkinter as tk
from tkinter import ttk


# -----------------------
# Tooltip Klasse
# -----------------------
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window:
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            background="lightyellow",
            relief="solid",
            borderwidth=1,
            font=("Arial", 12)
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


# -----------------------
# Setup Fenster
# -----------------------
class ActorInputPage:
    def __init__(self, root):
        self.root = root
        self.root.title("Arvendor - Akteure Tracker")

        self.actors = []
        self.validation_jobs = {}  # debounce!

        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill="both", expand=True)

        ttk.Label(self.main_frame, text="Akteure hinzufügen", font=("Arial", 16)).pack(pady=10)

        self.actor_frame = ttk.Frame(self.main_frame)
        self.actor_frame.pack()

        header = ttk.Frame(self.actor_frame)
        header.pack(fill="x", pady=5)

        ttk.Label(header, text="Name", width=23).grid(row=0, column=0)
        ttk.Label(header, text="Initiative", width=12).grid(row=0, column=1)
        ttk.Label(header, text="Wert (1-6)", width=10).grid(row=0, column=2)

        self.actor_entries = []
        self.add_actor_row()

        ttk.Button(self.main_frame, text="Akteur hinzufügen", command=self.add_actor_row).pack(pady=5)
        ttk.Button(self.main_frame, text="Weiter", command=self.save_actors).pack(pady=5)

    # -----------------------
    # DEBOUNCED VALIDATION
    # -----------------------
    def schedule_validation(self, init_entry, value_entry, init_error, value_error, key):
        # alten Timer abbrechen
        if key in self.validation_jobs:
            self.root.after_cancel(self.validation_jobs[key])

        # neuen Timer setzen (1200ms)
        self.validation_jobs[key] = self.root.after(
            1200,
            lambda: self.validate_row(init_entry, value_entry, init_error, value_error)
        )

    # -----------------------
    # VALIDATION LOGIC
    # -----------------------
    def validate_row(self, init_entry, value_entry, init_error, value_error):
        init_text = init_entry.get()
        value_text = value_entry.get()

        # INIT CHECK
        try:
            init_val = int(init_text)
            if init_val < 8:
                init_entry.config(highlightbackground="red", highlightthickness=2)
                init_error.config(text="≥ 8 erforderlich")
                init_valid = False
            else:
                init_entry.config(highlightthickness=0)
                init_error.config(text="")
                init_valid = True
        except:
            init_entry.config(highlightbackground="red", highlightthickness=2)
            init_error.config(text="nur Zahl ≥ 8")
            init_valid = False

        # DICE CHECK
        try:
            dice_val = int(value_text)
            if dice_val < 1 or dice_val > 6:
                value_entry.config(highlightbackground="red", highlightthickness=2)
                value_error.config(text="1–6 erlaubt")
                value_valid = False
            else:
                value_entry.config(highlightthickness=0)
                value_error.config(text="")
                value_valid = True
        except:
            value_entry.config(highlightbackground="red", highlightthickness=2)
            value_error.config(text="nur 1–6")
            value_valid = False

        return init_valid and value_valid

    # -----------------------
    # ROW
    # -----------------------
    def add_actor_row(self):
        row = ttk.Frame(self.actor_frame)
        row.pack(pady=3, fill="x")

        name_entry = ttk.Entry(row, width=20)
        name_entry.grid(row=0, column=0, padx=5)

        init_entry = tk.Entry(row, width=10, highlightthickness=0)
        init_entry.grid(row=0, column=1, padx=5)

        value_entry = tk.Entry(row, width=10, highlightthickness=0)
        value_entry.grid(row=0, column=2, padx=5)

        init_error = tk.Label(row, text="", fg="red", font=("Arial", 9))
        init_error.grid(row=0, column=3, padx=5)

        value_error = tk.Label(row, text="", fg="red", font=("Arial", 9))
        value_error.grid(row=0, column=4, padx=5)

        key = f"row_{len(self.actor_entries)}"

        def on_change(event):
            self.schedule_validation(init_entry, value_entry, init_error, value_error, key)

        init_entry.bind("<KeyRelease>", on_change)
        value_entry.bind("<KeyRelease>", on_change)

        self.actor_entries.append((name_entry, init_entry, value_entry, init_error, value_error))

    # -----------------------
    # SAVE
    # -----------------------
    def save_actors(self):
        self.actors.clear()

        for name, init, value, err1, err2 in self.actor_entries:
            try:
                initiative = int(init.get())
                dice_value = int(value.get())

                if initiative < 8 or dice_value < 1 or dice_value > 6:
                    continue

                self.actors.append({
                    "name": name.get(),
                    "current_value": 25 - (initiative + dice_value)
                })

            except:
                continue

        self.root.destroy()

        tracker_root = tk.Tk()
        TrackerPage(tracker_root, self.actors)
        tracker_root.mainloop()


# -----------------------
# Tracker Fenster (unverändert)
# -----------------------
class TrackerPage:
    def __init__(self, root, actors):
        self.root = root
        self.root.title("Initiative Tracker")

        self.actors = actors

        self.table_frame = ttk.Frame(self.root, padding="10")
        self.table_frame.pack(fill="both", expand=True)

        self.render_table()

    def render_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.table_frame, text="Reihenfolge", font=("Arial", 16))\
            .grid(row=0, column=0, columnspan=5, pady=10)

        self.actors.sort(key=lambda x: x["current_value"])

        groups = []
        current_group = []
        last_value = None

        for actor in self.actors:
            if last_value is None or actor["current_value"] == last_value:
                current_group.append(actor)
            else:
                groups.append(current_group)
                current_group = [actor]

            last_value = actor["current_value"]

        if current_group:
            groups.append(current_group)

        row_index = 1

        for g_index, group in enumerate(groups):

            for actor in group:
                row_frame = tk.Frame(self.table_frame, bd=2)

                if g_index == 0:
                    row_frame.config(highlightbackground="green", highlightthickness=2)

                row_frame.grid(row=row_index, column=0, columnspan=5, pady=2, sticky="w")

                tk.Label(row_frame, text=actor["name"], width=20)\
                    .grid(row=0, column=0, padx=5)

                btn_1 = tk.Button(row_frame, text="1 AkP",
                          command=lambda a=actor: self.apply_cost(a, 1))
                btn_1.grid(row=0, column=1)
                ToolTip(btn_1, "zum Beispiel Hinschmeißen")

                btn_2 = tk.Button(row_frame, text="3 AkP",
                          command=lambda a=actor: self.apply_cost(a, 3))
                btn_2.grid(row=0, column=2)
                ToolTip(btn_2, "Aktionen wie:\n  Gehen\n Waffen wechseln\n Aufstehen")

                btn_3 = tk.Button(row_frame, text="6 AkP",
                          command=lambda a=actor: self.apply_cost(a, 6))
                btn_3.grid(row=0, column=3)
                ToolTip(btn_3, "Aktionen wie:\n  Laufen\n Gegenstand aus dem Rucksack nehmen")

                btn_4 = tk.Button(row_frame, text="9 AkP",
                          command=lambda a=actor: self.apply_cost(a, 9))
                btn_4.grid(row=0, column=4)
                ToolTip(btn_4, "Aktionen wie:\n  Sprinten\n Schwerer Angriff")

                row_index += 1

        ttk.Button(
            self.table_frame,
            text="Nächste Begegnung / Begegnung beenden",
            command=self.reset_app
        ).grid(row=row_index + 1, column=0, columnspan=5, pady=15)

    def apply_cost(self, actor, cost):
        actor["current_value"] += cost
        self.render_table()

    def reset_app(self):
        self.root.destroy()
        root = tk.Tk()
        ActorInputPage(root)
        root.mainloop()


# -----------------------
# Start
# -----------------------
if __name__ == "__main__":
    root = tk.Tk()
    ActorInputPage(root)
    root.mainloop()
