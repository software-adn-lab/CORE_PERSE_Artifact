# CORE PERSE: UML Design Antipattern Detection Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type: DSR Artifact](https://img.shields.io/badge/Type-DSR%20Artifact-blue)](https://en.wikipedia.org/wiki/Design_science_research)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)]()
[![Language: Python](https://img.shields.io/badge/Language-Python-blue)]()

---

## 📄 Abstract

**CORE PERSE** (Combined Reasoning & Pervasive Search Engine) is a software artifact developed under the **Design Science Research (DSR)** methodology. Its primary objective is to enable the **early detection of software design antipatterns** directly from UML class diagrams before the implementation phase.

The artifact integrates **structural metrics, heuristic rules, and AI-based calibration** to identify design flaws such as *God Class* and *Hub-Like Dependency*. By shifting defect detection to the design phase, CORE PERSE reduces technical debt, improves maintainability, and enhances architectural quality.

---

## 🎯 Scope & Detection Capabilities

This tool is designed to analyze **software design artifacts**, specifically UML class diagrams represented in **XMI 2.1 format**, complemented with project documentation (PDF).

It detects the following antipatterns:

| # | Antipattern | Description |
|---|------------|------------|
| **1** | **God Class** | Class with excessive responsibilities, low cohesion, and high complexity. |
| **2** | **Hub-Like Dependency** | Class acting as a central node with excessive dependencies. |

---

## 🛠️ Technical Implementation

CORE PERSE is implemented as a **CLI-based analytical pipeline**, designed for reproducibility and flexibility in academic and research contexts.

- **Architecture:** Modular pipeline (Command Line Interface)  
- **Language:** Python 3.10+  
- **Processing:** Metric extraction + heuristic rules + AI calibration  
- **Input:** UML Class Diagram (XMI 2.1) + Project document (PDF)  
- **Output:** JSON reports (detections + metrics)  

### Core Metrics

- WMC (Weighted Methods per Class)  
- ATFD (Access to Foreign Data)  
- TCC (Tight Class Cohesion)  
- Fan-In / Fan-Out  
- LRC (Layer Responsibility Consistency)  
- Semantic metrics (MRR, SCoR, SVD)  

---

## ⚙️ Calibration Modes

CORE PERSE provides three calibration strategies:

| Mode | Description |
|------|------------|
| **Static** | Fixed thresholds defined in configuration files |
| **Classical** | Context-based calibration using textual input |
| **AI Automated** | Dynamic calibration using structural + semantic signals (Recommended) |

---

## 🚀 Usage Guide

### 1. Clone the Repository

```bash
git clone https://github.com/software-adn-lab/CORE_PERSE_Artifact.git
cd CORE_PERSE_Artifact
