import math
from collections import deque


class CalculusEngine:
    """
    Motor de calculo diferencial para CompuSense.
    Calcula derivadas (tasa de cambio instantanea), limites, y prediccion de saturacion.
    """

    def __init__(self, window_size=30):
        self.window_size = window_size
        self.cpu_history = deque(maxlen=window_size)
        self.ram_history = deque(maxlen=window_size)
        self.disk_history = deque(maxlen=window_size)
        self.time_history = deque(maxlen=window_size)
        self.current_time = 0.0

    def add_sample(self, cpu, ram, disk, dt=1.0):
        self.current_time += dt
        self.cpu_history.append(cpu)
        self.ram_history.append(ram)
        self.disk_history.append(disk)
        self.time_history.append(self.current_time)

    def _derivative(self, values, times):
        """
        Calcula la derivada de primer orden U'(t) usando diferencias centrales.
        Representa la tasa de cambio instantanea.
        """
        if len(values) < 2:
            return 0.0

        if len(values) >= 3:
            y1 = values[-3]
            y2 = values[-1]
            t1 = times[-3]
            t2 = times[-1]
            if t2 != t1:
                return (y2 - y1) / (t2 - t1)
            return 0.0

        y1 = values[-2]
        y2 = values[-1]
        t1 = times[-2]
        t2 = times[-1]
        if t2 != t1:
            return (y2 - y1) / (t2 - t1)
        return 0.0

    def cpu_derivative(self):
        return self._derivative(list(self.cpu_history), list(self.time_history))

    def ram_derivative(self):
        return self._derivative(list(self.ram_history), list(self.time_history))

    def disk_derivative(self):
        return self._derivative(list(self.disk_history), list(self.time_history))

    def _limit_analysis(self, current_value, derivative):
        """
        Analisis asintotico: evalua comportamiento cuando U(t) -> 100%.
        Retorna el valor limite (100%) y los segundos estimados para alcanzarlo.
        """
        limit = 100.0
        if derivative <= 0:
            return limit, float('inf')
        remaining = limit - current_value
        if remaining <= 0:
            return limit, 0.0
        seconds_to_limit = remaining / derivative
        return limit, seconds_to_limit

    def cpu_limit_analysis(self):
        if not self.cpu_history:
            return 100.0, float('inf')
        return self._limit_analysis(self.cpu_history[-1], self.cpu_derivative())

    def ram_limit_analysis(self):
        if not self.ram_history:
            return 100.0, float('inf')
        return self._limit_analysis(self.ram_history[-1], self.ram_derivative())

    def disk_limit_analysis(self):
        if not self.disk_history:
            return 100.0, float('inf')
        return self._limit_analysis(self.disk_history[-1], self.disk_derivative())

    def tangent_line(self, current_value, derivative, t_range=(-5, 5)):
        """
        Recta tangente en el punto actual: U(t) + U'(t) * (t - t_now).
        Retorna puntos (t, U_tangente) para graficar.
        """
        t_now = self.current_time
        ts = [t_now + i for i in range(t_range[0], t_range[1] + 1)]
        tangents = [current_value + derivative * (t - t_now) for t in ts]
        return ts, tangents

    def get_risk_level(self, derivative):
        """
        Nivel de riesgo basado en la pendiente (derivada):
        - Normal: derivada <= 0.5 (%/s)
        - Advertencia: 0.5 < derivada <= 2.0 (%/s)
        - Critico: derivada > 2.0 (%/s)
        """
        if derivative <= 0.5:
            return "normal"
        elif derivative <= 2.0:
            return "advertencia"
        else:
            return "critico"

    def get_all_metrics(self):
        cpu_d = self.cpu_derivative()
        ram_d = self.ram_derivative()
        disk_d = self.disk_derivative()
        cpu_lim, cpu_s = self.cpu_limit_analysis()
        ram_lim, ram_s = self.ram_limit_analysis()
        disk_lim, disk_s = self.disk_limit_analysis()

        return {
            "cpu": {
                "current": self.cpu_history[-1] if self.cpu_history else 0.0,
                "derivative": cpu_d,
                "limit": cpu_lim,
                "seconds_to_limit": cpu_s,
                "risk": self.get_risk_level(abs(cpu_d)),
            },
            "ram": {
                "current": self.ram_history[-1] if self.ram_history else 0.0,
                "derivative": ram_d,
                "limit": ram_lim,
                "seconds_to_limit": ram_s,
                "risk": self.get_risk_level(abs(ram_d)),
            },
            "disk": {
                "current": self.disk_history[-1] if self.disk_history else 0.0,
                "derivative": disk_d,
                "limit": disk_lim,
                "seconds_to_limit": disk_s,
                "risk": self.get_risk_level(abs(disk_d)),
            },
        }
