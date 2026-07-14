#!/usr/bin/env python3
"""
CompuSense - Sistema de Monitoreo de Recursos con Calculo Diferencial
Analiza la evolucion de recursos computacionales y predice saturacion
mediante derivadas y limites.
"""

import sys
import time
import threading

from monitor import SystemMonitor
from calculus import CalculusEngine
from graphs import ResourceGraph
from gui import AlertGUI


def main():
    print("=" * 55)
    print("   CompuSense - Monitoreo con Calculo Diferencial")
    print("=" * 55)
    print("Iniciando sistema de monitoreo...")
    print("Presiona Ctrl+C para detener.\n")

    monitor = SystemMonitor(interval=1.0)
    calculus = CalculusEngine(window_size=30)
    graph = ResourceGraph(max_points=60)
    gui = AlertGUI(on_close=lambda: sys.exit(0))

    running = True

    def on_close():
        nonlocal running
        running = False

    gui.on_close = on_close

    tick = 0
    try:
        while running:
            snap = monitor.snapshot()
            cpu, ram, disk = snap["cpu"], snap["ram"], snap["disk"]

            calculus.add_sample(cpu, ram, disk, dt=1.0)
            metrics = calculus.get_all_metrics()

            tangent_ts, tangent_vals = calculus.tangent_line(
                metrics["cpu"]["current"], metrics["cpu"]["derivative"], t_range=(-5, 10)
            )

            graph.update_data(cpu, ram, disk, tangent_ts, tangent_vals)
            graph.draw()
            gui.update_metrics(metrics)
            gui.update()

            tick += 1
            if tick % 10 == 0:
                print(
                    f"[t={tick}s] CPU={cpu:.1f}% ({metrics['cpu']['derivative']:+.2f} %/s) "
                    f"RAM={ram:.1f}% ({metrics['ram']['derivative']:+.2f} %/s) "
                    f"Disco={disk:.1f}% | Riesgo: CPU={metrics['cpu']['risk']} "
                    f"RAM={metrics['ram']['risk']} Disco={metrics['disk']['risk']}"
                )

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nDeteniendo CompuSense...")
    finally:
        graph.close()
        print("Sistema detenido.")


if __name__ == "__main__":
    main()
