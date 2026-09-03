import json
import os
from utils.date_calculator import get_today
from ui.theme import *


def has_valid_preferences(pref):
    if not isinstance(pref, dict):
        return False

    required_fields = [
        ("name", str),
        ("currency", str),
        ("monthly_limit", (int, float)),
        ("threshold_percent", (int, float)),
        ("savings", (int, float)),
    ]

    for field_name, expected_type in required_fields:
        value = pref.get(field_name)
        if value in (None, ""):
            return False
        if not isinstance(value, expected_type):
            return False

    return bool(str(pref.get("name", "")).strip())

def get_user():
    usernames=os.listdir("data/users")
    users=[]
    for sorting in usernames:
        if sorting.endswith(".json"):
            users.append((sorting[:-5]))
    return users

def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def open_user_json(username):
    if username.endswith(".json"):
        try:
            with open(f"data/users/{username}","r")as file:
                data=json.load(file)
        except Exception as e:
            data=str(e)
    else:
        try:
            with open(f"data/users/{username}.json") as file:
                data=json.load(file)
        except Exception as e:
            data=str(e)
    return data

def check_pass(username,user_pass):
    data=open_user_json(username)
    auth=data["auth"]
    if user_pass==auth["password"]:
        logged_in=True
    else:
        logged_in=False
    return logged_in

def check_user_exist(username_entry,info_lbl):
    entered_name=username_entry.get()
    users=get_user()
    if entered_name in users:
        available_space=False
        border=DARK["primary"]
        info_lbl.set(value="Username already exists")
    else:
        available_space=True
        border=GREEN_BORDER
        info_lbl.set(value="")
    #handling placeholder text "Username"
    if entered_name== "Username":
        border=DARK["primary"]
        username_entry.configure(border_color=border)
        return

    username_entry.configure(border_color=border)
    
def signupUser(username,password,parent):
    from tkinter import messagebox
    from ui.get_preferences import get_preferences
    data=read_json("data/defaults.json")
    auth=data.get("auth",{"username":"",
                          "password":""})
    auth["username"]=username
    auth["password"]=password
    data["auth"]=auth
    profile=data.get("profile",{"name":"",
                                "currency":""})
    profile["name"]=username

    pref=get_preferences(parent)
    if pref is None:
        messagebox.showerror("Closed","The Application has been closed by the user without submitting data\nRestart")
        parent.quit()
        parent.destroy()
        return False

    if not has_valid_preferences(pref):
        messagebox.showerror("Incomplete Setup","Please complete the setup form before continuing")
        parent.quit()
        parent.destroy()
        return False

    try:
        data["profile"]["name"]=str(pref.get("name",""))
        data["profile"]["currency"]=str(pref.get("currency",""))
        data["budget"]["monthly_limit"]=int(pref.get("monthly_limit",0))
        data["budget"]["threshold_percent"]=int(pref.get("threshold_percent",0))
        data["budget"]["month"]=get_today().strftime("%Y-%m")
        data["settings"]["theme"]=str(pref.get("theme","dark"))
        data["budget"]["saving_goal"]=int(pref.get("savings",0))
    except (AttributeError, TypeError, ValueError):
        messagebox.showerror("Closed","The Application has been closed by the user without submitting data\nRestart")
        parent.quit()
        parent.destroy()
        return False
    write_json(f"data/users/{username}.json",data)
    return True

def update_password(user,password):
    from tkinter import messagebox
    path=f"data/users/{user}.json"
    data=read_json(path)
    data["auth"]["password"]=password
    write_json(path,data)
    messagebox.showinfo("Success","Password updated successfully.")

def reset_userdata(username):
    data=open_user_json(username)
    default=read_json("data/defaults.json")
    default["auth"]=data["auth"]
    default["profile"]=data["profile"]
    default["budget"]["monthly_limit"]=data["budget"]["monthly_limit"]
    default["budget"]["threshold_percent"]=data["budget"]["threshold_percent"]
    default["settings"]["theme"]=data["settings"]["theme"]
    default["budget"]["month"]=get_today().strftime("%Y-%m")
    write_json(f"data/users/{username}.json",default)

def delete(username):
    try:
        os.remove(f"data/users/{username}.json")
    except:
        pass
    
def get_remember_default():
    data=read_json("data/app.json")
    users=get_user()
    if data["username"] not in users:
        data["username"]=""
        data["remember"]=0
        write_json("data/app.json",data)
    return data

def forgot_user():
    data=read_json("data/app.json")
    data["remember"]=0
    data["username"]=""
    write_json("data/app.json",data)

def get_category_values(type):
    if type=="Expense":
        data=read_json("data/app.json")
        return data["categories"]
    elif type=="Income":
        return ["Salary","Income","Money Added"]

def save_transaction(user,title,amount,type,category):
    data=open_user_json(user)
    transaction_data=data["data"]["transactions"]

    if transaction_data==[] or not(transaction_data):
        latest_id=0
    else:
        latest_tansaction=transaction_data[len(transaction_data)-1]
        latest_id=latest_tansaction["id"]

    id_current=latest_id+1
    today=str(get_today())

    transaction={
        "id":id_current,
        "date":today,
        "type":type,
        "category":category,
        "amount":amount,
        "title":title,
    }
    transaction_data.append(transaction)
    data["data"]["transactions"]=transaction_data

    #after transaction processing (e.g. balance update etc)
    if type=="Expense":
        data["data"]["balance"]=data["data"]["balance"]-amount
        data["budget"]["current_spent"]=data["budget"]["current_spent"]+amount
        data["analytics"]["monthly_summary"]["Expense"]=data["analytics"]["monthly_summary"]["Expense"]+amount
    else:
        data["data"]["balance"]=data["data"]["balance"]+amount
        data["analytics"]["monthly_summary"]["income"]=data["analytics"]["monthly_summary"]["income"]+amount

    write_json(f"data/users/{user}.json",data)

def get_id(user):
    data=open_user_json(user)
    transaction_data=data["data"]["transactions"]

    if transaction_data==[]:
        latest_id=0
    else:
        latest_tansaction=transaction_data[len(transaction_data)-1]
    return latest_tansaction["id"]

def change_budget_limit(user,new_limit):
    data=open_user_json(user)
    data["budget"]["monthly_limit"]=new_limit
    write_json(f"data/users/{user}.json",data)

def update_user_threshold(user,new_threshold):
    data=open_user_json(user)
    data["budget"]["threshold_percent"]=new_threshold
    write_json(f"data/users/{user}.json",data)

def change_savings(user,new_savings):
    data=open_user_json(user)
    data["analytics"]["monthly_summary"]["savings"]=new_savings
    write_json(f"data/users/{user}.json",data)

def delete_transaction_data(user, transaction_id):
    """
    Delete a transaction and undo all its effects on balance, budget, and analytics.
    Returns (success, message, deleted_uid) tuple.
    """
    data = open_user_json(user)
    transactions = data["data"]["transactions"]

    # Find the transaction
    deleted_txn = None
    for txn in transactions:
        if txn["id"] == transaction_id:
            deleted_txn = txn
            break

    if deleted_txn is None:
        return False, "Transaction not found", None

    deleted_amount = deleted_txn["amount"]
    deleted_expense = deleted_txn["type"] == "Expense"  #work as if func

    # Remove transaction
    transactions.remove(deleted_txn)

    # Renumber all IDs
    for i in range(len(transactions)):
        transactions[i]["id"] = i + 1

    # Update user file - undo transaction effects
    data["data"]["transactions"] = transactions

    if deleted_expense:
        data["data"]["balance"] += deleted_amount
        data["budget"]["current_spent"] -= deleted_amount
        data["analytics"]["monthly_summary"]["Expense"] -= deleted_amount
    else:
        data["data"]["balance"] -= deleted_amount
        data["analytics"]["monthly_summary"]["income"] -= deleted_amount

    write_json(f"data/users/{user}.json", data)

    return True, f"Transaction Deleted successfully\nid:{transaction_id}", transaction_id

def clear_empty_transactions(user):
    transactions = open_user_json(user)["data"]["transactions"]
    for transaction_id in reversed([txn["id"] for txn in transactions if txn["amount"] == 0]):
        delete_transaction_data(user, transaction_id)
