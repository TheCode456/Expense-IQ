import math
import customtkinter as ctk
from ui.new_transaction import new_transaction
from ui.theme import *
from utils.file_handler import change_savings, read_json, update_user_threshold,write_json,update_password,reset_userdata,delete,open_user_json,get_remember_default,forgot_user
from utils.date_calculator import *
from tkinter import messagebox

# callback holder for transactions delete action (set when transactions_tab is rendered)
current_delete_transaction = None
def clear_content(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def check_int(e):
        char=e.char
        valid="0123456789"
        if e.keycode==8 or e.keycode==46:
            return
        if char not in valid:
            return "break"

def recall_budget_tab(callback,content_frame,username):
    clear_content(content_frame)
    callback(content_frame,username)

def centered_window(parent,width,height):
    screen_width=parent.winfo_screenwidth()
    screen_height=parent.winfo_screenheight()
    x=screen_width//2-width//2
    y=screen_height//2-height//2
    parent.geometry(f"{width}x{height}+{x}+{y}")

def fill_topbar(username,topbar):
    global balance_lbl,welcome_lbl
    clear_content(topbar)

    data=read_json(f"data/users/{username}.json")
    name=data["profile"]["name"]
    name_str=f" Welcome, {str(name)} "
    balance=data["data"]["balance"]
    balance_str=f" Current Balance:{int(balance)} "
    alert_btn=ctk.CTkButton(topbar,text="Alerts",font=(fontfamily,16),fg_color=DARK["card"],corner_radius=10,hover_color=DANGER)
    alert_btn.pack(side="right",padx=20,pady=5,ipady=5)
    left_frame = ctk.CTkFrame(topbar, fg_color="transparent")
    left_frame.pack(side="left", padx=10)
    welcome_lbl=ctk.CTkLabel(left_frame,text=name_str,fg_color=DARK["card"],font=(fontfamily,16,"bold"),corner_radius=10)
    balance_lbl=ctk.CTkLabel(left_frame,text=balance_str,fg_color=DARK["card"],font=(fontfamily,20),corner_radius=10)


    welcome_lbl.pack( side="left",ipady=5)
    balance_lbl.pack( side="left", padx=10,ipady=5)

    welcome_lbl.bind('<Enter>', lambda e: welcome_lbl.configure(fg_color=DARK["card_hover"]))
    balance_lbl.bind('<Enter>', lambda e: balance_lbl.configure(fg_color=DARK["card_hover"]))
    welcome_lbl.bind('<Leave>', lambda e: welcome_lbl.configure(fg_color=DARK["card"]))
    balance_lbl.bind('<Leave>', lambda e: balance_lbl.configure(fg_color=DARK["card"]))

def Dashboard(content_frame,username):
    clear_content(content_frame)
    expense_frame=ctk.CTkFrame(content_frame,fg_color=DARK["frame"],corner_radius=24,border_color=RED_BORDER)
    expense_frame.place(relwidth=0.475,relheight=0.475,relx=0.025,y=16)
    ctk.CTkLabel(expense_frame,text="Expenses",font=(fontfamily,28,"bold"),text_color=DARK["text"]).pack(padx=20,pady=10,anchor="w")
    user_json=open_user_json(username)

    savingsCard=ctk.CTkFrame(content_frame,fg_color=DARK["card"],corner_radius=24,border_width=1,border_color=GREEN_BORDER)
    savingsCard.place(relwidth=0.475,relheight=0.47,relx=0.5,y=16)

    # Transaction Preview Section
    transaction_frame=ctk.CTkFrame(content_frame,fg_color=DARK["frame"],corner_radius=24,border_width=1,border_color=DARK["border"])
    transaction_frame.place(relwidth=0.95,relheight=0.475,relx=0.025,rely=0.5)

    # Header with View All button
    header_frame=ctk.CTkFrame(transaction_frame,fg_color="transparent")
    header_frame.pack(fill="x",padx=20,pady=(15,10))

    ctk.CTkLabel(
        header_frame,
        text="Recent Activity",
        font=(fontfamily,24,"bold"),
        text_color=DARK["text"]
    ).pack(side="left")

    view_all_btn=ctk.CTkButton(
        header_frame,
        text="View All →",
        font=(fontfamily,12),
        fg_color="transparent",
        hover_color=DARK["card_hover"],
        text_color=PRIMARY,
        width=100,
        height=32,
        command=lambda:transactions_tab(content_frame,username)
    )
    view_all_btn.pack(side="right")

    transactions=user_json["data"]["transactions"]
    currency=user_json["profile"]["currency"]

    if not transactions or transactions==[{}] or all(not t for t in transactions):
        ctk.CTkLabel(
            transaction_frame,
            text="No transactions yet",
            font=(fontfamily,16),
            text_color=DARK["subtext"]
        ).place(anchor="center",relx=0.5,rely=0.5)
    else:
        # Show last 4 transactions max (reduced for performance)
        preview_transactions=transactions[-4:] if len(transactions)>4 else transactions
        preview_transactions=list(reversed(preview_transactions))

        # Fixed container
        container=ctk.CTkFrame(transaction_frame,fg_color="transparent")
        container.pack(fill="both",expand=True,padx=20,pady=(0,15))

        for txn in preview_transactions:
            if not txn:
                continue

            # Simpler card - fewer nested frames
            card=ctk.CTkFrame(container,fg_color=DARK["card"],corner_radius=8,height=50)
            card.pack(fill="x",pady=3)
            card.pack_propagate(False)

            # Type indicator
            type_color=GAIN_COLOR if txn["type"]=="Income" else LOSS_COLOR
            indicator=ctk.CTkFrame(card,fg_color=type_color,width=4)
            indicator.pack(side="left",fill="y")

            # Title (left)
            ctk.CTkLabel(
                card,
                text=txn["title"],
                font=(fontfamily,12,"bold"),
                text_color=DARK["text"],
                anchor="w"
            ).pack(side="left",padx=12)

            # Amount (right)
            amount_prefix="+" if txn["type"]=="Income" else "-"
            ctk.CTkLabel(
                card,
                text=f"{amount_prefix}{currency} {int(txn['amount']):,}",
                font=(fontfamily,13,"bold"),
                text_color=type_color
            ).pack(side="right",padx=12)

    # Savings Card
    def AnimateChange(increment,AnimateTarget,delay):
        nonlocal saved,savings_progressbar,saved_label,target
        saved = saved + increment

        saved_label.configure(text=f"Saved : {saved}")
        try:
            val = saved / target
            savings_progressbar.set(val)
        except ZeroDivisionError:
            savings_progressbar.set(0)

        if saved < AnimateTarget:
            savingsCard.after(delay, lambda: AnimateChange(increment, AnimateTarget, delay))
        else:
            saved = AnimateTarget
            saved_label.configure(text=f"Saved : {saved}")
            saved_label.configure(font=(fontfamily,24,"bold"))
            return

    def addSavings():
        savingAmount=Value.get().strip() #strip to remove leading/trailing whitespace
        current_saved=saved
        try:
            amount=int(savingAmount)
        except ValueError:
            messagebox.showerror("Invalid Input","Please enter a valid number")
            return

        if amount <= 0:
            messagebox.showerror("Invalid Input","Please enter an amount greater than 0")
            return

        # updating user json
        change_savings(username,saved+amount)
        # UI
        duration=1000
        frame_delay=10
        frames=duration//frame_delay
        AnimateTarget=current_saved + amount
        increment = max(1, math.ceil(amount / frames))

        savingsCard.after(frame_delay,lambda:AnimateChange(increment,AnimateTarget,frame_delay))

    title=ctk.CTkLabel(savingsCard,text="Savings",font=(fontfamily,28,"bold"),text_color=DARK["text"])
    title.pack(padx=20,pady=10,anchor="w")
    target=user_json["budget"]["saving_goal"]
    target_text=ctk.CTkLabel(savingsCard,text=f"Target : {target}",font=(fontfamily,20),text_color=DARK["subtext"])
    target_text.pack(padx=20,pady=(0,20),anchor="w")
    saved=user_json["analytics"]["monthly_summary"]["savings"]
    saved_label=ctk.CTkLabel(savingsCard,text=f"Saved : {saved}",font=(fontfamily,24,"bold"),text_color=DARK["text"])
    saved_label.pack(padx=20,pady=16,anchor="w")
    savings_progressbar=ctk.CTkProgressBar(savingsCard,height=25,bg_color=DARK["card"],progress_color=SUCCESS)
    savings_progressbar.pack(padx=10,fill="x",side="bottom",pady=30)

    try:
        val=saved/target
        savings_progressbar.set(val)
    except:
        savings_progressbar.set(0)
    # add savings frame

    addFrame=ctk.CTkFrame(savingsCard,fg_color=DARK["card"],corner_radius=12,border_width=0)
    addFrame.place(relx=0.5,rely=0.64,anchor="w",relwidth=0.48)
    Value=ctk.StringVar(value=0)
    addValue=ctk.CTkEntry(addFrame,placeholder_text="Amount",textvariable=Value,font=(fontfamily,16),height=40,fg_color=DARK["frame"],border_width=0,corner_radius=12)
    addValue.pack(anchor="s",side="left",expand=True,fill="x",padx=(5,4),pady=8)  
    addValue.bind("<KeyPress>", lambda e: check_int(e))
    addValue.bind("<FocusIn>", lambda e: addValue.delete(0, 'end') if addValue.get() == "0" else None)
    
    addBtn=ctk.CTkButton(addFrame,text="+",font=("JetBrainsMono",28,"bold"),width=40,height=40,fg_color=PRIMARY,hover_color=PRIMARY_HOVER,corner_radius=12,command=addSavings)
    addBtn.pack(anchor="s",side="right",padx=(0,5),pady=8)

def transactions_tab(content_frame,user):
    clear_content(content_frame)
    data=open_user_json(user)
    transactions=data["data"]["transactions"]

    if not transactions or (len(transactions) == 1 and not transactions[0]):
        # Empty state - centered and minimal
        empty_container=ctk.CTkFrame(content_frame,fg_color="transparent")
        empty_container.place(anchor="center",relx=0.5,rely=0.5)

        ctk.CTkLabel(
            empty_container,
            text="No Transactions Yet",
            font=(fontfamily,20,"bold"),
            text_color=DARK["subtext"]
        ).pack(pady=(0,20))

        ctk.CTkButton(
            empty_container,
            text="+ Add Your First Transaction",
            width=220,
            height=45,
            corner_radius=10,
            fg_color=SUCCESS,
            hover_color=SUCCESS,
            text_color=DARK["bg"],
            font=(fontfamily,14,"bold"),
            command=lambda:new_transaction(user,Dashboard,content_frame,fill_topbar,topbar)
        ).pack()
    else:
        rows = len(transactions)

        # Zero-waste table container - every pixel counts
        table_container=ctk.CTkFrame(content_frame,fg_color=DARK["card"],corner_radius=12)
        table_container.pack(expand=True,fill="both",padx=20,pady=20)

        # Ultra-compact header - 42px total height
        header_row=ctk.CTkFrame(table_container,fg_color="transparent",height=42)
        header_row.pack(fill="x",padx=12,pady=(8,0))
        header_row.pack_propagate(False)

        # Left: Transaction count
        ctk.CTkLabel(
            header_row,
            text=f"{len(transactions)} Transactions",
            font=(fontfamily,14,"bold"),
            text_color=DARK["text"]
        ).pack(side="left",pady=9)

        # Right: Ultra-compact action pills
        actions=ctk.CTkFrame(header_row,fg_color="transparent")
        actions.pack(side="right",pady=9)

        # Delete button (appears on selection with count)
        delete_btn=ctk.CTkButton(
            actions,
            text="Delete",
            width=70,
            height=28,
            corner_radius=6,
            fg_color=DARK["frame"],
            hover_color=DANGER,
            text_color=DARK["subtext"],
            font=(fontfamily,11),
            border_width=1,
            border_color=DARK["border"],
            command=lambda:delete_transaction(user)
        )

        # New button - proper dark text contrast
        new_btn=ctk.CTkButton(
            actions,
            text="+ New",
            width=75,
            height=28,
            corner_radius=6,
            fg_color=SUCCESS,
            hover_color="#93d98e",
            text_color=DARK["bg"],
            font=(fontfamily,11,"bold"),
            command=lambda:new_transaction(user,Dashboard,content_frame,fill_topbar,topbar)
        )
        new_btn.pack(side="right")

        # Hair-thin divider (visual only, no spacing)
        ctk.CTkFrame(table_container,fg_color=DARK["border"],height=1).pack(fill="x",padx=12,pady=(6,0))

        # Maximum space table - absolutely zero wasted padding
        table_frame=ctk.CTkScrollableFrame(table_container,fg_color="transparent")
        table_frame.pack(expand=True,fill="both",padx=6,pady=(4,6))
        table_frame.rowconfigure(rows,uniform="a")
        table_frame.columnconfigure(0,weight=1,uniform="a")

        selected=[None,None]

        def hover_item(e):
            e.configure(fg_color=DARK["card_hover"])

        def unhover_item(e):
            e.configure(fg_color="transparent")

        def select_item(e,ID):
            nonlocal selected
            if selected[0]==None:
                selected[0]=e
                selected[1]=ID
                # Show delete button with selection indicator - minimal spacing
                delete_btn.configure(
                    text="Delete",
                    fg_color=DANGER,
                    text_color=DARK["bg"],
                    border_width=0
                )
                delete_btn.pack(side="right",padx=(0,6))
            else:
                selected[0].configure(border_color=DARK["card"])
                selected[0]=e
                selected[1]=ID
            e.configure(border_color=PRIMARY)

        # Table rows
        row_frame=[]
        for i in range(rows):
            txn = transactions[i]
            if txn["type"]=="Expense":
                color=LOSS_COLOR
            else:
                color=GAIN_COLOR

            row_frame.append(ctk.CTkFrame(table_frame,fg_color="transparent",border_width=1,border_color=DARK["card"]))
            row_frame[i].grid(row=i, column=0,columnspan=4, sticky="ew", padx=5, pady=5)

            row_frame[i].columnconfigure(0,weight=1,uniform="a")
            row_frame[i].columnconfigure(1,weight=4,uniform="a")
            row_frame[i].columnconfigure(2,weight=3,uniform="a")
            row_frame[i].columnconfigure(3,weight=2,uniform="a")
            row_frame[i].columnconfigure(4,weight=3,uniform="a")
            ctk.CTkLabel(row_frame[i], text=txn["id"],text_color=DARK["text"]).grid(row=0, column=0, padx=5, pady=5)
            ctk.CTkLabel(row_frame[i], text=txn["title"],text_color=DARK["text"]).grid(row=0, column=1, padx=5, pady=5)
            ctk.CTkLabel(row_frame[i], text=txn["amount"],text_color=color).grid(row=0, column=2, padx=5, pady=5)
            ctk.CTkLabel(row_frame[i], text=txn["date"],text_color=DARK["subtext"]).grid(row=0, column=3, padx=5, pady=5)
            ctk.CTkLabel(row_frame[i], text=txn["category"],text_color=DARK["subtext"]).grid(row=0, column=4, padx=5, pady=5)

            row_frame[i].bind("<Enter>", lambda e,index=i: hover_item(row_frame[index]))
            row_frame[i].bind("<Button-1>", lambda e,index=i,ID=txn["id"]: select_item(row_frame[index],ID))
            row_frame[i].bind("<Leave>", lambda e,index=i: unhover_item(row_frame[index]))

            for child in row_frame[i].winfo_children():
                child.bind("<Enter>", lambda e,index=i: hover_item(row_frame[index]))
                child.bind("<Button-1>", lambda e,index=i,ID=txn["id"]: select_item(row_frame[index],ID))
                child.bind("<Leave>", lambda e,index=i: unhover_item(row_frame[index]))

        def delete_transaction(user):
            uid=selected[1]
            deleted_amount=0
            deleted_expense=True

            if uid==None:
                messagebox.showerror("No Transaction Selected","Please select a transaction to delete")
                return

            # Find and remove transaction
            for txn in transactions[:]:
                if txn["id"]==uid:
                    deleted_amount=txn["amount"]
                    deleted_expense=txn["type"]=="Expense"
                    transactions.remove(txn)
                    break

            # Renumber all IDs
            for i in range(len(transactions)):
                transactions[i]["id"]=i+1

            #updating userFile
            data=open_user_json(user)
            data["data"]["transactions"]=transactions
            if deleted_expense:
                data["data"]["balance"]+=deleted_amount
                data["budget"]["current_spent"]-=deleted_amount
                data["analytics"]["monthly_summary"]["Expense"]-=deleted_amount
            if not deleted_expense:
                data["data"]["balance"]-=deleted_amount
                data["analytics"]["monthly_summary"]["income"]-=deleted_amount
            write_json(f"data/users/{user}.json",data)

            fill_topbar(user,topbar)
            messagebox.showinfo("Deleted",f"Transaction Deleted successfully\nid:{uid}")
            transactions_tab(content_frame,user)

        # expose delete action for global keybinds
        global current_delete_transaction
        current_delete_transaction = lambda: delete_transaction(user)
    
def budget_tab(content_frame, username):
    clear_content(content_frame)

    def update_threshold():
        new_threshold=threshold_entry.get()
        try:
            new_threshold=int(new_threshold)
            update_user_threshold(username,new_threshold)
            messagebox.showinfo("Updated","Alert threshold updated successfully")
            threshold_entry.delete(0, 'end')
            threshold_entry.insert(0, str(new_threshold))
            recall_budget_tab(budget_tab,content_frame,username)
            return
        except:
            messagebox.showerror("Invalid Input","Please enter a valid number")
            threshold_entry.delete(0, 'end')
            threshold_entry.insert(0, str(threshold))
            return

    def edit_budget():
        from utils.file_handler import change_budget_limit
        #the ui!
        menu=ctk.CTkInputDialog(text="Enter new monthly limit")
        new_limit=menu.get_input()
        try:
            new_limit=int(new_limit)
            change_budget_limit(username,new_limit)
            messagebox.showinfo("Success","Monthly limit updated successfully")
            #reload UI
            recall_budget_tab(budget_tab,content_frame,username)            
        except:
            messagebox.showerror("Invalid Input","Please enter a valid number")
            return

    def edit_savings(username):
        conformation_message="""Are you sure you want to edit the savings amount?\nThis action will ovrewrite the current saving amount with the new value you will enter\nTo add savings to your account go to the Dashboard tab and use the add savings option"""
        conformation=messagebox.askyesno("Confirmation",conformation_message)
        if not conformation:
            return
        menu=ctk.CTkInputDialog(text="Enter new savings amount")
        new_saving=menu.get_input()
        try:
            new_saving=int(new_saving)
            change_savings(username,new_saving)
            messagebox.showinfo("Success","Savings updated successfully")
            #reload UI
            recall_budget_tab(budget_tab,content_frame,username)            
        except:
            messagebox.showerror("Invalid Input","Please enter a valid number")
            return    
    
    # Create a scrollable frame with grid layout inside content_frame
    main_scroll_frame = ctk.CTkScrollableFrame(
        content_frame,
        fg_color=DARK["bg"],
        corner_radius=0
    )
    main_scroll_frame.pack(expand=True, fill="both")
    
    # Grid configuration on the scrollable frame - 3 columns always available
    main_scroll_frame.grid_columnconfigure(0, weight=1)
    main_scroll_frame.grid_columnconfigure(1, weight=1)
    main_scroll_frame.grid_columnconfigure(2, weight=1)
    
    main_scroll_frame.grid_rowconfigure(0, weight=0, minsize=200)   # Row 0: 3 cards
    main_scroll_frame.grid_rowconfigure(1, weight=0, minsize=140)   # Row 1: Progress bar
    main_scroll_frame.grid_rowconfigure(2, weight=0, minsize=140)   # Row 2: Quick Stats + Edit
    main_scroll_frame.grid_rowconfigure(3, weight=0, minsize=120)    # Row 3: Extra
    main_scroll_frame.grid_rowconfigure(4, weight=0, minsize=80)    # Row 4: Extra
    main_scroll_frame.grid_rowconfigure(5, weight=0, minsize=80)    # Row 5: Extra
    main_scroll_frame.grid_rowconfigure(6, weight=0, minsize=80)
    main_scroll_frame.grid_rowconfigure(7, weight=1)                # Extra space

    # Function to handle responsive layout
    # Function to handle responsive layout
    def update_layout():
        available_width = content_frame.winfo_width() - 60  # Account for padding
        
        if available_width < 500:
            # Single column layout - stack vertically
            budget_status_card.grid(row=0, column=0, columnspan=3, padx=7.5, pady=7.5, sticky="nsew")
            card2.grid(row=1, column=0, columnspan=3, padx=7.5, pady=7.5, sticky="nsew")
            card3.grid(row=2, column=0, columnspan=3, padx=7.5, pady=7.5, sticky="nsew")
            card4.grid(row=3, column=0, columnspan=3, padx=7.5, pady=7.5, sticky="nsew")
            card_target.grid(row=4, column=0, columnspan=3, padx=7.5, pady=7.5, sticky="nsew")
            card5.grid(row=5, column=0, columnspan=3, padx=7.5, pady=7.5, sticky="nsew")
            card6.grid(row=6, column=0, columnspan=3, padx=7.5, pady=7.5, sticky="nsew")
            card7.grid(row=7, column=0, columnspan=3, padx=7.5, pady=7.5, sticky="nsew")
            
        elif available_width < 1500:
            # Two column layout
            budget_status_card.grid(row=0, column=0, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card2.grid(row=0, column=1, columnspan=2, padx=7.5, pady=7.5, sticky="nsew")
            card3.grid(row=1, column=0, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card4.grid(row=1, column=1, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card_target.grid(row=1, column=2, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card5.grid(row=2, column=0, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card6.grid(row=2, column=1, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card7.grid(row=2, column=2, columnspan=1, padx=7.5, pady=7.5, sticky="nsew") 
            
        else:
            # Three column layout
            budget_status_card.grid(row=0, column=0, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card2.grid(row=0, column=1, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card3.grid(row=0, column=2, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card4.grid(row=1, column=0, columnspan=2, padx=7.5, pady=7.5, sticky="nsew")
            card_target.grid(row=1, column=2, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card5.grid(row=2, column=0, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card6.grid(row=2, column=1, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
            card7.grid(row=2, column=2, columnspan=1, padx=7.5, pady=7.5, sticky="nsew")
    # Get data
    data = open_user_json(username)
    budget_data = data["budget"]
    monthly_income = data["data"]["monthly_income"]
    balance = data["data"]["balance"]
    monthly_limit = budget_data["monthly_limit"]
    spent = budget_data["current_spent"]
    currency = data["profile"]["currency"]
    saving = data["analytics"]["monthly_summary"]["savings"]
    target = data.get("budget", {}).get("saving_goal", 0)
    try:
        spent_percent=float(round(spent/monthly_limit*100,2))
    except ZeroDivisionError:
        spent_percent=0
    threshold=data["budget"]["threshold_percent"]
    
    # Determine status color based on spending level
    if spent_percent<threshold:
        status_color=SUCCESS  # Green
        index=0
    elif spent_percent<100:
        status_color=WARNING  # Yellow
        index=1
    else:
        status_color=DANGER  # Red
        index=2
    
    # ===== ROW 0: BUDGET STATUS CARD =====
    budget_status_card = ctk.CTkFrame(main_scroll_frame,fg_color=DARK['card'],border_width=1,border_color=DARK["border"],corner_radius=15)

    title=ctk.CTkLabel(budget_status_card,text="Budget Status",font=(fontfamily,16,"bold"),text_color=DARK["text"])
    Monthly_Limit=ctk.CTkLabel(budget_status_card,text=f"Monthly Limit:{monthly_limit:,}",font=(fontfamily,12),text_color=DARK["subtext"])
    amount_display=ctk.CTkLabel(budget_status_card,text=f"{currency} {int(spent):,}({'100+' if spent_percent>100 else f'{spent_percent:.1f}'}%)",font=(fontfamily,32,"bold"),text_color=DARK["primary"])
    title.pack(anchor="w",padx=(20,0),pady=(15, 10))
    Monthly_Limit.pack(anchor="w",padx=20)
    amount_display.pack(anchor="w",padx=20,pady=(0,10))

    #progressbarr part
    spent_bar=ctk.CTkProgressBar(budget_status_card,height=12,corner_radius=6,bg_color=DARK["card"])
    spent_bar.pack(anchor="w",padx=20,pady=(0,12),fill="x")
    spent_bar.set(min(spent_percent/100, 1.0))
    spent_bar.configure(progress_color=status_color)

    badge_txt=["On Track","Caution","Over Budget"]
    badge=ctk.CTkLabel(budget_status_card,text=badge_txt[index],text_color=DARK["bg"],fg_color=status_color,font=(fontfamily,12,"bold"),corner_radius=8)
    badge.pack(anchor="e",side="bottom",padx=12,pady=12)

    # ===== ROW 1: INCOME v/s SPENDING =====
    card2=ctk.CTkFrame(main_scroll_frame,fg_color=DARK['card'],border_width=1,border_color=DARK["border"],corner_radius=15)
    title2=ctk.CTkLabel(card2,text="Income v/s Spending",font=(fontfamily,16,"bold"),text_color=DARK["text"])
    title2.pack(anchor="w",padx=(20,0),pady=(15, 10))
    comparison_frame=ctk.CTkFrame(card2,fg_color="transparent")
    comparison_frame.pack(side="bottom",expand=True,fill="both",padx=20,pady=(0,40))
    comparison_frame.columnconfigure((0,2),weight=20)
    comparison_frame.columnconfigure(1,weight=1)
    comparison_frame.rowconfigure(0,weight=1)
    comparison_frame.rowconfigure(1,weight=8)
    label_income=ctk.CTkLabel(comparison_frame,text="Monthly Income",font=(fontfamily,12),text_color=DARK["subtext"])
    label_income.grid(row=0,column=0,sticky="e",padx=20,pady=(10,0))
    income=ctk.CTkLabel(comparison_frame,text=f"\u2191 {currency} {int(monthly_income):,}",font=(fontfamily,28),text_color=GAIN_COLOR)
    income.grid(row=1,column=0,sticky="e",padx=20,pady=(10,0))

    divider=ctk.CTkLabel(comparison_frame,text="v/s",font=(fontfamily,16,"bold"),text_color=DARK["subtext"])
    divider.grid(row=0,column=1,sticky="ew",padx=10,pady=(10,0))

    label_spent=ctk.CTkLabel(comparison_frame,text=f"Spent",font=(fontfamily,12),text_color=DARK["subtext"])
    label_spent.grid(row=0,column=2,sticky="w",padx=20,pady=(10,0))
    spent_lbl=ctk.CTkLabel(comparison_frame,text=f"\u2193 {currency} {int(spent):,}",font=(fontfamily,28),text_color=LOSS_COLOR)
    spent_lbl.grid(row=1,column=2,sticky="w",padx=20,pady=(10,0))

    #===== ROW 2: SAVINGS CARD=====
    card3=ctk.CTkFrame(main_scroll_frame,fg_color=DARK['card'],border_width=2,border_color=PRIMARY,corner_radius=15) #highlighted border
    title3=ctk.CTkLabel(card3,text="Monthly Savings",font=(fontfamily,16,"bold"),text_color=DARK["text"])
    title3.pack(anchor="w",padx=(20,0),pady=(15, 10))
    savings=ctk.CTkLabel(card3,text=f"{currency} {int(saving):,}",font=(fontfamily,28),text_color=GAIN_COLOR)
    savings.pack(anchor="w",padx=(20,0),pady=(0, 10))

    saving_percent=saving/monthly_income*100 if monthly_income>0 else 100
    saving_percent_lbl=ctk.CTkLabel(card3,text=f"{saving_percent:.1f}% of Income",font=(fontfamily,12),text_color=DARK["subtext"])
    saving_percent_lbl.pack(anchor="w",padx=(20,0),pady=(0, 10))

    edit_btn=ctk.CTkButton(card3,text="Edit",font=(fontfamily, 16,"bold"),width=40,height=30,corner_radius=8,fg_color=PRIMARY,hover_color=PRIMARY_HOVER,command=lambda:edit_savings(username))
    edit_btn.place(anchor="se",relx=1,rely=1,x=-12,y=-12)

    # ===== ROW X: SAVINGS TARGET CARD =====
    card_target = ctk.CTkFrame(main_scroll_frame, fg_color=DARK['card'], border_width=1, border_color=DARK['border'], corner_radius=15)
    t_title = ctk.CTkLabel(card_target, text="Savings Target", font=(fontfamily,16,"bold"), text_color=DARK['text'])
    t_title.pack(anchor="w", padx=(20,0), pady=(15, 10))
    t_display = ctk.CTkLabel(card_target, text=f"Target: {currency} {int(target):,}", font=(fontfamily,20), text_color=DARK['subtext'])
    t_display.pack(anchor="w", padx=20, pady=(0, 10))

    # simple inline update controls (minimal variables)
    t_entry_var = ctk.StringVar(value=str(target))
    t_entry = ctk.CTkEntry(card_target, textvariable=t_entry_var, width=200, height=36, placeholder_text="Enter new target", fg_color=DARK['bg'], border_color=DARK['border'], text_color=DARK['text'])
    t_entry.pack(anchor="w", padx=20, pady=(0,10))
    def update_target():
        val = t_entry_var.get().strip()
        try:
            new = int(val) if val != "" else 0
        except ValueError:
            from tkinter import messagebox
            messagebox.showerror("Invalid","Please enter a valid number")
            return
        data["budget"]["saving_goal"] = new
        write_json(f"data/users/{username}.json", data)
        t_display.configure(text=f"Target: {currency} {int(new):,}")
    t_btn = ctk.CTkButton(card_target, text="Update Target", width=160, height=36, fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=update_target)
    t_btn.pack(anchor="w", padx=20, pady=(0,20))

    #===== CARD 4: BUDGET PROGRESS CARD ====
    card4=ctk.CTkFrame(main_scroll_frame,fg_color=DARK['card'],border_width=1,border_color=DARK["border"],corner_radius=15)
    title4=ctk.CTkLabel(card4,text="Budget Progress",font=(fontfamily,16,"bold"),text_color=DARK["text"])
    title4.pack(anchor="w",padx=(20,0),pady=(15, 10))
    info=ctk.CTkLabel(card4,text=f"You have spent {spent_percent:.1f}% of your monthly budget",font=(fontfamily,12),text_color=DARK["subtext"])
    info.pack(anchor="w",padx=(20,0),pady=(0, 10))
    progress_bar=ctk.CTkProgressBar(card4,height=20,corner_radius=10,bg_color=DARK["card"])
    progress_bar.pack(fill="x",padx=20,pady=(0, 20))
    progress_bar.set(min(spent_percent/100, 1.0))
    progress_bar.configure(progress_color=status_color)

    #===== CARD 5: QUICK STATS CARD =====
    card5=ctk.CTkFrame(main_scroll_frame,fg_color=DARK['card'],border_width=1,border_color=DARK["border"],corner_radius=15)
    title5=ctk.CTkLabel(card5,text="Quick Stats",font=(fontfamily,16,"bold"),text_color=DARK["text"])
    title5.pack(anchor="w",padx=(20,0),pady=(15, 10))
    days_left=get_days_remaining_in_month()
    days_remaining=ctk.CTkLabel(card5,text=f"\U0001F4C5 Days Remaining: {days_left}",font=(fontfamily,12),text_color=DARK["subtext"])
    days_remaining.pack(anchor="w",padx=(20,0),pady=(0, 10))
    total_days=get_total_days()
    daily_avg=int(spent/int(total_days-days_left) if days_left>0 else 0)
    daily_average=ctk.CTkLabel(card5,text=f"\U0001F4CA Daily Average: {currency} {daily_avg:.2f}/ Day",font=(fontfamily,12),text_color=DARK["subtext"])
    daily_average.pack(anchor="w",padx=(20,0),pady=(0, 10))
    suggesstions_txt=["You are doing Well.","Try to limit unnecessary expenses.","No more money left in balance to spend"]
    suggesstions_lbl=ctk.CTkLabel(card5,text=f"\U0001F914 Suggestion: {suggesstions_txt[index]}",font=(fontfamily,12),text_color=DARK["subtext"])
    suggesstions_lbl.pack(anchor="w",padx=(20,0),pady=(0, 10))

    #=====CARD 6: EDIT BUDGET CARD =====
    card6=ctk.CTkFrame(main_scroll_frame,fg_color=DARK['card'],border_width=1,border_color=DARK["border"],corner_radius=15)
    title6=ctk.CTkLabel(card6,text="Edit Budget",font=(fontfamily,16,"bold"),text_color=DARK["text"])
    title6.pack(anchor="w",padx=(20,0),pady=(15))
    current_data=ctk.CTkLabel(card6,text=f"{currency} {int(monthly_limit):,}",font=(fontfamily,28),text_color=DARK["subtext"])
    current_data.pack(anchor="w",padx=(20,0),pady=(0, 10))
    edit_btn=ctk.CTkButton(card6,text="Edit Monthly Limit",width=200,height=40,corner_radius=10,fg_color=PRIMARY,hover_color=PRIMARY_HOVER,command=edit_budget)
    edit_btn.pack(anchor="w",padx=(20,0),pady=(0, 20))

    #=====CARD 7: ALERT THRESHOLD CARD =====

    card7 = ctk.CTkFrame(main_scroll_frame, fg_color=DARK['card'], border_width=1, border_color=DARK["border"], corner_radius=15)
    title7 = ctk.CTkLabel(card7, text="Alert Settings", font=(fontfamily, 16, "bold"), text_color=DARK["text"])
    title7.pack(anchor="w", padx=(20,0), pady=(15, 10))
    edit_threshold_lbl = ctk.CTkLabel(card7, text=f"Current Threshold: {threshold}%", font=(fontfamily, 12), text_color=DARK["subtext"])
    edit_threshold_lbl.pack(anchor="w", padx=(20,0), pady=(0, 10))
    threshold_entry = ctk.CTkEntry(card7, height=40, corner_radius=10, placeholder_text=f"{threshold}", placeholder_text_color=DARK["subtext"], fg_color=DARK["bg"], border_color=DARK["border"])
    threshold_entry.pack(anchor="w",fill="x", padx=20, pady=(0, 20))
    cnf_btn = ctk.CTkButton(card7, text="Confirm", height=40, corner_radius=10, fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=update_threshold)
    cnf_btn.pack(anchor="w",fill="x", padx=20, pady=(0, 20))
    # Bind resize event to update layout

    resize_timer=None

    def resize_debounce(e):
        nonlocal resize_timer
        if resize_timer is not None:
            content_frame.after_cancel(resize_timer)  # Cancel the pending update
        # 120ms is the perfect quality/performance balance
        resize_timer = content_frame.after(120, update_layout)

    content_frame.bind("<Configure>", lambda e: resize_debounce(e))
    update_layout()  # Initial layout setup

def setting(content_frame, username, current_theme="dark"):
    clear_content(content_frame)
    data = read_json(f"data/users/{username}.json")

    # Select theme dict
    THEME = DARK if current_theme == "dark" else LIGHT

    # ===== Container Card =====
    top_left_card=ctk.CTkFrame(content_frame,bg_color="transparent",fg_color="transparent")
    top_left_card.pack(anchor="nw")

    theme_card = ctk.CTkFrame(top_left_card,fg_color=THEME["card"],corner_radius=15,border_width=2,border_color=THEME["border"])
    theme_card.pack(side="left",padx=30, pady=30,anchor="nw")

    # ===== Title =====
    title = ctk.CTkLabel(theme_card,text="Appearance",font=(fontfamily, 26, "bold"),text_color=THEME["text"])
    title.pack(anchor="w", padx=20, pady=(15, 5))
    subtitle = ctk.CTkLabel(theme_card,text="Choose your theme",font=(fontfamily, 16),text_color=THEME["subtext"])
    subtitle.pack(anchor="w", padx=20, pady=(0, 15))

    theme_var = ctk.StringVar()

    def update_var(value):
        # print("Theme:", value)
        data["settings"]["theme"] = value
        write_json(f"data/users/{username}.json", data)

    # ===== Segmented Button (BIG + Styled) =====
    themeToggle = ctk.CTkSegmentedButton(
        theme_card,
        values=["dark", "light"],
        variable=theme_var,
        command=update_var,

        # Styling
        width=300,
        height=45,
        corner_radius=10,

        fg_color=THEME["frame"],
        selected_color=THEME["primary"],
        selected_hover_color=THEME["primary_hover"],
        unselected_color=THEME["card"],
        text_color=THEME["text"],
        font=(fontfamily, 16, "bold")
    )
    themeToggle.pack(padx=20, pady=(0, 20))

    # ===== Set Default =====
    current = data.get("settings", {}).get("theme", "dark")
    themeToggle.set(current)

    #-------------------------------------------------------------------------------------------------------------------

    currency_card = ctk.CTkFrame(top_left_card,fg_color=THEME["card"],corner_radius=15,border_width=2,border_color=THEME["border"])
    currency_card.pack(side="left",padx=(0,30), pady=30,anchor="nw")
    # ===== Title =====
    title2 = ctk.CTkLabel(currency_card,text="Currency",font=(fontfamily, 26, "bold"),text_color=THEME["text"])
    title2.pack(anchor="w", padx=20, pady=(15, 5))
    subtitle2 = ctk.CTkLabel(currency_card,text="Choose your Currency",font=(fontfamily, 16),text_color=THEME["subtext"])
    subtitle2.pack(anchor="w", padx=20, pady=(0, 15))

    def SwitchCurrency(value):
        data["profile"]["currency"]=value
        write_json(f"data/users/{username}.json",data)

    currency_menu=ctk.CTkOptionMenu(
        currency_card,
        values=["USD","INR","EUR","GBP"],
        command=SwitchCurrency,
        # Styling
        width=300,
        height=45,
        corner_radius=10,

        fg_color=THEME["frame"],
        text_color=THEME["text"],
        dropdown_fg_color=THEME["frame"],
        button_color=THEME["primary"],
        button_hover_color=THEME["primary_hover"],
        dropdown_hover_color=THEME["card"],
        font=(fontfamily, 16, "bold")
    )
    currency_menu.pack(padx=20, pady=(0, 20))

    currency_menu.set(data["profile"]["currency"])

    #------------------------------------------------------------------------------------------------------------------------------------------------------
    password_Frame=ctk.CTkFrame(content_frame,bg_color="transparent",fg_color="transparent")
    password_Frame.pack(anchor="nw",padx=30)
    password_card = ctk.CTkFrame(password_Frame,fg_color=THEME["card"],corner_radius=15,border_width=2,border_color=THEME["border"])
    password_card.pack(side="left",padx=(0,30), pady=30,anchor="nw")
    # ===== Title =====
    title3 = ctk.CTkLabel(password_card,text="Change Password",font=(fontfamily, 26, "bold"),text_color=THEME["text"])
    title3.pack(anchor="w", padx=20, pady=(15, 5))
    subtitle3 = ctk.CTkLabel(password_card,text="Enter your new password",font=(fontfamily, 16),text_color=THEME["subtext"])
    subtitle3.pack(anchor="w", padx=20, pady=(0, 15))

    passEntry=ctk.CTkEntry(
        password_card,
        width=300,
        height=45,
        corner_radius=10,

        fg_color=THEME["card"],
        border_color=PRIMARY,
        placeholder_text_color=THEME["subtext"],
        text_color=THEME["text"],
        placeholder_text=data["auth"]["password"],
        font=(fontfamily, 16, "bold")
    )
    update_btn=ctk.CTkButton(
        password_card,
        text="UPDATE",
        command=lambda:update_password(username,passEntry.get()),
        width=300,
        height=45,
        corner_radius=10,

        fg_color=PRIMARY,
        hover_color=PRIMARY_HOVER,
        border_color=YELLOW_BORDER,
        text_color=THEME["text"]
    )

    passEntry.pack(padx=20, pady=(0, 20))
    update_btn.pack(padx=20, pady=(0, 20))

    # _____________________________________________________________________________________________________________________________________________

    button_frame=ctk.CTkFrame(content_frame,fg_color="transparent")
    button_frame.place(relx=1,rely=0,x=-30,y=30,anchor="ne")

    def reset():
        status=messagebox.askyesno(title="Are you sure?",message="All your transaction histories and customizations will be removed and cannot be recovered.\nAre you sure you want to reset your data?\nNote:The 5 preferences asked at account creation will not be cleared.")
        if status:
            reset_userdata(username)
            msg="All data of your account cleared except authentication data,profile(includes name and currency),monthly limit,threshold percent, and your theme preference\nTodelete your account you can click on Delete Account button in the Settings tab."
            messagebox.showinfo("Deletion Completed",msg)

    reset_btn=ctk.CTkButton(
        button_frame,
        text="RESET",
        command=reset,
        width=150,
        height=45,
        corner_radius=10,

        fg_color=WARNING,
        hover_color=WARNING,
        border_color=YELLOW_BORDER,
        text_color=DARK["bg"]
    )
    reset_btn.pack(pady=10)

    def deletion():
        status=messagebox.askyesno("Are you sure?","This action will delete all your data and it is not recoverable.\nWould you like to proceed?")
        askPass=ctk.CTkInputDialog(text="Enter your password",title="Verifcation Required")
        entered_password=askPass.get_input()
        data=open_user_json(username)
        password=data["auth"]["password"]

        if status:
            if entered_password==password:
                delete(username)
                quit()
            else:
                messagebox.showerror("Invalid Credentials","Enter valid password to delete account.")

    delete_btn=ctk.CTkButton(
        button_frame,
        text="DELETE",
        command=deletion,
        width=150,
        height=45,
        corner_radius=10,

        fg_color=DANGER,
        hover_color=DANGER,
        border_color=RED_BORDER,
        text_color=THEME["text"]
    )
    delete_btn.pack(pady=10)

    def forgot():
        forgot_user()
        messagebox.showinfo("Done","Now the user will not be automatically logged in")
        forgot_btn.configure(state="disabled")

    forgot_btn=ctk.CTkButton(button_frame,text="Show Login Window",width=150,height=45,corner_radius=10,fg_color=WARNING,hover_color=WARNING,border_color=YELLOW_BORDER,text_color=DARK["bg"],command=forgot)
    forgot_btn.pack(pady=10)

    if get_remember_default()["remember"]==1:
        forgot_btn.configure(state="enabled")
    else:
        forgot_btn.configure(state="disabled")


    #########################################################################################################################################################3

def main_ui(username,theme,login,remember):
    ###3 remember me feat
    data=get_remember_default()
    data["remember"]=remember
    if remember:
        data["username"]=username
    else:
        data["username"]=""
    write_json("data/app.json",data)
    #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$44
    font=ctk.FontManager.load_font(data.get("font","ui/assets/manrope-medium.ttf"))
    global fontfamily
    fontfamily="Manrope"
################################################################3
    try:
        login.destroy()
    except:
        pass

    root=ctk.CTk()
    root.title("Expense IQ: Expend Conciously")
    root.configure(fg_color=(LIGHT["bg"],DARK["bg"]))
    root.minsize(1200,560)
    

    centered_window(root,1280,720)
    root._set_appearance_mode(theme)
    # active tab tracking for context-aware keybinds
    #####################################################################
    active_tab = "dashboard"
    def switch_tab(tab_name, callback):
        nonlocal active_tab
        active_tab = tab_name
        callback(content_frame, username)
        # if overlay is currently visible, refresh its highlight to reflect new active tab
        try:
            if overlay_bg.winfo_viewable():
                try:
                    highlight_active()
                except NameError:
                    pass
        except NameError:
            # overlay not created yet
            pass
        
    ####### SIDEBAR ######################################################################################
    sidebar=ctk.CTkFrame(root,width=200,border_color=BLUE_BORDER,fg_color=(LIGHT["frame"],DARK["frame"]))
    sidebar.pack(side="left",fill="y")
    sidebar.pack_propagate(False)
    #------ SIDEBAR BUTTONS ------------------------------------------------------------------------------
    today=ctk.CTkLabel(sidebar,text=str(get_today()),font=(fontfamily,20,"bold"),fg_color="transparent")
    day=ctk.CTkLabel(sidebar,text=str(get_weekday_formatted()),font=(fontfamily,16,"bold"),fg_color="transparent")
    dashboard=ctk.CTkButton(sidebar,text="Dashboard",font=(fontfamily,24,"bold"),fg_color=DARK["card"],hover_color=DARK["border"],corner_radius=10,border_color=PRIMARY_HOVER,border_width=1,height=45,command=lambda: switch_tab('dashboard', Dashboard))
    transaction=ctk.CTkButton(sidebar,text="Transaction",font=(fontfamily,24,"bold"),fg_color=DARK["card"],hover_color=DARK["border"],corner_radius=10,border_color=PRIMARY_HOVER,border_width=1,height=45,command=lambda: switch_tab('transactions', transactions_tab))
    budget=ctk.CTkButton(sidebar,text="Budget",font=(fontfamily,24,"bold"),fg_color=DARK["card"],hover_color=DARK["border"],corner_radius=10,border_color=PRIMARY_HOVER,border_width=1,height=45,command=lambda: switch_tab('budget', budget_tab))
    analytics=ctk.CTkButton(sidebar,text="Analytics",font=(fontfamily,24,"bold"),fg_color=DARK["card"],hover_color=DARK["border"],corner_radius=10,border_color=PRIMARY_HOVER,border_width=1,height=45)
    settings=ctk.CTkButton(sidebar,text="Settings",font=(fontfamily,24,"bold"),fg_color=DARK["card"],hover_color=DARK["border"],corner_radius=10,border_color=PRIMARY_HOVER,border_width=1,height=45,command=lambda:setting(content_frame,username))
    logout=ctk.CTkButton(sidebar,text="Logout",font=(fontfamily,24,"bold"),fg_color=DARK["card"],hover_color=DANGER,corner_radius=10,border_color=RED_BORDER,border_width=1,height=45,command=lambda:[root.quit(),root.after(10,quit())]) # used quit instead of destroy to quit safely

    today.pack(pady=(15,0),padx=10,fill="x")
    day.pack(pady=(0,15),padx=10,fill="x")
    dashboard.pack(pady=10,padx=10,fill="x")
    transaction.pack(pady=10,padx=10,fill="x")
    budget.pack(pady=10,padx=10,fill="x")
    analytics.pack(pady=10,padx=10,fill="x")
    logout.pack(pady=10,padx=10,fill="x",side="bottom")
    settings.pack(pady=10,padx=10,fill="x",side="bottom")
    #################################################################################################
    global topbar
    topbar=ctk.CTkFrame(root,height=50,border_color=BLUE_BORDER,fg_color=(LIGHT["frame"],DARK["frame"]),corner_radius=0)
    topbar.pack(side="top",fill="x")
    topbar.pack_propagate(False)

    fill_topbar(username,topbar)

    content_frame=ctk.CTkFrame(root,border_color=BLUE_BORDER,fg_color=(LIGHT["frame"],DARK["frame"]))
    content_frame.pack(expand=True,fill="both",padx=20,pady=20)

    # render initial dashboard via the switch wrapper so active_tab is correct
    switch_tab('dashboard', Dashboard)

    # keybinds and overlay (context-aware)
    root.bind("<Control-b>", lambda e: switch_tab('budget', budget_tab))
    root.bind("<Control-t>", lambda e: switch_tab('transactions', transactions_tab))
    root.bind("<Control-d>", lambda e: switch_tab('dashboard', Dashboard))
    root.bind("<Control-w>", lambda e: [root.quit(), root.after(10, quit())])
    root.bind("<Control-B>", lambda e: switch_tab('budget', budget_tab))
    root.bind("<Control-T>", lambda e: switch_tab('transactions', transactions_tab))
    root.bind("<Control-D>", lambda e: switch_tab('dashboard', Dashboard))
    root.bind("<Control-W>", lambda e: [root.quit(), root.after(10, quit())])

    # overlay as a full-size Frame (single-window approach)
    overlay_bg = ctk.CTkFrame(root, fg_color=DARK["bg"])
    overlay_bg.place_forget()

    # simulate translucency by using a dark background with lowered visual weight
    try:
        overlay_bg.configure(fg_color=DARK["bg"])
    except Exception:
        overlay_bg.configure(fg_color=DARK["bg"])

    overlay_card = ctk.CTkFrame(overlay_bg, fg_color=DARK["card"], corner_radius=16, border_width=1, border_color=DARK["border"]) 
    # center card inside overlay
    overlay_card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.7)

    # section labels mapping for dynamic highlighting
    overlay_labels = {}

    def build_overlay_contents():
        for w in overlay_card.winfo_children():
            w.destroy()
        title = ctk.CTkLabel(overlay_card, text="Keybinds", font=(fontfamily,24,"bold"), text_color=PRIMARY)
        title.pack(pady=(12,6))

        sections = {
            'global': [("Dashboard", "Ctrl D"), ("Transactions", "Ctrl T"), ("Budget", "Ctrl B"), ("Settings", "Ctrl S"), ("Logout", "Ctrl W")],
            'transactions': [("New Transaction", "Ctrl N"), ("Delete Selected", "Ctrl Delete")],
            'budget': [("Edit Budget", "Ctrl E"), ("Update Threshold", "Ctrl U")],
            'settings': [("Reset Data", "Ctrl R"), ("Show Login", "Ctrl F")]
        }

        def make_section(name, items):
            frm = ctk.CTkFrame(overlay_card, fg_color="transparent")
            frm.pack(fill="x", padx=20, pady=6)
            hdr = ctk.CTkLabel(frm, text=name.title() + "", font=(fontfamily,18,"bold"))
            hdr.pack(anchor="w")
            overlay_labels[name] = hdr
            for it in items:
                row = ctk.CTkFrame(frm, fg_color="transparent")
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=it[0], font=(fontfamily,14)).pack(side="left", anchor="w")
                ctk.CTkLabel(row, text=it[1], font=(fontfamily,14), fg_color=DARK["card"], corner_radius=8).pack(side="right")

        make_section("global", sections['global'])
        make_section("transactions", sections['transactions'])
        make_section("budget", sections['budget'])
        # make_section("settings", sections['settings'])

    def highlight_active():
        # reset
        for name, lbl in overlay_labels.items():
            lbl.configure(text_color=DARK["text"], fg_color="transparent")
        # highlight current (map dashboard -> global group)
        map_name = 'global' if active_tab == 'dashboard' else active_tab
        if map_name in overlay_labels:
            overlay_labels[map_name].configure(text_color=PRIMARY, fg_color=DARK["card_hover"]) 

    def toggle_overlay(event=None):
        # show as a translucent top-level sized to the main window
        if overlay_bg.place_info():
            overlay_bg.place_forget()
        else:
            # show overlay sized to root (single-window) and lift it above other widgets
            root.update_idletasks()
            overlay_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
            overlay_bg.lift()
            build_overlay_contents()
            highlight_active()
            # clicking outside the card hides the overlay
            def on_overlay_click(e):
                if e.widget is overlay_bg:
                    overlay_bg.place_forget()
            overlay_bg.bind("<Button-1>", on_overlay_click)

    # key bindings
    root.bind("<Control-k>", toggle_overlay)
    root.bind("<Control-K>", toggle_overlay)
    root.bind("<Escape>", lambda e: overlay_bg.place_forget())
    root.bind("<Control-n>", lambda e: new_transaction(username, Dashboard, content_frame, fill_topbar, topbar) if active_tab=="transactions" else None)
    root.bind("<Control-N>", lambda e: new_transaction(username, Dashboard, content_frame, fill_topbar, topbar) if active_tab=="transactions" else None)
    root.bind("<Control-Delete>", lambda e: current_delete_transaction() if active_tab=="transactions" and current_delete_transaction else None)

    root.mainloop()
