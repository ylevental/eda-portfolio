# Open-Source EDA Portfolio

A collection of beginner-friendly electronics design projects built with free and
open-source EDA tools on Fedora Linux (KDE).

## Projects

| # | Project | Tool | Domain | Description |
|---|---------|------|--------|-------------|
| 1 | [RC Low-Pass Filter](ngspice-rc-filter/) | Ngspice | Analog | AC sweep analysis with Bode magnitude and phase plots |
| 2 | [Inverting Op-Amp Amplifier](qucs-s-opamp-amplifier/) | Qucs-S + Ngspice | Analog | Classic inverting amplifier with transient and AC analysis |
| 3 | [555 Timer Astable PCB](librepcb-555-timer/) | LibrePCB | Mixed-Signal | PCB layout for a blinking LED circuit using the 555 timer IC |

### Preview

**RC Low-Pass Filter — Bode Magnitude:**

![Bode Magnitude](ngspice-rc-filter/images/bode_magnitude.svg)

**Inverting Op-Amp — Transient Response:**

![Op-Amp Transient](qucs-s-opamp-amplifier/images/transient.svg)

**555 Timer — Capacitor Charge/Discharge and Output:**

![555 Timer Sim](librepcb-555-timer/images/sim_cap_output.svg)

## Tools & Versions

All tools were installed on **Fedora 43 (KDE Plasma)**:

```bash
# Install simulation tools
sudo dnf install ngspice qucs-s

# Install PCB design tool
flatpak install flathub org.librepcb.LibrePCB
```

## Running the Projects

### Ngspice (CLI)

```bash
cd ngspice-rc-filter/
ngspice rc_lowpass.cir
```

### Qucs-S (GUI)

1. Open Qucs-S
2. **File → Open** → select `qucs-s-opamp-amplifier/inverting_amp.sch`
3. Press **F2** or click **Simulate** to run

### LibrePCB (GUI)

1. Open LibrePCB
2. Follow the step-by-step recreation guide in `librepcb-555-timer/docs/`

## Repository Structure

```
eda-portfolio/
├── README.md
├── ngspice-rc-filter/
│   ├── README.md
│   ├── rc_lowpass.cir          ← Ngspice netlist (run directly)
│   ├── rc_lowpass_step.cir     ← Step response variant
│   ├── images/
│   │   ├── bode_magnitude.svg
│   │   ├── bode_phase.svg
│   │   └── step_response.svg
│   └── docs/
│       └── theory.md
├── qucs-s-opamp-amplifier/
│   ├── README.md
│   ├── inverting_amp.sch       ← Qucs-S schematic (open in Qucs-S)
│   ├── inverting_amp.cir       ← Ngspice netlist (standalone verification)
│   ├── images/
│   │   ├── ac_magnitude.svg
│   │   ├── ac_phase.svg
│   │   └── transient.svg
│   └── docs/
│       └── theory.md
└── librepcb-555-timer/
    ├── README.md
    ├── 555_astable.cir         ← Ngspice pre-layout simulation
    ├── images/
    │   └── sim_cap_output.svg
    └── docs/
        ├── theory.md
        └── build_guide.md
```

## License

This portfolio is released under the [MIT License](LICENSE).

## Author

Yuval Levental — [LinkedIn](https://www.linkedin.com) · [GitHub](https://github.com)
