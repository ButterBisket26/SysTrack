import customtkinter as ctk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import system_stats
from tkinter import ttk, messagebox
import csv
import os
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("SysTrack")
root.geometry("900x800")

log_file = "system_log.csv"
if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Time", "CPU%", "CPU Temp", "RAM%", "GPU%", "GPU Temp", "Disk%", "Upload KB/s", "Download KB/s", "FPS"
        ])

CPU_THRESHOLD = 90
GPU_THRESHOLD = 90
RAM_THRESHOLD = 90

logging_enabled = ctk.BooleanVar(value=False)

title_frame = ctk.CTkFrame(root, fg_color="transparent")
title_frame.pack(fill="x", padx=15, pady=(10, 5))

title = ctk.CTkLabel(title_frame, text="System Resource Monitor", font=("Segoe UI", 28, "bold"))
title.pack(side="left", padx=10)

log_toggle = ctk.CTkSwitch(title_frame, text="Enable Logging", variable=logging_enabled, 
                           font=("Segoe UI", 12))
log_toggle.pack(side="right", padx=10)

tabview = ctk.CTkTabview(root, width=880, height=700)
tabview.pack(padx=15, pady=10, fill="both", expand=True)

tab_overview = tabview.add("Overview")
tab_detailed = tabview.add("Detailed Stats")
tab_processes = tabview.add("Processes")

def get_color_for_usage(percentage):
    if percentage < 50:
        return "#4ade80"
    elif percentage < 75:
        return "#fbbf24"
    else:
        return "#ef4444"

def create_metric_card(parent, title_text):
    card = ctk.CTkFrame(parent, corner_radius=10, fg_color=("#2b2b2b", "#1a1a1a"))
    card.pack(fill="x", padx=15, pady=8)
    
    title = ctk.CTkLabel(card, text=title_text, font=("Segoe UI", 18, "bold"), 
                        anchor="w")
    title.pack(fill="x", padx=15, pady=(12, 5))
    
    return card

overview_scroll = ctk.CTkScrollableFrame(tab_overview, fg_color="transparent")
overview_scroll.pack(fill="both", expand=True, padx=5, pady=5)

cpu_card = create_metric_card(overview_scroll, "CPU")
cpu_label = ctk.CTkLabel(cpu_card, text="Usage: --%", anchor="w", font=("Segoe UI", 14))
cpu_label.pack(fill="x", padx=15, pady=(5, 0))
cpu_bar = ctk.CTkProgressBar(cpu_card, height=20, corner_radius=10)
cpu_bar.pack(fill="x", padx=15, pady=(8, 5))
cpu_bar.set(0)

cpu_info_frame = ctk.CTkFrame(cpu_card, fg_color="transparent")
cpu_info_frame.pack(fill="x", padx=15, pady=(0, 12))
cpu_freq_label = ctk.CTkLabel(cpu_info_frame, text="Frequency: -- MHz", 
                               anchor="w", font=("Segoe UI", 11), text_color="#a0a0a0")
cpu_freq_label.pack(side="left", padx=(0, 20))
cpu_temp_label = ctk.CTkLabel(cpu_info_frame, text="Temp: --°C", 
                              anchor="w", font=("Segoe UI", 11), text_color="#a0a0a0")
cpu_temp_label.pack(side="left")

ram_card = create_metric_card(overview_scroll, "Memory (RAM)")
ram_label = ctk.CTkLabel(ram_card, text="Usage: --%", anchor="w", font=("Segoe UI", 14))
ram_label.pack(fill="x", padx=15, pady=(5, 0))
ram_bar = ctk.CTkProgressBar(ram_card, height=20, corner_radius=10)
ram_bar.pack(fill="x", padx=15, pady=(8, 12))
ram_bar.set(0)

gpu_card = create_metric_card(overview_scroll, "GPU")
gpu_label = ctk.CTkLabel(gpu_card, text="Usage: --%", anchor="w", font=("Segoe UI", 14))
gpu_label.pack(fill="x", padx=15, pady=(5, 0))
gpu_bar = ctk.CTkProgressBar(gpu_card, height=20, corner_radius=10)
gpu_bar.pack(fill="x", padx=15, pady=(8, 5))
gpu_bar.set(0)

gpu_info_frame = ctk.CTkFrame(gpu_card, fg_color="transparent")
gpu_info_frame.pack(fill="x", padx=15, pady=(0, 12))
gpu_mem_label = ctk.CTkLabel(gpu_info_frame, text="Memory: -- / -- MB", 
                             anchor="w", font=("Segoe UI", 11), text_color="#a0a0a0")
gpu_mem_label.pack(side="left", padx=(0, 20))
gpu_temp_label = ctk.CTkLabel(gpu_info_frame, text="Temp: --°C", 
                              anchor="w", font=("Segoe UI", 11), text_color="#a0a0a0")
gpu_temp_label.pack(side="left")

disk_card = create_metric_card(overview_scroll, "Disk Storage")
disk_label = ctk.CTkLabel(disk_card, text="Usage: --%", anchor="w", font=("Segoe UI", 14))
disk_label.pack(fill="x", padx=15, pady=(5, 0))
disk_bar = ctk.CTkProgressBar(disk_card, height=20, corner_radius=10)
disk_bar.pack(fill="x", padx=15, pady=(8, 12))
disk_bar.set(0)

network_card = create_metric_card(overview_scroll, "Network")
net_frame = ctk.CTkFrame(network_card, fg_color="transparent")
net_frame.pack(fill="x", padx=15, pady=(5, 12))

upload_frame = ctk.CTkFrame(net_frame, fg_color=("#2d2d2d", "#0d0d0d"), corner_radius=8)
upload_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))
ctk.CTkLabel(upload_frame, text="↑ Upload", font=("Segoe UI", 11, "bold"), 
            text_color="#60a5fa").pack(pady=(8, 2))
upload_label = ctk.CTkLabel(upload_frame, text="-- KB/s", font=("Segoe UI", 16))
upload_label.pack(pady=(0, 8))

download_frame = ctk.CTkFrame(net_frame, fg_color=("#2d2d2d", "#0d0d0d"), corner_radius=8)
download_frame.pack(side="left", fill="x", expand=True)
ctk.CTkLabel(download_frame, text="↓ Download", font=("Segoe UI", 11, "bold"), 
            text_color="#34d399").pack(pady=(8, 2))
download_label = ctk.CTkLabel(download_frame, text="-- KB/s", font=("Segoe UI", 16))
download_label.pack(pady=(0, 8))

fps_card = create_metric_card(overview_scroll, "Performance")
fps_label = ctk.CTkLabel(fps_card, text="FPS: --", anchor="w", font=("Segoe UI", 16, "bold"))
fps_label.pack(fill="x", padx=15, pady=(5, 12))

detailed_scroll = ctk.CTkScrollableFrame(tab_detailed, fg_color="transparent")
detailed_scroll.pack(fill="both", expand=True, padx=5, pady=5)

graph_card = create_metric_card(detailed_scroll, "CPU Usage History")

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.set_facecolor("#1a1a1a")
fig.patch.set_facecolor("#1a1a1a")
ax.set_title("CPU Usage Over Time", color="white", fontsize=14, pad=10)
ax.tick_params(colors="white", labelsize=9)
ax.set_ylim(0, 100)
ax.set_xlim(0, 60)
ax.set_ylabel("Usage %", color="white", fontsize=10)
ax.set_xlabel("Seconds", color="white", fontsize=10)
ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)

x_data = deque(maxlen=60)
y_data = deque(maxlen=60)
line, = ax.plot([], [], color="#3b82f6", linewidth=2.5)
fill = ax.fill_between([], [], 0, color="#3b82f6", alpha=0.3)

canvas = FigureCanvasTkAgg(fig, master=graph_card)
canvas.get_tk_widget().pack(padx=15, pady=(10, 15), fill="x")

core_card = create_metric_card(detailed_scroll, "Per-Core CPU Usage")

core_inner_frame = ctk.CTkFrame(core_card, fg_color="transparent")
core_inner_frame.pack(fill="x", padx=15, pady=(5, 12))

num_cores = psutil.cpu_count(logical=True)
core_labels, core_bars = [], []
for i in range(num_cores):
    core_container = ctk.CTkFrame(core_inner_frame, fg_color="transparent")
    core_container.pack(fill="x", pady=3)
    
    label = ctk.CTkLabel(core_container, text=f"Core {i}: --%", anchor="w", 
                        font=("Segoe UI", 11), width=100)
    label.pack(side="left", padx=(0, 10))
    
    bar = ctk.CTkProgressBar(core_container, height=12, corner_radius=6)
    bar.pack(side="left", fill="x", expand=True)
    bar.set(0)
    
    core_labels.append(label)
    core_bars.append(bar)

process_scroll = ctk.CTkScrollableFrame(tab_processes, fg_color="transparent")
process_scroll.pack(fill="both", expand=True, padx=5, pady=5)

proc_card = create_metric_card(process_scroll, "Top Processes by CPU Usage")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", 
                background="#2b2b2b",
                foreground="white",
                fieldbackground="#2b2b2b",
                borderwidth=0,
                font=("Segoe UI", 10))
style.configure("Treeview.Heading",
                background="#1a1a1a",
                foreground="white",
                font=("Segoe UI", 11, "bold"))
style.map("Treeview",
         background=[("selected", "#3b82f6")])

columns = ("pid", "name", "cpu", "mem")
top_proc_table = ttk.Treeview(proc_card, columns=columns, show="headings", height=15)
top_proc_table.heading("pid", text="PID")
top_proc_table.heading("name", text="Process Name")
top_proc_table.heading("cpu", text="CPU %")
top_proc_table.heading("mem", text="Memory %")

top_proc_table.column("pid", width=80, anchor="center")
top_proc_table.column("name", width=300, anchor="w")
top_proc_table.column("cpu", width=100, anchor="center")
top_proc_table.column("mem", width=100, anchor="center")

scrollbar = ttk.Scrollbar(proc_card, orient="vertical", command=top_proc_table.yview)
top_proc_table.configure(yscrollcommand=scrollbar.set)

top_proc_table.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=(10, 15))
scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=(10, 15))

def update_ui():
    try:
        cpu = system_stats.get_cpu_usage()
        cpu_color = get_color_for_usage(cpu)
        cpu_bar.set(cpu / 100)
        cpu_bar.configure(progress_color=cpu_color)
        cpu_label.configure(text=f"Usage: {cpu:.1f}%")

        cpu_freq = system_stats.get_cpu_freq()
        cpu_freq_label.configure(text=f"Frequency: {cpu_freq:.0f} MHz")

        cpu_temp = system_stats.get_cpu_temp()
        cpu_temp_label.configure(text=f"Temp: {cpu_temp if cpu_temp else 'N/A'}°C")

        x_data.append(len(x_data))
        y_data.append(cpu)
        line.set_data(range(len(y_data)), y_data)
        ax.set_xlim(max(0, len(y_data) - 60), max(60, len(y_data)))
        
        global fill
        fill.remove()
        fill = ax.fill_between(range(len(y_data)), y_data, 0, color="#3b82f6", alpha=0.3)
        
        canvas.draw()

        cores = system_stats.get_cpu_per_core()
        for i, usage in enumerate(cores):
            core_labels[i].configure(text=f"Core {i}: {usage:.1f}%")
            core_bars[i].set(usage / 100)
            core_bars[i].configure(progress_color=get_color_for_usage(usage))

        ram_pct, ram_used, ram_total = system_stats.get_ram_usage()
        ram_bar.set(ram_pct / 100)
        ram_bar.configure(progress_color=get_color_for_usage(ram_pct))
        ram_label.configure(text=f"Usage: {ram_pct:.1f}% ({ram_used:.0f} MB / {ram_total:.0f} MB)")

        gpu_pct, gpu_used, gpu_total, gpu_temp = system_stats.get_gpu_usage()
        gpu_bar.set(gpu_pct / 100)
        gpu_bar.configure(progress_color=get_color_for_usage(gpu_pct))
        gpu_label.configure(text=f"Usage: {gpu_pct:.1f}%")
        gpu_mem_label.configure(text=f"Memory: {gpu_used:.0f} / {gpu_total:.0f} MB")
        gpu_temp_label.configure(text=f"Temp: {gpu_temp:.0f}°C")

        disk_pct, used, total, free = system_stats.get_disk_usage()
        disk_bar.set(disk_pct / 100)
        disk_bar.configure(progress_color=get_color_for_usage(disk_pct))
        disk_label.configure(text=f"Usage: {disk_pct:.1f}% ({used:.1f} GB / {total:.1f} GB)")

        up_kb, down_kb = system_stats.get_network_usage()
        
        up_display = up_kb
        down_display = down_kb
        unit = "MB/s" if max(up_kb, down_kb) > 1024 else "KB/s"
        if unit == "MB/s":
            up_display = up_kb / 1024
            down_display = down_kb / 1024
        upload_label.configure(text=f"{up_display:.2f} {unit}")
        download_label.configure(text=f"{down_display:.2f} {unit}")

        fps = system_stats.get_fps()
        fps_label.configure(text=f"FPS: {fps}")

        for row in top_proc_table.get_children():
            top_proc_table.delete(row)

        procs = [(p.info['pid'], p.info['name'], p.info['cpu_percent'], p.info['memory_percent'])
                 for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])]
        procs.sort(key=lambda x: x[2] if x[2] else 0, reverse=True)
        
        for i, proc in enumerate(procs[:20]):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            top_proc_table.insert("", "end", values=(
                proc[0],
                proc[1][:40],
                f"{proc[2]:.1f}" if proc[2] else "0.0",
                f"{proc[3]:.1f}" if proc[3] else "0.0"
            ), tags=(tag,))

        top_proc_table.tag_configure("evenrow", background="#2b2b2b")
        top_proc_table.tag_configure("oddrow", background="#252525")

        if cpu > CPU_THRESHOLD:
            messagebox.showwarning("CPU Alert", f"CPU Usage High: {cpu:.0f}%")
        if gpu_pct > GPU_THRESHOLD:
            messagebox.showwarning("GPU Alert", f"GPU Usage High: {gpu_pct:.0f}%")
        if ram_pct > RAM_THRESHOLD:
            messagebox.showwarning("RAM Alert", f"RAM Usage High: {ram_pct:.0f}%")

        if logging_enabled.get():
            with open(log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    time.strftime("%Y-%m-%d %H:%M:%S"),
                    cpu,
                    cpu_temp if cpu_temp else "N/A",
                    ram_pct,
                    gpu_pct,
                    gpu_temp,
                    disk_pct,
                    up_kb,
                    down_kb,
                    fps
                ])

    except Exception as e:
        print("Error:", e)
    finally:
        root.after(1000, update_ui)

update_ui()
root.mainloop()
