import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import json

from colours import dark as c
from tabs import Tabs
from image_button import ImageButton

class Root(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Initiative Tracker")
        self.configure(**c.f0)

        tabs = Tabs(self, active_configure=c.l0, inactive_configure=c.l, content_grid_options={}, **c.f)
        tabs.grid(row=0, column=0)

        self.tracker = Tracker(tabs, self)
        self.settings = Settings(tabs, self.tracker)
        tabs.add_tab("Tracker", self.tracker)
        tabs.add_tab("Settings", self.settings)
        
        save_button = tk.Label(tabs.top_frame, text="Clear", **c.l)
        save_button.bind("<Button-1>", lambda _: self.tracker.clear())
        save_button.grid(row=0, column=3)
        tk.Label(tabs.top_frame, **c.l).grid(row=0, column=2)
        load_button = tk.Label(tabs.top_frame, text="Load", **c.l)
        load_button.bind("<Button-1>", lambda _: self.load())
        load_button.grid(row=0, column=4)
        save_button = tk.Label(tabs.top_frame, text="Save", **c.l)
        save_button.bind("<Button-1>", lambda _: self.save())
        save_button.grid(row=0, column=5)

        self.bind("<Left>", lambda _: self.tracker.select_previous())
        self.bind("<Up>", lambda _: self.tracker.select_previous())
        self.bind("<Down>", lambda _: self.tracker.select_next())
        self.bind("<Right>", lambda _: self.tracker.select_next())

        self.bind("<Control-Left>", lambda _: self.tracker.decrement_round())
        self.bind("<Control-Up>", lambda _: self.tracker.decrement_round())
        self.bind("<Control-Down>", lambda _: self.tracker.increment_round())
        self.bind("<Control-Right>", lambda _: self.tracker.increment_round())

        tabs.top_frame.grid_columnconfigure(2, weight=1)

    def save(self):
        file = filedialog.asksaveasfile(
            mode="w",
            initialdir=__file__,
            initialfile=f"name.initiative.json",
            title="Save Initiative Order as",
            filetypes=[("json file", "*.json")],
            defaultextension=".json"
        )
        if file is not None:
            json.dump(self.tracker.get_save_data(), file)
            file.close()

    def load(self):
        filepath = filedialog.askopenfilename(
            initialdir=__file__,
            title="Select an Initiative Order file",
            filetypes=(("json files", "*.json*"), ("all files", "*.*"))
        )
        if filepath != "":
            with open(filepath) as file:
                self.tracker.set_data(json.load(file))

class Tracker(tk.Frame):
    icons = {}

    def __init__(self, parent, root):
        super().__init__(parent, **c.f0)
        self.root: Root = root

        self.entries = []
        self.entry_data = []
        self.selected = 0
        self.round = 1

        self.var_turn = tk.StringVar(value="Nobody here :(")
        self.var_round = tk.StringVar(value=f"Round {self.round}")
        self.var_name = tk.StringVar(value="")
        self.var_init = tk.StringVar(value="0")
        self.var_prio = tk.StringVar(value="0")
        self.var_notes = tk.StringVar(value="")

        if self.icons == {}:
            self.icons["add"] = tk.PhotoImage(file="icons/ButtonAdd.png")
            self.icons["add_active"] = tk.PhotoImage(file="icons/ButtonAddActive.png")
            self.icons["prev_round"] = tk.PhotoImage(file="icons/InitiativeButtonPrevRound.png")
            self.icons["prev_round_active"] = tk.PhotoImage(file="icons/InitiativeButtonPrevRoundActive.png")
            self.icons["prev"] = tk.PhotoImage(file="icons/InitiativeButtonPrev.png")
            self.icons["prev_active"] = tk.PhotoImage(file="icons/InitiativeButtonPrevActive.png")
            self.icons["next"] = tk.PhotoImage(file="icons/InitiativeButtonNext.png")
            self.icons["next_active"] = tk.PhotoImage(file="icons/InitiativeButtonNextActive.png")
            self.icons["next_round"] = tk.PhotoImage(file="icons/InitiativeButtonNextRound.png")
            self.icons["next_round_active"] = tk.PhotoImage(file="icons/InitiativeButtonNextRoundActive.png")

        self.round_frame = tk.Frame(self, **c.f0)
        self.entry_frame = tk.Frame(self, **c.f0)

        tk.Label(self.entry_frame, text="init", font=("Helvetica", 8, "italic"), **c.l0).grid(row=0, column=4, sticky="w")
        tk.Label(self.entry_frame, text="prio", font=("Helvetica", 8, "italic"), **c.l0).grid(row=0, column=5, sticky="w")
        tk.Label(self.entry_frame, text="name", font=("Helvetica", 8, "italic"), **c.l0).grid(row=0, column=7, sticky="w")
        tk.Label(self.entry_frame, text="notes", font=("Helvetica", 8, "italic"), **c.l0).grid(row=0, column=9, sticky="w")

        tk.Entry(self.entry_frame, textvariable=self.var_init, width=4, justify="center", **c.e).grid(row=1, column=4)
        tk.Entry(self.entry_frame, textvariable=self.var_prio, width=4, justify="center", **c.e).grid(row=1, column=5)
        tk.Entry(self.entry_frame, textvariable=self.var_name, width=20, **c.e).grid(row=1, column=7)
        tk.Entry(self.entry_frame, textvariable=self.var_notes, width=50, **c.e).grid(row=1, column=9)

        ttk.Separator(self.entry_frame, orient="horizontal").grid(row=2, columnspan=11, sticky="we", pady=3)

        add_button = ImageButton(self.entry_frame, self.icons["add"], self.icons["add_active"], lambda *_: self.read_add())
        add_button.bind("<Button-1>")
        add_button.grid(row=1, column=0)

        prev_round_button = ImageButton(self.round_frame, self.icons["prev_round"], self.icons["prev_round_active"], lambda *_: self.decrement_round())
        prev_button = ImageButton(self.round_frame, self.icons["prev"], self.icons["prev_active"], lambda *_: self.select_previous())
        label_round = tk.Label(self.round_frame, textvariable=self.var_round, **c.l0)
        next_button = ImageButton(self.round_frame, self.icons["next"], self.icons["next_active"], lambda *_: self.select_next())
        next_round_button = ImageButton(self.round_frame, self.icons["next_round"], self.icons["next_round_active"], lambda *_: self.increment_round())

        prev_round_button.grid(row=0, column=0)
        prev_button.grid(row=0, column=1, padx=1)
        label_round.grid(row=0, column=2)
        next_button.grid(row=0, column=3, padx=1)
        next_round_button.grid(row=0, column=4)

        tk.Label(self.round_frame, textvariable=self.var_turn, **c.l0).grid(row=1, column=0, columnspan=5)

        self.round_frame.grid(row=2, padx=1)
        ttk.Separator(self, orient="horizontal").grid(row=3, sticky="we")
        self.entry_frame.grid(row=4, sticky="we", padx=1)
    
    def get_save_data(self):
        self.update_data()
        data = {}
        data["round"] = self.round
        data["selected"] = self.selected
        data["entries"] = []
        for entry in self.entry_data:
            data["entries"].append(entry.get_data())
        return data

    def read_add(self):
        self.add(self.var_name.get(), int(self.var_init.get()), int(self.var_prio.get()), self.var_notes.get())

    def add(self, name, initiative, priority=0, notes="", color_index=0):
        new_data = Entry_Data(self, name, initiative, priority, color_index, notes)

        for index, data in enumerate(self.entry_data):
            if (data.initiative < initiative) or (data.initiative == initiative and data.priority < priority):
                self.entry_data.insert(index, new_data)
                self.assign_priority(index)
                break
        if new_data not in self.entry_data:
            self.entry_data.append(new_data)
            self.assign_priority(len(self.entry_data)-1)

        new_entry = Tracker_Entry(self.entry_frame, self, len(self.entries))
        new_entry.grid(len(self.entries)+3)
        self.entries.append(new_entry)
        self.update_entries()

        if len(self.entries) == 1 or self.selected >= len(self.entries) > 0:
            self.set_selected(0)
        self.update_moves()
    
    def clear(self):
        for entry in self.entries:
            entry.grid_forget()
        self.entries = []
        self.entry_data = []
        self.set_selected(0)
        self.set_round(1)

    def remove(self, index):
        if self.selected > index:
            self.select_previous()
        if self.selected >= len(self.entries)-1 and not self.selected == 0:
            self.select_next()
        self.entries.pop().grid_forget()
        self.entry_data.pop(index)
        if index != 0:
            self.assign_priority(index-1)
        self.update_entries()
        self.update_moves()

    def update_entries(self):
        for index, entry in enumerate(self.entries):
            entry.set_data(self.entry_data[index])
    
    def update_data(self):
        for entry in self.entries:
            entry.update_data()
    
    def update_entry_colors(self):
        for entry in self.entries:
            entry.update_color()            

    def update_moves(self):
        if len(self.entries) == 1:
            self.entries[0].update_moves()
        if len(self.entries) > 1:
            self.entries[-2].update_moves()
            self.entries[-1].update_moves()

    def sort(self):
        self.update_data()
        self.sort_data()
        self.update_priority()
        self.update_entries()

    def set_data(self, data):
        self.clear()
        self.set_round(data["round"])
        for entry in data["entries"]:
            self.add(entry["name"], entry["init"], entry["prio"], entry["notes"], entry["color_index"])
        self.update_idletasks()
        self.set_selected(data["selected"])
    
    def sort_data(self):
        sorted_data = []
        for data in self.entry_data:
            for index, data_2 in enumerate(sorted_data):
                if (data.initiative > data_2.initiative) or (data.initiative == data_2.initiative and data.priority > data_2.priority):
                    sorted_data.insert(index, data)
                    break
            if data not in sorted_data:
                sorted_data.append(data)
        self.entry_data = sorted_data

    def set_round(self, round):
        self.round = round
        self.var_round.set(f"Round {self.round}")
    
    def decrement_round(self):
        self.set_round(self.round-1)

    def increment_round(self):
        self.set_round(self.round+1)
    
    def set_selected(self, index):
        if not self.entries == []:
            self.entries[self.selected].deselect()
            self.selected = index
            if self.selected < 0:
                self.selected = len(self.entries)-1
                self.set_round(self.round-1)
            if self.selected >= len(self.entries):
                self.selected = 0
                self.set_round(self.round+1)
            self.entries[self.selected].select()
            name = self.entry_data[self.selected].name
            name = name if name != "" else "Nameless"
            self.var_turn.set(f"{name}'s turn")
        else:
            self.selected = 0
            self.var_turn.set("Nobody here :(")

    def select_previous(self):
        self.set_selected(self.selected-1)

    def select_next(self):
        self.set_selected(self.selected+1)
            
    def move_up(self, index):
        self.update_data()
        self.entry_data[index-1], self.entry_data[index] = self.entry_data[index], self.entry_data[index-1]
        self.assign_priority(index)
        self.update_entries()

    def move_down(self, index):
        self.update_data()
        self.entry_data[index], self.entry_data[index+1] = self.entry_data[index+1], self.entry_data[index]
        self.assign_priority(index)
        self.update_entries()
    
    def update_priority(self):
        for i in range(len(self.entries)):
            self.assign_priority(i)

    def assign_priority(self, index):
        init = self.entry_data[index].initiative
        while index+1 < len(self.entry_data) and self.entry_data[index+1].initiative >= init:
            index += 1
            self.entry_data[index].initiative = init
        prio = 0
        while index >= 0 and self.entry_data[index].initiative <= init:
            self.entry_data[index].initiative = init
            self.entry_data[index].priority = prio
            prio += 1
            index -= 1

class Entry_Data():

    def __init__(self, tracker, name, initiative, priority, color_index, notes=""):
        self.tracker: Tracker = tracker
        self.name: str = name
        self.initiative: int = initiative
        self.priority: int = priority
        self.notes: str = notes
        self.color_index: int = color_index
    
    def get_data(self):
        data = {}
        data["name"] = self.name
        data["init"] = self.initiative
        data["prio"] = self.priority
        data["notes"] = self.notes
        data["color_index"] = self.color_index
        return data
    
    def get_color(self):
        return self.tracker.root.settings.colors[self.color_index]

class Tracker_Entry():
    icons = {}

    def __init__(self, parent, tracker, index):
        if self.icons == {}:
            self.icons["up"] = tk.PhotoImage(file="icons/ButtonTop.png")
            self.icons["up_active"] = tk.PhotoImage(file="icons/ButtonTopActive.png")
            self.icons["down"] = tk.PhotoImage(file="icons/ButtonBot.png")
            self.icons["down_active"] = tk.PhotoImage(file="icons/ButtonBotActive.png")
            self.icons["remove"] = tk.PhotoImage(file="icons/ButtonDelete.png")
            self.icons["remove_active"] = tk.PhotoImage(file="icons/ButtonDeleteActive.png")
            self.icons["select_left"] = tk.PhotoImage(file="icons/SelectionButtonLeft.png")
            self.icons["select_right"] = tk.PhotoImage(file="icons/SelectionButtonRight.png")

        self.tracker: Tracker = tracker
        self.index = index

        self.var_init = tk.StringVar()
        self.var_prio = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_notes = tk.StringVar()

        self.button_remove = ImageButton(parent, self.icons["remove"], self.icons["remove_active"], lambda *_: self.tracker.remove(self.index))
        self.button_up = ImageButton(parent, self.icons["up"], self.icons["up_active"], lambda *_: self.tracker.move_up(self.index))
        self.button_down = ImageButton(parent, self.icons["down"], self.icons["down_active"], lambda *_: self.tracker.move_down(self.index))
        self.entry_init = tk.Entry(parent, width=4, textvariable=self.var_init, justify="center", **c.e)
        self.entry_prio = tk.Entry(parent, width=4, textvariable=self.var_prio, justify="center", **c.e)
        self.entry_name = tk.Entry(parent, width=20, textvariable=self.var_name, **c.e)
        self.entry_notes = tk.Entry(parent, textvariable=self.var_notes, width=50, **c.e)

        self.label_select_far_left = tk.Label(parent, image=self.icons["select_left"], highlightthickness=0, borderwidth=0)
        self.label_select_left = tk.Label(parent, image=self.icons["select_left"], highlightthickness=0, borderwidth=0)
        self.label_select_right = tk.Label(parent, image=self.icons["select_right"], highlightthickness=0, borderwidth=0)
        self.label_select_far_right = tk.Label(parent, image=self.icons["select_right"], highlightthickness=0, borderwidth=0)

        self.entry_init.bind("<Return>", lambda _: self.tracker.sort())
        self.entry_prio.bind("<Return>", lambda _: self.tracker.sort())
        self.entry_name.bind("<Button-3>", lambda _: self.next_color())
        self.entry_name.bind("<Shift-Button-3>", lambda _: self.previous_color())

    def set_data(self, data: Entry_Data):
        self.data = data
        self.var_init.set(str(data.initiative))
        self.var_prio.set(str(data.priority))
        self.var_name.set(data.name)
        self.entry_name.configure(bg=data.get_color())
        self.var_notes.set(data.notes)
    
    def update_data(self):
        try:
            self.data.initiative = int(self.var_init.get())
        except ValueError:
            pass
        try:
            self.data.priority = int(self.var_prio.get())
        except ValueError:
            pass
        self.data.name = self.var_name.get()
        self.data.notes = self.var_notes.get()

    def next_color(self):
        self.data.color_index += 1
        if self.data.color_index >= len(self.tracker.root.settings.colors):
            self.data.color_index = 0
        self.update_color()
    
    def previous_color(self):
        self.data.color_index -= 1
        if self.data.color_index < 0:
            self.data.color_index = len(self.tracker.root.settings.colors)-1
        self.update_color()
    
    def update_color(self):
        self.entry_name.configure(bg=self.data.get_color())

    def select(self):
        if not self.label_select_far_left.winfo_ismapped():
            self.label_select_far_left.grid(row=self.row, column=1)
        if not self.label_select_left.winfo_ismapped():
            self.label_select_left.grid(row=self.row, column=6)
        if not self.label_select_right.winfo_ismapped():
            self.label_select_right.grid(row=self.row, column=8)
        if not self.label_select_far_right.winfo_ismapped():
            self.label_select_far_right.grid(row=self.row, column=10)
    
    def deselect(self):
        if self.label_select_far_left.winfo_ismapped():
            self.label_select_far_left.grid_forget()
        if self.label_select_left.winfo_ismapped():
            self.label_select_left.grid_forget()
        if self.label_select_right.winfo_ismapped():
            self.label_select_right.grid_forget()
        if self.label_select_far_right.winfo_ismapped():
            self.label_select_far_right.grid_forget()

    def grid(self, row):
        self.row = row
        self.button_remove.grid(row=row, column=0)
        self.entry_init.grid(row=row, column=4, sticky="we", padx=(1,0))
        self.entry_prio.grid(row=row, column=5, sticky="we", padx=(1,0))
        self.entry_name.grid(row=row, column=7, sticky="we")
        self.entry_notes.grid(row=row, column=9, padx=(1,0))
    
    def update_moves(self):
        if self.button_up.winfo_ismapped() and self.index == 0:
            self.button_up.grid_forget()
        elif not self.button_up.winfo_ismapped() and not self.index == 0:
            self.button_up.grid(row=self.row, column=2, padx=(1,0))

        if self.button_down.winfo_ismapped() and self.index == len(self.tracker.entries) - 1:
            self.button_down.grid_forget()
        elif not self.button_down.winfo_ismapped() and not self.index == len(self.tracker.entries) - 1:
            self.button_down.grid(row=self.row, column=3, padx=(1,0))

    def grid_forget(self):
        if self.button_up.winfo_ismapped():
            self.button_up.grid_forget()
        if self.button_down.winfo_ismapped():
            self.button_down.grid_forget()
        if self.label_select_far_left.winfo_ismapped():
            self.label_select_far_left.grid_forget()
        if self.label_select_left.winfo_ismapped():
            self.label_select_left.grid_forget()
        if self.label_select_right.winfo_ismapped():
            self.label_select_right.grid_forget()
        if self.label_select_far_right.winfo_ismapped():
            self.label_select_far_right.grid_forget()
        
        self.button_remove.grid_forget()
        self.entry_init.grid_forget()
        self.entry_prio.grid_forget()
        self.entry_name.grid_forget()
        self.entry_notes.grid_forget()
        
class Settings(tk.Frame):
    colors = []

    def __init__(self, parent, tracker):
        super().__init__(parent, **c.f0)
        self.load()
        self.tracker: Tracker = tracker

        tk.Label(self, text="Team Colors", **c.l0).grid(row=0, column=0, sticky="w", padx=1)
        for index in range(len(self.colors)):
            new_color_entry = Color_Entry(self, index)
            new_color_entry.grid(row=index+1)
    
    def save(self):
        with open("data/settings.json", "w") as file:
            json.dump(self.get_data(), file)
    
    def load(self):
        with open("data/settings.json", "r") as file:
            self.set_data(json.load(file))
    
    def get_data(self):
        return {"colors": self.colors}

    def set_data(self, data):
        self.colors = data["colors"]

class Color_Entry():

    def __init__(self, settings, index):
        self.settings: Settings = settings
        self.index = index

        self.color = tk.StringVar(value=self.settings.colors[index])
        self.entry = tk.Entry(settings, textvariable=self.color, **c.e)
        self.label = tk.Label(settings, width=10, text="valid", bg=self.color.get(), fg=c.fg)

        self.color.trace_add("write", self.update_color)

    def grid(self, row):
        self.entry.grid(row=row, column=0, padx=(10,0))
        self.label.grid(row=row, column=1, padx=(3,0))
    
    def update_color(self, *_):
        value = self.color.get()
        valid = len(value) == 7
        if valid:
            for pos, char in enumerate(value):
                if pos == 0 and char != "#":
                    valid = False
                    break
                if pos > 0 and char not in "0123456789ABCDEF":
                    valid = False
                    break
        if valid:
            self.label.configure(bg=value, text="valid")
            self.settings.colors[self.index] = value
            self.settings.tracker.update_entry_colors()
            self.settings.save()
        else:
            self.label.configure(bg=c.bg0, text="invalid")

root = Root()
root.mainloop()