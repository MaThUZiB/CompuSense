import tkinter as tk
from tkinter import font as tkfont


COLORS = {
    "normal": "#1a1a2e",
    "advertencia": "#e67e22",
    "critico": "#e74c3c",
    "texto_normal": "#00ff88",
    "texto_alerta": "#ffffff",
    "bg_card": "#16213e",
    "bg_panel": "#0f3460",
}


class AlertGUI:
    """
    Interfaz grafica con Tkinter que muestra el estado de los recursos
    y genera alertas visuales (cambio de color) cuando la pendiente
    supera niveles de riesgo.
    """

    def __init__(self, on_close=None):
        self.on_close = on_close
        self.root = tk.Tk()
        self.root.title("CompuSense - Consola de Alertas")
        self.root.geometry("520x620")
        self.root.configure(bg=COLORS["normal"])
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.title_font = tkfont.Font(family="Consolas", size=16, weight="bold")
        self.label_font = tkfont.Font(family="Consolas", size=11)
        self.value_font = tkfont.Font(family="Consolas", size=18, weight="bold")
        self.small_font = tkfont.Font(family="Consolas", size=9)

        self._build_ui()
        self.current_risk = "normal"

    def _build_ui(self):
        header = tk.Label(
            self.root,
            text="CompuSense",
            font=self.title_font,
            bg=COLORS["normal"],
            fg=COLORS["texto_normal"],
        )
        header.pack(pady=(15, 5))

        subtitle = tk.Label(
            self.root,
            text="Monitoreo de Recursos con Calculo Diferencial",
            font=self.small_font,
            bg=COLORS["normal"],
            fg="#aaaaaa",
        )
        subtitle.pack()

        self.cards_frame = tk.Frame(self.root, bg=COLORS["normal"])
        self.cards_frame.pack(pady=10, padx=10, fill="x")

        self.cpu_card = self._create_card("CPU", "cpu")
        self.ram_card = self._create_card("RAM", "ram")
        self.disk_card = self._create_card("DISCO", "disk")

        alert_frame = tk.Frame(self.root, bg=COLORS["bg_panel"], bd=2, relief="groove")
        alert_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(
            alert_frame,
            text="ALERTAS PREDICTIVAS",
            font=self.label_font,
            bg=COLORS["bg_panel"],
            fg=COLORS["texto_normal"],
        ).pack(pady=(8, 2))

        self.alert_text = tk.Text(
            alert_frame,
            height=8,
            width=50,
            bg=COLORS["bg_card"],
            fg=COLORS["texto_normal"],
            font=self.small_font,
            state="disabled",
            relief="flat",
        )
        self.alert_text.pack(padx=10, pady=5)

        status_frame = tk.Frame(self.root, bg=COLORS["normal"])
        status_frame.pack(pady=5)
        self.status_label = tk.Label(
            status_frame,
            text="Estado: NORMAL",
            font=self.label_font,
            bg=COLORS["normal"],
            fg=COLORS["texto_normal"],
        )
        self.status_label.pack()

    def _create_card(self, title, key):
        card = tk.Frame(self.cards_frame, bg=COLORS["bg_card"], bd=1, relief="raised")
        card.pack(side="left", padx=5, fill="both", expand=True)

        tk.Label(
            card, text=title, font=self.label_font, bg=COLORS["bg_card"], fg="#aaaaaa"
        ).pack(pady=(8, 0))

        value_label = tk.Label(
            card, text="0.0%", font=self.value_font, bg=COLORS["bg_card"], fg="#ffffff"
        )
        value_label.pack(pady=2)

        deriv_label = tk.Label(
            card, text="U'(t): 0.00 %/s", font=self.small_font, bg=COLORS["bg_card"], fg="#888888"
        )
        deriv_label.pack()

        time_label = tk.Label(
            card, text="Saturacion: -- s", font=self.small_font, bg=COLORS["bg_card"], fg="#888888"
        )
        time_label.pack(pady=(0, 8))

        return {"frame": card, "value": value_label, "deriv": deriv_label, "time": time_label}

    def _update_card(self, card, current, derivative, seconds, risk):
        card["value"].config(text=f"{current:.1f}%")

        risk_colors = {"normal": "#00ff88", "advertencia": "#e67e22", "critico": "#e74c3c"}
        card["value"].config(fg=risk_colors.get(risk, "#ffffff"))

        card["deriv"].config(text=f"U'(t): {derivative:+.2f} %/s")

        if seconds < float("inf") and seconds >= 0:
            card["time"].config(text=f"Saturacion: {seconds:.0f} s")
        else:
            card["time"].config(text="Saturacion: -- s")

    def update_metrics(self, metrics):
        overall_risk = "normal"
        alerts = []

        for key, label in [("cpu", "CPU"), ("ram", "RAM"), ("disk", "Disco")]:
            m = metrics[key]
            self._update_card(
                {
                    "frame": None,
                    "value": self.__dict__[f"{key}_card" if key != "disk" else "disk_card"]["value"],
                    "deriv": self.__dict__[f"{key}_card" if key != "disk" else "disk_card"]["deriv"],
                    "time": self.__dict__[f"{key}_card" if key != "disk" else "disk_card"]["time"],
                },
                m["current"],
                m["derivative"],
                m["seconds_to_limit"],
                m["risk"],
            )
            if m["risk"] == "critico":
                overall_risk = "critico"
                alerts.append(
                    f"[CRITICO] {label}: saturacion en ~{m['seconds_to_limit']:.0f}s (U'={m['derivative']:+.2f} %/s)"
                )
            elif m["risk"] == "advertencia" and overall_risk != "critico":
                overall_risk = "advertencia"
                alerts.append(
                    f"[ALERTA] {label}: aceleracion detectada (U'={m['derivative']:+.2f} %/s)"
                )

        self.current_risk = overall_risk
        bg = COLORS[overall_risk]
        self.root.configure(bg=bg)

        risk_text = {"normal": "NORMAL", "advertencia": "ADVERTENCIA", "critico": "CRITICO"}
        risk_fg = {"normal": COLORS["texto_normal"], "advertencia": "#e67e22", "critico": "#e74c3c"}

        self.status_label.config(
            text=f"Estado: {risk_text[overall_risk]}",
            bg=bg,
            fg=risk_fg[overall_risk],
        )

        self.alert_text.config(state="normal")
        self.alert_text.delete("1.0", "end")
        if alerts:
            self.alert_text.insert("end", "\n".join(alerts))
        else:
            self.alert_text.insert("end", "Sistema estable. Sin alertas.")
        self.alert_text.config(state="disabled", bg=COLORS["bg_card"], fg=risk_fg[overall_risk])

    def _on_close(self):
        if self.on_close:
            self.on_close()
        self.root.destroy()

    def update(self):
        self.root.update_idletasks()
        self.root.update()
