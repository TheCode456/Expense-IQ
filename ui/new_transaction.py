import customtkinter as ctk
from ui.theme import *
from utils.file_handler import get_category_values,save_transaction,get_id
from utils.date_calculator import get_today
from tkinter import messagebox
# ---------------- COLORS ----------------
BG = DARK["frame"]
SURFACE = DARK["bg"]
TEXT = DARK["text"]
SUBTEXT = DARK["subtext"]
ACCENT = PRIMARY
ACCENT_HOVER = PRIMARY_HOVER
ACCENT_PRESSED = PRIMARY_HOVER
GREEN = SUCCESS
BORDER = DARK["border"]
DANGER = DANGER


def centered_window(parent, width, height):
    screen_width = parent.winfo_screenwidth()
    screen_height = parent.winfo_screenheight()
    x = screen_width // 2 - width // 2
    y = screen_height // 2 - height // 2
    parent.geometry(f"{width}x{height}+{x}+{y}")
    parent.resizable(False,False)

def update_table(callback,content,user):
    callback(content,user)

def new_transaction(user,callback,content_frm,topbar,topbar_frame):
    window=ctk.CTk()
    window.title("Provide Data for your Account")
    centered_window(window, 800, 300)
    window.resizable(False, False)
    window.configure(fg_color=BG)
    # window.overrideredirect(True)
    window.attributes("-topmost", True)
    window.bind('<Escape>',lambda _:window.destroy())

    def validate_int(event):
        if event.char.isdigit() or event.keysym in ['BackSpace', 'Delete', 'Left', 'Right',"Escape",'Control','Alt']:
            return
        else:
            return "break" #how does break prevents input of chars? Ans: In Tkinter, returning the string "break" from an event handler prevents the default behavior associated with that event. In this case, when a non-digit character is pressed, the event handler returns "break", which tells Tkinter to stop processing the event further. This means that the character will not be inserted into the entry widget, effectively preventing the input of non-digit characters.
        
    def new():
        title=title_entry.get()
        amount=int(amount_entry.get())
        type=type_value.get()

        category="Salary"

        if type=="Expense":
            category=Category_entry.get()
        save_transaction(user,title,amount,type,category)
        window.destroy()
        update_table(callback,content_frm,user)
        topbar(user,topbar_frame)
        messagebox.showinfo("Successfull Transaction",f"The transaction for title :{title} has successfully added to your data.")


    def color_type():
        txt=type_value.get()
        if txt=="Expense":
            type_btn.configure(selected_color=DANGER)
            Category_entry.configure(state="normal")
        else:
            type_btn.configure(selected_color=SUCCESS)
            Category_entry.configure(state="disabled")

    ctk.CTkLabel(window,text="New Transaction",font=("Bahnschrift SemiBold", 36, "bold"),text_color=TEXT).pack(side="top",anchor="center")

    title_frame=ctk.CTkFrame(window,fg_color=DARK["card"],width=500)
    title_frame.pack(side="left",expand=True,fill="both",padx=20,pady=20)
    title_frame.pack_propagate(False)

    title_txt=ctk.CTkLabel(title_frame,text="TITLE",font=("Segoe UI",24,"bold")).pack(anchor="nw",padx=10,pady=10)
    title_entry=ctk.CTkEntry(title_frame,placeholder_text="Title of the Transaction",fg_color=DARK["bg"],font=("Cascadia Code",20),border_color=BLUE_BORDER)
    title_entry.pack(fill="x",padx=(10,20))

    amount_txt=ctk.CTkLabel(title_frame,text="AMOUNT",font=("Segoe UI",24,"bold")).pack(anchor="nw",padx=10,pady=10)
    amount_entry=ctk.CTkEntry(title_frame,placeholder_text="Amount",fg_color=DARK["bg"],font=("Cascadia Code",20),border_color=BLUE_BORDER)
    amount_entry.pack(fill="x",padx=(10,20))

    amount_entry.bind('<KeyPress>',lambda e : validate_int(e))

    other_inputs=ctk.CTkFrame(window,fg_color=DARK["card"])
    other_inputs.pack(side="left",expand=True,fill="both",padx=(0,20),pady=20)

    type_value = ctk.StringVar()

    type_btn = ctk.CTkSegmentedButton(
        other_inputs,
        values=["Expense", "Income"],
        variable=type_value,
        fg_color=DARK["frame"],
        selected_color=DANGER,       # red for expense
        selected_hover_color=DARK["card"],
        unselected_color=DARK["bg"],
        unselected_hover_color=DARK["border"],
        text_color="white",
        corner_radius=8,
        command=lambda _ :[color_type(),cnf_btn.configure(state="normal")],
    )
    type_btn.pack(in_=other_inputs, padx=15, pady=10,anchor="ne",fill="x")

    Category_txt=ctk.CTkLabel(other_inputs,text="CATEGORY",font=("Segoe UI",24,"bold")).pack(anchor="nw",padx=10,pady=10)
    Category_entry=ctk.CTkOptionMenu(other_inputs,values=get_category_values(),fg_color=DARK["bg"],font=("Cascadia Code",20))
    Category_entry.pack(fill="x",padx=(10,20))

    cnf_btn=ctk.CTkButton(other_inputs,text="Conform",fg_color=PRIMARY,hover_color=PRIMARY_HOVER,text_color=DARK["text"],corner_radius=15,command=new,state="disabled")
    cnf_btn.pack(side="bottom",fill="x",padx=20,pady=10)

    window.mainloop()