import tkinter as tk
from tkinter import ttk, filedialog
import re, time, csv, random

# ==========================================
# Matrix Rain Background Effect
# ==========================================
class MatrixRain:
    def __init__(self, canvas, width, height, font=("Courier New", 12), glyphs="01"):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.font = font
        self.glyphs = glyphs
        self.drops = [0 for _ in range(width // 15)]

    def step(self):
        self.canvas.delete("matrix")
        for i in range(len(self.drops)):
            x = i * 15
            y = self.drops[i] * 15
            char = random.choice(self.glyphs)
            self.canvas.create_text(x, y, text=char, fill="#00FF41",
                                    font=self.font, tags="matrix")
            if y > self.height and random.random() > 0.975:
                self.drops[i] = 0
            self.drops[i] += 1

# ==========================================
# Feature Extraction + Scoring
# ==========================================
def extract_features(url):
    return {
        "has_ip": bool(re.search(r'\d+\.\d+\.\d+\.\d+', url)),
        "has_at": "@" in url,
        "long_url": len(url) > 75,
        "suspicious_words": any(word in url for word in
                                ["login", "verify", "update", "signin", "bank", "secure", "account"]),
        "https": url.startswith("https://"),
        "dot_count": url.count(".") > 3,
        "hyphen": "-" in url,
        "fake_google": "goog1e" in url or "g00gle" in url
    }

def calculate_score(features):
    score = 0
    score += features["has_ip"] * 2
    score += features["has_at"] * 2
    score += features["long_url"] * 1
    score += features["suspicious_words"] * 3
    score += (not features["https"]) * 2
    score += features["dot_count"] * 2
    score += features["hyphen"] * 2
    score += features["fake_google"] * 3
    return score

def classify_url(url):
    features = extract_features(url)
    score = calculate_score(features)
    if score >= 6:
        return "⚠️ Phishing Detected", score, features
    else:
        return "✅ Safe Website", score, features

# ==========================================
# Logging Function
# ==========================================
import csv
import time

def log_result(url, verdict, score, features):
    with open("phishing_log.csv", "a", newline="", encoding="utf-8") as file:  # ✅ added encoding
        writer = csv.writer(file)
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), url, verdict, score, features])


# ==========================================
# UI Actions
# ==========================================
def on_check_url():
    url = url_entry.get().strip()
    if not url:
        result_label.config(text="❌ Please enter a URL!", fg="red")
        return

    # Animate progress bar
    progress_bar["value"] = 0
    for i in range(0, 101, 10):
        progress_bar["value"] = i
        root.update_idletasks()
        time.sleep(0.05)

    verdict, score, features = classify_url(url)
    result_label.config(text=f"{verdict}\nScore: {score}/10",
                        fg=("red" if "Phishing" in verdict else "lime"))

    scan_console.config(state="normal")
    scan_console.insert("end", f"[SCAN] {url} → {verdict} (score={score})\n")
    scan_console.see("end")
    scan_console.config(state="disabled")

    report_box.config(state="normal")
    report_box.delete("1.0", "end")
    report_box.insert("end", f"Detailed Features:\n{features}")
    report_box.config(state="disabled")

    # Log result
    log_result(url, verdict, score, features)

def on_check_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not file_path: return

    with open(file_path, newline="") as f:
        reader = csv.reader(f)
        urls = list(reader)

    for row in urls:
        if not row: continue
        url = row[0].strip()
        verdict, score, features = classify_url(url)

        scan_console.config(state="normal")
        scan_console.insert("end", f"[CSV] {url} → {verdict} (score={score})\n")
        scan_console.see("end")
        scan_console.config(state="disabled")

        # Log result
        log_result(url, verdict, score, features)

# ==========================================
# Build GUI (with Progress Bar)
# ==========================================
WIDTH, HEIGHT = 980, 640
root = tk.Tk()
root.title("Phishing URL Detector — Hacker Terminal (Advanced)")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.configure(bg="#0B0B0B")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                   highlightthickness=0, bg="#0B0B0B")
canvas.place(x=0, y=0)
matrix = MatrixRain(canvas, WIDTH, HEIGHT, font=("Courier New", 12), glyphs="01")

def animate():
    matrix.step()
    root.after(33, animate)
animate()

ui = tk.Frame(root, bg="#0B0B0B")
ui.place(relx=0.5, rely=0.5, anchor="center")

title = tk.Label(ui, text="💻 PHISHING URL DETECTOR — ADVANCED",
                 font=("Courier New", 22, "bold"),
                 bg="#0B0B0B", fg="#39FF14")
title.grid(row=0, column=0, columnspan=3, pady=(10, 20))

lbl = tk.Label(ui, text="Enter URL:", font=("Courier New", 14),
               bg="#0B0B0B", fg="#39FF14")
lbl.grid(row=1, column=0, sticky="e", padx=(0, 10))

url_entry = tk.Entry(ui, font=("Courier New", 14), width=58,
                     bd=0, relief="flat", bg="#141414",
                     fg="#39FF14", insertbackground="#39FF14")
url_entry.grid(row=1, column=1, sticky="we", pady=5)

btn_frame = tk.Frame(ui, bg="#0B0B0B")
btn_frame.grid(row=1, column=2, rowspan=2, padx=(12, 0))

btn_style = dict(bg="#0B0B0B", fg="#39FF14",
                 activebackground="#0B0B0B", activeforeground="#39FF14",
                 font=("Courier New", 12, "bold"),
                 bd=2, relief="ridge",
                 width=16, cursor="hand2")

check_btn = tk.Button(btn_frame, text="SCAN URL", command=on_check_url, **btn_style)
check_btn.pack(pady=(0, 6))
csv_btn = tk.Button(btn_frame, text="SCAN CSV", command=on_check_csv, **btn_style)
csv_btn.pack()

result_label = tk.Label(ui, text="", font=("Courier New", 16, "bold"),
                        bg="#0B0B0B", fg="#39FF14", anchor="w")
result_label.grid(row=2, column=0, columnspan=3, sticky="we", pady=(10, 5))

progress_bar = ttk.Progressbar(ui, orient="horizontal", length=600, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, pady=(0, 15))

console_frame = tk.Frame(ui, bg="#0B0B0B")
console_frame.grid(row=4, column=0, columnspan=3, pady=(0, 10))

scan_console = tk.Text(console_frame, height=14, width=62,
                       bg="#0D0D0D", fg="#2cff2c",
                       font=("Courier New", 11), relief="flat")
scan_console.pack(side="left", padx=(0, 6))
scan_console.config(state="disabled")

report_box = tk.Text(console_frame, height=14, width=46,
                     bg="#0D0D0D", fg="#39FF14",
                     font=("Courier New", 11), relief="flat")
report_box.pack(side="left")
report_box.config(state="disabled")

footer = tk.Label(ui, text="Developed by Ayan Chogle • Cybersecurity ",
                  font=("Courier New", 10),
                  bg="#0B0B0B", fg="#39FF14")
footer.grid(row=5, column=0, columnspan=3, pady=(10, 0))

def on_enter(e): e.widget.config(bd=3)
def on_leave(e): e.widget.config(bd=2)
for b in (check_btn, csv_btn):
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)

url_entry.focus_set()
root.mainloop()
