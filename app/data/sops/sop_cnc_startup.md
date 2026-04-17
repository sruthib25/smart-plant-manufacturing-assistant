# SOP-102: CNC Machine Start-up Procedure
**Machine ID:** CNC-204 / CNC-205
**Shift:** Start of Shift

## Pre-Start Inspection
- Check coolant level (Refill with Type C-20 if low).
- Verify way lube reservoir is > 1/4 full.
- Remove any chips from the vise area.
- Ensure door interlocks are functioning.

## Power-Up Sequence
1.  **Main Breaker**: Turn handle to 'ON' position on rear cabinet.
2.  **Control On**: Press green 'Power On' button on front panel. Wait for Windows boot.
3.  **Reset E-Stop**: Twist and pull red E-Stop button. Press blue 'Reset' key.
4.  **Reference Return**:
    - Select 'Zero Return' mode.
    - Press 'All Axes' or cycle X, Y, Z buttons.
    - Verify 'Home' lights turn green.

## Warm-Up Program
- Load Program `O0001` (Spindle Warm-up).
- Run for 10 minutes at 50% rapid override.
- **Caution**: Listen for unusual spindle noise during warm-up.
