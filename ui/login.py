import customtkinter as ctk
from tkinter import ttk,messagebox
from PIL import Image
import json
from ui.theme import *
from utils.file_handler import get_user,check_user_exist,signupUser,open_user_json,get_remember_default
from ui.main_ui import main_ui

def centered_window(parent,width,height):
    screen_width=parent.winfo_screenwidth()
    screen_height=parent.winfo_screenheight()
    x=screen_width//2-width//2
    y=screen_height//2-height//2
    parent.geometry(f"{width}x{height}+{x}+{y}")

    

def login_window(on_login):
    global current_mode
    root=ctk.CTk()
    root.title("Expense IQ: Expend Conciously")
    root.configure(fg_color=(LIGHT["bg"],DARK["bg"]))
    # root._set_appearance_mode("light")
    root.geometry("1100x720")
    root.bind("<Control-w>",lambda event:root.destroy())
    root.bind("<Control-W>",lambda event:root.destroy())
    centered_window(root,1100,720)
    root.minsize(660,500)
    
    def on_click(username):
        
        if (on_login(username,root,current_mode,remeber_status.get()))==False:
            messagebox.showerror("Wrong Credentials",f"The enterred password for the user({username}) is wrong")

    # ctk.set_appearance_mode("light")
    def changemode():
        global current_mode
        global user_label_list
        if current_mode == "dark":
            root.iconify()
            current_mode = "light"
            root._set_appearance_mode("light")
            LoginFrame.configure(fg_color=LIGHT["frame"])
            SignupFrame.configure(fg_color=LIGHT["frame"])
            notebook.configure(fg_color=LIGHT["bg"],bg_color=LIGHT["bg"],segmented_button_fg_color=LIGHT["frame"])
            icon = ctk.CTkImage(light_image=lightimg,dark_image=lightimg,size=(50, 50))
            modeBtn.configure(bg_color="transparent",width=0,fg_color=LIGHT["bg"],image=icon,hover_color=LIGHT["card"])
            title1["text_color"]=LIGHT["text"]
            title2["text_color"]=LIGHT["text"]
            # for i in range(len(user_label_list)):
            #     user_label_list[i].configure(text_color=LIGHT["text"])

            root.deiconify()
        else:
            root.iconify()
            current_mode = "dark"
            root._set_appearance_mode("dark")
            LoginFrame.configure(fg_color=DARK["frame"])
            SignupFrame.configure(fg_color=DARK["frame"])
            notebook.configure(fg_color=DARK["bg"],bg_color="transparent",segmented_button_fg_color=DARK["frame"])
            icon = ctk.CTkImage(light_image=darkimg,dark_image=darkimg,size=(50, 50))
            modeBtn.configure(bg_color="transparent",width=0,fg_color=DARK["bg"],image=icon,hover_color="grey")
            title1["text_color"]=DARK["text"]
            title2["text_color"]=DARK["text"]
            # for i in range(len(user_label_list)):
            #     user_label_list[i].configure(text_color=DARK["text"])
            
            root.deiconify()

    if root._get_appearance_mode()=="light":
        current_mode="light"
    else:
        current_mode="dark"

    #button MODE
    lightimg=Image.open("ui/assets/light.png")
    darkimg=Image.open("ui/assets/dark.png")
    icon = ctk.CTkImage(light_image=lightimg,dark_image=darkimg,size=(50, 50))
    # light_icon = ctk.CTkImage(light_image=lightimg,size=(50, 50))
    modeBtn=ctk.CTkButton(root,text="",corner_radius=0,image=icon,bg_color="transparent",width=0,fg_color="transparent",hover_color="grey",command=lambda:messagebox.showinfo("Coming Soon","The Light mode version of the app is coming soon!"))
    modeBtn.pack(side="top",anchor="ne")


    notebook = ctk.CTkTabview(root,fg_color="transparent",bg_color="transparent",corner_radius=0)
    notebook.configure(
        segmented_button_fg_color=(LIGHT["frame"], DARK["frame"]),
        segmented_button_selected_color=PRIMARY,
        segmented_button_selected_hover_color=PRIMARY_HOVER
    )
    notebook.pack(expand=True, fill="both")

    loginTab = notebook.add("     Login     ")
    SignupTab = notebook.add("     Signup     ")

    if current_mode=="light":
        framecolor=LIGHT["frame"]
    else:
        framecolor=DARK["frame"]


    LoginFrame=ctk.CTkScrollableFrame(loginTab,corner_radius=5,fg_color=framecolor,bg_color="transparent",border_color=DARK["frame"])
    LoginFrame.pack(expand=True,fill="both")
    SignupFrame=ctk.CTkFrame(SignupTab,corner_radius=5,fg_color=framecolor,bg_color="transparent")
    SignupFrame.pack(expand=True,fill="both")


    LoginFrame.columnconfigure(0,weight=1)
    LoginFrame.columnconfigure(1,weight=1)
    users=get_user()
    usernames=[]
    for i in users:
        data=open_user_json(i)
        usernames.append(data["profile"]["name"])
    LoginFrame.rowconfigure(0,weight=1,uniform="a")
    title1=ctk.CTkLabel(LoginFrame,text="User Name",font=("Arial",16,"bold"),text_color=(LIGHT["text"],DARK["text"]))
    title1.grid(row=0,column=0)
    title2=ctk.CTkLabel(LoginFrame,text="Login",font=("Arial",16,"bold"),text_color=(LIGHT["text"],DARK["text"]))
    title2.grid(row=0,column=1)
    user_label_list=[]
    for i in range(2,len(users)+2):
        LoginFrame.rowconfigure(i-1,weight=1,uniform="a")
        ctk.CTkLabel(LoginFrame,text=usernames[i-2],font=("Arial",14)).grid(row=i,column=0,pady=10)
        ctk.CTkButton(LoginFrame,text="Login",font=("Arial",14,"bold"),fg_color=BLUE_BORDER,hover_color=INFO,text_color=DARK["text"],command=lambda u=users[i-2]:on_click(u) ).grid(row=i,column=1,pady=10)

    bottom_frame=ctk.CTkFrame(loginTab,fg_color=DARK["frame"],bg_color="transparent",corner_radius=0)
    bottom_frame.pack(side="bottom",fill="x",ipady=5)

    remeber_status=ctk.IntVar(value=get_remember_default()["remember"])

    remeber_me=ctk.CTkCheckBox(bottom_frame,text="Remeber Me",variable=remeber_status,offvalue=0,onvalue=1,bg_color=DARK["frame"],cursor="hand2")

    #bottom layout    
    ctk.CTkButton(bottom_frame,text="Doesn't have an account? Sign Up",font=("Arial",11),text_color=DARK["subtext"],fg_color=DARK["frame"],border_color=DARK["frame"],hover_color=DARK["frame"],cursor="hand2",corner_radius=5,border_width=0,command=lambda:notebook.set("     Signup     ")).pack(side="bottom",fill="x")
    remeber_me.pack(side="bottom")


    ## Signup ############################################################################################################################


    Signup_txt=ctk.CTkLabel(SignupFrame,text="SIGN UP",font=("Lucida Sans",20,"bold"),text_color=(LIGHT["text"],DARK["text"]))
    Signup_txt.pack(pady=10)

    def clearentry(entry):
        last_index=len(entry.get())
        entry.delete(0,last_index)
    def fill_entry(widget,text):
        if widget.get()=="" or widget.get()==" ":
            widget.insert(0,text)
            widget["border_color"]=LIGHT["primary"]

    def passfill(text="Password"):
        if password_entry.get()=="" or password_entry.get()==" ":
            password_entry.insert(0,text)
            conform_password_entry.pack_forget()

    y=1
    def animate_signup_btn():
        nonlocal y
        if y > 0.8:     
            y=y-0.001      
            signUpBtn.place(relx=0.5,rely=y,anchor="n")
            root.after(1,animate_signup_btn)

    def check_match():
        conform_password_entry.after(100,checkmatch)
        

    def checkmatch():
        check_user_exist(username_entry,info)
        if password_entry.get()==conform_password_entry.get() and password_entry.get()!="Password" and username_entry.cget("border_color")==GREEN_BORDER:
            signUpBtn.configure(state="enabled",cursor="hand2")
            animate_signup_btn()
        else:
            signUpBtn.configure(state="disabled",cursor="hand2")

    username_entry=ctk.CTkEntry(SignupFrame,border_color=LIGHT["primary"],fg_color=(LIGHT["card"],DARK["card"]),corner_radius=5,width=250,height=30,border_width=1)
    username_entry.pack(pady=(50,15))
    username_entry.insert(0,"Username")
    username_entry.bind('<FocusIn>',lambda event:clearentry(username_entry))
    username_entry.bind('<FocusOut>',lambda event:[fill_entry(username_entry,"Username"),check_user_exist(username_entry,info)])

    password_entry=ctk.CTkEntry(SignupFrame,border_color=LIGHT["primary"],fg_color=(LIGHT["card"],DARK["card"]),corner_radius=5,width=250,height=30,border_width=1)
    password_entry.pack(pady=(0,15))
    password_entry.insert(0,"Password")
    password_entry.bind('<FocusIn>',lambda event:[clearentry(password_entry),conform_password_entry.pack(pady=(0,20))])
    password_entry.bind('<FocusOut>',lambda event:passfill())
    password_entry.bind('<KeyPress>',lambda event:check_match())

    conform_password_entry=ctk.CTkEntry(SignupFrame,border_color=LIGHT["primary"],fg_color=(LIGHT["card"],DARK["card"]),corner_radius=5,width=250,height=30,border_width=1)
    
    conform_password_entry.insert(0,"Conform Password")
    conform_password_entry.bind('<FocusIn>',lambda event:[clearentry(conform_password_entry),check_match()])
    conform_password_entry.bind('<FocusOut>',lambda event:fill_entry(conform_password_entry,"Conform Password"))
    conform_password_entry.bind('<KeyPress>',lambda event:check_match())

    username_entry.bind("<Control-BackSpace>",lambda e:username_entry.delete(0, "end"))
    password_entry.bind("<Control-BackSpace>",lambda e:password_entry.delete(0, "end"))
    conform_password_entry.bind("<Control-BackSpace>",lambda e:conform_password_entry.delete(0, "end"))

    info=ctk.StringVar(value="")
    information=ctk.CTkLabel(SignupFrame,textvariable=info,font=("Arial",11),text_color=DANGER)
    information.place(relx=0.5,rely=0.55,anchor="center")

    def signUp(username,password):
        done=signupUser(username,password,root)
        if done:
            main_ui(username,"dark",root,remeber_status.get())

    signUpBtn=ctk.CTkButton(SignupFrame,text="Sign UP",text_color=DARK["bg"],text_color_disabled=DARK["subtext"],fg_color=LIGHT["primary"],hover_color=INFO,cursor="hand2",corner_radius=5,width=200,height=30,border_width=2,font=("Arial",14,"bold"),state="disabled",command=lambda:signUp(username_entry.get(),password_entry.get()))

    ctk.CTkButton(SignupFrame,text="Already have an account? Sign In",font=("Arial",11),text_color=DARK["subtext"],fg_color="transparent",hover_color=DARK["frame"],cursor="hand2",corner_radius=5,border_width=0,command=lambda:notebook.set("     Login     ")).pack(side="bottom")

    signUpBtn.place(relx=0.5,rely=1,anchor="n")

    root.mainloop()
