# Inverting Op-Amp Amplifier Theory

## Ideal Op-Amp Assumptions

1. **Infinite open-loop gain** (A → ∞)
2. **Infinite input impedance** (no current into op-amp inputs)
3. **Zero output impedance**

These assumptions lead to two key rules for negative-feedback circuits:
- The voltage at the inverting (−) input equals the voltage at the
  non-inverting (+) input ("virtual short")
- No current flows into either input terminal

## Deriving the Gain

With the non-inverting input grounded, the virtual short means the inverting
input is also at 0 V (a "virtual ground").

Applying KCL at the inverting input node:

```
Current through R1 = Current through Rf

(Vin − 0) / R1 = (0 − Vout) / Rf

Vout / Vin = −Rf / R1
```

For R1 = 1 kΩ and Rf = 10 kΩ:

```
Av = −10 kΩ / 1 kΩ = −10
```

The negative sign indicates **phase inversion**: when the input goes
positive, the output goes negative.

## Input and Output Impedance

The input impedance seen by the source is simply R1, because the inverting
input is held at virtual ground:

```
Zin = R1 = 1 kΩ
```

The output impedance of the ideal circuit is 0 Ω (the op-amp drives
the output directly).

## Gain-Bandwidth Product

A real op-amp has a finite gain-bandwidth product (GBW). For example,
a typical LM741 has GBW ≈ 1 MHz. The closed-loop bandwidth is:

```
f_3dB = GBW / |Av| = 1 MHz / 10 = 100 kHz
```

Our ideal op-amp model uses a gain of 10⁶, so the simulated bandwidth
will be much higher than a real device. Replacing the ideal model with
a LM741 SPICE model would show the realistic bandwidth limitation.

## Stability Consideration

The inverting configuration is inherently stable for resistive feedback
because the feedback is purely negative. Adding capacitance in the
feedback path (e.g., for an integrator) requires care to ensure
phase margin remains adequate.
