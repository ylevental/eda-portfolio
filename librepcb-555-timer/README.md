# 555 Timer Astable Multivibrator — Programmatic LibrePCB Generation

A complete 555 timer blinking LED PCB generated entirely from Python scripts.
No manual EDA interaction — the scripts produce a full LibrePCB project with
schematic, circuit netlist, component library, board layout, ground plane,
and routed traces that pass DRC with zero errors.

## What Makes This Different

Most EDA tutorials walk through GUI clicks. This project generates the entire
LibrePCB project programmatically — reverse-engineering the `.lp` S-expression
file format, extracting UUIDs from installed libraries, and computing trace
geometry that provably avoids all clearance violations.

Key technical challenges solved:

- **UUID dependency resolution** — every LibrePCB element references others by
  UUID. The generator extracts and maps ~50 UUIDs across components, symbols,
  devices, packages, pads, pins, and signals.
- **Project-local library elements** — the NE555 timer and a THT bipolar
  capacitor device don't exist in the standard library, so the scripts generate
  them from scratch with correct signal-to-pad mappings.
- **Two-layer routing with via insertion** — the 555 netlist is non-planar
  (provably impossible to route on a single copper layer). The router uses
  top-copper stubs with vias to bottom-copper corridors, with mathematically
  verified zero-crossing geometry.

## Circuit

```
    VCC (+5V)
     │
    [R1 10kΩ]
     │
     ├────── pin 7 (DISCH)
     │
    [R2 47kΩ]          ┌──────────┐
     │                 │  NE555   │
     ├── pin 2 (TRIG)  │          │
     ├── pin 6 (THRESH) │   pin 3 ├──[R3 470Ω]──LED──GND
     │                 │          │
    [C1 10µF]          │   pin 8 ├── VCC
     │                 │   pin 1 ├── GND
    GND                │   pin 5 ├──[C2 10nF]──GND
                       └──────────┘
```

## Bill of Materials

| Ref | Value   | Package          | Description              |
|-----|---------|------------------|--------------------------|
| U1  | NE555   | DIP-8            | Timer IC                 |
| R1  | 10 kΩ   | Axial (THT 0207) | Charge resistor (high)   |
| R2  | 47 kΩ   | Axial (THT 0207) | Charge resistor (low)    |
| R3  | 470 Ω   | Axial (THT 0207) | LED current limiter      |
| C1  | 10 µF   | Radial THT       | Timing capacitor         |
| C2  | 10 nF   | Radial THT       | Decoupling (pin 5)       |
| D1  | LED     | 5mm THT          | Output indicator (red)   |
| J1  | 2-pin   | Pin header 1x02  | Power input (5V + GND)   |

All components are through-hole for easy assembly and because THT pads
exist on both copper layers (eliminating the need for vias at pad locations).

## Timing

| Parameter  | Formula                    | Value       |
|------------|----------------------------|-------------|
| T_high     | 0.693 × (R1 + R2) × C1    | **0.395 s** |
| T_low      | 0.693 × R2 × C1           | **0.326 s** |
| Period     | T_high + T_low             | **0.721 s** |
| Frequency  | 1 / Period                 | **≈ 1.39 Hz** |
| Duty cycle | T_high / Period            | **≈ 54.8%** |

The LED blinks at roughly 1.4 Hz — easily visible.

## Pre-Layout Simulation

Verify timing with Ngspice before generating the PCB:

```bash
ngspice 555_astable.cir
```

![555 Timer Simulation](images/sim_cap_output.svg)

## Usage

### Generate the full project

```bash
python3 generate_555.py
```

This creates a complete LibrePCB project at
`~/LibrePCB-Workspace/projects/555_Timer_Astable/` including:

- Project metadata and settings
- Circuit netlist with 7 nets and 14 component instances
- Schematic with all symbols placed and wired
- Board with all footprints placed on a 150×100mm PCB
- Ground plane on bottom copper
- Project-local NE555 component/device and THT bipolar capacitor device
- All required library elements copied into the project

### Route the board

```bash
python3 simple_route6.py
```

This adds routed traces to the board using a two-layer geometric router:

- Top copper: short horizontal stubs from pads to approach columns
- Vias at column points (far from all component pads)
- Bottom copper: corridors connecting via columns
- Ground plane on bottom copper auto-connects all GND pads

Open the project in LibrePCB and run DRC to verify — zero errors.

### Prerequisites

- Python 3.6+
- LibrePCB 1.2+ installed with official libraries downloaded
- Workspace at `~/LibrePCB-Workspace` (default location)

## PCB Design

**Board size:** 150 × 100 mm

**Layer stackup:** 2-layer (top copper + bottom copper ground plane)

**Routing strategy:** The 555 timer's netlist is non-planar — nets like
THRESH_TRIG connect pins on both sides of the DIP-8 IC, creating crossing
connections that cannot be resolved on a single copper layer. The router
solves this with a two-layer approach:

- Each net gets unique approach column X-coordinates at the board edges
  (left: x=8, 15, 22 — right: x=128, 132, 136, 142)
- Each net gets a unique corridor Y-coordinate on bottom copper
  (y=12, 20, 80, 88, 96)
- Top-copper stubs run horizontally from pads to vias at the columns
- Bottom-copper corridors run horizontally between column vias
- Vertical column segments on bottom copper connect vias to corridors

This geometry was verified to have zero crossings between any column
and any corridor from a different net.

## Screenshots

| File | Description |
|------|-------------|
| `images/555_Timer_Astable_Schematics.pdf` | Complete schematic with all nets wired |
| `images/555_Timer_Astable_Board.pdf` | Board layout |

## Files

| File | Description |
|------|-------------|
| `generate_555.py` | Generates the complete LibrePCB project from scratch |
| `simple_route6.py` | Two-layer geometric router with via insertion |
| `555_astable.cir` | Pre-layout Ngspice simulation |
| `docs/build_guide.md` | Technical walkthrough of the generation approach |
| `docs/theory.md` | 555 timer operating theory |

## What I Learned

This project started as a simple EDA portfolio exercise and became a deep
dive into PCB design fundamentals:

- **LibrePCB's S-expression file format** — undocumented, reverse-engineered
  by inspecting manually-created projects
- **UUID dependency chains** — components reference symbols, devices reference
  packages, signals map to pads through multiple indirection layers
- **Graph planarity** — the 555 netlist cannot be embedded in a plane without
  crossings, requiring two copper layers
- **Clearance constraints** — DIP-8 pins are 2.54mm apart, so vertical traces
  near the IC always violate clearance to adjacent pins. The solution is
  horizontal approach from offset columns.
- **Ground planes** — through-hole pads connect to both layers automatically,
  so GND routing is "free" with a bottom-layer ground plane

## References

- [LibrePCB Documentation](https://librepcb.org/docs/)
- [NE555 Datasheet (TI)](https://www.ti.com/product/NE555)
- Horowitz & Hill, *The Art of Electronics*, Ch. 10
