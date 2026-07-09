# app.py
import os
import sys
import subprocess
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog
import random
import string
import webbrowser
import urllib.request
import zipfile
import re
import ctypes

# ==========================================
# KHẮC PHỤC LỖI CRASH KHI ẨN CONSOLE (VỚI NUITKA/PYINSTALLER)
# ==========================================
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

# ==========================================
# KHAI BÁO ID ỨNG DỤNG ĐỂ FIX TASKBAR
# ==========================================
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('truongphan.autolienquan.pro.main')
except: pass

# ==========================================
# 1. CHECK & INSTALL THƯ VIỆN
# ==========================================
def check_libs_sync():
    if getattr(sys, 'frozen', False) or "__compiled__" in globals(): return
    print("[*] Đang kiểm tra thư viện...")
    libs = {"cv2": "opencv-python", "numpy": "numpy", "PIL": "Pillow", "requests": "requests", "pandas": "pandas", "openpyxl": "openpyxl"}
    for lib_import, pip_name in libs.items():
        try: __import__(lib_import)
        except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

check_libs_sync()

import cv2
import numpy as np
import queue
import pandas as pd
from PIL import Image, ImageTk

class AntidetectApp:
    def __init__(self, root):
        self.root = root
        
        self.root.title("AUTO LIÊN QUÂN V2")
        self.root.geometry("1280x850")
        self.root.minsize(900, 600) 
        
        base_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_path, "logo", "logo.png")
        ico_path = os.path.join(base_path, "logo", "logo.ico")
        
        if os.path.exists(logo_path):
            try:
                if os.path.exists(ico_path):
                    self.root.iconbitmap(ico_path)
                self.app_icon = tk.PhotoImage(file=logo_path)
                self.root.iconphoto(True, self.app_icon)
            except: self.app_icon = None
        else: self.app_icon = None

        self.bg_color, self.panel_color, self.accent_color, self.text_color, self.success_color, self.danger_color, self.warning_color = "#0B0F19", "#151A25", "#3B82F6", "#E2E8F0", "#10B981", "#EF4444", "#F59E0B"
        self.root.configure(bg=self.bg_color)

        self.config_file = "config.json"
        self.ld_path = tk.StringVar(value=self.load_config_path())
        self.ld_path.trace_add("write", self.save_config_path)

        self.is_bot_running = False
        self.start_time = 0
        self.accounts = []
        self.file_name = "accounts.txt"
        self.hide_pass = True
        
        self.script_folder = "script"; os.makedirs(self.script_folder, exist_ok=True); os.makedirs("png", exist_ok=True)
        self.current_script_file = os.path.join(self.script_folder, "default.json")
        self.script_steps = self.load_script(self.current_script_file)
        
        self.batch_size = self.last_run_index = 0
        self.vm_toggle_state = self.acc_toggle_state = False

        self.setup_styles(); self.build_ui(); self.load_vms(); self.load_accounts(); self.load_scripts_list(); self.refresh_script_tree()
        self.update_timer(); self.on_action_change()

    def custom_messagebox(self, title, message, msg_type="info"):
        dlg = tk.Toplevel(self.root)
        dlg.title(title); dlg.configure(bg=self.panel_color); dlg.transient(self.root); dlg.grab_set()
        if self.app_icon: dlg.iconphoto(False, self.app_icon)
        color = self.success_color if msg_type == "info" else self.danger_color if msg_type == "error" else self.warning_color
        tk.Label(dlg, text=message, bg=self.panel_color, fg=self.text_color, font=("Segoe UI", 11), justify=tk.CENTER, wraplength=400).pack(pady=30, padx=25)
        btn_frame = tk.Frame(dlg, bg=self.panel_color); btn_frame.pack(side=tk.BOTTOM, pady=20)
        if msg_type in ["info", "error", "warning"]:
            tk.Button(btn_frame, text="Đóng" if msg_type == "error" else "Xác nhận", bg=color, fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, width=15, command=dlg.destroy, cursor="hand2").pack()
        elif msg_type == "yesno":
            self.yesno_result = False
            def on_yes(): self.yesno_result = True; dlg.destroy()
            def on_no(): self.yesno_result = False; dlg.destroy()
            tk.Button(btn_frame, text="Đồng ý", bg=self.danger_color if title == "Xác nhận" else self.success_color, fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, width=12, command=on_yes, cursor="hand2").pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="Hủy", bg="#475569", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, width=12, command=on_no, cursor="hand2").pack(side=tk.LEFT, padx=10)
        dlg.update_idletasks()
        dlg.geometry(f"{dlg.winfo_width() + 40}x{dlg.winfo_height() + 10}+{self.root.winfo_x() + (self.root.winfo_width() // 2) - ((dlg.winfo_width() + 40) // 2)}+{self.root.winfo_y() + (self.root.winfo_height() // 2) - ((dlg.winfo_height() + 10) // 2)}")
        self.root.wait_window(dlg)
        if msg_type == "yesno": return self.yesno_result

    def custom_askstring(self, title, prompt, initialvalue=""):
        dlg = tk.Toplevel(self.root)
        dlg.title(title); dlg.configure(bg=self.panel_color); dlg.transient(self.root); dlg.grab_set()
        if self.app_icon: dlg.iconphoto(False, self.app_icon)
        tk.Label(dlg, text=prompt, bg=self.panel_color, fg=self.text_color, font=("Segoe UI", 11)).pack(pady=(25, 10), padx=25, anchor=tk.W)
        entry = tk.Entry(dlg, bg="#0F172A", fg="white", font=("Segoe UI", 11), insertbackground='white', borderwidth=0)
        entry.pack(fill=tk.X, padx=25, ipady=6)
        if initialvalue: entry.insert(0, initialvalue)
        entry.focus_set()
        self.ask_result = None
        def on_ok(e=None): self.ask_result = entry.get(); dlg.destroy()
        def on_cancel(): self.ask_result = None; dlg.destroy()
        dlg.bind('<Return>', on_ok)
        btn_frame = tk.Frame(dlg, bg=self.panel_color); btn_frame.pack(side=tk.BOTTOM, pady=25)
        tk.Button(btn_frame, text="Xác nhận", bg=self.accent_color, fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, width=12, command=on_ok, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Hủy", bg="#475569", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, width=12, command=on_cancel, cursor="hand2").pack(side=tk.LEFT, padx=10)
        dlg.update_idletasks()
        dlg.geometry(f"450x{dlg.winfo_height() + 20}+{self.root.winfo_x() + (self.root.winfo_width() // 2) - 225}+{self.root.winfo_y() + (self.root.winfo_height() // 2) - ((dlg.winfo_height() + 20) // 2)}")
        self.root.wait_window(dlg)
        return self.ask_result

    def custom_manual_input(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Nhập tài khoản thủ công"); dlg.configure(bg=self.panel_color); dlg.transient(self.root); dlg.grab_set()
        if self.app_icon: dlg.iconphoto(False, self.app_icon)
        frame = tk.Frame(dlg, bg=self.panel_color); frame.pack(pady=20, padx=25, fill=tk.BOTH, expand=True)
        entries = []
        for i, text in enumerate(["Tài khoản (*):", "Mật Khẩu (*):", "Mail:", "Pass Mail:"]):
            tk.Label(frame, text=text, bg=self.panel_color, fg=self.text_color, font=("Segoe UI", 11, "bold" if "*" in text else "normal")).grid(row=i, column=0, sticky=tk.W, pady=8, padx=(0, 15))
            ent = tk.Entry(frame, bg="#0F172A", fg="white", font=("Segoe UI", 11), insertbackground='white', borderwidth=0, width=35)
            ent.grid(row=i, column=1, pady=8, ipady=5); entries.append(ent)
        entries[0].focus_set()
        self.manual_data = None
        def on_ok(e=None):
            if not entries[0].get().strip() or not entries[1].get().strip(): return self.custom_messagebox("Cảnh báo", "Tài khoản & Mật khẩu trống!", "warning")
            self.manual_data = [entries[0].get().strip(), entries[1].get().strip(), entries[2].get().strip(), entries[3].get().strip(), "", ""]
            dlg.destroy()
        def on_cancel(): dlg.destroy()
        dlg.bind('<Return>', on_ok)
        btn_frame = tk.Frame(dlg, bg=self.panel_color); btn_frame.pack(side=tk.BOTTOM, pady=25)
        tk.Button(btn_frame, text="Thêm", bg=self.success_color, fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, width=20, command=on_ok, cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Hủy", bg="#475569", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, width=12, command=on_cancel, cursor="hand2").pack(side=tk.LEFT, padx=10)
        dlg.update_idletasks()
        dlg.geometry(f"{dlg.winfo_width() + 40}x{dlg.winfo_height() + 20}+{self.root.winfo_x() + (self.root.winfo_width() // 2) - ((dlg.winfo_width() + 40) // 2)}+{self.root.winfo_y() + (self.root.winfo_height() // 2) - ((dlg.winfo_height() + 20) // 2)}")
        self.root.wait_window(dlg)
        return self.manual_data

    def load_config_path(self):
        if os.path.exists(self.config_file):
            try: return json.load(open(self.config_file, "r", encoding="utf-8")).get("ld_path", r"C:\LDPlayer\LDPlayer9")
            except: pass
        return r"C:\LDPlayer\LDPlayer9"

    def save_config_path(self, *args):
        try: json.dump({"ld_path": self.ld_path.get()}, open(self.config_file, "w", encoding="utf-8"), indent=4)
        except: pass
            
    def load_script(self, path):
        if os.path.exists(path):
            try: return json.load(open(path, "r", encoding="utf-8"))
            except: pass
        return []

    def save_script(self):
        try: json.dump(self.script_steps, open(self.current_script_file, "w", encoding="utf-8"), indent=4, ensure_ascii=False); self.load_scripts_list()
        except: pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.bg_color)
        style.configure('Panel.TFrame', background=self.panel_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color, font=('Segoe UI', 10))
        style.configure('Panel.TLabel', background=self.panel_color, foreground=self.text_color, font=('Segoe UI', 10))
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background="#1E293B", foreground="#94A3B8", padding=[35, 12], font=('Segoe UI', 11, 'bold'), borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', self.accent_color)], foreground=[('selected', "#FFFFFF")])
        style.configure('Treeview', background=self.panel_color, fieldbackground=self.panel_color, foreground=self.text_color, rowheight=40, font=('Segoe UI', 11), borderwidth=0)
        style.configure('Treeview.Heading', background="#1E293B", foreground="#FFFFFF", font=('Segoe UI', 11, 'bold'), borderwidth=0, padding=[5, 5])
        style.map('Treeview', background=[('selected', '#334155')])

    def build_ui(self):
        footer = tk.Frame(self.root, bg="#0F172A", height=50); footer.pack(side=tk.BOTTOM, fill=tk.X)
        lbl_copy = tk.Label(footer, text="© Bản quyền Trường Phan", fg=self.accent_color, font=('Segoe UI', 11, 'bold', 'underline'), cursor="hand2", bg="#0F172A")
        lbl_copy.pack(side=tk.LEFT, padx=20, pady=12); lbl_copy.bind("<Button-1>", lambda e: webbrowser.open("http://apqt.top"))
        tk.Label(footer, text="⏱ 0s", bg="#0F172A", fg="#FFFFFF", font=('Segoe UI', 11, 'bold')).pack(side=tk.RIGHT, padx=20); self.lbl_timer = footer.winfo_children()[1]
        
        header = tk.Frame(self.root, bg=self.panel_color, pady=10, padx=15); header.pack(fill=tk.X, pady=(0, 10)); header.columnconfigure(1, weight=1) 
        tk.Label(header, text="Đường dẫn LDPlayer:", bg=self.panel_color, fg=self.text_color, font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        path_frame = tk.Frame(header, bg=self.panel_color); path_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        tk.Entry(path_frame, textvariable=self.ld_path, width=45, bg="#0F172A", fg="#FFFFFF", font=('Segoe UI', 10), borderwidth=0, insertbackground='white').pack(side=tk.LEFT, ipady=6, padx=(10, 5))
        tk.Button(path_frame, text="📁 Chọn LDPlayer", command=self.browse_ld_path, bg="#475569", fg="white", font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, padx=10, pady=4, cursor="hand2").pack(side=tk.LEFT)
        tk.Button(header, text="🔄 Làm mới LD", command=self.load_vms, bg="#334155", fg="white", width=12, font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=4, cursor="hand2").grid(row=0, column=2, padx=(10, 5), sticky=tk.E)
        tk.Button(header, text="📱 Làm mới Phone", command=self.refresh_phone, bg="#0ea5e9", fg="white", width=15, font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, pady=4, cursor="hand2").grid(row=0, column=3, padx=(0, 10), sticky=tk.E)

        content_frame = tk.Frame(header, bg=self.panel_color); content_frame.grid(row=1, column=0, columnspan=4, pady=10, sticky=tk.NSEW)
        
        action_frame = tk.Frame(content_frame, bg=self.panel_color); action_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.btn_start = tk.Button(action_frame, text="▶ CHẠY AUTO", font=("Segoe UI", 12, "bold"), bg=self.accent_color, fg="white", pady=6, width=20, relief=tk.FLAT, command=self.start_auto, cursor="hand2"); self.btn_start.pack(pady=(0, 6))
        self.btn_next = tk.Button(action_frame, text="⏭ CHẠY TIẾP THEO", font=("Segoe UI", 11, "bold"), bg="#8B5CF6", fg="white", pady=5, width=22, relief=tk.FLAT, command=self.run_next_batch, cursor="hand2"); self.btn_next.pack(pady=6)
        self.btn_stop = tk.Button(action_frame, text="⏹ DỪNG", font=("Segoe UI", 12, "bold"), bg="#475569", fg="#94A3B8", disabledforeground="#94A3B8", pady=6, width=20, relief=tk.FLAT, command=lambda: None); self.btn_stop.pack(pady=(6, 0))

        vm_frame = tk.Frame(content_frame, bg=self.panel_color, highlightbackground="#334155", highlightthickness=1); vm_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        vm_scroll_y = ttk.Scrollbar(vm_frame, orient=tk.VERTICAL); vm_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        vm_scroll_x = ttk.Scrollbar(vm_frame, orient=tk.HORIZONTAL); vm_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.vm_tree = ttk.Treeview(vm_frame, columns=("check", "name"), show="headings", height=4, yscrollcommand=vm_scroll_y.set, xscrollcommand=vm_scroll_x.set)
        vm_scroll_y.config(command=self.vm_tree.yview); vm_scroll_x.config(command=self.vm_tree.xview)
        
        self.vm_tree.heading("check", text="✔"); self.vm_tree.heading("name", text="Danh sách Máy (Xanh = Đang chạy)")
        self.vm_tree.column("check", width=50, minwidth=50, stretch=tk.NO, anchor=tk.CENTER); self.vm_tree.column("name", width=400, minwidth=300, stretch=tk.YES, anchor=tk.W)
        self.vm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.vm_tree.bind('<Button-1>', self.on_vm_tree_click)
        self.vm_tree.tag_configure('checked_stopped', foreground=self.warning_color, font=('Segoe UI', 11, 'bold'))
        self.vm_tree.tag_configure('unchecked_stopped', foreground='#94A3B8', font=('Segoe UI', 11))
        self.vm_tree.tag_configure('checked_running', foreground=self.success_color, font=('Segoe UI', 11, 'bold')) 
        self.vm_tree.tag_configure('unchecked_running', foreground=self.success_color, font=('Segoe UI', 11))

        self.nb = ttk.Notebook(self.root); self.nb.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        for text, func in [(" 1: Accounts ", self.tab_autologin), (" 2: Cấu Hình ", self.tab_macro), (" 3: Trạng Thái ", self.tab_result), (" 4: Hướng Dẫn ", self.tab_guide)]:
            frame = ttk.Frame(self.nb, style='Panel.TFrame'); self.nb.add(frame, text=text); func(frame)

    def set_stop_btn_state(self, is_running):
        if is_running: self.btn_stop.config(bg=self.danger_color, fg="white", command=self.stop_auto, cursor="hand2")
        else: self.btn_stop.config(bg="#475569", fg="#94A3B8", command=lambda: None, cursor="arrow")

    def browse_ld_path(self):
        if path := filedialog.askdirectory(title="Chọn thư mục chứa LDPlayer"): self.ld_path.set(path); self.load_vms()

    def on_vm_tree_click(self, event):
        region = self.vm_tree.identify("region", event.x, event.y)
        if region == "heading":
            if self.vm_tree.identify_column(event.x) == '#1':
                self.vm_toggle_state = not self.vm_toggle_state
                state_char = "☑" if self.vm_toggle_state else "☐"
                for item_id in self.vm_tree.get_children():
                    vals = list(self.vm_tree.item(item_id, 'values')); vals[0] = state_char
                    is_running = "running" in self.vm_tree.item(item_id, 'tags')[0] if self.vm_tree.item(item_id, 'tags') else False
                    self.vm_tree.item(item_id, values=vals, tags=(f"{'checked' if state_char == '☑' else 'unchecked'}_{'running' if is_running else 'stopped'}",))
        elif region == "cell" and self.vm_tree.identify_column(event.x) == '#1':
            if item_id := self.vm_tree.identify_row(event.y):
                vals = list(self.vm_tree.item(item_id, 'values')); vals[0] = "☐" if vals[0] == "☑" else "☑"
                is_running = "running" in self.vm_tree.item(item_id, 'tags')[0] if self.vm_tree.item(item_id, 'tags') else False
                self.vm_tree.item(item_id, values=vals, tags=(f"{'checked' if vals[0] == '☑' else 'unchecked'}_{'running' if is_running else 'stopped'}",))

    def get_selected_vms(self): return [self.vm_tree.item(i, 'values')[1].split('-')[0].strip() for i in self.vm_tree.get_children() if self.vm_tree.item(i, 'values')[0] == "☑"]
    
    def refresh_phone(self):
        if self.ld_path.get().strip():
            self.ld_path.set("")
        self.load_vms()

    def load_vms(self):
        for item in self.vm_tree.get_children(): self.vm_tree.delete(item)
        ld_dir = self.ld_path.get().strip()
        if ld_dir and os.path.exists(os.path.join(ld_dir, "ldconsole.exe")):
            for l in self.ldc("list2").split('\n'):
                if len(p := l.split(',')) >= 5: self.vm_tree.insert("", tk.END, values=("☐", f"{p[0]} - {p[1]}"), tags=("unchecked_running" if p[4] == '1' else "unchecked_stopped",))
        else:
            try:
                startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                out = subprocess.check_output(["adb", "devices"], startupinfo=startupinfo, creationflags=0x08000000).decode('utf-8')
                for line in out.strip().split('\n')[1:]:
                    if '\t' in line:
                        dev_id, state = line.split('\t')
                        if state.strip() == 'device':
                            try: model = subprocess.check_output(["adb", "-s", dev_id, "shell", "getprop", "ro.product.model"], startupinfo=startupinfo, creationflags=0x08000000).decode('utf-8').strip()
                            except: model = "Real Phone"
                            self.vm_tree.insert("", tk.END, values=("☐", f"{dev_id} - {model}"), tags=("unchecked_running",))
            except: pass

    def tab_result(self, p):
        top_f = tk.Frame(p, bg=self.panel_color); top_f.pack(fill=tk.X, pady=10)
        self.lbl_status = tk.Label(top_f, text="TRẠNG THÁI: ĐANG CHỜ LỆNH...", bg=self.panel_color, fg=self.warning_color, font=('Segoe UI', 14, 'bold')); self.lbl_status.pack(side=tk.LEFT, padx=20)
        tk.Button(top_f, text="🗑 Xóa Lịch Sử", command=self.clear_log, bg=self.danger_color, fg="white", font=('Segoe UI', 9, 'bold'), relief=tk.FLAT, padx=15, pady=4, cursor="hand2").pack(side=tk.RIGHT, padx=20)
        self.txt_log = tk.Text(p, bg="#000000", fg="#34D399", font=("Consolas", 11), state=tk.DISABLED, borderwidth=0, padx=15, pady=15); self.txt_log.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    def clear_log(self): self.txt_log.config(state=tk.NORMAL); self.txt_log.delete(1.0, tk.END); self.txt_log.config(state=tk.DISABLED)

    def tab_autologin(self, p):
        right_wrapper = tk.Frame(p, bg=self.panel_color)
        right_wrapper.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=15)
        
        right_canvas = tk.Canvas(right_wrapper, bg=self.panel_color, highlightthickness=0, width=250)
        right_scroll_y = ttk.Scrollbar(right_wrapper, orient=tk.VERTICAL, command=right_canvas.yview)
        right_scroll_x = ttk.Scrollbar(right_wrapper, orient=tk.HORIZONTAL, command=right_canvas.xview)
        right_canvas.configure(yscrollcommand=right_scroll_y.set, xscrollcommand=right_scroll_x.set)
        
        right_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        right_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_p = tk.Frame(right_canvas, bg=self.panel_color)
        right_canvas.create_window((0, 0), window=right_p, anchor="nw")
        right_p.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")))
        
        tk.Button(right_p, text="Đánh Dấu", font=("Segoe UI", 10, "bold"), bg=self.success_color, fg="white", pady=12, width=28, relief=tk.FLAT, command=self.mark_account, cursor="hand2").pack(pady=(20, 15))
        tk.Button(right_p, text="Bỏ Đánh Dấu", font=("Segoe UI", 10, "bold"), bg="#475569", fg="white", pady=10, width=28, relief=tk.FLAT, command=self.unmark_account, cursor="hand2").pack(pady=(0, 15))
        tk.Button(right_p, text="🗑 Xóa Tài Khoản", font=("Segoe UI", 10, "bold"), bg=self.danger_color, fg="white", pady=10, width=28, relief=tk.FLAT, command=self.delete_account, cursor="hand2").pack(pady=(0, 0))

        left_p = tk.Frame(p, bg=self.panel_color); left_p.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        toolbar = tk.Frame(left_p, bg=self.panel_color); toolbar.pack(fill=tk.X, pady=(0, 10))
        tk.Button(toolbar, text="📁 Nhập File", font=("Segoe UI", 9, "bold"), bg="#475569", fg="white", relief=tk.FLAT, command=self.import_txt, padx=10, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=(0,5))
        tk.Button(toolbar, text="📄 Tải File Mẫu", font=("Segoe UI", 9, "bold"), bg="#8B5CF6", fg="white", relief=tk.FLAT, command=self.download_sample_file, padx=10, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=(0,5))
        tk.Button(toolbar, text="✍ Nhập Thủ Công", font=("Segoe UI", 9, "bold"), bg="#10B981", fg="white", relief=tk.FLAT, command=self.add_manual_account, padx=10, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=(0,5))
        tk.Button(toolbar, text="👁 Ẩn/Hiện MK", font=("Segoe UI", 9, "bold"), bg="#64748B", fg="white", relief=tk.FLAT, command=self.toggle_password, padx=10, pady=4, cursor="hand2").pack(side=tk.LEFT, padx=(0,0))
        tk.Label(toolbar, text="* Có thể Bấm đúp chuột để Chọn/Bỏ chọn", bg=self.panel_color, fg="#94A3B8", font=('Segoe UI', 9, 'italic')).pack(side=tk.RIGHT)

        tree_frame = tk.Frame(left_p, bg=self.panel_color); tree_frame.pack(fill=tk.BOTH, expand=True)
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL); tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL); tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree = ttk.Treeview(tree_frame, columns=("check", "stt", "tk", "mk", "mail", "pmail", "note"), show="headings", height=10, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.config(command=self.tree.yview); tree_scroll_x.config(command=self.tree.xview)
        
        for col, width, anchor, text in [("check", 50, tk.CENTER, "✔"), ("stt", 40, tk.CENTER, "STT"), ("tk", 120, tk.W, "Tài Khoản"), ("mk", 100, tk.W, "Mật Khẩu"), ("mail", 140, tk.W, "Mail"), ("pmail", 100, tk.W, "Pass Mail"), ("note", 150, tk.W, "Ghi Chú")]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, minwidth=width, stretch=tk.NO if col in ['check', 'stt'] else tk.YES, anchor=anchor)
            
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); self.tree.bind('<Button-1>', self.on_acc_tree_click); self.tree.bind('<Double-1>', self.on_acc_tree_double_click) 
        self.tree.tag_configure('checked', foreground=self.warning_color, font=('Segoe UI', 12, 'bold')); self.tree.tag_configure('unchecked', foreground='#94A3B8', font=('Segoe UI', 12))
        self.tree.tag_configure('success', background=self.success_color, foreground='white', font=('Segoe UI', 11)); self.tree.tag_configure('failed', background=self.danger_color, foreground='white', font=('Segoe UI', 11))  

    def add_manual_account(self):
        if data := self.custom_manual_input():
            if not any(a[0] == data[0] for a in self.accounts):
                self.accounts.append(data); self.tree.insert("", tk.END, values=("☐", len(self.accounts), data[0], "***" if self.hide_pass else data[1], data[2], "***" if self.hide_pass else data[3], data[5]), tags=('unchecked',)); self.save_accounts_file()
            else: self.custom_messagebox("Trùng lặp", f"Tài khoản '{data[0]}' đã tồn tại.", "warning")

    def download_sample_file(self):
        try:
            pd.DataFrame({"Tài Khoản": ["taikhoan1"], "Mật Khẩu": ["matkhau1"], "Mail": ["mail1@gmail.com"], "Pass Mail": ["passmail1"]}).to_excel("Mau_Nhap_Tai_Khoan.xlsx", index=False)
            with open("Mau_Nhap_Tai_Khoan.txt", 'w', encoding='utf-8') as f: f.write("taikhoan1|matkhau1|mail1@gmail.com|passmail1\n")
            self.custom_messagebox("Thành công", "Đã xuất 2 file mẫu thành công.", "info")
        except: pass

    def on_acc_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading" and self.tree.identify_column(event.x) == '#1':
            self.acc_toggle_state = not self.acc_toggle_state
            state_char = "☑" if self.acc_toggle_state else "☐"
            for item_id in self.tree.get_children():
                vals = list(self.tree.item(item_id, 'values')); vals[0] = state_char
                tags = [t for t in self.tree.item(item_id, 'tags') if t not in ['checked', 'unchecked']]; tags.append('checked' if state_char == "☑" else 'unchecked')
                self.tree.item(item_id, values=vals, tags=tuple(tags))
        elif region == "cell" and self.tree.identify_column(event.x) == '#1':
            if item_id := self.tree.identify_row(event.y):
                vals = list(self.tree.item(item_id, 'values')); vals[0] = "☐" if vals[0] == "☑" else "☑"
                tags = [t for t in self.tree.item(item_id, 'tags') if t not in ['checked', 'unchecked']]; tags.append('checked' if vals[0] == "☑" else 'unchecked')
                self.tree.item(item_id, values=vals, tags=tuple(tags))

    def on_acc_tree_double_click(self, event):
        if self.tree.identify("region", event.x, event.y) == "cell":
            if item_id := self.tree.identify_row(event.y):
                vals = list(self.tree.item(item_id, 'values')); vals[0] = "☐" if vals[0] == "☑" else "☑"
                tags = [t for t in self.tree.item(item_id, 'tags') if t not in ['checked', 'unchecked']]; tags.append('checked' if vals[0] == "☑" else 'unchecked')
                self.tree.item(item_id, values=vals, tags=tuple(tags))

    def delete_account(self):
        if not (sel := self.tree.selection()): return self.custom_messagebox("Lỗi", "Vui lòng chọn tài khoản.", "warning")
        if not self.custom_messagebox("Xác nhận", f"Xóa {len(sel)} tài khoản?", "yesno"): return
        for idx in sorted([self.tree.index(item) for item in sel], reverse=True):
            if idx < len(self.accounts): del self.accounts[idx]
        for item_id in sel: self.tree.delete(item_id)
        for i, item_id in enumerate(self.tree.get_children()): vals = list(self.tree.item(item_id, 'values')); vals[1] = i + 1; self.tree.item(item_id, values=vals)
        self.save_accounts_file()

    def tab_macro(self, p):
        right_wrapper = tk.Frame(p, bg=self.panel_color)
        right_wrapper.pack(side=tk.RIGHT, fill=tk.Y, padx=15, pady=15)
        
        right_canvas = tk.Canvas(right_wrapper, bg=self.panel_color, highlightthickness=0, width=380)
        right_scroll_y = ttk.Scrollbar(right_wrapper, orient=tk.VERTICAL, command=right_canvas.yview)
        right_scroll_x = ttk.Scrollbar(right_wrapper, orient=tk.HORIZONTAL, command=right_canvas.xview)
        right_canvas.configure(yscrollcommand=right_scroll_y.set, xscrollcommand=right_scroll_x.set)
        
        right_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        right_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_p = tk.Frame(right_canvas, bg=self.panel_color)
        right_canvas.create_window((0, 0), window=right_p, anchor="nw")
        right_p.bind("<Configure>", lambda e: right_canvas.configure(scrollregion=right_canvas.bbox("all")))

        tk.Label(right_p, text="TÙY CHỈNH BƯỚC", font=("Segoe UI", 12, "bold"), bg=self.panel_color, fg=self.accent_color).grid(row=0, column=0, columnspan=2, pady=(0, 15))
        tk.Label(right_p, text="Tên Bước:", bg=self.panel_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.txt_step_name = tk.Entry(right_p, width=30, font=("Segoe UI", 10), bg="#0F172A", fg="white", borderwidth=0, insertbackground='white'); self.txt_step_name.grid(row=1, column=1, pady=8, ipady=4); self.txt_step_name.insert(0, "Bước mới")
        tk.Label(right_p, text="Hành Động:", bg=self.panel_color, fg=self.text_color, font=("Segoe UI", 10)).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.cb_action = ttk.Combobox(right_p, values=["Click Ảnh", "Check Ảnh (Cố định 60s)", "Click Tọa Độ", "Nhập Tài Khoản", "Nhập Mật Khẩu", "Mở App", "Xóa Data App", "Cài APK", "Chạy Script Khác", "Delay (Nghỉ)", "Quay lại Bước (Lặp)", "Kết thúc Kịch Bản"], width=28, state="readonly", font=("Segoe UI", 10))
        self.cb_action.grid(row=2, column=1, pady=8); self.cb_action.set("Click Ảnh"); self.cb_action.bind("<<ComboboxSelected>>", self.on_action_change)
        
        self.lbl_value = tk.Label(right_p, text="Giá Trị:", bg=self.panel_color, fg=self.text_color, font=("Segoe UI", 10)); self.lbl_value.grid(row=3, column=0, sticky=tk.W, pady=8)
        self.val_frame = tk.Frame(right_p, bg=self.panel_color); self.val_frame.grid(row=3, column=1, sticky=tk.W)
        self.txt_value = tk.Entry(self.val_frame, width=15, font=("Segoe UI", 10), bg="#0F172A", fg="white", borderwidth=0, insertbackground='white'); self.txt_value.pack(side=tk.LEFT, ipady=4)
        tk.Button(self.val_frame, text="📁", command=self.browse_file, bg="#475569", fg="white", borderwidth=0, padx=6, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=(4,2))
        tk.Button(self.val_frame, text="📸 Cắt", command=self.capture_and_crop, bg="#8B5CF6", fg="white", borderwidth=0, padx=6, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=2)
        tk.Button(self.val_frame, text="📍 Tọa Độ", command=self.get_coordinates, bg="#F59E0B", fg="white", borderwidth=0, padx=6, pady=3, cursor="hand2").pack(side=tk.LEFT, padx=2)

        self.lbl_timeout = tk.Label(right_p, text="Thời gian chờ Max (s):", bg=self.panel_color, fg=self.text_color, font=("Segoe UI", 10)); self.lbl_timeout.grid(row=4, column=0, sticky=tk.W, pady=8)
        self.txt_timeout = tk.Entry(right_p, width=30, font=("Segoe UI", 10), bg="#0F172A", fg="white", borderwidth=0, insertbackground='white'); self.txt_timeout.grid(row=4, column=1, pady=8, ipady=4); self.txt_timeout.insert(0, "10")
        self.lbl_delay = tk.Label(right_p, text="Nghỉ sau khi xong (s):", bg=self.panel_color, fg=self.text_color, font=("Segoe UI", 10)); self.lbl_delay.grid(row=5, column=0, sticky=tk.W, pady=8)
        self.txt_delay = tk.Entry(right_p, width=30, font=("Segoe UI", 10), bg="#0F172A", fg="white", borderwidth=0, insertbackground='white'); self.txt_delay.grid(row=5, column=1, pady=8, ipady=4); self.txt_delay.insert(0, "1")
        self.lbl_retry = tk.Label(right_p, text="Số lần thử (Retry):", bg=self.panel_color, fg=self.text_color, font=("Segoe UI", 10)); self.lbl_retry.grid(row=6, column=0, sticky=tk.W, pady=8)
        self.txt_retries = tk.Entry(right_p, width=30, font=("Segoe UI", 10), bg="#0F172A", fg="white", borderwidth=0, insertbackground='white'); self.txt_retries.grid(row=6, column=1, pady=8, ipady=4); self.txt_retries.insert(0, "1")
        
        btn_f = tk.Frame(right_p, bg=self.panel_color); btn_f.grid(row=7, column=0, columnspan=2, pady=25)
        tk.Button(btn_f, text="➕ Thêm Bước", command=self.add_macro_step, bg=self.success_color, fg="white", font=("Segoe UI", 9, "bold"), width=14, pady=6, relief=tk.FLAT, cursor="hand2").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_f, text="🔄 Cập Nhật", command=self.update_macro_step, bg=self.accent_color, fg="white", font=("Segoe UI", 9, "bold"), width=14, pady=6, relief=tk.FLAT, cursor="hand2").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_f, text="❌ Xóa Bước", command=self.delete_macro_step, bg=self.danger_color, fg="white", font=("Segoe UI", 9, "bold"), width=14, pady=6, relief=tk.FLAT, cursor="hand2").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_f, text="💾 LƯU SCRIPT", command=self.save_script_btn, bg="#8B5CF6", fg="white", font=("Segoe UI", 9, "bold"), width=14, pady=6, relief=tk.FLAT, cursor="hand2").grid(row=1, column=1, padx=5, pady=5)
        
        move_f = tk.Frame(right_p, bg=self.panel_color); move_f.grid(row=8, column=0, columnspan=2)
        tk.Button(move_f, text="▲ Lên", command=self.move_step_up, bg="#475569", fg="white", font=("Segoe UI", 9, "bold"), width=10, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)
        tk.Button(move_f, text="▼ Xuống", command=self.move_step_down, bg="#475569", fg="white", font=("Segoe UI", 9, "bold"), width=10, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=5)

        left_p = tk.Frame(p, bg=self.panel_color); left_p.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        top_left = tk.Frame(left_p, bg=self.panel_color); top_left.pack(fill=tk.X, pady=(0, 10))
        tk.Label(top_left, text="Chọn Script:", font=("Segoe UI", 10, "bold"), bg=self.panel_color, fg="#E2E8F0").pack(side=tk.LEFT)
        self.cb_scripts = ttk.Combobox(top_left, state="readonly", width=30, font=("Segoe UI", 10)); self.cb_scripts.pack(side=tk.LEFT, padx=10); self.cb_scripts.bind("<<ComboboxSelected>>", self.on_script_select)
        tk.Button(top_left, text="Tạo Mới", command=self.new_script_prompt, bg=self.success_color, fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, cursor="hand2").pack(side=tk.LEFT)
        
        tree_frame = tk.Frame(left_p, bg=self.panel_color); tree_frame.pack(fill=tk.BOTH, expand=True)
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL); tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL); tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.macro_tree = ttk.Treeview(tree_frame, columns=("stt", "name", "action", "value", "timeout", "delay", "retries"), show="headings", height=15, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        tree_scroll_y.config(command=self.macro_tree.yview); tree_scroll_x.config(command=self.macro_tree.xview)
        
        for col, text, width, anchor in [("stt", "Bước", 50, tk.CENTER), ("name", "Tên Bước", 100, tk.W), ("action", "Hành Động", 150, tk.W), ("value", "Giá Trị", 120, tk.W), ("timeout", "Chờ(s)", 60, tk.CENTER), ("delay", "Nghỉ(s)", 60, tk.CENTER), ("retries", "Lặp", 50, tk.CENTER)]:
            self.macro_tree.heading(col, text=text)
            self.macro_tree.column(col, width=width, minwidth=width, stretch=tk.NO if col in ['stt', 'timeout', 'delay', 'retries'] else tk.YES, anchor=anchor)
            
        self.macro_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); self.macro_tree.bind('<<TreeviewSelect>>', self.on_macro_select)

    def new_script_prompt(self):
        if name := self.custom_askstring("Tạo mới", "Nhập tên kịch bản mới:"):
            self.current_script_file = os.path.join(self.script_folder, name + (".json" if not name.endswith(".json") else "")); self.script_steps = []; self.save_script(); self.refresh_script_tree()

    def check_install_adb(self):
        try:
            startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(["adb", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, startupinfo=startupinfo)
            self.custom_messagebox("Trạng thái", "ADB đã được cài đặt và hoạt động bình thường.", "info")
        except FileNotFoundError:
            if self.custom_messagebox("Thiếu môi trường", "Hệ thống chưa cài đặt ADB. Cài đặt tự động?", "yesno"): threading.Thread(target=self.download_and_setup_adb, daemon=True).start()

    def download_and_setup_adb(self):
        self.root.after(0, lambda: self.log("⏳ Đang tải ADB..."))
        try:
            urllib.request.urlretrieve("https://dl.google.com/android/repository/platform-tools-latest-windows.zip", "adb_temp.zip")
            with zipfile.ZipFile("adb_temp.zip", 'r') as zip_ref: zip_ref.extractall("adb_toolkit")
            os.remove("adb_temp.zip"); adb_folder = os.path.abspath(os.path.join("adb_toolkit", "platform-tools")); os.environ["PATH"] += os.pathsep + adb_folder
            subprocess.run(["powershell", "-Command", f'[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";{adb_folder}", "User")'], capture_output=True, creationflags=0x08000000)
            self.root.after(0, lambda: self.custom_messagebox("Hoàn tất", f"Cài đặt ADB thành công!\n{adb_folder}", "info"))
        except Exception as e: self.root.after(0, lambda: self.custom_messagebox("Lỗi", f"Lỗi tải ADB:\n{e}", "error"))

    def tab_guide(self, p):
        canvas = tk.Canvas(p, bg=self.panel_color, highlightthickness=0); scrollbar = ttk.Scrollbar(p, orient="vertical", command=canvas.yview); scrollable_frame = tk.Frame(canvas, bg=self.panel_color)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))); canvas.create_window((0, 0), window=scrollable_frame, anchor="nw"); canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20); scrollbar.pack(side="right", fill="y"); canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        tk.Label(scrollable_frame, text="HƯỚNG DẪN SỬ DỤNG - AUTO ĐĂNG NHẬP", font=("Segoe UI", 16, "bold"), bg=self.panel_color, fg=self.accent_color, pady=10).pack(anchor=tk.W)
        link_frame_1 = tk.Frame(scrollable_frame, bg=self.panel_color); link_frame_1.pack(anchor=tk.W, pady=5)
        tk.Label(link_frame_1, text="⛔ Yêu cầu kết nối: ", font=("Segoe UI", 12, "bold"), bg=self.panel_color, fg=self.danger_color).pack(side=tk.LEFT)
        tk.Button(link_frame_1, text="🔍 CÀI ĐẶT ADB TỰ ĐỘNG", command=self.check_install_adb, bg="#8B5CF6", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=10, cursor="hand2").pack(side=tk.LEFT, padx=10)
        
        guide_text = '''======================================================
Dưới đây là nội dung văn bản chi tiết được trích xuất từ các hình ảnh hướng dẫn của bạn:

⛔ LƯU Ý ĐẶC BIỆT VỀ LDPLAYER (VUI LÒNG ĐỌC KỸ):
Phần mềm KHÔNG tự động mở LDPlayer. Bạn CẦN MỞ SẴN các LDPlayer trước khi nhấn CHẠY AUTO.

Hệ thống nhận diện thiết bị qua ADB và ID LDPlayer để chia luồng công việc chính xác.

-> Nếu bạn chọn 3 LDPlayer nhưng chưa mở đủ, tiến trình sẽ báo lỗi và dừng lại.

Kích thước màn hình: BẮT BUỘC sử dụng CÙNG 1 ĐỘ PHÂN GIẢI cho tất cả các tab LDPlayer.

Khuyên dùng chế độ Màn hình ngang (Landscape) để tối ưu tính năng nhận diện ảnh.

🔧 TAB 2: ACCOUNTS (QUẢN LÝ TÀI KHOẢN)
📁 Nhập File TXT: Danh sách định dạng: [TàiKhoản] [MậtKhẩu] (phân cách bằng Khoảng trắng hoặc Tab).

Nút [▶ CHẠY AUTO]: Chọn N tài khoản và N LDPlayer. Hệ thống sẽ chia đều để chạy song song.

Nút [⏭ CHẠY TIẾP THEO]: Tiện ích nâng cao. Sau khi chạy xong lượt đầu, nhấn nút này để phần mềm tự động dời lựa chọn (✔) xuống nhóm tài khoản tiếp theo và khởi chạy lập tức.

📝 Đánh Dấu: Hỗ trợ đính kèm ghi chú lưu trực tiếp vào danh sách.

⚙️ TAB 3: CẤU HÌNH (THIẾT LẬP KỊCH BẢN)
* CÁC HÀNH ĐỘNG ĐẶC BIỆT:

Check Ảnh (Cố định 60s): Dò tìm hình ảnh LIÊN TỤC trên màn hình. Nếu sau 60 giây không tìm thấy sẽ báo lỗi yêu cầu cập nhật lại ảnh gốc. Ngăn chặn triệt để kẹt tool.

Click Ảnh: Tìm và click. Cho phép thiết lập Thời gian chờ Max.

Click Tọa Độ: Tương tác qua tọa độ X Y. Hỗ trợ nút [📍 Tọa Độ] trích xuất vị trí chuẩn xác.

Chạy Script Khác: Gọi tệp tin kịch bản phụ vào kịch bản hiện tại. Quản lý logic dễ dàng hơn.

Mở App / Xóa Data: Sử dụng Tên gói ứng dụng (Ví dụ: com.garena.game.kgvn).

Lưu Script: Xác nhận tên kịch bản mới khi lưu hệ thống.'''
        tk.Label(scrollable_frame, text=guide_text, font=("Segoe UI", 11), bg=self.panel_color, fg=self.text_color, justify=tk.LEFT).pack(anchor=tk.W, pady=10)

    def on_action_change(self, event=None):
        act = self.cb_action.get()
        if act in ["Nhập Tài Khoản", "Nhập Mật Khẩu", "Delay (Nghỉ)", "Kết thúc Kịch Bản"]: self.lbl_value.grid_remove(); self.val_frame.grid_remove()
        else: self.lbl_value.grid(); self.val_frame.grid()
        if act == "Check Ảnh (Cố định 60s)": self.lbl_timeout.grid_remove(); self.txt_timeout.grid_remove()
        else: self.lbl_timeout.grid(); self.txt_timeout.grid()

    def toggle_password(self):
        self.hide_pass = not self.hide_pass
        for item_id in self.tree.get_children():
            if (idx := self.tree.index(item_id)) < len(self.accounts):
                vals = list(self.tree.item(item_id, 'values')); vals[3] = "***" if self.hide_pass else self.accounts[idx][1]; vals[5] = "***" if self.hide_pass else self.accounts[idx][3]; self.tree.item(item_id, values=vals)

    def load_scripts_list(self):
        scripts = [f for f in os.listdir(self.script_folder) if f.endswith('.json')]
        if not scripts: scripts = ["default.json"]; self.save_script()
        self.cb_scripts['values'] = scripts; current_name = os.path.basename(self.current_script_file); self.cb_scripts.set(current_name if current_name in scripts else scripts[0])

    def on_script_select(self, event):
        if sel := self.cb_scripts.get(): self.current_script_file = os.path.join(self.script_folder, sel); self.script_steps = self.load_script(self.current_script_file); self.refresh_script_tree()

    def save_script_btn(self):
        if name := self.custom_askstring("Lưu trữ", "Tên kịch bản:", initialvalue=os.path.basename(self.current_script_file)):
            self.current_script_file = os.path.join(self.script_folder, name + (".json" if not name.endswith(".json") else "")); self.save_script(); self.custom_messagebox("Thành công", f"Đã lưu {name}.", "info")

    def get_coordinates(self):
        if not (vms := self.get_selected_vms()): return self.custom_messagebox("Lỗi", "Chọn 1 Máy để lấy tọa độ.", "error")
        idx = vms[0]; p_guest, p_host = f"/sdcard/screen_c_{idx}.png", f"screen_c_{idx}.png"
        self.run_adb(idx, f"shell screencap -p {p_guest}", 10); self.run_adb(idx, f"pull {p_guest} {p_host}", 10)
        if not os.path.exists(p_host): return self.custom_messagebox("Lỗi", "Không thể lấy ảnh.", "error")
        top = tk.Toplevel(self.root); top.title("Tọa độ")
        
        img = Image.open(p_host)
        max_w, max_h = 800, 700
        scale = min(max_w / img.width, max_h / img.height, 1.0)
        display_w, display_h = int(img.width * scale), int(img.height * scale)
        resample_filter = getattr(Image, 'Resampling', Image).LANCZOS
        display_img = img.resize((display_w, display_h), resample_filter)
        
        tk_img = ImageTk.PhotoImage(display_img)
        canvas = tk.Canvas(top, width=display_w, height=display_h, cursor="cross"); canvas.pack()
        canvas.image = tk_img; canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
        
        def on_click(e): 
            real_x, real_y = int(e.x / scale), int(e.y / scale)
            self.cb_action.set("Click Tọa Độ"); self.on_action_change()
            self.txt_value.delete(0, tk.END); self.txt_value.insert(0, f"{real_x} {real_y}"); top.destroy()
            
        canvas.bind("<Button-1>", on_click)
        top.protocol("WM_DELETE_WINDOW", lambda: (top.destroy(), img.close(), os.remove(p_host) if os.path.exists(p_host) else None))

    def browse_file(self):
        act = self.cb_action.get(); p = filedialog.askopenfilename(filetypes=[("APK", "*.apk")] if act == "Cài APK" else ([("JSON", "*.json")] if act == "Chạy Script Khác" else [("PNG", "*.png")]))
        if p: self.txt_value.delete(0, tk.END); self.txt_value.insert(0, p if act == "Cài APK" else os.path.basename(p))

    def refresh_script_tree(self):
        for item in self.macro_tree.get_children(): self.macro_tree.delete(item)
        for i, s in enumerate(self.script_steps): self.macro_tree.insert("", tk.END, values=(i+1, s.get("step_name", ""), s["action"], s.get("value", ""), s.get("timeout", 10), s.get("delay", 1), s.get("retries", 1)))

    def get_macro_inputs(self): return {"step_name": self.txt_step_name.get() or "Bước", "action": self.cb_action.get(), "value": self.txt_value.get(), "timeout": float(self.txt_timeout.get() or 10), "delay": float(self.txt_delay.get() or 1), "retries": int(self.txt_retries.get() or 1)}
    def add_macro_step(self): self.script_steps.append(self.get_macro_inputs()); self.refresh_script_tree(); self.save_script()
    def update_macro_step(self):
        if sel := self.macro_tree.selection(): self.script_steps[self.macro_tree.index(sel[0])] = self.get_macro_inputs(); self.refresh_script_tree(); self.save_script()
    def delete_macro_step(self):
        if sel := self.macro_tree.selection(): del self.script_steps[self.macro_tree.index(sel[0])]; self.refresh_script_tree(); self.save_script()
    def move_step_up(self):
        if (sel := self.macro_tree.selection()) and (idx := self.macro_tree.index(sel[0])) > 0:
            self.script_steps[idx], self.script_steps[idx-1] = self.script_steps[idx-1], self.script_steps[idx]; self.refresh_script_tree(); self.macro_tree.selection_set(self.macro_tree.get_children()[idx-1]); self.save_script()
    def move_step_down(self):
        if (sel := self.macro_tree.selection()) and (idx := self.macro_tree.index(sel[0])) < len(self.script_steps) - 1:
            self.script_steps[idx], self.script_steps[idx+1] = self.script_steps[idx+1], self.script_steps[idx]; self.refresh_script_tree(); self.macro_tree.selection_set(self.macro_tree.get_children()[idx+1]); self.save_script()

    def on_macro_select(self, event):
        if sel := self.macro_tree.selection():
            s = self.script_steps[self.macro_tree.index(sel[0])]; self.txt_step_name.delete(0, tk.END); self.txt_step_name.insert(0, s.get("step_name", ""))
            self.cb_action.set(s["action"]); self.on_action_change(); self.txt_value.delete(0, tk.END); self.txt_value.insert(0, s.get("value", ""))
            self.txt_timeout.delete(0, tk.END); self.txt_timeout.insert(0, str(s.get("timeout", 10))); self.txt_delay.delete(0, tk.END); self.txt_delay.insert(0, str(s.get("delay", 1)))
            self.txt_retries.delete(0, tk.END); self.txt_retries.insert(0, str(s.get("retries", 1)))

    def capture_and_crop(self):
        if not (vms := self.get_selected_vms()): return self.custom_messagebox("Lỗi", "Chọn 1 Máy.", "error")
        idx = vms[0]; p_guest, p_host = f"/sdcard/sc_{idx}.png", f"sc_{idx}.png"
        self.run_adb(idx, f"shell screencap -p {p_guest}", 10); self.run_adb(idx, f"pull {p_guest} {p_host}", 10)
        if not os.path.exists(p_host): return self.custom_messagebox("Lỗi", "Lỗi chụp ảnh.", "error")
        top = tk.Toplevel(self.root); top.title("Cắt Ảnh")
        
        img = Image.open(p_host)
        max_w, max_h = 800, 700
        scale = min(max_w / img.width, max_h / img.height, 1.0)
        display_w, display_h = int(img.width * scale), int(img.height * scale)
        resample_filter = getattr(Image, 'Resampling', Image).LANCZOS
        display_img = img.resize((display_w, display_h), resample_filter)
        
        tk_img = ImageTk.PhotoImage(display_img)
        canvas = tk.Canvas(top, width=display_w, height=display_h, cursor="cross"); canvas.pack()
        canvas.image = tk_img; canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)
        
        rect = None; start_x = start_y = 0
        def on_press(e): nonlocal rect, start_x, start_y; start_x, start_y = e.x, e.y; rect = canvas.create_rectangle(e.x, e.y, e.x, e.y, outline='red')
        def on_drag(e): canvas.coords(rect, start_x, start_y, e.x, e.y)
        def on_release(e):
            if abs(e.x - start_x) > 5:
                rnd = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + ".png"
                rx1, ry1 = int(min(start_x, e.x) / scale), int(min(start_y, e.y) / scale)
                rx2, ry2 = int(max(start_x, e.x) / scale), int(max(start_y, e.y) / scale)
                img.crop((rx1, ry1, rx2, ry2)).save(os.path.join("png", rnd))
                self.txt_value.delete(0, tk.END); self.txt_value.insert(0, rnd); top.destroy()
                
        canvas.bind("<ButtonPress-1>", on_press); canvas.bind("<B1-Motion>", on_drag); canvas.bind("<ButtonRelease-1>", on_release)
        top.protocol("WM_DELETE_WINDOW", lambda: (top.destroy(), img.close(), os.remove(p_host) if os.path.exists(p_host) else None))

    def parse_account_line(self, line):
        parts = [p.strip() for p in (line.split('|') if '|' in line else re.split(r'[,\t;:/\\]+|\s+', line)) if p.strip()]
        while len(parts) < 6: parts.append("")
        if parts[2] in ['success', 'failed', 'unchecked']: parts[4], parts[5], parts[2], parts[3] = parts[2], parts[3], "", ""
        return parts[:6]

    def save_accounts_file(self):
        try:
            with open(self.file_name, 'w', encoding='utf-8') as f:
                for acc in self.accounts: f.write(f"{acc[0]}|{acc[1]}|{acc[2]}|{acc[3]}|{acc[4]}|{acc[5]}\n")
        except: pass

    def get_selected_accounts(self): return [{"id": it, "tk": self.tree.item(it, 'values')[2], "mk": self.accounts[self.tree.index(it)][1] if self.tree.index(it) < len(self.accounts) else ""} for it in self.tree.get_children() if self.tree.item(it, 'values')[0] == "☑"]

    def mark_account(self):
        if not (sel := self.tree.selection()): return
        if (note := self.custom_askstring("Ghi chú", "Nội dung:")) is not None:
            for it in sel:
                tags = [t for t in self.tree.item(it, 'tags') if t not in ['failed', 'checked', 'unchecked']]; tags.append('success'); self.tree.item(it, tags=tuple(tags))
                vals = list(self.tree.item(it, 'values')); vals[6] = note; self.tree.item(it, values=vals)
                if (idx := self.tree.index(it)) < len(self.accounts): self.accounts[idx][4], self.accounts[idx][5] = 'success', note
            self.save_accounts_file()

    def unmark_account(self):
        for it in self.tree.selection():
            tags = [t for t in self.tree.item(it, 'tags') if t not in ['success', 'failed']]; self.tree.item(it, tags=tuple(tags))
            vals = list(self.tree.item(it, 'values')); vals[6] = ""; self.tree.item(it, values=vals)
            if (idx := self.tree.index(it)) < len(self.accounts): self.accounts[idx][4], self.accounts[idx][5] = '', ''
        self.save_accounts_file()

    def import_txt(self):
        if not (p := filedialog.askopenfilename(filetypes=[("All Files", "*.*"), ("Excel", "*.xlsx *.xls"), ("Text", "*.txt *.csv")])): return
        try:
            if p.endswith(('.xlsx', '.xls')):
                for _, r in pd.read_excel(p).iterrows():
                    tk_v = str(r.iloc[0]).strip() if pd.notna(r.iloc[0]) else ""
                    if not tk_v or tk_v == "nan" or any(a[0] == tk_v for a in self.accounts): continue
                    self.accounts.append([tk_v, str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else "", str(r.iloc[2]).strip() if len(r)>2 and pd.notna(r.iloc[2]) else "", str(r.iloc[3]).strip() if len(r)>3 and pd.notna(r.iloc[3]) else "", "unchecked", ""])
                    self.tree.insert("", tk.END, values=("☐", len(self.accounts), tk_v, "***" if self.hide_pass else self.accounts[-1][1], self.accounts[-1][2], "***" if self.hide_pass else self.accounts[-1][3], ""), tags=('unchecked',))
            else:
                for l in open(p, 'r', encoding='utf-8', errors='ignore'):
                    if not l.strip(): continue
                    d = self.parse_account_line(l)
                    if d[0] and not any(a[0] == d[0] for a in self.accounts):
                        self.accounts.append(d); self.tree.insert("", tk.END, values=("☐", len(self.accounts), d[0], "***" if self.hide_pass else d[1], d[2], "***" if self.hide_pass else d[3], d[5]), tags=(d[4] if d[4] in ['success', 'failed'] else 'unchecked',))
            self.save_accounts_file(); self.custom_messagebox("Thành công", "Nạp dữ liệu hoàn tất.", "info")
        except: self.custom_messagebox("Lỗi", "File không hợp lệ.", "error")

    def load_accounts(self):
        if os.path.exists(self.file_name):
            for l in open(self.file_name, 'r', encoding='utf-8'):
                if l.strip(): d = self.parse_account_line(l); self.accounts.append(d); self.tree.insert("", tk.END, values=("☐", len(self.accounts), d[0], "***" if self.hide_pass else d[1], d[2], "***" if self.hide_pass else d[3], d[5]), tags=(d[4] if d[4] in ['success', 'failed'] else 'unchecked',))

    def update_account_result(self, it, status, note_text):
        tags = [t for t in self.tree.item(it, 'tags') if t not in ['success', 'failed']]; tags.append(status); self.tree.item(it, tags=tuple(tags))
        vals = list(self.tree.item(it, 'values')); vals[6] = note_text; self.tree.item(it, values=vals)
        if (idx := self.tree.index(it)) < len(self.accounts): self.accounts[idx][4], self.accounts[idx][5] = status, note_text
        self.save_accounts_file()

    def log(self, msg): self.root.after(0, lambda: (self.txt_log.config(state=tk.NORMAL), self.txt_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n"), self.txt_log.see(tk.END), self.txt_log.config(state=tk.DISABLED)))
    def update_timer(self):
        if self.is_bot_running and self.start_time > 0: self.root.after(0, lambda: self.lbl_timer.config(text=f"⏱ {int(time.time() - self.start_time)}s"))
        self.root.after(1000, self.update_timer)
    def update_status(self, text, color): self.root.after(0, lambda: self.lbl_status.config(text=f"TRẠNG THÁI: {text}", fg=color))
    
    def ldc(self, cmd_string, timeout=15):
        try: return subprocess.Popen(f'"{os.path.join(self.ld_path.get(), "ldconsole.exe")}" {cmd_string}', shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000).communicate(timeout=timeout)[0].decode('utf-8', errors='ignore').strip()
        except: return "ERROR"

    def run_adb(self, idx, cmd_string, timeout=15):
        ld_dir = self.ld_path.get().strip()
        if ld_dir and os.path.exists(os.path.join(ld_dir, "ldconsole.exe")) and str(idx).isdigit():
            return self.ldc(f'adb --index {idx} --command "{cmd_string}"', timeout)
        else:
            try:
                startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                return subprocess.Popen(f'adb -s {idx} {cmd_string}', shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo, creationflags=0x08000000).communicate(timeout=timeout)[0].decode('utf-8', errors='ignore').strip()
            except: return "ERROR"

    def is_device_running(self, idx):
        ld_dir = self.ld_path.get().strip()
        if ld_dir and os.path.exists(os.path.join(ld_dir, "ldconsole.exe")) and str(idx).isdigit():
            return "running" in self.ldc(f"isrunning --index {idx}")
        return True

    def get_screen(self, idx):
        p_g, p_h = f"/sdcard/sc_{idx}.png", f"sc_{idx}.png"
        self.run_adb(idx, f"shell screencap -p {p_g}", 10); self.run_adb(idx, f"pull {p_g} {p_h}", 10)
        img = cv2.imread(p_h) if os.path.exists(p_h) else None
        if os.path.exists(p_h): os.remove(p_h)
        return img

    def find_image(self, idx, t_name, threshold=0.8):
        t_path = os.path.join("png", t_name)
        if not os.path.exists(t_path) or (screen := self.get_screen(idx)) is None or (template := cv2.imread(t_path)) is None: return None
        try:
            _, max_val, _, max_loc = cv2.minMaxLoc(cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED))
            return (max_loc[0] + template.shape[1]//2, max_loc[1] + template.shape[0]//2) if max_val >= threshold else None
        except: return None

    def click_image(self, idx, t_name, timeout=10, delay=1):
        start = time.time()
        while time.time() - start < timeout and self.is_bot_running:
            if pos := self.find_image(idx, t_name): self.run_adb(idx, f"shell input tap {pos[0]} {pos[1]}"); return True
            time.sleep(delay)
        return False

    def start_auto(self):
        self.save_accounts_file()
        
        accs, vms = self.get_selected_accounts(), self.get_selected_vms()
        if not accs or not vms or not self.script_steps: return self.custom_messagebox("Lỗi", "Thiếu dữ liệu chạy.", "error")
        self.batch_size, self.worker_vms = len(accs), vms[:len(accs)]
        if len(self.worker_vms) < self.batch_size: return self.custom_messagebox("Lỗi", "Số Thiết Bị nhỏ hơn Tài Khoản.", "error")
        if not_run := [i for i in self.worker_vms if not self.is_device_running(i)]: return self.custom_messagebox("Lỗi", f"Thiết bị {','.join(not_run)} chưa chạy.", "error")
        self.last_run_index = self.tree.index(accs[0]['id']); self.execute_batch()

    def run_next_batch(self):
        self.save_accounts_file()
        
        if self.batch_size == 0: return
        items = self.tree.get_children()
        for it in items:
            v, t = list(self.tree.item(it, 'values')), list(self.tree.item(it, 'tags')); v[0] = "☐"; t = [x for x in t if x != 'checked']; t.append('unchecked'); self.tree.item(it, values=v, tags=tuple(t))
        self.last_run_index += self.batch_size
        if self.last_run_index >= len(items): return self.custom_messagebox("Hoàn thành", "Đã chạy hết danh sách.", "info")
        for it in items[self.last_run_index:min(self.last_run_index + self.batch_size, len(items))]:
            v, t = list(self.tree.item(it, 'values')), list(self.tree.item(it, 'tags')); v[0] = "☑"; t = [x for x in t if x != 'unchecked']; t.append('checked'); self.tree.item(it, values=v, tags=tuple(t))
        self.execute_batch()

    def execute_batch(self):
        items = self.tree.get_children()[self.last_run_index:min(self.last_run_index + self.batch_size, len(self.tree.get_children()))]
        accs = [{"id": it, "tk": self.tree.item(it, 'values')[2], "mk": self.accounts[self.tree.index(it)][1]} for it in items]
        self.nb.select(2); self.is_bot_running = True; self.start_time = time.time()
        self.btn_start.config(state=tk.DISABLED); self.btn_next.config(state=tk.DISABLED); self.set_stop_btn_state(True)
        self.update_status("HỆ THỐNG ĐANG CHẠY...", self.accent_color)
        threading.Thread(target=self.auto_login_thread, args=(self.worker_vms, accs), daemon=True).start()

    def stop_auto(self):
        self.is_bot_running = False; self.btn_start.config(state=tk.NORMAL); self.btn_next.config(state=tk.NORMAL); self.set_stop_btn_state(False)
        self.update_status("ĐÃ DỪNG", self.danger_color); self.log("🛑 Đã dừng luồng.")

    def auto_login_thread(self, vms, accs):
        q = queue.Queue(); [q.put(a) for a in accs]
        threads = [threading.Thread(target=self.vm_worker_dynamic, args=(i, q), daemon=True) for i in vms]
        for t in threads: t.start()
        for t in threads: t.join()
        if self.is_bot_running: self.root.after(0, self.stop_auto); self.log("✅ Xong lượt.")

    def execute_steps(self, steps_data, idx, acc):
        step_idx = 0
        while step_idx < len(steps_data) and self.is_bot_running:
            s = steps_data[step_idx]
            act, val, timeout, delay, retries = s.get("action"), s.get("value", ""), float(s.get("timeout", 10)), float(s.get("delay", 1)), int(s.get("retries", 1))
            
            if act == "Kết thúc Kịch Bản": return True
            if act == "Quay lại Bước (Lặp)":
                try: 
                    if 0 <= int(val)-1 < len(steps_data): step_idx = int(val)-1; time.sleep(delay); continue
                except: pass
                step_idx += 1; continue
            if act == "Chạy Script Khác":
                if sub := self.load_script(os.path.join(self.script_folder, val)):
                    if not self.execute_steps(sub, idx, acc): return False 
                step_idx += 1; continue

            succ = False
            for r in range(retries):
                if not self.is_bot_running: break
                if act == "Check Ảnh (Cố định 60s)":
                    st = time.time()
                    while time.time() - st < 60 and self.is_bot_running:
                        if pos := self.find_image(idx, val): self.run_adb(idx, f"shell input tap {pos[0]} {pos[1]}"); succ = True; break
                        time.sleep(1)
                    if not succ: return False 
                else:
                    self.log(f"▶ [{idx}] {act}")
                    if act == "Click Ảnh": succ = self.click_image(idx, val, timeout, 1)
                    elif act == "Click Tọa Độ": 
                        try: self.run_adb(idx, f"shell input tap {val.split()[0]} {val.split()[1]}"); succ = True
                        except: pass
                    elif act == "Nhập Tài Khoản": self.run_adb(idx, f"shell input text {acc['tk']}"); succ = True
                    elif act == "Nhập Mật Khẩu": self.run_adb(idx, f"shell input text {acc['mk']}"); succ = True
                    elif act == "Mở App": self.run_adb(idx, f"shell monkey -p {val} -c android.intent.category.LAUNCHER 1"); succ = True
                    elif act == "Xóa Data App": self.run_adb(idx, f"shell pm clear {val}"); succ = True
                    elif act == "Cài APK": self.run_adb(idx, f"install {val}", 120); succ = True
                    elif act == "Delay (Nghỉ)": time.sleep(timeout); succ = True
                if succ: break
            time.sleep(delay); step_idx += 1
        return True

    def vm_worker_dynamic(self, idx, q):
        while self.is_bot_running and not q.empty():
            try: acc = q.get_nowait()
            except: break
            if self.execute_steps(self.script_steps, idx, acc): self.root.after(0, lambda a=acc: self.update_account_result(a['id'], 'success', 'Hoàn tất ✅'))
            else: self.root.after(0, lambda a=acc: self.update_account_result(a['id'], 'failed', 'Lỗi ❌'))
            q.task_done()

if __name__ == "__main__":
    root_main = tk.Tk()
    main_app = AntidetectApp(root_main)
    root_main.mainloop()