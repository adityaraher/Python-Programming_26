import os
import re
import shutil
import subprocess
from datetime import date, datetime
import pandas as pd

# Portable path setup: resolves relative to this script's location regardless of folder name or working directory
APP_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(APP_DIR, "Datasets")

CSV_SCHEMAS = {
    "Login_Dataset.csv": [
        "user_id",
        "username",
        "password",
        "user_role",
        "acc_status",
    ],
    "Admin_Dataset.csv": [
        "admin_id",
        "admin_fname",
        "admin_lname",
        "office_email",
        "office_contact",
        "clearance_lvl",
        "security_pin",
        "emergency_contact",
        "assigned_region",
    ],
    "Employee_Dataset.csv": [
        "emp_id",
        "emp_fname",
        "emp_lname",
        "emp_address",
        "office_location",
        "department",
        "access_tier",
        "office_email",
        "office_contact",
    ],
    "Customer_Dataset.csv": [
        "cust_id",
        "cust_fname",
        "cust_lname",
        "cust_address",
        "cust_contact",
        "cust_email",
        "credit_limit",
        "cust_joindate",
        "acc_status",
        "join_date",
    ],
    "Contractor_Dataset.csv": [
        "contr_id",
        "contr_fname",
        "contr_lname",
        "contr_address",
        "contr_contact",
        "contr_email",
        "compliance_status",
    ],
    "Shipment_Dataset.csv": [
        "shipm_id",
        "cust_id",
        "contr_id",
        "veh_id",
        "receiv_name",
        "receiv_contact",
        "goods_weight",
        "goods_type",
        "service_type",
        "pickup_loc",
        "pickup_date",
        "delivery_loc",
        "delivery_date",
        "comp_commission",
        "estim_cost",
        "contr_payput",
        "shipm_status",
        "shipm_verification",
        "verification_notes",
        "transit_notes",
    ],
    "Fleet_Dataset.csv": [
        "veh_id",
        "contr_id",
        "veh_type",
        "max_capacity_kg",
        "allowed_goods_type",
        "veh_status",
        "curr_shipm_id",
    ],
}

FARES = {
    "CITY": 45.00,
    "ICTY": 85.00,
    "ISTT": 140.00,
    "INTL": 1500.00,
    "GENERAL": 1.00,
    "EXPRESS": 1.45,
    "FRAGILE": 1.20,
    "ELECTRONICS": 1.15,
    "PERISHABLE": 1.25,
    "HEAVY": 1.15,
    "PARCEL": 0.85,
}

SERVICES = {"1": "GENERAL", "2": "EXPRESS"}
GOODS = {
    "1": "GENERAL",
    "2": "FRAGILE",
    "3": "ELECTRONICS",
    "4": "PERISHABLE",
    "5": "HEAVY",
    "6": "PARCEL",
}


def clear():
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)


def width():
    return shutil.get_terminal_size((75, 24)).columns


def pause(msg=">>>[SYSTEM] Press Enter to continue..."):
    input(msg)


def _fix_cols(df, cols):
    df = df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = None
    return df[cols]


def load_all_datasets():
    os.makedirs(BASE_DIR, exist_ok=True)
    data = {}

    for fname, cols in CSV_SCHEMAS.items():
        key = fname.replace(".csv", "")
        csv_path = os.path.join(BASE_DIR, fname)
        if os.path.exists(csv_path):
            df = _fix_cols(pd.read_csv(csv_path), cols)
        else:
            df = pd.DataFrame(columns=cols)
            df.to_csv(csv_path, index=False)
        data[key] = df

    if len(data["Login_Dataset"]) == 0:
        data["Login_Dataset"] = pd.DataFrame(
            [
                {
                    "user_id": "IND-00001",
                    "username": "parthppawar08@gmail.com",
                    "password": "parth123",
                    "user_role": "admin",
                    "acc_status": "active",
                }
            ],
            columns=CSV_SCHEMAS["Login_Dataset.csv"],
        )
        data["Login_Dataset"].to_csv(os.path.join(BASE_DIR, "Login_Dataset.csv"), index=False)

    if len(data["Admin_Dataset"]) == 0:
        data["Admin_Dataset"] = pd.DataFrame(
            [
                {
                    "admin_id": "IND-00001",
                    "admin_fname": "Parth",
                    "admin_lname": "Pawar",
                    "office_email": "parthppawar08@gmail.com",
                    "office_contact": 7972228710,
                    "clearance_lvl": "SuperAdmin",
                    "security_pin": "pp0403",
                    "emergency_contact": 7972228710,
                    "assigned_region": "UNV",
                }
            ],
            columns=CSV_SCHEMAS["Admin_Dataset.csv"],
        )
        data["Admin_Dataset"].to_csv(os.path.join(BASE_DIR, "Admin_Dataset.csv"), index=False)

    return data


def save_all_datasets(datasets):
    os.makedirs(BASE_DIR, exist_ok=True)
    for fname, cols in CSV_SCHEMAS.items():
        key = fname.replace(".csv", "")
        df_clean = _fix_cols(datasets[key], cols)
        datasets[key] = df_clean
        df_clean.to_csv(os.path.join(BASE_DIR, fname), index=False)


def next_id(df, col, prefix):
    if len(df) == 0 or col not in df.columns:
        return f"{prefix}-00001"
    nums = []
    for item in df[col].dropna().astype(str):
        parts = item.strip().split("-")
        if parts and parts[-1].isdigit():
            nums.append(int(parts[-1]))
    return f"{prefix}-{(max(nums) + 1) if nums else 1:05d}"


def fmt_date(val):
    if val is None or pd.isna(val) or str(val).strip() == "":
        return "N/A"
    if isinstance(val, (date, datetime)):
        return val.strftime("%d-%m-%Y")
    txt = str(val).strip()
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(txt, fmt).strftime("%d-%m-%Y")
        except ValueError:
            pass
    return txt


# -------------------- INPUT PROMPTS --------------------
def ask_service():
    w = width()
    while True:
        print("-" * w)
        print("Service Types:  [1] General Service     [2] Express Service")
        print("-" * w)
        ch = input(">>>[SYSTEM] Select Service Type (1-2): ").strip()
        if ch in SERVICES:
            return SERVICES[ch]
        print(">>>[ERROR] Invalid Input!")


def ask_goods():
    w = width()
    opts = [
        ("1", "General"),
        ("2", "Fragile"),
        ("3", "Electronics"),
        ("4", "Perishable"),
        ("5", "Heavy"),
        ("6", "Parcel"),
    ]
    while True:
        print("-" * w)
        print("Available Goods Types:")
        for i, (k, label) in enumerate(opts, start=1):
            cell = f"[{k}] {label}"
            if i % 3 == 0:
                print(f"  {cell}")
            else:
                print(f"  {cell:<22}", end="")
        print("\n" + "-" * w)
        ch = input(">>>[SYSTEM] Select Goods Type (1-6): ").strip()
        if ch in GOODS:
            return GOODS[ch]
        print(">>>[ERROR] Invalid Input!")


def ask_weight():
    while True:
        try:
            val = float(input(">>>[SYSTEM] Enter Goods Weight (kg): ").strip())
            if val > 0:
                return val
            print(">>>[ERROR] Weight must be > 0.")
        except ValueError:
            print(">>>[ERROR] Invalid Input!")


def ask_name():
    while True:
        name = input(">>>[SYSTEM] Enter Receiver Name: ").strip()
        if name and re.fullmatch(r"[A-Za-z ]+", name):
            return name
        print(">>>[ERROR] Invalid Input!")


def ask_contact():
    while True:
        c = input(">>>[SYSTEM] Enter Receiver Contact (10 digits): ").strip()
        if c.isdigit() and len(c) == 10:
            return c
        print(">>>[ERROR] Invalid Input!")


def ask_loc(label):
    while True:
        raw = input(f">>>[SYSTEM] Enter {label} (City, State, Country): ").strip()
        if not raw:
            print(">>>[ERROR] Invalid Input!")
            continue
        parts = [p.strip() for p in raw.split(",")] if "," in raw else raw.split()
        if len(parts) == 3 and all(parts):
            return ", ".join(parts), parts
        print(">>>[ERROR] Use format 'City, State, Country'.")


def ask_date(label="Pickup Date"):
    while True:
        raw = input(f">>>[SYSTEM] Enter {label} (DD-MM-YYYY): ").strip()
        try:
            dt = datetime.strptime(raw, "%d-%m-%Y").date()
            if dt >= date.today():
                return dt
            print(">>>[ERROR] Date cannot be in the past.")
        except ValueError:
            print(">>>[ERROR] Invalid date or format.")


# -------------------- FARE & ID CALCULATION --------------------
def calc_shipment(ship_df, p_list, d_list, weight, service, goods):
    if p_list[2].lower() != d_list[2].lower():
        zone = "INTL"
    elif p_list[1].lower() != d_list[1].lower():
        zone = "ISTT"
    elif p_list[0].lower() != d_list[0].lower():
        zone = "ICTY"
    else:
        zone = "CITY"

    if len(ship_df) == 0:
        seq = 1
    else:
        last = str(ship_df["shipm_id"].iloc[-1])
        try:
            seq = int(last.split("-")[-1]) + 1
        except ValueError:
            seq = len(ship_df) + 1

    shipm_id = f"SHP-{zone}-{seq:05d}"
    comm_rate = 0.20 if service == "EXPRESS" else 0.15
    payout = round(FARES[zone] * float(weight) * FARES[service] * FARES[goods], 2)
    comm_amt = round(payout * comm_rate, 2)
    estim_cost = round(payout + comm_amt, 2)
    return shipm_id, payout, comm_amt, estim_cost


def show_summary(d):
    w = width()
    rows = [
        ("Shipment ID", d["shipm_id"]),
        ("Pickup Date", fmt_date(d["pickup_date"])),
        ("Pickup Location", d["pickup_loc"]),
        ("Delivery Location", d["delivery_loc"]),
        ("Receiver Name", d["receiv_name"]),
        ("Receiver Contact", d["receiv_contact"]),
        ("Goods Type", d["goods_type"]),
        ("Goods Weight", f"{float(d['goods_weight']):.2f} kg"),
        ("Service Type", d["service_type"]),
        ("Contractor Payout", f"Rs. {float(d['contr_payput']):.2f}"),
        ("Company Commission", f"Rs. {float(d['comp_commission']):.2f}"),
        ("Estimated Cost", f"Rs. {float(d['estim_cost']):.2f}"),
    ]
    print("-" * w)
    print("SHIPMENT BOOKING SUMMARY".center(w))
    print("-" * w)
    for k, v in rows:
        print(f"  {k:<22}: {v}")
    print("-" * w)


def show_tracking_card(row):
    w = width()

    def g(col, fallback="None"):
        v = row.get(col)
        if v is None or pd.isna(v) or str(v).strip() == "":
            return fallback
        return str(v)

    wt = float(row["goods_weight"]) if pd.notna(row.get("goods_weight")) else 0.0
    cost = float(row["estim_cost"]) if pd.notna(row.get("estim_cost")) else 0.0

    print("-" * w)
    print("SHIPMENT TRACKING CARD".center(w))
    print("-" * w)
    print(f"  {'Shipment ID':<22}: {g('shipm_id', 'N/A')}")
    print(f"  {'Customer ID':<22}: {g('cust_id', 'N/A')}")
    print(f"  {'Shipment Status':<22}: {g('shipm_status', '[PENDING]')}")
    print(f"  {'Verification':<22}: {g('shipm_verification', 'NV')}")
    print(f"  {'Pickup Date':<22}: {fmt_date(row.get('pickup_date'))}")
    print(f"  {'Pickup Location':<22}: {g('pickup_loc', 'N/A')}")
    print(f"  {'Delivery Date':<22}: {fmt_date(row.get('delivery_date'))}")
    print(f"  {'Delivery Location':<22}: {g('delivery_loc', 'N/A')}")
    print(f"  {'Receiver Name':<22}: {g('receiv_name', 'N/A')}")
    print(f"  {'Receiver Contact':<22}: {g('receiv_contact', 'N/A')}")
    print(f"  {'Service Type':<22}: {g('service_type', 'N/A')}")
    print(f"  {'Goods Type & Weight':<22}: {g('goods_type', 'N/A')} ({wt:.2f} kg)")
    print(f"  {'Contractor ID':<22}: {g('contr_id', 'Unassigned')}")
    print(f"  {'Vehicle ID':<22}: {g('veh_id', 'Unassigned')}")
    print(f"  {'Estimated Cost':<22}: Rs. {cost:.2f}")
    print(f"  {'Verification Notes':<22}: {g('verification_notes')}")
    print(f"  {'Transit Notes':<22}: {g('transit_notes')}")
    print("-" * w)


# -------------------- CUSTOMER APPLICATION --------------------
def cust_book_shipment(datasets, user_id):
    clear()
    w = width()
    ship_df = datasets["Shipment_Dataset"]
    ship_cols = CSV_SCHEMAS["Shipment_Dataset.csv"]

    print("=" * w)
    print("BOOK A NEW SHIPMENT".center(w))
    print("=" * w)

    service = ask_service()
    goods = ask_goods()
    weight = ask_weight()
    r_name = ask_name()
    r_cont = ask_contact()
    p_loc, p_list = ask_loc("Pickup Location")
    d_loc, d_list = ask_loc("Delivery Location")
    p_date = ask_date("Pickup Date")

    shipm_id, payout, comm_amt, estim_cost = calc_shipment(
        ship_df, p_list, d_list, weight, service, goods
    )

    rec = {
        "shipm_id": shipm_id,
        "cust_id": user_id,
        "contr_id": None,
        "veh_id": None,
        "receiv_name": r_name,
        "receiv_contact": r_cont,
        "goods_weight": weight,
        "goods_type": goods,
        "service_type": service,
        "pickup_loc": p_loc,
        "pickup_date": p_date.strftime("%d-%m-%Y"),
        "delivery_loc": d_loc,
        "delivery_date": None,
        "comp_commission": comm_amt,
        "estim_cost": estim_cost,
        "contr_payput": payout,
        "shipm_status": "[PENDING]",
        "shipm_verification": "NV",
        "verification_notes": None,
        "transit_notes": f"Booked at {datetime.now().strftime('%d-%m-%Y %H:%M')}",
    }

    while True:
        clear()
        show_summary(rec)
        ans = input(">>>[SYSTEM] Confirm booking? (y/n): ").strip().lower()
        if ans == "y":
            datasets["Shipment_Dataset"] = pd.concat(
                [ship_df, pd.DataFrame([rec], columns=ship_cols)],
                ignore_index=True,
            )
            save_all_datasets(datasets)
            print(f">>>[SYSTEM] Shipment {rec['shipm_id']} booked successfully.")
            pause()
            return
        elif ans == "n":
            print("-" * w)
            print("  [1] Edit Shipment Details")
            print("  [2] Cancel Booking")
            print("-" * w)
            sub = input(">>>[SYSTEM] Choose option (1-2): ").strip()
            if sub == "2":
                print(">>>[SYSTEM] Booking cancelled.")
                pause()
                return
            elif sub == "1":
                print("  [1] Service Type    [2] Goods Type     [3] Goods Weight")
                print("  [4] Pickup Loc.     [5] Delivery Loc.  [6] Pickup Date")
                print("  [7] Receiver Name   [8] Receiver Cont.")
                f_ch = input(">>>[SYSTEM] Select field to edit (1-8): ").strip()
                recalc = False
                if f_ch == "1":
                    rec["service_type"] = ask_service()
                    recalc = True
                elif f_ch == "2":
                    rec["goods_type"] = ask_goods()
                    recalc = True
                elif f_ch == "3":
                    rec["goods_weight"] = ask_weight()
                    recalc = True
                elif f_ch == "4":
                    rec["pickup_loc"], p_list = ask_loc("Pickup Location")
                    recalc = True
                elif f_ch == "5":
                    rec["delivery_loc"], d_list = ask_loc("Delivery Location")
                    recalc = True
                elif f_ch == "6":
                    rec["pickup_date"] = ask_date("Pickup Date").strftime("%d-%m-%Y")
                elif f_ch == "7":
                    rec["receiv_name"] = ask_name()
                elif f_ch == "8":
                    rec["receiv_contact"] = ask_contact()
                else:
                    print(">>>[ERROR] Invalid Input!")
                    pause()
                    continue

                if recalc:
                    new_id, new_pay, new_comm, new_cost = calc_shipment(
                        ship_df,
                        p_list,
                        d_list,
                        rec["goods_weight"],
                        rec["service_type"],
                        rec["goods_type"],
                    )
                    rec["shipm_id"] = new_id
                    rec["contr_payput"] = new_pay
                    rec["comp_commission"] = new_comm
                    rec["estim_cost"] = new_cost
            else:
                print(">>>[ERROR] Invalid Input!")
                pause()
        else:
            print(">>>[ERROR] Enter 'y' or 'n'.")
            pause()


def cust_track_shipment(datasets, user_id=None, all_rows=False):
    clear()
    w = width()
    df = datasets["Shipment_Dataset"]
    view_df = df if all_rows else df[df["cust_id"].astype(str).str.strip() == str(user_id).strip()]

    while True:
        print("=" * w)
        print("TRACK SHIPMENT".center(w))
        print("=" * w)
        if len(view_df) == 0:
            print(">>>[SYSTEM] No shipments found.")
            pause()
            return
        print("Available IDs: " + ", ".join(view_df["shipm_id"].astype(str).tail(10).tolist()))
        sid = input(">>>[SYSTEM] Enter Shipment ID (or 'B' to go back): ").strip().upper()
        if sid == "B":
            return
        m = view_df[view_df["shipm_id"].astype(str).str.strip().str.upper() == sid]
        if m.empty:
            print(f">>>[ERROR] Shipment '{sid}' not found.")
            pause()
            clear()
            continue
        show_tracking_card(m.iloc[-1])
        if input(">>>[SYSTEM] Track another? (y/n): ").strip().lower() != "y":
            return
        clear()


def cust_edit_or_cancel(datasets, user_id, mode="edit"):
    clear()
    w = width()
    df = datasets["Shipment_Dataset"]
    mine = df[df["cust_id"].astype(str).str.strip() == str(user_id).strip()]

    print("=" * w)
    print(("EDIT SHIPMENT" if mode == "edit" else "CANCEL SHIPMENT").center(w))
    print("=" * w)
    if len(mine) == 0:
        print(">>>[SYSTEM] No shipments found.")
        pause()
        return
    print("Your Shipments: " + ", ".join(mine["shipm_id"].astype(str).tolist()))
    sid = input(">>>[SYSTEM] Enter Shipment ID (or 'B' to go back): ").strip().upper()
    if sid == "B":
        return

    mask = df["shipm_id"].astype(str).str.strip().str.upper() == sid
    if not mask.any():
        print(">>>[ERROR] Shipment ID not found.")
        pause()
        return

    idx = df[mask].index[-1]
    curr_status = str(df.loc[idx, "shipm_status"]).strip().upper()

    if mode == "edit":
        if curr_status not in ("[PENDING]", "BOOKED"):
            print(f">>>[ERROR] Cannot edit shipment in status [{curr_status}].")
            pause()
            return
        print("  [1] Receiver Name   [2] Receiver Contact   [3] Pickup Date")
        ch = input(">>>[SYSTEM] Choose field (1-3): ").strip()
        if ch == "1":
            df.loc[idx, "receiv_name"] = ask_name()
        elif ch == "2":
            df.loc[idx, "receiv_contact"] = ask_contact()
        elif ch == "3":
            df.loc[idx, "pickup_date"] = ask_date("Pickup Date").strftime("%d-%m-%Y")
        else:
            print(">>>[ERROR] Invalid Input!")
            pause()
            return
        save_all_datasets(datasets)
        print(">>>[SYSTEM] Shipment updated.")
        pause()
    else:
        if curr_status in ("IN_TRANSIT", "DELIVERED", "CANCELLED"):
            print(f">>>[ERROR] Cannot cancel shipment in status [{curr_status}].")
            pause()
            return
        est = float(df.loc[idx, "estim_cost"]) if pd.notna(df.loc[idx, "estim_cost"]) else 0.0
        cancel_fee = round(est * 0.10, 2)
        print("-" * w)
        print(f"  {'Shipment ID':<22}: {sid}")
        print(f"  {'Estimated Cost':<22}: Rs. {est:.2f}")
        print(f"  {'Cancellation Fee (10%)':<22}: Rs. {cancel_fee:.2f}")
        print("-" * w)
        if input(">>>[SYSTEM] Confirm cancellation? (y/n): ").strip().lower() == "y":
            df.loc[idx, "shipm_status"] = "CANCELLED"
            note = f"Cancelled by customer (Fee: Rs. {cancel_fee:.2f})"
            old_n = str(df.loc[idx, "transit_notes"]) if pd.notna(df.loc[idx, "transit_notes"]) else ""
            df.loc[idx, "transit_notes"] = f"{old_n} | {note}".strip(" |")
            save_all_datasets(datasets)
            print(">>>[SYSTEM] Shipment marked CANCELLED.")
        else:
            print(">>>[SYSTEM] Cancellation aborted.")
        pause()


def customer_portal(datasets, user_id):
    while True:
        clear()
        w = width()
        print("=" * w)
        print("GLOBALTRANS — CUSTOMER APPLICATION".center(w))
        print("=" * w)
        print(f"  Customer ID: {user_id}")
        print("-" * w)
        print("  [1] Order Management System")
        print("  [2] Support")
        print("  [3] Logout")
        print("-" * w)
        ch = input(">>>[SYSTEM] Select option (1-3): ").strip()

        if ch == "1":
            while True:
                clear()
                print("=" * w)
                print("ORDER MANAGEMENT SYSTEM".center(w))
                print("=" * w)
                print("  [1] Book a shipment")
                print("  [2] Track a shipment")
                print("  [3] Cancel a shipment")
                print("  [4] Edit / Modify a shipment")
                print("  [5] Back")
                print("-" * w)
                sub = input(">>>[SYSTEM] Select option (1-5): ").strip()
                if sub == "1":
                    cust_book_shipment(datasets, user_id)
                elif sub == "2":
                    cust_track_shipment(datasets, user_id=user_id)
                elif sub == "3":
                    cust_edit_or_cancel(datasets, user_id, mode="cancel")
                elif sub == "4":
                    cust_edit_or_cancel(datasets, user_id, mode="edit")
                elif sub == "5":
                    break
                else:
                    print(">>>[ERROR] Invalid Input!")
                    pause()
        elif ch == "2":
            clear()
            print("=" * w)
            print("CUSTOMER SUPPORT".center(w))
            print("=" * w)
            print("  [1] User Support (Common)   [2] Shipment Support")
            s_opt = input(">>>[SYSTEM] Choose support type (1-2): ").strip()
            if s_opt == "2":
                sid = input(">>>[SYSTEM] Enter Shipment ID: ").strip().upper()
                msg = input(">>>[SYSTEM] Describe shipment issue: ").strip()
                print(f">>>[SYSTEM] Ticket logged for {sid}: {msg}")
            else:
                msg = input(">>>[SYSTEM] Describe your account/general query: ").strip()
                print(f">>>[SYSTEM] General support ticket logged: {msg}")
            pause()
        elif ch == "3":
            return
        else:
            print(">>>[ERROR] Invalid Input!")
            pause()


# -------------------- EMPLOYEE APPLICATION --------------------
def employee_portal(datasets, user_id):
    while True:
        clear()
        w = width()
        ship_df = datasets["Shipment_Dataset"]
        contr_df = datasets["Contractor_Dataset"]

        print("=" * w)
        print("GLOBALTRANS — EMPLOYEE APPLICATION".center(w))
        print("=" * w)
        print(f"  Employee ID: {user_id}")
        print("-" * w)
        print("  [1] View Pending Shipments Queue")
        print("  [2] Verify / Inspect Shipment")
        print("  [3] Verify Contractor Acc.")
        print("  [4] Manage Customer & Contractor Disputes")
        print("  [5] Support")
        print("  [6] Account Management & Logout")
        print("-" * w)
        ch = input(">>>[SYSTEM] Select option (1-6): ").strip()

        if ch == "1":
            q = ship_df[ship_df["shipm_verification"].astype(str).str.upper() == "NV"]
            if len(q) == 0:
                print(">>>[SYSTEM] Pending shipments queue is empty.")
            else:
                cols = ["shipm_id", "cust_id", "pickup_loc", "delivery_loc", "goods_type", "goods_weight", "service_type", "shipm_verification"]
                print(q[cols].to_string(index=False))
            pause()

        elif ch == "2":
            q = ship_df[ship_df["shipm_verification"].astype(str).str.upper() == "NV"]
            if len(q) == 0:
                print(">>>[SYSTEM] No shipments awaiting verification.")
                pause()
                continue
            cols = ["shipm_id", "cust_id", "pickup_loc", "delivery_loc", "goods_type", "goods_weight", "estim_cost", "contr_payput"]
            print(q[cols].to_string(index=False))
            sid = input(">>>[SYSTEM] Select Shipment ID to inspect: ").strip().upper()
            mask = ship_df["shipm_id"].astype(str).str.strip().str.upper() == sid
            if not mask.any():
                print(">>>[ERROR] Shipment not found.")
                pause()
                continue
            idx = ship_df[mask].index[-1]
            print("  [1] Approve & Push to Job Marketplace")
            print("  [2] Reject / Flag shipment (Requires a reason)")
            act = input(">>>[SYSTEM] Inspection action (1-2): ").strip()
            if act == "1":
                ship_df.loc[idx, "shipm_verification"] = "VERIFIED"
                ship_df.loc[idx, "shipm_status"] = "MARKETPLACE"
                ship_df.loc[idx, "verification_notes"] = f"Approved by {user_id}"
                save_all_datasets(datasets)
                print(f">>>[SYSTEM] {sid} approved and pushed to Job Marketplace.")
            elif act == "2":
                reason = input(">>>[SYSTEM] Enter rejection/flag reason (required): ").strip()
                if not reason:
                    print(">>>[ERROR] Reason is required to reject/flag a shipment.")
                else:
                    ship_df.loc[idx, "shipm_verification"] = "FLAGGED"
                    ship_df.loc[idx, "shipm_status"] = "FLAGGED"
                    ship_df.loc[idx, "verification_notes"] = f"Flagged by {user_id}: {reason}"
                    save_all_datasets(datasets)
                    print(f">>>[SYSTEM] {sid} flagged with reason.")
            else:
                print(">>>[ERROR] Invalid choice.")
            pause()

        elif ch == "3":
            if len(contr_df) == 0:
                print(">>>[SYSTEM] No contractors in Contractor_Dataset.csv.")
                pause()
                continue
            print(contr_df.to_string(index=False))
            cid = input(">>>[SYSTEM] Select Contractor ID: ").strip().upper()
            cmask = contr_df["contr_id"].astype(str).str.strip().str.upper() == cid
            if not cmask.any():
                print(">>>[ERROR] Contractor not found.")
                pause()
                continue
            cidx = contr_df[cmask].index[-1]
            print("  [1] Approve Contractor    [2] Reject / Flag Contractor")
            c_act = input(">>>[SYSTEM] Choose action (1-2): ").strip()
            if c_act == "1":
                contr_df.loc[cidx, "compliance_status"] = "APPROVED"
                save_all_datasets(datasets)
                print(f">>>[SYSTEM] Contractor {cid} approved.")
            elif c_act == "2":
                contr_df.loc[cidx, "compliance_status"] = "FLAGGED"
                save_all_datasets(datasets)
                print(f">>>[SYSTEM] Contractor {cid} flagged.")
            else:
                print(">>>[ERROR] Invalid choice.")
            pause()

        elif ch == "4":
            sid = input(">>>[SYSTEM] Enter Shipment ID for dispute review: ").strip().upper()
            note = input(">>>[SYSTEM] Enter dispute resolution note: ").strip()
            mask = ship_df["shipm_id"].astype(str).str.strip().str.upper() == sid
            if mask.any():
                idx = ship_df[mask].index[-1]
                prev = str(ship_df.loc[idx, "transit_notes"]) if pd.notna(ship_df.loc[idx, "transit_notes"]) else ""
                ship_df.loc[idx, "transit_notes"] = f"{prev} | Dispute ({user_id}): {note}".strip(" |")
                save_all_datasets(datasets)
                print(">>>[SYSTEM] Dispute note recorded.")
            else:
                print(">>>[ERROR] Shipment ID not found.")
            pause()

        elif ch == "5":
            print(">>>[SYSTEM] Employee Support Desk: ops-support@globaltrans.local")
            pause()

        elif ch == "6":
            emp_df = datasets["Employee_Dataset"]
            m = emp_df[emp_df["emp_id"].astype(str).str.strip() == user_id]
            if not m.empty:
                print(m.to_string(index=False))
            if input(">>>[SYSTEM] Logout now? (y/n): ").strip().lower() == "y":
                return

        else:
            print(">>>[ERROR] Invalid Input!")
            pause()


# -------------------- CONTRACTOR APPLICATION --------------------
def contr_manage_fleet(datasets, contr_id):
    fleet_df = datasets["Fleet_Dataset"]
    fleet_cols = CSV_SCHEMAS["Fleet_Dataset.csv"]
    while True:
        clear()
        w = width()
        mine = fleet_df[fleet_df["contr_id"].astype(str).str.strip() == contr_id]
        print("=" * w)
        print("CONTRACTOR FLEET MANAGEMENT (Fleet_Dataset.csv)".center(w))
        print("=" * w)
        if len(mine) == 0:
            print(">>>[SYSTEM] No vehicles registered under your contractor ID.")
        else:
            print(mine.to_string(index=False))
        print("-" * w)
        print("  [1] Add Vehicle    [2] Update Vehicle Status    [3] Back")
        print("-" * w)
        op = input(">>>[SYSTEM] Select option (1-3): ").strip()
        if op == "1":
            vid = next_id(fleet_df, "veh_id", "VEH")
            vtype = input(">>>[SYSTEM] Vehicle Type (VAN/TRUCK/MINI_TRUCK): ").strip().upper()
            cap = ask_weight()
            allowed = ask_goods()
            row = {
                "veh_id": vid,
                "contr_id": contr_id,
                "veh_type": vtype,
                "max_capacity_kg": cap,
                "allowed_goods_type": allowed,
                "veh_status": "AVAILABLE",
                "curr_shipm_id": None,
            }
            fleet_df = pd.concat([fleet_df, pd.DataFrame([row], columns=fleet_cols)], ignore_index=True)
            datasets["Fleet_Dataset"] = fleet_df
            save_all_datasets(datasets)
            print(f">>>[SYSTEM] Added vehicle {vid}.")
            pause()
        elif op == "2":
            vid = input(">>>[SYSTEM] Enter Vehicle ID: ").strip().upper()
            mask = (fleet_df["veh_id"].astype(str).str.strip().str.upper() == vid) & (
                fleet_df["contr_id"].astype(str).str.strip() == contr_id
            )
            if not mask.any():
                print(">>>[ERROR] Vehicle not found under your ID.")
                pause()
                continue
            vidx = fleet_df[mask].index[-1]
            st = input(">>>[SYSTEM] Status [AVAILABLE / MAINTENANCE]: ").strip().upper()
            if st in ("AVAILABLE", "MAINTENANCE"):
                fleet_df.loc[vidx, "veh_status"] = st
                save_all_datasets(datasets)
                print(">>>[SYSTEM] Vehicle status updated.")
            else:
                print(">>>[ERROR] Invalid status.")
            pause()
        elif op == "3":
            return


def contractor_portal(datasets, user_id):
    while True:
        clear()
        w = width()
        ship_df = datasets["Shipment_Dataset"]
        fleet_df = datasets["Fleet_Dataset"]

        print("=" * w)
        print("GLOBALTRANS — CONTRACTOR APPLICATION".center(w))
        print("=" * w)
        print(f"  Contractor ID: {user_id}")
        print("-" * w)
        print("  [1] Job Marketplace (View & Accept)")
        print("  [2] Job Management (Active, Edit, Status, Payouts, Past Jobs)")
        print("  [3] Support")
        print("  [4] Account Management & Fleet")
        print("  [5] Logout")
        print("-" * w)
        ch = input(">>>[SYSTEM] Select option (1-5): ").strip()

        if ch == "1":
            market = ship_df[
                (ship_df["shipm_verification"].astype(str).str.upper() == "VERIFIED")
                & (ship_df["contr_id"].isna() | (ship_df["contr_id"].astype(str).str.strip().isin(["", "None", "nan"])))
            ]
            if len(market) == 0:
                print(">>>[SYSTEM] No open shipments in Job Marketplace.")
                pause()
                continue
            for _, r in market.iterrows():
                print("-" * w)
                print(f"  Shipment ID  : {r['shipm_id']}")
                print(f"  Route & Date : {r['pickup_loc']} -> {r['delivery_loc']} | Pickup: {fmt_date(r['pickup_date'])}")
                print(f"  Cargo Specs  : {r['goods_type']} | {r['goods_weight']} kg | {r['service_type']}")
                print(f"  Payout       : Rs. {r['contr_payput']}")
            print("-" * w)
            if input(">>>[SYSTEM] Accept a shipment? (y/n): ").strip().lower() == "y":
                sid = input(">>>[SYSTEM] Enter Shipment ID: ").strip().upper()
                smask = ship_df["shipm_id"].astype(str).str.strip().str.upper() == sid
                if not smask.any():
                    print(">>>[ERROR] Shipment not found.")
                    pause()
                    continue
                sidx = ship_df[smask].index[-1]
                avail_veh = fleet_df[
                    (fleet_df["contr_id"].astype(str).str.strip() == user_id)
                    & (fleet_df["veh_status"].astype(str).str.upper() == "AVAILABLE")
                ]
                if len(avail_veh) == 0:
                    print(">>>[ERROR] No AVAILABLE vehicles in your fleet. Add one in Account -> Fleet first.")
                    pause()
                    continue
                print(avail_veh.to_string(index=False))
                vid = input(">>>[SYSTEM] Select Vehicle ID: ").strip().upper()
                vmask = fleet_df["veh_id"].astype(str).str.strip().str.upper() == vid
                if not vmask.any():
                    print(">>>[ERROR] Vehicle not found.")
                    pause()
                    continue
                vidx = fleet_df[vmask].index[-1]
                ship_df.loc[sidx, "contr_id"] = user_id
                ship_df.loc[sidx, "veh_id"] = vid
                ship_df.loc[sidx, "shipm_status"] = "BOOKED"
                fleet_df.loc[vidx, "veh_status"] = "ASSIGNED"
                fleet_df.loc[vidx, "curr_shipm_id"] = sid
                save_all_datasets(datasets)
                print(f">>>[SYSTEM] Job {sid} accepted with vehicle {vid}.")
            pause()

        elif ch == "2":
            active_statuses = ("BOOKED", "PICKED_UP", "IN_TRANSIT", "ASSIGNED")
            active = ship_df[
                (ship_df["contr_id"].astype(str).str.strip() == user_id)
                & (ship_df["shipm_status"].astype(str).str.upper().isin(active_statuses))
            ]
            print("-" * w)
            print("JOB MANAGEMENT".center(w))
            print("-" * w)
            print("  [1] Display Active Jobs")
            print("  [2] Edit Active Job (Reassign Vehicle / Cancel Before Pickup)")
            print("  [3] Update Shipment Status (BOOKED -> PICKED_UP -> IN_TRANSIT -> DELIVERED)")
            print("  [4] Payouts Summary")
            print("  [5] Past Jobs (DELIVERED / CANCELLED)")
            print("-" * w)
            j_op = input(">>>[SYSTEM] Select option (1-5): ").strip()

            if j_op == "1":
                if len(active) == 0:
                    print(">>>[SYSTEM] No active jobs.")
                else:
                    cols = ["shipm_id", "veh_id", "pickup_loc", "pickup_date", "delivery_loc", "receiv_contact", "goods_weight", "goods_type", "service_type", "shipm_status", "contr_payput"]
                    print(active[cols].to_string(index=False))
                pause()
            elif j_op == "2":
                sid = input(">>>[SYSTEM] Enter Active Shipment ID: ").strip().upper()
                smask = (ship_df["shipm_id"].astype(str).str.strip().str.upper() == sid) & (
                    ship_df["contr_id"].astype(str).str.strip() == user_id
                )
                if not smask.any():
                    print(">>>[ERROR] Active job not found.")
                    pause()
                    continue
                sidx = ship_df[smask].index[-1]
                print("  [1] Reassign to another vehicle")
                print("  [2] Cancel / Release job (only before pickup)")
                e_op = input(">>>[SYSTEM] Choose option (1-2): ").strip()
                if e_op == "1":
                    avail_veh = fleet_df[
                        (fleet_df["contr_id"].astype(str).str.strip() == user_id)
                        & (fleet_df["veh_status"].astype(str).str.upper() == "AVAILABLE")
                    ]
                    if len(avail_veh) == 0:
                        print(">>>[ERROR] No other AVAILABLE vehicle.")
                    else:
                        print(avail_veh.to_string(index=False))
                        new_vid = input(">>>[SYSTEM] New Vehicle ID: ").strip().upper()
                        old_vid = str(ship_df.loc[sidx, "veh_id"])
                        old_vmask = fleet_df["veh_id"].astype(str).str.strip().str.upper() == old_vid
                        new_vmask = fleet_df["veh_id"].astype(str).str.strip().str.upper() == new_vid
                        if new_vmask.any():
                            if old_vmask.any():
                                fleet_df.loc[old_vmask, "veh_status"] = "AVAILABLE"
                                fleet_df.loc[old_vmask, "curr_shipm_id"] = None
                            fleet_df.loc[new_vmask, "veh_status"] = "ASSIGNED"
                            fleet_df.loc[new_vmask, "curr_shipm_id"] = sid
                            ship_df.loc[sidx, "veh_id"] = new_vid
                            save_all_datasets(datasets)
                            print(f">>>[SYSTEM] Reassigned {sid} to {new_vid}.")
                        else:
                            print(">>>[ERROR] Vehicle not found.")
                elif e_op == "2":
                    cur_st = str(ship_df.loc[sidx, "shipm_status"]).strip().upper()
                    if cur_st not in ("BOOKED", "ASSIGNED"):
                        print(f">>>[ERROR] Can only release job before pickup (current: {cur_st}).")
                    else:
                        old_vid = str(ship_df.loc[sidx, "veh_id"])
                        old_vmask = fleet_df["veh_id"].astype(str).str.strip().str.upper() == old_vid
                        if old_vmask.any():
                            fleet_df.loc[old_vmask, "veh_status"] = "AVAILABLE"
                            fleet_df.loc[old_vmask, "curr_shipm_id"] = None
                        ship_df.loc[sidx, "contr_id"] = None
                        ship_df.loc[sidx, "veh_id"] = None
                        ship_df.loc[sidx, "shipm_status"] = "MARKETPLACE"
                        save_all_datasets(datasets)
                        print(f">>>[SYSTEM] Released job {sid} back to marketplace.")
                else:
                    print(">>>[ERROR] Invalid option.")
                pause()
            elif j_op == "3":
                sid = input(">>>[SYSTEM] Enter Shipment ID: ").strip().upper()
                smask = (ship_df["shipm_id"].astype(str).str.strip().str.upper() == sid) & (
                    ship_df["contr_id"].astype(str).str.strip() == user_id
                )
                if not smask.any():
                    print(">>>[ERROR] Shipment not found.")
                    pause()
                    continue
                sidx = ship_df[smask].index[-1]
                nxt_st = input(">>>[SYSTEM] New status [PICKED_UP / IN_TRANSIT / DELIVERED]: ").strip().upper()
                if nxt_st in ("PICKED_UP", "IN_TRANSIT", "DELIVERED"):
                    ship_df.loc[sidx, "shipm_status"] = nxt_st
                    ship_df.loc[sidx, "transit_notes"] = input(">>>[SYSTEM] Transit notes: ").strip()
                    if nxt_st == "DELIVERED":
                        ship_df.loc[sidx, "delivery_date"] = date.today().strftime("%d-%m-%Y")
                        vid = str(ship_df.loc[sidx, "veh_id"])
                        vmask = fleet_df["veh_id"].astype(str).str.strip().str.upper() == vid
                        if vmask.any():
                            fleet_df.loc[vmask, "veh_status"] = "AVAILABLE"
                            fleet_df.loc[vmask, "curr_shipm_id"] = None
                    save_all_datasets(datasets)
                    print(f">>>[SYSTEM] Status updated to {nxt_st}.")
                else:
                    print(">>>[ERROR] Invalid status.")
                pause()
            elif j_op == "4":
                mine_all = ship_df[ship_df["contr_id"].astype(str).str.strip() == user_id]
                done = mine_all[mine_all["shipm_status"].astype(str).str.upper() == "DELIVERED"]
                earned = pd.to_numeric(done["contr_payput"], errors="coerce").fillna(0).sum()
                pending_pay = pd.to_numeric(mine_all["contr_payput"], errors="coerce").fillna(0).sum() - earned
                print(f"  {'Earned Payouts (Delivered)':<26}: Rs. {earned:.2f}")
                print(f"  {'In-Progress Payouts':<26}: Rs. {pending_pay:.2f}")
                pause()
            elif j_op == "5":
                past = ship_df[
                    (ship_df["contr_id"].astype(str).str.strip() == user_id)
                    & (ship_df["shipm_status"].astype(str).str.upper().isin(["DELIVERED", "CANCELLED"]))
                ]
                if len(past) == 0:
                    print(">>>[SYSTEM] No past jobs.")
                else:
                    cols = ["shipm_id", "veh_id", "pickup_loc", "delivery_loc", "delivery_date", "goods_type", "goods_weight", "shipm_status", "contr_payput"]
                    print(past[cols].to_string(index=False))
                pause()
            else:
                print(">>>[ERROR] Invalid option.")
                pause()

        elif ch == "3":
            print("  [1] General Support    [2] Contractor Support")
            _ = input(">>>[SYSTEM] Enter support message: ").strip()
            print(">>>[SYSTEM] Support request submitted.")
            pause()

        elif ch == "4":
            print("  [1] Display Account Details   [2] Modify Account Details   [3] Manage Fleet")
            a_op = input(">>>[SYSTEM] Choose option (1-3): ").strip()
            cdf = datasets["Contractor_Dataset"]
            m = cdf[cdf["contr_id"].astype(str).str.strip() == user_id]
            if a_op == "1":
                print(m.to_string(index=False) if not m.empty else ">>>[SYSTEM] No profile row found.")
                pause()
            elif a_op == "2" and not m.empty:
                cidx = m.index[-1]
                cdf.loc[cidx, "contr_contact"] = ask_contact()
                cdf.loc[cidx, "contr_address"] = input(">>>[SYSTEM] New Address: ").strip()
                save_all_datasets(datasets)
                print(">>>[SYSTEM] Account details updated.")
                pause()
            elif a_op == "3":
                contr_manage_fleet(datasets, user_id)

        elif ch == "5":
            return
        else:
            print(">>>[ERROR] Invalid Input!")
            pause()


# -------------------- ADMIN APPLICATION --------------------
def admin_portal(datasets, user_id):
    while True:
        clear()
        w = width()
        ship_df = datasets["Shipment_Dataset"]
        print("=" * w)
        print("GLOBALTRANS — ADMIN CONTROL PORTAL".center(w))
        print("=" * w)
        print(f"  Admin ID: {user_id}  |  Total Shipments: {len(ship_df)}")
        print("-" * w)
        print("  [1] View All Shipments")
        print("  [2] Financial & Revenue Overview")
        print("  [3] Track Any Shipment")
        print("  [4] Add User (Customer / Employee / Contractor)")
        print("  [5] Logout")
        print("-" * w)
        ch = input(">>>[SYSTEM] Select option (1-5): ").strip()

        if ch == "1":
            if len(ship_df) == 0:
                print(">>>[SYSTEM] No shipments recorded.")
            else:
                cols = ["shipm_id", "cust_id", "contr_id", "veh_id", "service_type", "estim_cost", "contr_payput", "shipm_status"]
                print(ship_df[cols].to_string(index=False))
            pause()
        elif ch == "2":
            rev = pd.to_numeric(ship_df["estim_cost"], errors="coerce").fillna(0).sum()
            pay = pd.to_numeric(ship_df["contr_payput"], errors="coerce").fillna(0).sum()
            comm = pd.to_numeric(ship_df["comp_commission"], errors="coerce").fillna(0).sum()
            print(f"  {'Total Customer Billing':<24}: Rs. {rev:.2f}")
            print(f"  {'Total Contractor Payouts':<24}: Rs. {pay:.2f}")
            print(f"  {'Total Company Commission':<24}: Rs. {comm:.2f}")
            pause()
        elif ch == "3":
            cust_track_shipment(datasets, all_rows=True)
        elif ch == "4":
            print("  [1] Customer    [2] Employee    [3] Contractor")
            u_ch = input(">>>[SYSTEM] Role to create (1-3): ").strip()
            fname = input(">>>[SYSTEM] First Name: ").strip()
            lname = input(">>>[SYSTEM] Last Name: ").strip()
            uname = input(">>>[SYSTEM] Username: ").strip()
            pwd = input(">>>[SYSTEM] Password: ").strip()

            if u_ch == "1":
                uid = next_id(datasets["Login_Dataset"], "user_id", "CUST")
                today_str = date.today().strftime("%d-%m-%Y")
                crow = {
                    "cust_id": uid,
                    "cust_fname": fname,
                    "cust_lname": lname,
                    "cust_address": input(">>>[SYSTEM] Address: ").strip(),
                    "cust_contact": ask_contact(),
                    "cust_email": uname,
                    "credit_limit": 50000,
                    "cust_joindate": today_str,
                    "acc_status": "active",
                    "join_date": today_str,
                }
                datasets["Customer_Dataset"] = pd.concat(
                    [datasets["Customer_Dataset"], pd.DataFrame([crow], columns=CSV_SCHEMAS["Customer_Dataset.csv"])],
                    ignore_index=True,
                )
                role = "customer"
            elif u_ch == "2":
                uid = next_id(datasets["Login_Dataset"], "user_id", "EMP")
                erow = {
                    "emp_id": uid,
                    "emp_fname": fname,
                    "emp_lname": lname,
                    "emp_address": input(">>>[SYSTEM] Address: ").strip(),
                    "office_location": input(">>>[SYSTEM] Office Location: ").strip(),
                    "department": input(">>>[SYSTEM] Department: ").strip(),
                    "access_tier": "L1",
                    "office_email": uname,
                    "office_contact": ask_contact(),
                }
                datasets["Employee_Dataset"] = pd.concat(
                    [datasets["Employee_Dataset"], pd.DataFrame([erow], columns=CSV_SCHEMAS["Employee_Dataset.csv"])],
                    ignore_index=True,
                )
                role = "employee"
            elif u_ch == "3":
                uid = next_id(datasets["Login_Dataset"], "user_id", "CONTR")
                corow = {
                    "contr_id": uid,
                    "contr_fname": fname,
                    "contr_lname": lname,
                    "contr_address": input(">>>[SYSTEM] Address: ").strip(),
                    "contr_contact": ask_contact(),
                    "contr_email": uname,
                    "compliance_status": "PENDING",
                }
                datasets["Contractor_Dataset"] = pd.concat(
                    [datasets["Contractor_Dataset"], pd.DataFrame([corow], columns=CSV_SCHEMAS["Contractor_Dataset.csv"])],
                    ignore_index=True,
                )
                role = "contractor"
            else:
                print(">>>[ERROR] Invalid role choice.")
                pause()
                continue

            lrow = {
                "user_id": uid,
                "username": uname,
                "password": pwd,
                "user_role": role,
                "acc_status": "active",
            }
            datasets["Login_Dataset"] = pd.concat(
                [datasets["Login_Dataset"], pd.DataFrame([lrow], columns=CSV_SCHEMAS["Login_Dataset.csv"])],
                ignore_index=True,
            )
            save_all_datasets(datasets)
            print(f">>>[SYSTEM] Registered {role} with ID {uid}.")
            pause()
        elif ch == "5":
            return
        else:
            print(">>>[ERROR] Invalid Input!")
            pause()


# -------------------- LOGIN PORTAL --------------------
def login_portal():
    datasets = load_all_datasets()
    while True:
        clear()
        w = width()
        users = datasets["Login_Dataset"]
        print("=" * w)
        print("GLOBALTRANS LOGISTICS MANAGEMENT SYSTEM — LOGIN".center(w))
        print("=" * w)
        print("  [1] Customer Login     [2] Employee Login")
        print("  [3] Contractor Login   [4] Admin Login")
        print("  [5] Exit")
        print("-" * w)

        role_map = {"1": "customer", "2": "employee", "3": "contractor", "4": "admin"}
        opt = input(">>>[SYSTEM] Select portal (1-5): ").strip()
        if opt == "5":
            clear()
            print(">>>[SYSTEM] Exiting GlobalTrans System.")
            return
        if opt not in role_map:
            print(">>>[ERROR] Invalid selection!")
            pause()
            continue

        target_role = role_map[opt]
        uname = input(">>>[SYSTEM] Username: ").strip()
        pwd = input(">>>[SYSTEM] Password: ").strip()

        hit = users[
            (users["username"].astype(str).str.strip() == uname)
            & (users["password"].astype(str).str.strip() == pwd)
            & (users["user_role"].astype(str).str.strip().str.lower() == target_role)
        ]

        if hit.empty:
            print(">>>[ERROR] Invalid credentials or role.")
            pause()
            continue

        row = hit.iloc[0]
        acc_st = str(row.get("acc_status", "active")).strip().lower()
        if acc_st != "active":
            print(f">>>[ERROR] Account is [{acc_st}].")
            pause()
            continue

        uid = str(row["user_id"]).strip()
        if target_role == "customer":
            customer_portal(datasets, uid)
        elif target_role == "employee":
            employee_portal(datasets, uid)
        elif target_role == "contractor":
            contractor_portal(datasets, uid)
        elif target_role == "admin":
            admin_portal(datasets, uid)


if __name__ == "__main__":
    login_portal()
