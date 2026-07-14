import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque


class ResourceGraph:
    """
    Renderiza curvas cartesianas de consumo y recta tangente predictiva
    usando Matplotlib. Eje X = tiempo, Eje Y = porcentaje de saturacion.
    """

    def __init__(self, max_points=60):
        self.max_points = max_points
        self.times = deque(maxlen=max_points)
        self.cpu_data = deque(maxlen=max_points)
        self.ram_data = deque(maxlen=max_points)
        self.disk_data = deque(maxlen=max_points)
        self.tangent_ts = []
        self.tangent_vals = []
        self.current_time = 0.0

        plt.ion()
        self.fig, (self.ax_main, self.ax_deriv) = plt.subplots(2, 1, figsize=(10, 6))
        self.fig.suptitle("CompuSense - Monitoreo en Tiempo Real", fontsize=13, fontweight="bold")
        self.fig.canvas.manager.set_window_title("CompuSense Graficos")
        self._setup_axes()

    def _setup_axes(self):
        self.ax_main.set_xlabel("Tiempo (s)")
        self.ax_main.set_ylabel("Uso (%)")
        self.ax_main.set_title("Funcion de Carga U(t)")
        self.ax_main.set_ylim(0, 110)
        self.ax_main.axhline(y=100, color="red", linestyle="--", alpha=0.5, label="Limite 100%")
        self.ax_main.legend(loc="upper left", fontsize=8)
        self.ax_main.grid(True, alpha=0.3)

        self.ax_deriv.set_xlabel("Tiempo (s)")
        self.ax_deriv.set_ylabel("U'(t) (%/s)")
        self.ax_deriv.set_title("Tasa de Cambio Instantanea (Derivada)")
        self.ax_deriv.grid(True, alpha=0.3)

    def update_data(self, cpu, ram, disk, tangent_ts=None, tangent_vals=None):
        self.current_time += 1.0
        self.times.append(self.current_time)
        self.cpu_data.append(cpu)
        self.ram_data.append(ram)
        self.disk_data.append(disk)
        if tangent_ts is not None and tangent_vals is not None:
            self.tangent_ts = tangent_ts
            self.tangent_vals = tangent_vals

    def draw(self):
        self.ax_main.cla()
        self.ax_deriv.cla()
        self._setup_axes()

        if len(self.times) > 0:
            ts = list(self.times)

            self.ax_main.plot(ts, list(self.cpu_data), "b-", linewidth=1.5, label="CPU")
            self.ax_main.plot(ts, list(self.ram_data), "g-", linewidth=1.5, label="RAM")
            self.ax_main.plot(ts, list(self.disk_data), "m-", linewidth=1.5, label="Disco")

            if self.tangent_ts and self.tangent_vals:
                self.ax_main.plot(
                    self.tangent_ts,
                    self.tangent_vals,
                    "r--",
                    linewidth=1.2,
                    alpha=0.7,
                    label="Tangente predictiva",
                )

            self.ax_main.legend(loc="upper left", fontsize=8)

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def close(self):
        plt.ioff()
        plt.close(self.fig)
