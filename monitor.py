import time
import psutil


class SystemMonitor:
    """
    Captura metricas del sistema en tiempo real usando psutil.
    Accede a las API del sistema operativo para extraer uso de CPU, RAM y disco.
    """

    def __init__(self, interval=1.0):
        self.interval = interval
        psutil.cpu_percent(interval=None)

    def get_cpu_percent(self):
        return psutil.cpu_percent(interval=None)

    def get_ram_percent(self):
        return psutil.virtual_memory().percent

    def get_disk_percent(self):
        disk = psutil.disk_usage("/")
        return disk.percent

    def get_top_processes(self, n=5):
        procs = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                if info["cpu_percent"] is not None:
                    procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda p: p.get("cpu_percent", 0) or 0, reverse=True)
        return procs[:n]

    def snapshot(self):
        return {
            "cpu": self.get_cpu_percent(),
            "ram": self.get_ram_percent(),
            "disk": self.get_disk_percent(),
            "timestamp": time.time(),
        }
