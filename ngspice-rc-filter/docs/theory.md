# RC Low-Pass Filter Theory

## Transfer Function

The voltage-divider relationship between the resistor impedance (R) and the
capacitor impedance (1/jωC) gives the transfer function:

```
H(jω) = Vout / Vin = 1 / (1 + jωRC)
```

In terms of the cutoff frequency ω_c = 1 / RC:

```
H(jω) = 1 / (1 + j·ω/ω_c)
```

## Magnitude and Phase

The magnitude (in dB) and phase are:

```
|H(jω)| = 1 / sqrt(1 + (ω/ω_c)²)

|H|_dB  = −10 · log₁₀(1 + (ω/ω_c)²)

∠H(jω) = −arctan(ω/ω_c)
```

At the cutoff frequency (ω = ω_c):
- Magnitude = 1/√2 ≈ 0.707 → **−3.01 dB**
- Phase = **−45°**

## Step Response

When driven by a unit step, the output follows:

```
v_out(t) = 1 − exp(−t / τ)     for t ≥ 0
```

where τ = RC is the time constant.

| Time    | v_out | % of final |
|---------|-------|------------|
| t = τ   | 0.632 | 63.2%     |
| t = 2τ  | 0.865 | 86.5%     |
| t = 3τ  | 0.950 | 95.0%     |
| t = 5τ  | 0.993 | 99.3%     |

## Relationship Between Bandwidth and Rise Time

For a first-order system, the 10%–90% rise time is:

```
t_r ≈ 2.2 · τ = 2.2 · RC = 0.35 / f_c
```

With our values: t_r ≈ 2.2 × 10 µs = **22 µs**

This inverse relationship between bandwidth and rise time is a fundamental
concept in signal processing and communications.
