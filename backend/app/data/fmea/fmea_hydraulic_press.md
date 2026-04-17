# FMEA-505: Hydraulic Press Failure Modes
**Machine ID:** PRESS-505
**System:** Hydraulics

## Failure Modes
| Component | Failure Mode | Potential Cause | Sev | Occ | Det | RPN | Recommended Action |
|-----------|--------------|-----------------|-----|-----|-----|-----|--------------------|
| Pump      | Loss of Pressure | Seal wear, Low fluid | 8 | 4 | 3 | 96 | Replenish fluid weekly; Inspect seals monthly |
| Valve     | Stuck Open | Debris in oil | 7 | 3 | 5 | 105 | Install finer filtration; flush system yearly |
| Hose      | Burst / Leak | Fatigue / Abrasion | 9 | 2 | 8 | 144 | Replace hoses every 2 years; Use protective sleeves |
| Cooler    | Overheating | Fan failure, clogged fins | 6 | 4 | 2 | 48 | Clean fins weekly; Monitor fan current |

## Critical Controls
- **Oil Level Sensor**: Trips if level < 20%.
- **Relief Valve**: Set to 160 bar max.
- **Temp Switch**: Cutoff at 65°C.
