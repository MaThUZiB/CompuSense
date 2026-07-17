# CompuSense

**Sistema de Monitoreo de Recursos con Cálculo Diferencial**

CompuSense analiza la evolución de recursos computacionales en tiempo real y predice la saturación de CPU, RAM y disco mediante derivadas, límites y rectas tangentes.

## Funcionalidades

- Monitoreo en tiempo real de CPU, RAM y disco
- Cálculo de derivada de primer orden U'(t) con diferencias centrales
- Análisis asintótico: predicción de tiempo hasta saturación (U(t) → 100%)
- Recta tangente predictiva para visualizar la tendencia
- Sistema de alertas por niveles de riesgo:
  - **Normal**: U'(t) ≤ 0.5 %/s
  - **Advertencia**: 0.5 < U'(t) ≤ 2.0 %/s
  - **Crítico**: U'(t) > 2.0 %/s
- Interfaz gráfica con Tkinter (consola de alertas)
- Gráficos en tiempo real con Matplotlib (curvas de carga y derivadas)
- Detección de los 5 procesos con mayor consumo

## Requisitos

- Python 3.10+
- Linux (usa APIs de `/proc` vía psutil)

## Instalación

```bash
cd Projects/CompuSense
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Uso
python main.py
Esto abre dos ventanas:
1. Gráficos (Matplotlib) — curvas U(t) y derivadas U'(t)
2. Consola de Alertas (Tkinter) — métricas y alertas predictivas
Presiona Ctrl+C en la terminal o cierra la ventana para detener.
Estructura
CompuSense/
├── main.py          # Punto de entrada, loop principal
├── monitor.py       # Captura de métricas con psutil
├── calculus.py      # Motor de cálculo diferencial
├── graphs.py        # Gráficos en tiempo real con Matplotlib
├── gui.py           # Interfaz gráfica con Tkinter
└── requirements.txt # Dependencias
