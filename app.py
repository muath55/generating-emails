import os
import random
import threading
import queue
import smtplib
import dns.resolver
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor, as_completed

# ─── Configuration ──────────────────────────────────────────

EMAILS_FOLDER  = 'emails'
GENERATED_FILE = os.path.join(EMAILS_FOLDER, 'emails-generated.txt')
VALID_FILE     = os.path.join(EMAILS_FOLDER, 'valid_emails.txt')
INVALID_FILE   = os.path.join(EMAILS_FOLDER, 'invalid_emails.txt')
os.makedirs(EMAILS_FOLDER, exist_ok=True)
MAX_THREADS = 10

# ─── Data Lists ─────────────────────────────────────────────

first_names = [
    'James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph',
    'Thomas', 'Charles', 'Christopher', 'Daniel', 'Matthew', 'Anthony', 'Mark',
    'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Kenneth', 'Kevin', 'Brian',
    'George', 'Edward', 'Ronald', 'Timothy', 'Jason', 'Jeffrey', 'Ryan', 'Jacob',
    'Gary', 'Nicholas', 'Eric', 'Jonathan', 'Stephen', 'Larry', 'Justin', 'Scott',
    'Brandon', 'Benjamin', 'Samuel', 'Gregory', 'Alexander', 'Frank', 'Patrick',
    'Jack', 'Dennis', 'Jerry', 'Tyler', 'Mary', 'Patricia', 'Jennifer', 'Linda',
    'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen', 'Nancy', 'Margaret',
    'Lisa', 'Betty', 'Dorothy', 'Sandra', 'Ashley', 'Kimberly', 'Donna', 'Emily',
    'Michelle', 'Carol', 'Amanda', 'Melissa', 'Deborah', 'Stephanie', 'Rebecca',
    'Sharon', 'Laura', 'Cynthia', 'Kathleen', 'Amy', 'Shirley', 'Angela', 'Helen',
    'Anna', 'Brenda', 'Pamela', 'Nicole', 'Emma', 'Katherine', 'Christine', 'Debra',
    'Rachel', 'Catherine', 'Carolyn', 'Janet', 'Ruth', 'Maria', 'Heather', 'Diane',
    'Virginia', 'Julie', 'Joyce', 'Victoria'
]

last_names = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
    'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
    'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
    'Carter', 'Roberts', 'Gomez', 'Phillips', 'Evans', 'Turner', 'Diaz', 'Parker',
    'Cruz', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales', 'Murphy',
    'Cook', 'Rogers', 'Gutierrez', 'Ortiz', 'Morgan', 'Cooper', 'Peterson', 'Bailey',
    'Reed', 'Kelly', 'Howard'
]
domain_list = ['gmail.com','yahoo.com','outlook.com','hotmail.com','protonmail.com']

# ─── Helper Functions ────────────────────────────────────────

def generate_email(domain=None):
    states = ['ny', 'ca', 'tx', 'fl', 'il', 'pa', 'oh', 'mi', 'ga', 'nc', 'nj']
    cities = ['nyc', 'la', 'houston', 'chicago', 'philly', 'atlanta', 'dallas', 'miami', 'boston', 'seattle']
    suffixes = ['dev', 'runner', 'gamer', 'pro', 'life', 'tech', 'usa', 'mail', 'home', 'net']
    
    fn = random.choice(first_names).lower()
    ln = random.choice(last_names).lower()
    city_or_state = random.choice(states + cities)
    suffix = random.choice(suffixes)
    birth_year = str(random.randint(1970, 2005))
    
    sep = random.choice([".", "_", ""])
    domain = domain if domain else random.choices(
        domain_list, weights=[50, 20, 15, 10, 5], k=1
    )[0]
    
    formats = [
        f"{fn}{sep}{ln}{sep}{birth_year}",
        f"{fn[0]}{sep}{ln}{sep}{city_or_state}",
        f"{ln}{sep}{fn[0]}{sep}{birth_year}",
        f"{fn}{sep}{ln}{sep}{suffix}{sep}{city_or_state}",
        f"{fn}{sep}{ln}",
        f"{fn}{sep}{ln}{random.randint(1, 999)}"
    ]
    
    return random.choice(formats) + f"@{domain}"


def append_to_file(path, emails):
    with open(path, 'a') as f:
        for e in emails:
            f.write(e + '\n')

def check_email_smtp(email, pause_evt, stop_evt):
    while pause_evt.is_set() and not stop_evt.is_set():
        pass
    if stop_evt.is_set():
        return None
    domain = email.split('@')[-1]
    try:
        mx = dns.resolver.resolve(domain,'MX')[0].exchange.to_text()
        server = smtplib.SMTP(timeout=10)
        server.connect(mx)
        server.helo('etest.com')
        server.mail('mouad@notou.com')
        code,_ = server.rcpt(email)
        server.quit()
        return (email, code == 250)
    except:
        return (email, False)


# ─── GUI ────────────────────────────────────────────────────

def create_interface():
    root = tk.Tk()
    root.title("💌 Email Toolkit")
    root.geometry("800x720")
    root.configure(bg="#1f1f1f")

    # ── Style ────────────────────────────────────────────────
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", 
        background="#1f1f1f",
        foreground="white",
        fieldbackground="#121212",
        bordercolor="#1f1f1f",
        lightcolor="#1f1f1f",
        darkcolor="#1f1f1f"
    )

    style.configure("TNotebook", background="#1f1f1f", borderwidth=0)
    style.configure("TNotebook.Tab",
        background="#333333", foreground="white",
        padding=(12,6), font=("Segoe UI",10,"bold"),
        borderwidth=0
    )
    style.map("TNotebook.Tab",
        background=[("selected", "#1f1f1f")],
        foreground=[("selected", "white")]
    )

    style.configure("TButton",
        background="#008cff", foreground="white",
        padding=(6,4), relief="flat",
        font=("Segoe UI", 9, "bold")
    )
    style.map("TButton",
        background=[("active", "#006bb3"), ("disabled", "#555555")]
    )

    style.configure("TEntry",
        fieldbackground="#121212", foreground="white",
        borderwidth=0, padding=4
    )
    style.configure("TCombobox",
        fieldbackground="#121212", foreground="white",
        borderwidth=0, padding=4
    )

    style.configure("TLabel", background="#1f1f1f", foreground="white")
    style.configure("TCheckbutton", background="#1f1f1f", foreground="white")

    # ── Logging Terminal ─────────────────────────────────────
    log_q = queue.Queue()
    pause_evt = threading.Event()
    stop_evt  = threading.Event()

    terminal = tk.Text(root, height=14,
                       bg="#0a0a0a", fg="#39ff14",
                       insertbackground="white",
                       font=("Consolas",10),
                       bd=0,
                       highlightthickness=0)
    terminal.pack(fill='x', padx=20, pady=(10,5))
    terminal.configure(state='disabled')

    def log(msg):
        terminal.configure(state='normal')
        terminal.insert(tk.END, msg + "\n")
        terminal.see(tk.END)
        terminal.configure(state='disabled')

    def poll():
        while not log_q.empty():
            log(log_q.get())
        root.after(100, poll)
    root.after(100, poll)

    # ── Tabs ─────────────────────────────────────────────────
    nb = ttk.Notebook(root)
    nb.pack(fill='both', expand=True, padx=20, pady=5)

    # --- Generate Tab ---
    gen = ttk.Frame(nb, padding=20)
    nb.add(gen, text="Generate Emails")
    for i in range(4):
        gen.columnconfigure(i, weight=1)

    ttk.Label(gen, text="Number of Emails:")\
        .grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0,5))
    cnt = tk.StringVar(value="100")
    ttk.Entry(gen, textvariable=cnt)\
        .grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,10))

    ttk.Label(gen, text="Domain:")\
        .grid(row=2, column=0, columnspan=2, sticky='ew')
    dom = tk.StringVar(value=domain_list[0])
    ttk.Combobox(gen, textvariable=dom, values=domain_list, state="readonly")\
        .grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0,10))

    clr = tk.BooleanVar()
    ttk.Checkbutton(gen, text="Clear old data before generate", variable=clr)\
        .grid(row=4, column=0, columnspan=2, sticky='w', pady=(0,10))

    ttk.Label(gen, text="Output File:")\
        .grid(row=5, column=0, columnspan=2, sticky='ew')
    outg = tk.StringVar(value=GENERATED_FILE)
    ttk.Entry(gen, textvariable=outg)\
        .grid(row=6, column=0, columnspan=2, sticky='ew', pady=(0,10))

    def generate_emails():
        try:
            num = int(cnt.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return

        output_path = outg.get()
        domain = dom.get()

        emails = [generate_email(domain) for _ in range(num)]
        
        if clr.get():
            open(output_path, 'w').close()

        append_to_file(output_path, emails)
        log_q.put(f"[✔] Generated {num} emails saved to '{output_path}'.")

    ttk.Button(gen, text="Generate", command=generate_emails)\
        .grid(row=7, column=0, columnspan=2, sticky='ew')



    ttk.Button(gen, text="Generate", command=generate_emails).grid(row=7, column=0, columnspan=2, sticky='ew', pady=(10,0))


    # --- Verify Tab ---
    verify = ttk.Frame(nb, padding=20)
    nb.add(verify, text="Verify Emails")

    ttk.Label(verify, text="Input File:")\
        .grid(row=0, column=0, sticky='ew', pady=(0,5))
    inf = tk.StringVar(value=GENERATED_FILE)
    ttk.Entry(verify, textvariable=inf)\
        .grid(row=1, column=0, sticky='ew', pady=(0,5))

    ttk.Label(verify, text="Valid Output File:")\
        .grid(row=2, column=0, sticky='ew', pady=(0,5))
    outv = tk.StringVar(value=VALID_FILE)
    ttk.Entry(verify, textvariable=outv)\
        .grid(row=3, column=0, sticky='ew', pady=(0,5))

    ttk.Label(verify, text="Invalid Output File:")\
        .grid(row=4, column=0, sticky='ew', pady=(0,5))
    outi = tk.StringVar(value=INVALID_FILE)
    ttk.Entry(verify, textvariable=outi)\
        .grid(row=5, column=0, sticky='ew', pady=(0,5))

    # Adding a label to display the status message (Done or Error)
    status_label = ttk.Label(verify, text="Status: Waiting...")
    status_label.grid(row=7, column=0, sticky='ew', pady=(10, 5))

    # Stop Event Flag
    stop_evt = threading.Event()
    pause_evt = threading.Event()

    def start_verify():
        stop_evt.clear()  # Reset the stop event to continue the process
        pause_evt.clear()  # Reset the pause event to continue the process
        status_label.config(text="Status: Verifying...")  # Set status to "Verifying"
        try:
            emails = [l.strip() for l in open(inf.get()) if l.strip()]
        except:
            return messagebox.showerror("Error", "Cannot open input file.")
        
        open(outv.get(), 'w').close()  # Clear the valid output file
        open(outi.get(), 'w').close()  # Clear the invalid output file

        def verify_worker(email):
            result = check_email_smtp(email, pause_evt, stop_evt)
            if result:
                e, valid = result
                if valid:
                    append_to_file(outv.get(), [e])
                    log_q.put(f"[VALID]   {e}")
                else:
                    append_to_file(outi.get(), [e])
                    log_q.put(f"[INVALID] {e}")
            return result

        def run_verification():
            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                futures = [executor.submit(verify_worker, email) for email in emails]
                for _ in as_completed(futures):
                    if stop_evt.is_set():
                        break
            status_label.config(text="Status: Done ✅")

        threading.Thread(target=run_verification).start()

    def stop_verify():
        stop_evt.set()
        status_label.config(text="Status: Stopped ❌")

    def pause_resume():
        if not pause_evt.is_set():
            pause_evt.set()
            status_label.config(text="Status: Paused ⏸️")
        else:
            pause_evt.clear()
            status_label.config(text="Status: Resumed ▶️")

    ttk.Button(verify, text="Start", command=start_verify)\
        .grid(row=6, column=0, sticky='ew', pady=(10, 5))
    ttk.Button(verify, text="Pause/Resume", command=pause_resume)\
        .grid(row=8, column=0, sticky='ew', pady=(5, 5))
    ttk.Button(verify, text="Stop", command=stop_verify)\
        .grid(row=9, column=0, sticky='ew', pady=(5, 5))

    # --- Arrange Tab ---
    arrange = ttk.Frame(nb, padding=20)
    nb.add(arrange, text="Arrange Emails")

    ttk.Label(arrange, text="Email Editor:")\
        .grid(row=0, column=0, sticky='w', pady=(0,5))

    email_text = tk.Text(arrange, height=25, width=70, bg="#0a0a0a", fg="white", insertbackground="white")
    email_text.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=(0,10))

    arrange.columnconfigure(0, weight=1)
    arrange.columnconfigure(1, weight=1)
    arrange.columnconfigure(2, weight=1)
    arrange.rowconfigure(1, weight=1)

    def arrange_data():
        raw = email_text.get("1.0", tk.END)
        emails = raw.replace(',', '\n').replace(';', '\n').splitlines()
        cleaned = sorted(set(email.strip() for email in emails if email.strip()))
        email_text.delete("1.0", tk.END)
        email_text.insert(tk.END, "\n".join(cleaned))

    def sort_emails(reverse=False):
        emails = email_text.get("1.0", tk.END).strip().splitlines()
        emails = [e.strip() for e in emails if e.strip()]
        emails.sort(reverse=reverse)
        email_text.delete("1.0", tk.END)
        email_text.insert(tk.END, '\n'.join(emails))

    def remove_duplicates():
        emails = email_text.get("1.0", tk.END).strip().splitlines()
        seen = set()
        unique_emails = []
        for email in emails:
            email = email.strip()
            if email and email not in seen:
                unique_emails.append(email)
                seen.add(email)
        email_text.delete("1.0", tk.END)
        email_text.insert(tk.END, '\n'.join(unique_emails))

    def save_cleaned():
        emails = email_text.get("1.0", tk.END).strip()
        if emails:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                    filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, 'w') as f:
                    f.write(emails)
                messagebox.showinfo("Saved", f"Saved to:\n{file_path}")

    ttk.Button(arrange, text="Arrange", command=arrange_data)\
        .grid(row=2, column=0, sticky='ew', pady=(10,0))
    ttk.Button(arrange, text="Sort A–Z", command=lambda: sort_emails(False))\
        .grid(row=2, column=1, sticky='ew', pady=(10,0))
    ttk.Button(arrange, text="Sort Z–A", command=lambda: sort_emails(True))\
        .grid(row=2, column=2, sticky='ew', pady=(10,0))
    ttk.Button(arrange, text="Remove Duplicates", command=remove_duplicates)\
        .grid(row=3, column=0, columnspan=1, sticky='ew', pady=(5,0))
    ttk.Button(arrange, text="Save Cleaned", command=save_cleaned)\
        .grid(row=3, column=1, columnspan=2, sticky='ew', pady=(5,0))

    root.mainloop()

if __name__ == "__main__":
    create_interface()
