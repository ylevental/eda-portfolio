# 555 Timer Astable Mode Theory

## How the 555 Works

The 555 timer IC contains two comparators, an SR flip-flop, a discharge
transistor, and a resistive voltage divider that sets two threshold
voltages:

- **Upper threshold:** 2/3 × VCC ≈ 3.33 V (at 5 V supply)
- **Lower threshold:** 1/3 × VCC ≈ 1.67 V

The output toggles based on the capacitor voltage crossing these
thresholds.

## Astable Operating Cycle

### Phase 1: Capacitor Charging (Output HIGH)

The capacitor charges through R1 + R2 from the lower threshold
(VCC/3) toward the upper threshold (2VCC/3):

```
v_C(t) = VCC − (VCC − VCC/3) · exp(−t / τ_charge)

τ_charge = (R1 + R2) · C1
```

The output is HIGH during this phase. Charging ends when v_C reaches
2VCC/3.

### Phase 2: Capacitor Discharging (Output LOW)

The discharge transistor (pin 7) turns on, providing a path to ground
through R2 only. The capacitor discharges from 2VCC/3 toward VCC/3:

```
v_C(t) = (2VCC/3) · exp(−t / τ_discharge)

τ_discharge = R2 · C1
```

The output is LOW during this phase. Discharging ends when v_C drops
to VCC/3, and the cycle repeats.

## Timing Equations

The time for each phase is derived from the exponential charge/discharge
between the 1/3 and 2/3 thresholds:

```
T_high = ln(2) × (R1 + R2) × C1 = 0.693 × (R1 + R2) × C1
T_low  = ln(2) × R2 × C1         = 0.693 × R2 × C1
```

The total period and frequency:

```
T = T_high + T_low = 0.693 × (R1 + 2·R2) × C1
f = 1 / T = 1.44 / ((R1 + 2·R2) × C1)
```

The duty cycle:

```
D = T_high / T = (R1 + R2) / (R1 + 2·R2)
```

## Our Design Values

With R1 = 10 kΩ, R2 = 47 kΩ, C1 = 10 µF:

| Parameter | Calculation | Result |
|-----------|-------------|--------|
| T_high | 0.693 × 57,000 × 10⁻⁵ | 0.395 s |
| T_low  | 0.693 × 47,000 × 10⁻⁵ | 0.326 s |
| Period | T_high + T_low | 0.721 s |
| Frequency | 1 / 0.721 | 1.39 Hz |
| Duty cycle | 57k / 104k | 54.8% |

## LED Current

The output HIGH voltage is approximately VCC − 1.7 V (saturation drop).
With a red LED (forward voltage ≈ 1.8 V) and R3 = 470 Ω:

```
I_LED = (V_out − V_LED) / R3
      = (3.3 − 1.8) / 470
      ≈ 3.2 mA
```

This is well within the typical LED range (2–20 mA) and within the
555's output current capability (up to 200 mA).

## Pin 5 Bypass Capacitor

C2 (10 nF) on pin 5 (CONTROL VOLTAGE) filters noise on the internal
voltage divider. Without it, electrical noise can cause erratic
threshold crossings and timing jitter. This is a standard practice
in all 555 circuits.
