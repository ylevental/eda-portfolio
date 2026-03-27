# Technical Guide — Programmatic LibrePCB Project Generation

This document explains how `generate_555.py` and `simple_route6.py` work,
covering the LibrePCB file format, UUID resolution, and routing geometry.

## LibrePCB File Format

LibrePCB projects use S-expressions (Lisp-like syntax) in `.lp` files.
A project consists of:

```
555_Timer_Astable/
├── .librepcb-project          # marker file containing "2"
├── project/
│   ├── metadata.lp            # project name, author, UUID
│   ├── settings.lp            # output job settings
│   ├── jobs.lp                # fabrication output jobs
│   └── settings.user.lp       # user preferences
├── circuit/
│   └── circuit.lp             # netlist: nets, components, signals
├── schematics/
│   └── main/
│       └── schematic.lp       # symbol placements, netsegments (wires)
├── boards/
│   └── default/
│       └── board.lp           # device placements, traces, planes, vias
└── library/                   # project-local copies of library elements
    ├── cmp/                   # components (with .librepcb-cmp markers)
    ├── dev/                   # devices
    ├── pkg/                   # packages
    └── sym/                   # symbols
```

Every element (net, component, device, pad, pin, symbol, package) is
identified by a UUID. References between elements use these UUIDs, creating
deep dependency chains.

## UUID Resolution

The generator resolves UUIDs by crawling the installed libraries at
`~/LibrePCB-Workspace/data/libraries/remote/`. For example, to place
a resistor on the board:

1. Find the **component** UUID for "Resistor" (`ef80cd5e...`)
2. Find its **symbol variant** UUID for the schematic symbol
3. Find the **device** UUID that maps this component to a package (`a0e021c0...` for THT 0207)
4. Find the **package** UUID for the physical footprint (`41a60506...`)
5. Find the **pad** UUIDs within that package (pin 1: `181c5e6c...`, pin 2: `b809afd1...`)
6. Find the **signal** UUIDs within the component (maps to net assignments)
7. Find the **footprint** UUID within the package (for board placement)

The generator hardcodes these UUIDs after extraction. For components not
in the standard library (NE555, THT bipolar capacitor), it generates
project-local library elements with fresh UUIDs.

## Project-Local Components

### NE555 Timer

The NE555 doesn't exist as a single component in LibrePCB's libraries.
The generator creates:

- A **component** (`librepcb_component`) with 8 signals matching the 555 pinout
- A **device** (`librepcb_device`) mapping those signals to DIP-8 package pads
- Uses the existing "Generic IC 8-Pin" symbol from the IC library

### THT Bipolar Capacitor

The standard library has SMD bipolar capacitor devices but no THT version.
The generator creates a device mapping the "Capacitor Bipolar" component
signals to the radial capacitor package pads.

## Schematic Generation

The schematic places symbols on a 2.54mm grid with 15 netsegments wiring
every pin. Each netsegment contains:

- **Junctions** at wire bend points
- **Netlabels** for net identification
- **Netlines** connecting pins to junctions

## Board Generation

### Component Placement

Components are placed on a 150×100mm board with 25mm+ spacing:

```
  J1(5,35)  R1(40,75)  R2(40,35)  U1(70,50)  C2(70,25)  C1(95,25)  R3(105,65)  D1(145,65)
```

Components at y=35 and y=65 are deliberately offset from the IC's pin
band (y≈46–54) so horizontal trace stubs from IC pins never pass
through other components.

### Ground Plane

A copper fill on the bottom layer assigned to the GND net. Since all
components are through-hole, their GND pads connect to this plane
automatically — no explicit GND traces needed.

## Routing Strategy (simple_route6.py)

### The Planarity Problem

The 555 timer's netlist is non-planar. THRESH_TRIG connects U1 pin 2
(left side) and pin 6 (right side). VCC connects pin 4 (left) and
pin 8 (right). These nets interleave with DISCHARGE (pin 7, right) and
OUTPUT (pin 3, left), creating crossings that cannot be resolved on a
single copper layer.

### Two-Layer Solution

Every connection follows this pattern:

1. **Top copper stub**: horizontal trace from pad to a via at an
   "approach column" X-coordinate
2. **Via**: transitions from top copper to bottom copper
3. **Bottom copper column**: vertical trace from via down/up to a
   corridor Y-coordinate
4. **Bottom copper corridor**: horizontal trace connecting column
   endpoints within the same net

### Approach Columns (unique per net)

Left side (for IC left pins):
- VCC: x = 8
- OUTPUT: x = 15
- THRESH_TRIG: x = 22

Right side (for IC right pins):
- CONTROL: x = 128
- THRESH_TRIG: x = 132
- DISCHARGE: x = 136
- VCC: x = 142

### Corridors (unique per net)

- THRESH_TRIG: y = 12
- CONTROL: y = 20
- OUTPUT: y = 80
- DISCHARGE: y = 88
- VCC: y = 96
- GND: handled by ground plane (no corridor needed)

### Verification

The column/corridor geometry was verified programmatically: no vertical
column segment from one net intersects any horizontal corridor from a
different net. This guarantees zero clearance violations on the bottom
copper layer.

Top copper stubs are all horizontal at unique Y values (each IC pin has
a different Y coordinate), so they never cross each other either.

### LED_ANODE Exception

The LED_ANODE net (R3 → D1) routes entirely on top copper since both
components are far from the IC and no other top-copper traces exist in
that region. The trace approaches D1 from above (y=72) to avoid passing
over the LED body.

## Running DRC

After generation and routing, open the project in LibrePCB:

```bash
flatpak run org.librepcb.LibrePCB
```

Navigate to the board editor and run **Tools → Design Rule Check**.
Expected result: zero errors.
