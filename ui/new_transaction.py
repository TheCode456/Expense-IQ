import customtkinter as ctk
from ui.theme import DARK, PRIMARY, PRIMARY_HOVER, SUCCESS, DANGER, BLUE_BORDER
from utils.file_handler import get_category_values, save_transaction
from tkinter import messagebox

BG = DARK["frame"]
TEXT = DARK["text"]

def centered_window(parent, width, height):
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()
    x = screen_width // 2 - width // 2
    y = screen_height // 2 - height // 2
    parent.geometry(f"{width}x{height}+{x}+{y}")
    parent.resizable(False, False)

def update_table(callback, content, user):
    callback(content, user)

def new_transaction(user, callback, content_frm, topbar, topbar_frame):
    window = ctk.CTk()
    window.title("Provide Data for your Account")
    centered_window(window, 800, 300)
    window.resizable(False, False)
    window.configure(fg_color=BG)
    # window.overrideredirect(True)
    window.attributes("-topmost", True)
    window.bind('<Escape>', lambda _: window.destroy())

    def update_category_values():
        transaction_type = type_value.get()
        categories = get_category_values(transaction_type)
        Category_entry.configure(values=categories)
        Category_entry.set(categories[0])

    def validate_int(event):
        if event.char.isdigit() or event.keysym in [
            'BackSpace',
            'Delete',
            'Left',
            'Right',
            "Escape",
            'Control',
            'Alt'
        ]:
            return
        else:
            return "break"
            # how does break prevents input of chars? Ans: In Tkinter, returning the string "break" from an event handler prevents the default behavior associated with the event. In this case, when a non-digit character is pressed, the event handler returns "break", which tells Tkinter to stop processing the event further. This means that the character will not be inserted into the entry widget.

    def new():
        title = title_entry.get()
        amount = int(amount_entry.get())
        type = type_value.get()
        category = Category_entry.get()

        save_transaction(user, title, amount, type, category)

        window.destroy()
        update_table(callback, content_frm, user)
        topbar(user, topbar_frame)

        messagebox.showinfo(
            "Successfull Transaction",
            f"The transaction for title :{title} has successfully added to your data."
        )

    def color_type():
        txt = type_value.get()
        if txt == "Expense":
            type_btn.configure(selected_color=DANGER)
        else:
            type_btn.configure(selected_color=SUCCESS)

    def update_confirm_button(event=None):
        title = title_entry.get().strip()
        amount = amount_entry.get().strip()

        if title and amount:
            cnf_btn.configure(state="normal")
        else:
            cnf_btn.configure(state="disabled")

    ctk.CTkLabel(
        window,
        text="New Transaction",
        font=("Bahnschrift SemiBold", 36, "bold"),
        text_color=TEXT
    ).pack(side="top", anchor="center")

    title_frame = ctk.CTkFrame(
        window,
        fg_color=DARK["card"],
        width=500
    )
    title_frame.pack(
        side="left",
        expand=True,
        fill="both",
        padx=20,
        pady=20
    )
    title_frame.pack_propagate(False)

    ctk.CTkLabel(
        title_frame,
        text="TITLE",
        font=("Segoe UI", 24, "bold")
    ).pack(anchor="nw", padx=10, pady=10)

    title_entry = ctk.CTkEntry(
        title_frame,
        placeholder_text="Title of the Transaction",
        fg_color=DARK["bg"],
        font=("Cascadia Code", 20),
        border_color=BLUE_BORDER
    )
    title_entry.pack(fill="x", padx=(10, 20))

    ctk.CTkLabel(
        title_frame,
        text="AMOUNT",
        font=("Segoe UI", 24, "bold")
    ).pack(anchor="nw", padx=10, pady=10)

    amount_entry = ctk.CTkEntry(
        title_frame,
        placeholder_text="Amount",
        fg_color=DARK["bg"],
        font=("Cascadia Code", 20),
        border_color=BLUE_BORDER
    )
    amount_entry.pack(fill="x", padx=(10, 20))

    amount_entry.bind('<KeyPress>', validate_int)

    other_inputs = ctk.CTkFrame(
        window,
        fg_color=DARK["card"]
    )
    other_inputs.pack(
        side="left",
        expand=True,
        fill="both",
        padx=(0, 20),
        pady=20
    )

    type_value = ctk.StringVar(value="Expense")

    type_btn = ctk.CTkSegmentedButton(
        other_inputs,
        values=["Expense", "Income"],
        variable=type_value,
        fg_color=DARK["frame"],
        selected_color=DANGER,
        selected_hover_color=DARK["card"],
        unselected_color=DARK["bg"],
        unselected_hover_color=DARK["border"],
        text_color="white",
        corner_radius=8,
        command=lambda _: [color_type(), update_category_values()]
    )
    type_btn.pack(
        in_=other_inputs,
        padx=15,
        pady=10,
        anchor="ne",
        fill="x"
    )

    ctk.CTkLabel(
        other_inputs,
        text="CATEGORY",
        font=("Segoe UI", 24, "bold")
    ).pack(anchor="nw", padx=10, pady=10)

    Category_entry = ctk.CTkOptionMenu(
        other_inputs,
        fg_color=DARK["bg"],
        font=("Cascadia Code", 20)
    )
    Category_entry.pack(fill="x", padx=(10, 20))

    update_category_values()

    cnf_btn = ctk.CTkButton(
        other_inputs,
        text="Conform",
        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        text_color=DARK["text"],
        corner_radius=15,
        command=new,
        state="disabled"
    )
    cnf_btn.pack(
        side="bottom",
        fill="x",
        padx=20,
        pady=10
    )

    # Check the fields AFTER the key has been processed.
    # This avoids the KeyPress issue where .get() sees the previous text.
    title_entry.bind("<KeyRelease>", update_confirm_button)
    amount_entry.bind("<KeyRelease>", update_confirm_button)

    window.mainloop()