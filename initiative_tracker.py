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

        tabs = Tabs(self, active_configure=c.l0, inactive_configure=c.l, content_grid_options={"sticky": "nswe", "padx": 5, "pady": 5}, **c.f)
        tabs.grid(row=0, column=0, sticky="nswe")

        self.tracker = Tracker(tabs, self)
        self.settings = Settings(tabs, self.tracker)
        tabs.add_tab("Tracker", self.tracker)
        tabs.add_tab("Settings", self.settings)
        
        tk.Label(tabs.top_frame, **c.l).grid(row=0, column=2)

        clear_button = tk.Label(tabs.top_frame, text="Clear", **c.l)
        clear_button.bind("<Button-1>", lambda _: self.tracker.clear())
        clear_button.bind("<Enter>", lambda _: clear_button.configure(**c.l0))
        clear_button.bind("<Leave>", lambda _: clear_button.configure(**c.l))
        clear_button.grid(row=0, column=3, padx=(5, 0))

        load_button = tk.Label(tabs.top_frame, text="Load", **c.l)
        load_button.bind("<Button-1>", lambda _: self.load())
        load_button.bind("<Enter>", lambda _: load_button.configure(**c.l0))
        load_button.bind("<Leave>", lambda _: load_button.configure(**c.l))
        load_button.grid(row=0, column=4, padx=(5, 0))

        save_button = tk.Label(tabs.top_frame, text="Save", **c.l)
        save_button.bind("<Button-1>", lambda _: self.save())
        save_button.bind("<Enter>", lambda _: save_button.configure(**c.l0))
        save_button.bind("<Leave>", lambda _: save_button.configure(**c.l))
        save_button.grid(row=0, column=5, padx=(5, 0))

        self.bind("<Left>", lambda _: self.tracker.select_previous())
        self.bind("<Up>", lambda _: self.tracker.select_previous())
        self.bind("<Down>", lambda _: self.tracker.select_next())
        self.bind("<Right>", lambda _: self.tracker.select_next())

        self.bind("<Control-Left>", lambda _: self.tracker.decrement_round())
        self.bind("<Control-Up>", lambda _: self.tracker.decrement_round())
        self.bind("<Control-Down>", lambda _: self.tracker.increment_round())
        self.bind("<Control-Right>", lambda _: self.tracker.increment_round())

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        tabs.grid_rowconfigure(2, weight=1)
        tabs.grid_columnconfigure(0, weight=1)

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

        self.entries: list[TrackerEntry] = []
        self.entry_data: list[EntryData] = []
        self.selected = 0
        self.round = 1

        self.var_turn = tk.StringVar(value="Nobody here :(")
        self.var_round = tk.StringVar(value=f"Round {self.round}")

        self.var_name = tk.StringVar(value="")
        self.var_init = tk.StringVar(value="0")
        self.var_prio = tk.StringVar(value="0")

        self.var_health_points = tk.StringVar(value="10")
        self.var_spell_points = tk.StringVar(value="0")

        self.var_actions = tk.StringVar(value="1")
        self.var_bonus_actions = tk.StringVar(value="1")
        self.var_reactions = tk.StringVar(value="1")
        self.var_surge_dice = tk.StringVar(value="0")

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
        
        description_font = ("Helvetica", 8, "italic")
        tk.Label(self.entry_frame, text="init", font=description_font, **c.l0).grid(row=0, column=4, sticky="w")
        tk.Label(self.entry_frame, text="prio", font=description_font, **c.l0).grid(row=0, column=5, sticky="w")
        tk.Label(self.entry_frame, text="name", font=description_font, **c.l0).grid(row=0, column=7, sticky="w")

        tk.Label(self.entry_frame, text="health points", font=description_font, **c.l0).grid(row=0, column=9, sticky="w")
        tk.Label(self.entry_frame, text="spell points", font=description_font, **c.l0).grid(row=0, column=10, sticky="w")

        tk.Label(self.entry_frame, text="A", font=description_font, **c.l0).grid(row=0, column=11, sticky="w")
        tk.Label(self.entry_frame, text="BA", font=description_font, **c.l0).grid(row=0, column=12, sticky="w")
        tk.Label(self.entry_frame, text="R", font=description_font, **c.l0).grid(row=0, column=13, sticky="w")
        tk.Label(self.entry_frame, text="SD", font=description_font, **c.l0).grid(row=0, column=14, sticky="w")

        tk.Label(self.entry_frame, text="notes", font=description_font, **c.l0).grid(row=0, column=16, sticky="w")

        tk.Entry(self.entry_frame, textvariable=self.var_init, width=4, justify="center", **c.e).grid(row=1, column=4, padx=1, sticky="we")
        tk.Entry(self.entry_frame, textvariable=self.var_prio, width=4, justify="center", **c.e).grid(row=1, column=5, padx=1, sticky="we")
        tk.Entry(self.entry_frame, textvariable=self.var_name, width=20, **c.e).grid(row=1, column=7, padx=1)

        tk.Entry(self.entry_frame, textvariable=self.var_health_points, width=8, justify="center", **c.e).grid(row=1, column=9, padx=1, sticky="we")
        tk.Entry(self.entry_frame, textvariable=self.var_spell_points, width=8, justify="center", **c.e).grid(row=1, column=10, padx=6, sticky="we")

        tk.Entry(self.entry_frame, textvariable=self.var_actions, width=2, justify="center", **c.e).grid(row=1, column=11, padx=1)
        tk.Entry(self.entry_frame, textvariable=self.var_bonus_actions, width=2, justify="center", **c.e).grid(row=1, column=12, padx=1)
        tk.Entry(self.entry_frame, textvariable=self.var_reactions, width=2, justify="center", **c.e).grid(row=1, column=13, padx=1)
        tk.Entry(self.entry_frame, textvariable=self.var_surge_dice, width=2, justify="center", **c.e).grid(row=1, column=14, padx=1)

        tk.Entry(self.entry_frame, textvariable=self.var_notes, width=50, **c.e).grid(row=1, column=16, padx=1, sticky="we")

        ttk.Separator(self.entry_frame, orient="horizontal").grid(row=2, columnspan=18, sticky="we", pady=3)

        add_button = ImageButton(self.entry_frame, self.icons["add"], self.icons["add_active"], lambda *_: self.read_add())
        add_button.bind("<Button-1>")
        add_button.grid(row=1, column=0)

        prev_round_button = ImageButton(self.round_frame, self.icons["prev_round"], self.icons["prev_round_active"], lambda *_: self.decrement_round())
        prev_button = ImageButton(self.round_frame, self.icons["prev"], self.icons["prev_active"], lambda *_: self.select_previous())
        label_round = tk.Label(self.round_frame, textvariable=self.var_round, **c.l0)
        next_button = ImageButton(self.round_frame, self.icons["next"], self.icons["next_active"], lambda *_: self.select_next())
        next_round_button = ImageButton(self.round_frame, self.icons["next_round"], self.icons["next_round_active"], lambda *_: self.increment_round())

        tk.Label(self.round_frame, textvariable=self.var_turn, font=("Helvetica", 16, "bold"), **c.l0).grid(row=0, column=0, columnspan=5, pady=(5, 0))

        prev_round_button.grid(row=1, column=0)
        prev_button.grid(row=1, column=1, padx=1)
        label_round.grid(row=1, column=2)
        next_button.grid(row=1, column=3, padx=1)
        next_round_button.grid(row=1, column=4)

        self.round_frame.grid(row=2, padx=5)
        ttk.Separator(self, orient="horizontal").grid(row=3, padx=5, sticky="we")
        self.entry_frame.grid(row=4, padx=5, sticky="we")

        self.entry_frame.grid_columnconfigure(16, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
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
        self.add(
            name = self.var_name.get(),
            initiative = int(self.var_init.get()),
            priority = int(self.var_prio.get()),
            health_points = int(self.var_health_points.get()),
            spell_points = int(self.var_spell_points.get()),
            actions = int(self.var_actions.get()),
            bonus_actions = int(self.var_bonus_actions.get()),
            reactions = int(self.var_reactions.get()),
            surge_dice = int(self.var_surge_dice.get()),
            notes = self.var_notes.get()
        )

    def add(self, name: str = "", initiative: int = 0, priority: int = 0,
            health_points: int = 10, spell_points: int = 0,
            current_health_points: int = -1, current_spell_points: int = -1,
            actions: int = 1, bonus_actions: int = 1, reactions: int = 1, surge_dice: int = 0,
            current_actions: int = -1, current_bonus_actions: int = -1, current_reactions: int = -1, current_surge_dice: int = -1,
            notes: str = "", color_index: int = 0,
            force_priority: bool = False):
        
        new_data = EntryData(self,
            name = name, initiative = initiative, priority = priority,
            health_points = health_points, spell_points = spell_points,
            current_health_points = current_health_points, current_spell_points = current_spell_points,
            actions = actions, bonus_actions = bonus_actions, reactions = reactions, surge_dice = surge_dice,
            current_actions = current_actions, current_bonus_actions = current_bonus_actions, current_reactions = current_reactions, current_surge_dice = current_surge_dice,
            notes = notes, color_index = color_index
        )

        for index, data in enumerate(self.entry_data):
            if (data.initiative < initiative) or (data.initiative == initiative and data.priority < priority):
                self.entry_data.insert(index, new_data)
                self.assign_priority(index)
                break
        if new_data not in self.entry_data:
            self.entry_data.append(new_data)
            if not force_priority:
                self.assign_priority(len(self.entry_data)-1)

        new_entry = TrackerEntry(self.entry_frame, self, len(self.entries))
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
            self.add(**entry, force_priority=True)
        self.update_idletasks()
        self.set_selected(data["selected"])
    
    def sort_data(self):
        sorted_data: list[EntryData] = []
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
        if len(self.entries) > self.selected:
            self.entries[self.selected].end_turn()

        self.set_selected(self.selected+1)

        if len(self.entries) > self.selected:
            self.entries[self.selected].start_turn()
    
    def move_up(self, index: int):
        self.update_data()
        self.entry_data[index-1], self.entry_data[index] = self.entry_data[index], self.entry_data[index-1]
        self.assign_priority(index)
        self.update_entries()

    def move_down(self, index: int):
        self.update_data()
        self.entry_data[index], self.entry_data[index+1] = self.entry_data[index+1], self.entry_data[index]
        self.assign_priority(index)
        self.update_entries()
    
    def update_priority(self):
        for i in range(len(self.entries)):
            self.assign_priority(i)

    def assign_priority(self, index: int):
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

class EntryData():

    def __init__(self, tracker: Tracker,
            name: str = "", initiative: int = 0, priority: int = 0,
            health_points: int = 10, spell_points: int = 0,
            current_health_points: int = -1, current_spell_points: int = -1,
            actions: int = 1, bonus_actions: int = 1, reactions: int = 1, surge_dice: int = 0,
            current_actions: int = -1, current_bonus_actions: int = -1, current_reactions: int = -1, current_surge_dice: int = -1,
            notes: str = "", color_index: int = 0):
        
        self.tracker: Tracker = tracker

        self.name: str = name
        self.initiative: int = initiative
        self.priority: int = priority

        self.health_points: int = health_points
        self.spell_points: int = spell_points

        self.current_health_points: int = health_points if current_health_points == -1 else current_health_points
        self.current_spell_points: int = spell_points if current_spell_points == -1 else current_spell_points

        self.actions: int = actions
        self.bonus_actions: int = bonus_actions
        self.reactions: int = reactions
        self.surge_dice: int = surge_dice

        self.current_actions: int = actions if current_actions == -1 else current_actions
        self.current_bonus_actions: int = bonus_actions if current_bonus_actions == -1 else current_bonus_actions
        self.current_reactions: int = reactions if current_reactions == -1 else current_reactions
        self.current_surge_dice: int = surge_dice if current_surge_dice == -1 else current_surge_dice

        self.notes: str = notes
        self.color_index: int = color_index
    
    def get_data(self):
        data = {}
        data["name"] = self.name
        data["initiative"] = self.initiative
        data["priority"] = self.priority

        data["health_points"] = self.health_points
        data["spell_points"] = self.spell_points

        data["current_health_points"] = self.current_health_points
        data["current_spell_points"] = self.current_spell_points

        data["actions"] = self.actions
        data["bonus_actions"] = self.bonus_actions
        data["reactions"] = self.reactions
        data["surge_dice"] = self.surge_dice

        data["current_actions"] = self.current_actions
        data["current_bonus_actions"] = self.current_bonus_actions
        data["current_reactions"] = self.current_reactions
        data["current_surge_dice"] = self.current_surge_dice

        data["notes"] = self.notes
        data["color_index"] = self.color_index
        return data
    
    def get_color(self):
        return self.tracker.root.settings.colors[self.color_index]

class TrackerEntry():
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

        self.var_health_points = tk.StringVar()
        self.var_spell_points = tk.StringVar()
        self.var_health_change = tk.StringVar()
        self.var_spell_change = tk.StringVar()

        self.var_actions = tk.StringVar()
        self.var_bonus_actions = tk.StringVar()
        self.var_reactions = tk.StringVar()
        self.var_surge_dice = tk.StringVar()

        self.var_notes = tk.StringVar()

        self.button_remove = ImageButton(parent, self.icons["remove"], self.icons["remove_active"], lambda *_: self.tracker.remove(self.index))
        self.button_up = ImageButton(parent, self.icons["up"], self.icons["up_active"], lambda *_: self.tracker.move_up(self.index))
        self.button_down = ImageButton(parent, self.icons["down"], self.icons["down_active"], lambda *_: self.tracker.move_down(self.index))

        self.entry_init = tk.Entry(parent, width=4, textvariable=self.var_init, justify="center", **c.e)
        self.entry_prio = tk.Entry(parent, width=4, textvariable=self.var_prio, justify="center", **c.e)
        self.entry_name = tk.Entry(parent, width=20, textvariable=self.var_name, **c.e)

        resource_font = ("Latin Modern Mono Caps", 13, "bold")
        self.frame_health = tk.Frame(parent, bg=c.bg0)
        self.frame_health.grid_columnconfigure(0, weight=1)
        self.label_health_points = tk.Label(self.frame_health, textvariable=self.var_health_points, font=resource_font, justify="center", fg="#60F060", bg=c.bg0)
        self.entry_health_points = tk.Entry(self.frame_health, textvariable=self.var_health_change, justify="center", **c.e, width=5)
        self.label_health_points.grid(row=0, column=0, padx=6, sticky="swe")
        self.entry_health_points.grid(row=0, column=1, padx=1)

        self.frame_spell = tk.Frame(parent, bg=c.bg0)
        self.frame_spell.grid_columnconfigure(0, weight=1)
        self.label_spell_points = tk.Label(self.frame_spell, textvariable=self.var_spell_points, font=resource_font, justify="center", fg="#40A0F0", bg=c.bg0)
        self.entry_spell_points = tk.Entry(self.frame_spell, textvariable=self.var_spell_change, justify="center", **c.e, width=5)
        self.label_spell_points.grid(row=0, column=0, padx=6, sticky="swe")
        self.entry_spell_points.grid(row=0, column=1, padx=1)

        self.label_actions = tk.Label(parent, textvariable=self.var_actions, justify="center", font=resource_font, bg=c.bg0, fg="#A060F0")
        self.label_bonus_actions = tk.Label(parent, textvariable=self.var_bonus_actions, justify="center", font=resource_font, bg=c.bg0, fg="#F06060")
        self.label_reactions = tk.Label(parent, textvariable=self.var_reactions, justify="center", font=resource_font, bg=c.bg0, fg="#F0A020")
        self.label_surge_dice = tk.Label(parent, textvariable=self.var_surge_dice, justify="center", font=resource_font, bg=c.bg0, fg="#A0F020")

        self.entry_notes = tk.Entry(parent, textvariable=self.var_notes, width=50, **c.e)

        self.label_select_far_left = tk.Label(parent, image=self.icons["select_left"], highlightthickness=0, borderwidth=0)
        self.label_select_left = tk.Label(parent, image=self.icons["select_left"], highlightthickness=0, borderwidth=0)
        self.label_select_center = tk.Label(parent, image=self.icons["select_right"], highlightthickness=0, borderwidth=0)
        self.label_select_right = tk.Label(parent, image=self.icons["select_left"], highlightthickness=0, borderwidth=0)
        self.label_select_far_right = tk.Label(parent, image=self.icons["select_right"], highlightthickness=0, borderwidth=0)

        self.entry_init.bind("<Return>", lambda _: self.tracker.sort())
        self.entry_prio.bind("<Return>", lambda _: self.tracker.sort())

        self.entry_name.bind("<Button-3>", lambda _: self.next_color())
        self.entry_name.bind("<Shift-Button-3>", lambda _: self.previous_color())

        self.entry_health_points.bind("<Return>", lambda _: self.change_health_points())
        self.entry_spell_points.bind("<Return>", lambda _: self.change_spell_points())

        self.label_actions.bind("<Button-1>", lambda _: self.use_action())
        self.label_actions.bind("<Button-3>", lambda _: self.add_action())
        self.label_actions.bind("<Enter>", lambda _: self.label_actions.configure(bg=c.bg1))
        self.label_actions.bind("<Leave>", lambda _: self.label_actions.configure(bg=c.bg0))

        self.label_bonus_actions.bind("<Button-1>", lambda _: self.use_bonus_action())
        self.label_bonus_actions.bind("<Button-3>", lambda _: self.add_bonus_action())
        self.label_bonus_actions.bind("<Enter>", lambda _: self.label_bonus_actions.configure(bg=c.bg1))
        self.label_bonus_actions.bind("<Leave>", lambda _: self.label_bonus_actions.configure(bg=c.bg0))

        self.label_reactions.bind("<Button-1>", lambda _: self.use_reaction())
        self.label_reactions.bind("<Button-3>", lambda _: self.add_reaction())
        self.label_reactions.bind("<Enter>", lambda _: self.label_reactions.configure(bg=c.bg1))
        self.label_reactions.bind("<Leave>", lambda _: self.label_reactions.configure(bg=c.bg0))

        self.label_surge_dice.bind("<Button-1>", lambda _: self.use_surge_die())
        self.label_surge_dice.bind("<Button-3>", lambda _: self.add_surge_die())
        self.label_surge_dice.bind("<Enter>", lambda _: self.label_surge_dice.configure(bg=c.bg1))
        self.label_surge_dice.bind("<Leave>", lambda _: self.label_surge_dice.configure(bg=c.bg0))

    def set_data(self, data: EntryData):
        self.data = data

        self.var_init.set(str(data.initiative))
        self.var_prio.set(str(data.priority))

        self.var_name.set(data.name)
        self.entry_name.configure(bg=data.get_color())

        self.var_health_points.set(f"{data.current_health_points}/{data.health_points}")
        self.var_spell_points.set(f"{data.current_spell_points}/{data.spell_points}")

        self.var_actions.set(str(data.current_actions))
        self.var_bonus_actions.set(str(data.current_bonus_actions))
        self.var_reactions.set(str(data.current_reactions))
        self.var_surge_dice.set(str(data.current_surge_dice))

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
        self.data.current_actions = self.var_actions.get()
        self.data.current_bonus_actions = self.var_bonus_actions.get()
        self.data.current_reactions = self.var_reactions.get()
        self.data.current_surge_dice = self.var_surge_dice.get()
    
    def start_turn(self):
        self.var_surge_dice.set(self.var_reactions.get())
        self.var_actions.set(str(self.data.actions))
        self.var_bonus_actions.set(str(self.data.bonus_actions))
        self.var_reactions.set(str(self.data.reactions))

    def end_turn(self):
        actions = int(self.var_actions.get())
        bonus_actions = int(self.var_bonus_actions.get())
        reactions = int(self.var_reactions.get())

        self.var_actions.set("0")
        self.var_bonus_actions.set("0")
        self.var_reactions.set(str(actions + bonus_actions + reactions))
    
    def change_health_points(self):
        change = int(self.var_health_change.get())
        self.data.current_health_points = max(0, min(self.data.current_health_points + change, self.data.health_points))
        self.var_health_points.set(f"{self.data.current_health_points}/{self.data.health_points}")
        self.var_health_change.set("")
    
    def change_spell_points(self):
        change = int(self.var_spell_change.get())
        self.data.current_spell_points = max(0, min(self.data.current_spell_points + change, self.data.spell_points))
        self.var_spell_points.set(f"{self.data.current_spell_points}/{self.data.spell_points}")
        self.var_spell_change.set("")
    
    def use_action(self):       self.var_actions.set(str(max(0, int(self.var_actions.get()) - 1)))
    def add_action(self):       self.var_actions.set(str(int(self.var_actions.get()) + 1))

    def use_bonus_action(self): self.var_bonus_actions.set(str(max(0, int(self.var_bonus_actions.get()) - 1)))
    def add_bonus_action(self): self.var_bonus_actions.set(str(int(self.var_bonus_actions.get()) + 1))

    def use_reaction(self):     self.var_reactions.set(str(max(0, int(self.var_reactions.get()) - 1)))
    def add_reaction(self):     self.var_reactions.set(str(int(self.var_reactions.get()) + 1))

    def use_surge_die(self):    self.var_surge_dice.set(str(max(0, int(self.var_surge_dice.get()) - 1)))
    def add_surge_die(self):    self.var_surge_dice.set(str(int(self.var_surge_dice.get()) + 1))

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
        if not self.label_select_center.winfo_ismapped():
            self.label_select_center.grid(row=self.row, column=8)
        if not self.label_select_right.winfo_ismapped():
            self.label_select_right.grid(row=self.row, column=15)
        if not self.label_select_far_right.winfo_ismapped():
            self.label_select_far_right.grid(row=self.row, column=17)
    
    def deselect(self):
        if self.label_select_far_left.winfo_ismapped():
            self.label_select_far_left.grid_forget()
        if self.label_select_left.winfo_ismapped():
            self.label_select_left.grid_forget()
        if self.label_select_center.winfo_ismapped():
            self.label_select_center.grid_forget()
        if self.label_select_right.winfo_ismapped():
            self.label_select_right.grid_forget()
        if self.label_select_far_right.winfo_ismapped():
            self.label_select_far_right.grid_forget()

    def grid(self, row):
        self.row = row
        self.button_remove.grid(row=row, column=0)

        self.entry_init.grid(row=row, column=4, sticky="we", padx=1)
        self.entry_prio.grid(row=row, column=5, sticky="we", padx=1)
        self.entry_name.grid(row=row, column=7, sticky="we", padx=1)

        self.frame_health.grid(row=row, column=9, sticky="we", padx=1)
        self.frame_spell.grid(row=row, column=10, sticky="we", padx=6)

        self.label_actions.grid(row=row, column=11, sticky="swe", padx=1)
        self.label_bonus_actions.grid(row=row, column=12, sticky="swe", padx=1)
        self.label_reactions.grid(row=row, column=13, sticky="swe", padx=1)
        self.label_surge_dice.grid(row=row, column=14, sticky="swe", padx=1)

        self.entry_notes.grid(row=row, column=16, sticky="we", padx=1, pady=1)
    
    def update_moves(self):
        if self.button_up.winfo_ismapped() and self.index == 0:
            self.button_up.grid_forget()
        elif not self.button_up.winfo_ismapped() and not self.index == 0:
            self.button_up.grid(row=self.row, column=2, padx=1)

        if self.button_down.winfo_ismapped() and self.index == len(self.tracker.entries) - 1:
            self.button_down.grid_forget()
        elif not self.button_down.winfo_ismapped() and not self.index == len(self.tracker.entries) - 1:
            self.button_down.grid(row=self.row, column=3, padx=1)

    def grid_forget(self):
        if self.button_up.winfo_ismapped():
            self.button_up.grid_forget()
        if self.button_down.winfo_ismapped():
            self.button_down.grid_forget()
        if self.label_select_far_left.winfo_ismapped():
            self.label_select_far_left.grid_forget()
        if self.label_select_left.winfo_ismapped():
            self.label_select_left.grid_forget()
        if self.label_select_center.winfo_ismapped():
            self.label_select_center.grid_forget()
        if self.label_select_right.winfo_ismapped():
            self.label_select_right.grid_forget()
        if self.label_select_far_right.winfo_ismapped():
            self.label_select_far_right.grid_forget()
        
        self.button_remove.grid_forget()
        self.entry_init.grid_forget()
        self.entry_prio.grid_forget()
        self.entry_name.grid_forget()
        self.frame_health.grid_forget()
        self.frame_spell.grid_forget()
        self.label_actions.grid_forget()
        self.label_bonus_actions.grid_forget()
        self.label_reactions.grid_forget()
        self.label_surge_dice.grid_forget()
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
        with open("settings.json", "w") as file:
            json.dump(self.get_data(), file)
    
    def load(self):
        with open("settings.json", "r") as file:
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