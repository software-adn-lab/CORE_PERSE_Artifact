# src/calibration/calibrator.py
from __future__ import annotations
from statistics import mean, stdev
from typing import Dict, List
from src.metrics.structural import WMC, ATFD
from src.metrics.architectural import FanInOut, LRC
from src.domain.model import UMLModel

class Calibrator:
    """Ajusta los rangos de normalización y, opcionalmente,
    reajusta los cortes GodClassScore según el tamaño del sistema."""
    def __init__(self, base_cfg: Dict[str, float] | None = None):
        # base_cfg suele venir de config.json.
        self.cfg = base_cfg or {}

    # ---------- DISTRIBUCIONAL ----------
    def _metric_values(self, model: UMLModel) -> Dict[str, List[float]]:
        # Instanciamos calculadores para levantar distribuciones del sistema.
        wmc = WMC(); atfd = ATFD(); fan = FanInOut(); lrc = LRC()

        # Cada clave guarda la lista de valores por clase.
        # Ejemplo: wmc=[0,1,3,2,...]
        values = dict(
            wmc=[wmc.calc(c) for c in model.classes.values()],
            atfd=[atfd.calc(c) for c in model.classes.values()],
            fanin=[fan.calc_in(c) for c in model.classes.values()],
            fanout=[fan.calc_out(c) for c in model.classes.values()],
            lrc=[lrc.calc(c, model) for c in model.classes.values()],
        )
        return values

    def _p95(self, seq: List[float]) -> float:
        # Percentil 95 aproximado para recortar outliers extremos.
        # Si la secuencia esta vacia, devolvemos 1 para evitar divisiones por cero.
        if not seq: return 1
        k = int(0.95 * len(seq))
        return sorted(seq)[k]

    def calibrate(self, model: UMLModel, context_txt: str | None = None) -> Dict[str, float]:
        # Paso 1: recolectar metricas observadas en el sistema actual.
        vals = self._metric_values(model)

        # Rango de normalización basado en min / p95
        # Ejemplo: si wmc=[0,1,2,10], p95 ayuda a no sobredimensionar por un outlier.
        self.cfg["wmc_min"], self.cfg["wmc_max"] = min(vals["wmc"]), self._p95(vals["wmc"])
        self.cfg["atfd_min"], self.cfg["atfd_max"] = min(vals["atfd"]), self._p95(vals["atfd"])
        self.cfg["fanin_max"]  = self._p95(vals["fanin"])
        self.cfg["fanout_max"] = self._p95(vals["fanout"])
        self.cfg["lrc_max"]    = max(vals["lrc"])  # En general ≤ número de capas

        # ---------- SEMÁNTICA ----------
        if context_txt:
            # Estimacion simple de "tamano" del contexto textual.
            # 300 palabras ~ 1 pagina (aprox).
            pages = max(len(context_txt.split()) // 300, 1)  # 300 tokens ≈ 1 pág.

            # A mas paginas, mas flexible se vuelve el umbral de score.
            scale = 1 + (pages / 10)          # tesis de 30 págs ⇒ scale ≈ 4

            # Recalibracion de cortes para suspicious/god-class.
            self.cfg["score_suspicious"] = 0.50 * (scale / (scale + 1))
            self.cfg["score_godclass"]   = 0.75 * (scale / (scale + 1))

        return self.cfg
