# src/detectors/god_class.py
from __future__ import annotations

from typing import Dict, Any
from src.domain.model import UMLModel


class GodClassDetector:
    """
    Calcula el GodClassScore y clasifica la clase como:
        • god-class      (score ≥  score_godclass)
        • suspicious     (score ≥  score_suspicious)
        • normal         (score  < score_suspicious)
    Los umbrales y rangos de normalización provienen de `cfg`,
    de modo que el detector se adapta a los valores calculados
    dinámicamente por el Calibrator.  Si los umbrales no existen
    en la configuración, se usan 0.75 y 0.50 como valores
    por defecto (estándar de la literatura).
    """

    def __init__(self, cfg: Dict[str, Any], calculators: Dict[str, Any]) -> None:
        # Configuracion de rangos y umbrales (puede venir de config/calibracion).
        self.cfg = cfg

        # Inyeccion de calculadores para desacoplar el detector de implementaciones.
        self.wmc = calculators["wmc"]
        self.atfd = calculators["atfd"]
        self.tcc = calculators["tcc"]
        self.lrc = calculators["lrc"]
        self.fan = calculators["fan"]

        # Umbrales de decisión (heredados o recalibrados)
        self.thr_godclass = cfg.get("score_godclass", 0.75)
        self.thr_susp     = cfg.get("score_suspicious", 0.50)

    # ------------------------------------------------------------------ #
    def detect(self, model: UMLModel):
        # Lista de hallazgos que se devolvera en report.json -> god_class.
        findings = []

        for cls in model.classes.values():
            # ---------- métricas brutas -------------------------------- #
            # Ejemplo tipico: WMC=5, ATFD=3, TCC=0.4, FanIn=2, FanOut=4, LRC=3
            w   = self.wmc.calc(cls)
            a   = self.atfd.calc(cls)
            t   = self.tcc.calc(cls)
            fi  = self.fan.calc_in(cls)
            fo  = self.fan.calc_out(cls)
            lrc = self.lrc.calc(cls, model)

            # ---------- normalización 0-1 ------------------------------ #
            # Min-max para WMC y ATFD usando cfg (wmc_min/max, atfd_min/max).
            w_n   = self._norm(w,  "wmc")
            a_n   = self._norm(a,  "atfd")

            # FanIn/FanOut/LRC se normalizan por maximos globales esperados.
            fi_n  = min(fi  / max(self.cfg.get("fanin_max",  1), 1), 1)
            fo_n  = min(fo  / max(self.cfg.get("fanout_max", 1), 1), 1)
            lrc_n = min(lrc / max(self.cfg.get("lrc_max",    1), 1), 1)

            # En TCC, valores bajos son peores; por eso se invierte: 1 - TCC.
            t_n   = 1 - t  # menor cohesión = peor

            # ---------- puntuaciones parciales ------------------------- #
            # p_base pondera complejidad/acoplamiento/cohesion.
            # Formula: 0.4*WMC + 0.3*ATFD + 0.3*(1-TCC)
            p_base = 0.4 * w_n + 0.3 * a_n + 0.3 * t_n

            # p_arq pondera arquitectura (capas y conectividad).
            # Formula: 0.4*LRC + 0.3*FanOut + 0.3*FanIn
            p_arq  = 0.4 * lrc_n + 0.3 * fo_n + 0.3 * fi_n

            # Semántica aún no integrada: placeholder para el futuro
            # Score final actual:
            # score = 0.5*p_base + 0.3*p_arq
            # Nota: hay 0.2 reservado para semantica futura.
            score = 0.5 * p_base + 0.3 * p_arq

            # ---------- clasificación ---------------------------------- #
            # Etiquetado por umbrales calibrados.
            if score >= self.thr_godclass:
                label = "god-class"
            elif score >= self.thr_susp:
                label = "suspicious"
            else:
                # DEBUG ↓ (puedes desactivar esta línea si ya no la necesitas)
                print(
                    f"[DEBUG] {cls.name:20}  score={score:.2f}  "
                    f"WMC={w}  ATFD={a}  TCC={t:.2f}  "
                    f"FanIn={fi}  FanOut={fo}  LRC={lrc}"
                )
                continue

            # ---------- reporte --------------------------------------- #
            # Se guarda una fila del reporte para esta clase.
            # Ejemplo de salida:
            # {
            #   "class": "Guest",
            #   "score": 0.47,
            #   "label": "god-class",
            #   "metrics": {...}
            # }
            findings.append(
                {
                    "class": cls.name,
                    "score": round(score, 2),
                    "label": label,
                    "metrics": {
                        "WMC": w,
                        "ATFD": a,
                        "TCC": round(t, 2),
                        "FanIn": fi,
                        "FanOut": fo,
                        "LRC": lrc,
                    },
                }
            )
        return findings

    # ------------------------------------------------------------------ #
    def _norm(self, x: float, key: str) -> float:
        """
        Normalización min-max.  Devuelve 0.0 cuando el denominador es 0.
        """
        # Min-max sobre el rango configurado para la metrica key.
        # Ejemplo: x=6, min=0, max=12 -> 0.5
        rng = self.cfg.get(f"{key}_max", 1) - self.cfg.get(f"{key}_min", 0)
        if rng == 0:
            return 0.0
        return (x - self.cfg.get(f"{key}_min", 0)) / rng
