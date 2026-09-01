import customtkinter as ctk
from ui.theme import *

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


def get_preferences(parent):
    pref=None
    ctk.set_appearance_mode("dark")
    window = ctk.CTkToplevel(parent)
    window.focus()
    window.title("Provide Data for your Account")
    centered_window(window, 1000, 400)
    window.resizable(False, False)
    window.configure(fg_color=BG)

    def check_int(e):
        char=e.char
        valid="0123456789"
        if e.keycode==8 or e.keycode==46:
            return
        if char not in valid:
            return "break"

    def enable_button():
        if nameEntry.get()=="" or budgetEntry.get()=="" or currencySelection.get()=="" or savings_entry.get()=="":
            submit_button.configure(state="disabled")
        else:
            submit_button.configure(state="normal")

    def submit_data():
        nonlocal data
        name=nameEntry.get().strip()
        budget_text=budgetEntry.get().strip()
        savings_text=savings_entry.get().strip()

        if not name or not budget_text or not savings_text or not currencySelection.get():
            return

        try:
            budget=float(budget_text)
            savings=float(savings_text)
        except ValueError:
            return

        threshold=thresholdValue.get()
        currency=currencySelection.get()
        theme="dark"

        data["name"]=name
        data["monthly_limit"]=budget
        data["threshold_percent"]=threshold
        data["currency"]=currency
        data["theme"]=theme
        data["savings"]=savings

        window.destroy()

    def cancel_window():
        nonlocal data
        data = None
        window.destroy()

    questions=["What should we call you?","Set your monthly spending budget","Warn me when spending reaches ","Which currency do you follow","Set your monthly Savings Target"]
    data={
        "name":"",
        "monthly_limit":0,
        "threshold_percent":0,
        "currency":"",
        "savings":0
    }
    keys=["name","monthly_limit","threshold_percent","currency","savings"]
    current_index=0

    left_frame=ctk.CTkFrame(window,fg_color=BG)
    left_frame.pack(side="left",fill="both",expand=True)
    right_frame=ctk.CTkFrame(window,fg_color=BG)
    right_frame.pack(side="right",fill="both",expand=True)

    title=ctk.CTkLabel(left_frame,text="Provide some Information",text_color=TEXT,font=("Dubai Medium",24))
    title.pack(pady=16)

    one=ctk.CTkLabel(left_frame,text=questions[0],text_color=TEXT,font=("Dubai Medium",20))
    one.pack(anchor="w",padx=20,pady=(0,16))
    nameEntry=ctk.CTkEntry(left_frame,placeholder_text="Name....",width=500,text_color=TEXT,font=("Dubai Medium",20),border_color=BORDER,fg_color=SURFACE)
    nameEntry.pack(anchor="w",padx=20,pady=(0,20))

    two=ctk.CTkLabel(left_frame,text=questions[1],text_color=TEXT,font=("Dubai Medium",20))
    two.pack(anchor="w",padx=20,pady=(0,16))
    budgetEntry=ctk.CTkEntry(left_frame,placeholder_text="Budget....",width=150,text_color=TEXT,font=("Dubai Medium",20),border_color=BORDER,fg_color=SURFACE)
    budgetEntry.pack(anchor="w",padx=20,pady=(0,20))
    budgetEntry.bind("<KeyPress>",lambda e:check_int(e))
    
    thresholdValue=ctk.IntVar(value=80)
    three_txt=questions[2] + f" {thresholdValue.get()}%"
    three=ctk.CTkLabel(left_frame,text=three_txt,text_color=TEXT,font=("Dubai Medium",20))
    three.pack(anchor="w",padx=20,pady=(0,16))
    
    threshold_slider=ctk.CTkSlider(left_frame,from_=0,to=100,variable=thresholdValue,height=20,corner_radius=80,command=lambda e:three.configure(text=questions[2] + f" {thresholdValue.get()}%"),width=500,fg_color=BORDER,progress_color=ACCENT,button_color=ACCENT,button_hover_color=ACCENT_HOVER)
    threshold_slider.pack(anchor="w",padx=20,pady=(0,20))

    #right frame widgets
    secondary_text=ctk.CTkLabel(right_frame,text="Select your preferences",text_color=TEXT,font=("Dubai Medium",24))
    secondary_text.pack(pady=16)
    four=ctk.CTkLabel(right_frame,text=questions[3],text_color=TEXT,font=("Dubai Medium",20))
    four.pack(anchor="w",padx=20,pady=(0,16))
    currencySelection=ctk.CTkOptionMenu(right_frame,
        values=["INR","USD","EUR","GBP"],
        # Styling
        width=300,
        height=45,
        corner_radius=10,

        fg_color=SURFACE,
        text_color=TEXT,
        dropdown_fg_color=SURFACE,
        button_color=ACCENT,
        button_hover_color=ACCENT_HOVER,
        dropdown_hover_color=BG,
        font=("Segoe UI", 16, "bold")
    )
    currencySelection.pack(anchor="w",padx=20,pady=(0,20))

    five=ctk.CTkLabel(right_frame,text=questions[4],text_color=TEXT,font=("Dubai Medium",20))
    five.pack(anchor="w",padx=20,pady=(0,16))
    savings_entry=ctk.CTkEntry(right_frame,placeholder_text="Savings....",width=150,text_color=TEXT,font=("Dubai Medium",20),border_color=BORDER,fg_color=SURFACE)
    savings_entry.pack(anchor="w",padx=20,pady=(0,16))
    savings_entry.bind("<KeyPress>",lambda e:check_int(e))

    button_row = ctk.CTkFrame(right_frame, fg_color="transparent")
    button_row.pack(side="bottom", padx=60, pady=20, fill="x")

    cancel_button=ctk.CTkButton(button_row,text="Cancel",width=90,height=50,corner_radius=10,fg_color=BORDER,hover_color=ACCENT_HOVER,command=cancel_window)
    cancel_button.pack(side="left")

    submit_button=ctk.CTkButton(button_row,text="Submit",width=200,height=50,corner_radius=10,fg_color=ACCENT,hover_color=ACCENT_HOVER,command=lambda:submit_data(),state="disabled")
    submit_button.pack(side="right")

    #binding all
    nameEntry.bind("<KeyRelease>",lambda e:enable_button())
    budgetEntry.bind("<KeyRelease>",lambda e:enable_button())
    savings_entry.bind("<KeyRelease>",lambda e:enable_button())
    budgetEntry.bind("<Control-BackSpace>",lambda e:budgetEntry.delete(0, "end"))
    window.protocol("WM_DELETE_WINDOW", cancel_window)
    window.grab_set()
    window.wait_window()
    return data
