import psutil
import GPUtil
import time

# For network speed calculations
_prev_net = psutil.net_io_counters()
_prev_time = time.time()

# For FPS measurement
_last_frame_time = time.time()
_fps = 0

# ========== CPU ==========
def get_cpu_usage():
    return psutil.cpu_percent(interval=None)

def get_cpu_per_core():
    return psutil.cpu_percent(percpu=True, interval=None)

def get_cpu_freq():
    freq = psutil.cpu_freq()
    return freq.current if freq else 0

def get_cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None
        for name, entries in temps.items():
            for entry in entries:
                if "core" in entry.label.lower() or "cpu" in entry.label.lower():
                    return round(entry.current, 1)
        all_temps = [t.current for group in temps.values() for t in group]
        return round(sum(all_temps) / len(all_temps), 1)
    except Exception:
        return None

# ========== RAM ==========
def get_ram_usage():
    mem = psutil.virtual_memory()
    percent = mem.percent
    used = round(mem.used / (1024 ** 2), 2)
    total = round(mem.total / (1024 ** 2), 2)
    return percent, used, total

# ========== DISK ==========
def get_disk_usage():
    disk = psutil.disk_usage('/')
    total = round(disk.total / (1024 ** 3), 2)
    used = round(disk.used / (1024 ** 3), 2)
    free = round(disk.free / (1024 ** 3), 2)
    percent = disk.percent
    return percent, used, total, free

# ========== NETWORK ==========
def get_network_usage():
    global _prev_net, _prev_time
    current = psutil.net_io_counters()
    now = time.time()
    duration = now - _prev_time
    upload_speed = (current.bytes_sent - _prev_net.bytes_sent) / duration / 1024
    download_speed = (current.bytes_recv - _prev_net.bytes_recv) / duration / 1024
    _prev_net = current
    _prev_time = now
    return round(upload_speed, 2), round(download_speed, 2)

# ========== GPU ==========
def get_gpu_usage():
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return 0, 0, 0, 0
        gpu = gpus[0]
        usage = round(gpu.load * 100, 2)
        mem_used = round(gpu.memoryUsed, 2)
        mem_total = round(gpu.memoryTotal, 2)
        temp = round(gpu.temperature, 2)
        return usage, mem_used, mem_total, temp
    except Exception:
        return 0, 0, 0, 0

# ========== FPS ==========
def get_fps():
    global _last_frame_time, _fps
    now = time.time()
    dt = now - _last_frame_time
    if dt == 0:
        return _fps
    _fps = 1.0 / dt
    _last_frame_time = now
    return round(_fps, 1)
