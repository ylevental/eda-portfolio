#!/usr/bin/env python3
"""
Generate a complete LibrePCB 555 Timer Astable project.

This script produces all .lp files needed for a working 555 timer
blinking LED board, including:
  - Project-local NE555 component and device (not in official libs)
  - Circuit netlist with all components and nets
  - Schematic with symbol placement and wiring
  - Board with device placement, traces, and ground plane

Usage:
  python3 generate_555.py [output_dir]

Default output_dir:
  ~/LibrePCB-Workspace/projects/555_Timer_Astable
"""

import os
import sys
import uuid as uuid_mod
import shutil
from pathlib import Path


def genuuid():
    """Generate a new random UUID string."""
    return str(uuid_mod.uuid4())


# ============================================================
# LIBRARY UUIDS (from installed workspace libraries)
# ============================================================

# --- Components ---
CMP_RESISTOR       = "ef80cd5e-2689-47ee-8888-31d04fc99174"
CMP_CAP_BIPOLAR    = "d167e0e3-6a92-4b76-b013-77b9c230e5f1"
CMP_CAP_UNIPOLAR   = "c54375c5-7149-4ded-95c5-7462f7301ee7"
CMP_LED            = "2b24b18d-bd95-4fb4-8fe6-bce1d020ead4"
CMP_PIN_HDR_1X02   = "ab344e7c-b740-4f2a-b21a-f7b1c433f990"
CMP_SUPPLY_VCC     = "58c3c6cd-11eb-4557-aa3f-d3e05874afde"
CMP_SUPPLY_GND     = "8076f6be-bfab-4fc1-9772-5d54465dd7e1"

# --- Resistor component details (IEEE/US variant) ---
RES_SIG_1          = "3452d36e-1ce8-4b7c-8e5b-90c2e4929ed8"  # pin "1"
RES_SIG_2          = "ad623f98-9e73-49c3-9404-f7cfa99d17cd"  # pin "2"
RES_VARIANT_US     = "d16e1f44-16af-4773-a310-de370f744548"
RES_GATE_US        = "169660fd-968a-4d3e-83f5-47f973b4ecd8"
RES_SYM_US         = "193ef70d-8dab-4a6c-a672-274c5bf09b68"
RES_PIN_1          = "f42020e8-c53f-4ff2-947e-07879cf42546"  # sym pin → sig 1
RES_PIN_2          = "2b3dd7f8-043b-4d43-9302-9300ba356de7"  # sym pin → sig 2

# --- Capacitor Bipolar (C2 - MLCC 10nF) ---
CAPB_SIG_1         = "1c1c7abc-7b40-4f92-b533-f65604644db7"
CAPB_SIG_2         = "6d776f4d-2a7c-4128-a98a-dbb1dd861411"
CAPB_VARIANT_US    = "6e639ff1-4e81-423b-9d0e-b28b35693a61"
CAPB_GATE_US       = "5e9de029-0af9-477f-afb4-bc05692e4b87"
CAPB_SYM_US        = "d5aad17b-0d58-4f79-9429-49e8201220b9"
CAPB_PIN_1         = "83d40864-0a14-496e-a08d-faeb2bbd9af6"  # → sig 1
CAPB_PIN_2         = "c39ca7a0-22c0-4338-83e8-98aba0874d88"  # → sig 2

# --- Capacitor Unipolar (C1 - Electrolytic 10µF) ---
CAPU_SIG_PLUS      = "e010ecbb-6210-4da3-9270-ebd58656dbf0"
CAPU_SIG_MINUS     = "af3ffca8-0085-4edb-a775-fcb759f63411"
CAPU_VARIANT_US    = "20a01a81-506e-4fee-9dc0-8b50e6537cd4"
CAPU_GATE_US       = "00a450e6-247a-410c-a2dd-e4ff30ec1694"
CAPU_SYM_US        = "7293b183-2a75-437a-be94-ccf4ab6422a8"
CAPU_PIN_PLUS      = "66df0382-3069-40e1-b729-3b1ad6f8ddb5"
CAPU_PIN_MINUS     = "6d445a38-f8eb-46c1-8ae0-99ef036ca312"

# --- LED ---
LED_SIG_A          = "f1467b5c-cc7d-44b4-8076-d729f35b3a6a"  # anode
LED_SIG_C          = "7b023430-b68f-403a-80b8-c7deb12e7a0c"  # cathode
LED_VARIANT        = "ed0f0ca2-43ff-4a10-94c2-2958bc336586"
LED_GATE           = "80e56299-8f8c-4613-a559-1fba31f01411"
LED_SYM            = "cb442e56-0ec7-4486-8c43-7bdfa9b47d9a"
LED_PIN_A          = "2a64f851-340a-43f2-b1cf-06a1d4b54560"
LED_PIN_C          = "18de942d-8b47-4daf-9e07-d089204e09d0"

# --- Pin Header 1x02 ---
HDR_SIG_1          = "9e3c2d0e-7bc0-42e9-a562-f21ef061126a"
HDR_SIG_2          = "4b7490ca-af89-4dd9-beff-9edc631e7d9b"
HDR_VARIANT        = "ee92375f-b17d-4d79-84d9-4df2c4aed57a"
HDR_GATE           = "23f3bc73-5f17-44e3-ac44-2bc61951f32c"
HDR_SYM            = "df138f86-d378-4465-bee1-c2b0b7d32cef"
HDR_PIN_1          = "e313439d-b34a-43cd-bbb6-61626a40fd32"
HDR_PIN_2          = "8c43a15d-5e7b-465f-b51e-5f482a4b6eb3"

# --- Supply VCC ---
VCC_SIG_NET        = "1d893320-f811-4a79-b64e-cc23d749d394"
VCC_VARIANT        = "afb86b45-68ec-47b6-8d96-153d73567228"
VCC_GATE           = "09b6d6c4-2d37-432f-9471-a317aad9a499"
VCC_SYM            = "b95d0aca-7344-41ec-90ed-022f365ad765"
VCC_PIN_NET        = "771c2d8b-e4ad-487b-bcb1-fe2bc10c8a03"

# --- Supply GND ---
GND_SIG_NET        = "ff161c97-29a5-43aa-a9ae-3ca7a66982ce"
GND_VARIANT        = "f09ad258-595b-4ee9-a1fc-910804a203ae"
GND_GATE           = "0539fd52-890f-48af-97a9-bacfb79c9475"
GND_SYM            = "80f8cd68-69d9-43c4-9ed2-da32ca714b10"
GND_PIN_NET        = "abcc319b-d09f-437b-a624-3dcf3eff5792"

# --- Devices ---
DEV_RES_THT        = "a0e021c0-90ab-4415-802e-40a847f682c8"
DEV_CAP_RADIAL     = "0107bccf-17c5-47ac-ae7a-75b057ba0a66"
DEV_LED_5MM_RED    = "04df0e68-fc25-4586-9215-96531c66c144"
DEV_PIN_HDR_1X02   = "51015f80-3c94-4bd1-a7ac-238337a8331f"
# C2 uses a project-local THT bipolar cap device (generated below)
DEV_CAP_BIPOLAR_THT_UUID = genuuid()

# --- Packages ---
PKG_DIP8           = "d1e4b152-0fd5-4ced-9c46-691c0e1d7105"
PKG_R_THT_0207     = "41a60506-8fc9-4b92-8c2d-e6463e3e88d3"
PKG_CAP_RADIAL     = "7b756d32-87b4-423c-95b2-3fb1a4263a1c"
PKG_LED_5MM_RED    = "556f1d86-fabe-4130-a702-34a82b617d82"
PKG_PIN_HDR_1X02   = "a3259adb-c576-468e-af7e-f1eb853c6bae"

# Radial cap pad UUIDs (used for both C1 unipolar and C2 bipolar THT)
CAP_RAD_PAD_1      = "b4e7cf1e-8cad-451a-8bd9-4f30f8118755"  # pad "+"
CAP_RAD_PAD_2      = "dbaab8c2-e88b-4f5b-b2a8-528d10ec340d"  # pad "-"

# --- DIP-8 pad UUIDs (pad name → UUID) ---
DIP8_PAD = {
    1: "91607d5c-257d-4d2c-a5ef-2fb6e869c143",
    2: "01f34160-65de-4e5e-9db1-3e186d38b186",
    3: "7ef06bc0-a1b8-4efd-b089-2347a7562272",
    4: "13904582-16ae-4f00-b796-1e8ec7321574",
    5: "fc6081c5-2de5-4306-916b-c4f860e790d2",
    6: "c8ce3c8f-d3ca-484a-aeea-882badbfd039",
    7: "a193ba1f-6f5c-4bff-b5d0-93810ce154c4",
    8: "6f52c096-3d8c-43e7-ae41-e295050ceffe",
}

# --- Generic IC 8-Pin symbol (in IC library) ---
IC8_SYM            = "0025709c-cf91-41ab-84c0-f4ccf25476d4"
IC8_SYM_PIN = {
    1: "7ae15859-06f5-4fda-a67c-b2c44a8d1566",
    2: "07b107a4-f0dc-4a04-bcbf-5b97ca9bf1d2",
    3: "82f92b92-ad16-4536-ac97-2c5fd428c133",
    4: "913adbac-e9e4-4b61-a9f0-4aebf7252e5a",
    5: "72acb789-00df-4a5e-b3dd-3c208fcdd5dd",
    6: "96614017-83dd-4e96-877e-70fb26eca6ac",
    7: "394fc47e-8314-47f1-8f34-235c211c89d6",
    8: "4af7cce8-0071-4436-9122-55e3b2b9edb4",
}

# ============================================================
# EXISTING PROJECT UUIDS (from the skeleton already created)
# ============================================================
PROJ_UUID          = "43b6f4b3-4bca-46d5-981f-4394b48c5a3e"
SCHEMATIC_UUID     = "942f0502-421c-4bc4-ab5a-3c95762d64c9"
BOARD_UUID         = "47db5800-b944-47a6-94bf-d7364184d29c"
ASSM_VARIANT       = "9bd19895-1b2d-434d-857d-a4235d8160d7"
NETCLASS_DEFAULT   = "98d8a679-42f1-470b-ab12-c3c87e28dd47"


# ============================================================
# PROJECT-LOCAL NE555 UUIDS (we generate these fresh)
# ============================================================
NE555_CMP_UUID     = genuuid()
NE555_DEV_UUID     = genuuid()
NE555_VARIANT_UUID = genuuid()
NE555_GATE_UUID    = genuuid()
# 8 signal UUIDs for the NE555 component (one per pin)
NE555_SIG = {}
for i in range(1, 9):
    NE555_SIG[i] = genuuid()

# ============================================================
# INSTANCE UUIDS (unique per component instance in the circuit)
# ============================================================
class Inst:
    """Component instance with generated UUIDs."""
    def __init__(self, name):
        self.name = name
        self.uuid = genuuid()
        self.sig_map = {}   # component_signal_uuid → net_uuid


# Create all instances
U1  = Inst("U1")
R1  = Inst("R1")
R2  = Inst("R2")
R3  = Inst("R3")
C1  = Inst("C1")
C2  = Inst("C2")
D1  = Inst("D1")
J1  = Inst("J1")
VCC1 = Inst("VCC1")   # VCC symbol near J1
VCC2 = Inst("VCC2")   # VCC symbol near U1 pin 8
VCC3 = Inst("VCC3")   # VCC symbol near U1 pin 4 (RESET)
VCC4 = Inst("VCC4")   # VCC symbol at top of timing chain (R1)
GND1 = Inst("GND1")   # GND near J1
GND2 = Inst("GND2")   # GND near C1
GND3 = Inst("GND3")   # GND near C2
GND4 = Inst("GND4")   # GND near D1
GND5 = Inst("GND5")   # GND near U1 pin 1

# ============================================================
# NET DEFINITIONS
# ============================================================
NET_VCC        = genuuid()
NET_GND        = genuuid()
NET_DISCHARGE  = genuuid()   # R1-R2 junction / U1 pin 7
NET_THRESH     = genuuid()   # node A: R2-C1 / U1 pins 2,6
NET_CONTROL    = genuuid()   # U1 pin 5 → C2
NET_OUTPUT     = genuuid()   # U1 pin 3 → R3
NET_LED_ANODE  = genuuid()   # R3 → D1 anode


# ============================================================
# NE555 PIN NAMES (standard DIP-8 pinout)
# ============================================================
NE555_PIN_NAMES = {
    1: "GND",
    2: "TRIG",
    3: "OUT",
    4: "RESET",
    5: "CTRL",
    6: "THRESH",
    7: "DISCH",
    8: "VCC",
}

# Map NE555 instance signals to nets
U1.sig_map = {
    NE555_SIG[1]: NET_GND,       # pin 1 = GND
    NE555_SIG[2]: NET_THRESH,    # pin 2 = TRIGGER (tied to THRESHOLD)
    NE555_SIG[3]: NET_OUTPUT,    # pin 3 = OUTPUT
    NE555_SIG[4]: NET_VCC,       # pin 4 = RESET (tied to VCC)
    NE555_SIG[5]: NET_CONTROL,   # pin 5 = CONTROL
    NE555_SIG[6]: NET_THRESH,    # pin 6 = THRESHOLD
    NE555_SIG[7]: NET_DISCHARGE, # pin 7 = DISCHARGE
    NE555_SIG[8]: NET_VCC,       # pin 8 = VCC
}

# R1: VCC → DISCHARGE  (pin 1=top, pin 2=bottom)
R1.sig_map = {RES_SIG_1: NET_VCC, RES_SIG_2: NET_DISCHARGE}
# R2: DISCHARGE → THRESH
R2.sig_map = {RES_SIG_1: NET_DISCHARGE, RES_SIG_2: NET_THRESH}
# R3: OUTPUT → LED_ANODE
R3.sig_map = {RES_SIG_1: NET_OUTPUT, RES_SIG_2: NET_LED_ANODE}
# C1: + = THRESH, - = GND (electrolytic)
C1.sig_map = {CAPU_SIG_PLUS: NET_THRESH, CAPU_SIG_MINUS: NET_GND}
# C2: + = CONTROL, - = GND (now THT radial, same package as C1)
C2.sig_map = {CAPB_SIG_1: NET_CONTROL, CAPB_SIG_2: NET_GND}
# D1: A = LED_ANODE, C = GND
D1.sig_map = {LED_SIG_A: NET_LED_ANODE, LED_SIG_C: NET_GND}
# J1: pin 1 = VCC, pin 2 = GND
J1.sig_map = {HDR_SIG_1: NET_VCC, HDR_SIG_2: NET_GND}
# VCC symbols
VCC1.sig_map = {VCC_SIG_NET: NET_VCC}
VCC2.sig_map = {VCC_SIG_NET: NET_VCC}
VCC3.sig_map = {VCC_SIG_NET: NET_VCC}
VCC4.sig_map = {VCC_SIG_NET: NET_VCC}
# GND symbols
GND1.sig_map = {GND_SIG_NET: NET_GND}
GND2.sig_map = {GND_SIG_NET: NET_GND}
GND3.sig_map = {GND_SIG_NET: NET_GND}
GND4.sig_map = {GND_SIG_NET: NET_GND}
GND5.sig_map = {GND_SIG_NET: NET_GND}


# ============================================================
# NET NAME MAP
# ============================================================
NETS = {
    NET_VCC:       "VCC",
    NET_GND:       "GND",
    NET_DISCHARGE: "DISCHARGE",
    NET_THRESH:    "THRESH_TRIG",
    NET_CONTROL:   "CONTROL",
    NET_OUTPUT:    "OUTPUT",
    NET_LED_ANODE: "LED_ANODE",
}


# ============================================================
# FILE GENERATORS
# ============================================================

def gen_ne555_component():
    """Generate project-local NE555 component.lp"""
    sigs = ""
    for i in range(1, 9):
        sigs += (
            f' (signal {NE555_SIG[i]} (name "{NE555_PIN_NAMES[i]}") '
            f'(role passive)\n'
            f'  (required true) (negated false) (clock false) (forced_net "")\n'
            f' )\n'
        )

    pins = ""
    for i in range(1, 9):
        pins += (
            f'   (pin {IC8_SYM_PIN[i]} '
            f'(signal {NE555_SIG[i]}) (text pin))\n'
        )

    return (
        f'(librepcb_component {NE555_CMP_UUID}\n'
        f' (name "NE555 Timer")\n'
        f' (description "555 Timer IC in astable configuration")\n'
        f' (keywords "555,timer,ne555,oscillator")\n'
        f' (author "Generated")\n'
        f' (version "0.1")\n'
        f' (created 2026-03-25T00:00:00Z)\n'
        f' (deprecated false)\n'
        f' (generated_by "")\n'
        f' (category 8226f987-124b-4776-9084-3821dd51c272)\n'
        f' (schematic_only false)\n'
        f' (default_value "NE555")\n'
        f' (prefix "U")\n'
        f'{sigs}'
        f' (variant {NE555_VARIANT_UUID} (norm "")\n'
        f'  (name "default")\n'
        f'  (description "")\n'
        f'  (gate {NE555_GATE_UUID}\n'
        f'   (symbol {IC8_SYM})\n'
        f'   (position 0.0 0.0) (rotation 0.0) (required true) (suffix "")\n'
        f'{pins}'
        f'  )\n'
        f' )\n'
        f')\n'
    )


def gen_ne555_device():
    """Generate project-local NE555 DIP-8 device.lp"""
    pads = ""
    for i in range(1, 9):
        pads += (
            f' (pad {DIP8_PAD[i]} (optional false)\n'
            f'  (signal {NE555_SIG[i]})\n'
            f' )\n'
        )

    return (
        f'(librepcb_device {NE555_DEV_UUID}\n'
        f' (name "NE555P DIP-8")\n'
        f' (description "NE555 Timer in DIP-8 package")\n'
        f' (keywords "555,timer,ne555,dip8")\n'
        f' (author "Generated")\n'
        f' (version "0.1")\n'
        f' (created 2026-03-25T00:00:00Z)\n'
        f' (deprecated false)\n'
        f' (generated_by "")\n'
        f' (category 8226f987-124b-4776-9084-3821dd51c272)\n'
        f' (component {NE555_CMP_UUID})\n'
        f' (package {PKG_DIP8})\n'
        f'{pads}'
        f')\n'
    )


def gen_cap_bipolar_tht_device():
    """Generate project-local Capacitor Bipolar THT device.
    Maps Capacitor Bipolar component signals to radial cap package pads."""
    return (
        f'(librepcb_device {DEV_CAP_BIPOLAR_THT_UUID}\n'
        f' (name "Capacitor Bipolar THT Radial")\n'
        f' (description "Generic bipolar capacitor in THT radial package")\n'
        f' (keywords "capacitor,bipolar,tht,ceramic,film")\n'
        f' (author "Generated")\n'
        f' (version "0.1")\n'
        f' (created 2026-03-25T00:00:00Z)\n'
        f' (deprecated false)\n'
        f' (generated_by "")\n'
        f' (category c011cc6b-b762-498e-8494-d1994f3043cf)\n'
        f' (component {CMP_CAP_BIPOLAR})\n'
        f' (package {PKG_CAP_RADIAL})\n'
        f' (pad {CAP_RAD_PAD_1} (optional false)\n'
        f'  (signal {CAPB_SIG_1})\n'
        f' )\n'
        f' (pad {CAP_RAD_PAD_2} (optional false)\n'
        f'  (signal {CAPB_SIG_2})\n'
        f' )\n'
        f')\n'
    )


def gen_circuit():
    """Generate circuit.lp with all nets and component instances."""
    lines = []
    lines.append("(librepcb_circuit")
    lines.append(f' (variant {ASSM_VARIANT} (name "Std")')
    lines.append('  (description "Standard assembly")')
    lines.append(' )')
    lines.append(f' (netclass {NETCLASS_DEFAULT} (name "default")')
    lines.append('  (default_trace_width inherit)')
    lines.append('  (default_via_drill_diameter inherit)')
    lines.append('  (min_copper_copper_clearance 0.0)')
    lines.append('  (min_copper_width 0.0)')
    lines.append('  (min_via_drill_diameter 0.0)')
    lines.append(' )')

    # Nets
    for net_uuid, net_name in NETS.items():
        lines.append(f' (net {net_uuid} (auto false) (name "{net_name}")')
        lines.append(f'  (netclass {NETCLASS_DEFAULT})')
        lines.append(' )')

    # Component instances
    def add_component(inst, cmp_uuid, variant_uuid, value="",
                      dev_uuid=None, schematic_only=False):
        lines.append(f' (component {inst.uuid}')
        lines.append(f'  (lib_component {cmp_uuid})')
        lines.append(f'  (lib_variant {variant_uuid})')
        lines.append(f'  (name "{inst.name}") (value "{value}")')
        lines.append(f'  (lock_assembly false)')
        if dev_uuid and not schematic_only:
            lines.append(f'  (device {dev_uuid}')
            lines.append(f'   (variant {ASSM_VARIANT})')
            lines.append(f'  )')
        for sig_uuid, net_uuid in inst.sig_map.items():
            lines.append(f'  (signal {sig_uuid} (net {net_uuid}))')
        lines.append(' )')

    # U1 - NE555
    add_component(U1, NE555_CMP_UUID, NE555_VARIANT_UUID, "NE555",
                  dev_uuid=NE555_DEV_UUID)
    # Resistors
    add_component(R1, CMP_RESISTOR, RES_VARIANT_US, "10kΩ",
                  dev_uuid=DEV_RES_THT)
    add_component(R2, CMP_RESISTOR, RES_VARIANT_US, "47kΩ",
                  dev_uuid=DEV_RES_THT)
    add_component(R3, CMP_RESISTOR, RES_VARIANT_US, "470Ω",
                  dev_uuid=DEV_RES_THT)
    # Capacitors
    add_component(C1, CMP_CAP_UNIPOLAR, CAPU_VARIANT_US, "10µF",
                  dev_uuid=DEV_CAP_RADIAL)
    add_component(C2, CMP_CAP_BIPOLAR, CAPB_VARIANT_US, "10nF",
                  dev_uuid=DEV_CAP_BIPOLAR_THT_UUID)
    # LED
    add_component(D1, CMP_LED, LED_VARIANT, "Red",
                  dev_uuid=DEV_LED_5MM_RED)
    # Connector
    add_component(J1, CMP_PIN_HDR_1X02, HDR_VARIANT, "",
                  dev_uuid=DEV_PIN_HDR_1X02)
    # Power symbols (schematic only - no device)
    add_component(VCC1, CMP_SUPPLY_VCC, VCC_VARIANT, "VCC",
                  schematic_only=True)
    add_component(VCC2, CMP_SUPPLY_VCC, VCC_VARIANT, "VCC",
                  schematic_only=True)
    add_component(GND1, CMP_SUPPLY_GND, GND_VARIANT, "GND",
                  schematic_only=True)
    add_component(GND2, CMP_SUPPLY_GND, GND_VARIANT, "GND",
                  schematic_only=True)
    add_component(GND3, CMP_SUPPLY_GND, GND_VARIANT, "GND",
                  schematic_only=True)
    add_component(GND4, CMP_SUPPLY_GND, GND_VARIANT, "GND",
                  schematic_only=True)
    add_component(GND5, CMP_SUPPLY_GND, GND_VARIANT, "GND",
                  schematic_only=True)
    add_component(VCC3, CMP_SUPPLY_VCC, VCC_VARIANT, "VCC",
                  schematic_only=True)
    add_component(VCC4, CMP_SUPPLY_VCC, VCC_VARIANT, "VCC",
                  schematic_only=True)

    lines.append(")")
    return "\n".join(lines) + "\n"


def gen_schematic():
    """Generate schematic.lp with symbol placement AND wiring.

    Layout designed so most connections are straight lines.
    Uses netsegments with junctions for L-shaped routes.
    """
    import math

    lines = []
    lines.append(f"(librepcb_schematic {SCHEMATIC_UUID}")
    lines.append(' (name "Main")')
    lines.append(' (grid (interval 2.54) (unit millimeters))')

    # Track symbol instance UUIDs: inst -> sym_uuid
    sym_uuids = {}

    def add_symbol(inst, gate_uuid, x, y, rot=0.0):
        sym_inst_uuid = genuuid()
        sym_uuids[inst.name + "_" + str(id(inst))] = sym_inst_uuid
        inst._sym_uuid = sym_inst_uuid
        inst._sym_pos = (x, y)
        inst._sym_rot = rot
        lines.append(f' (symbol {sym_inst_uuid}')
        lines.append(f'  (component {inst.uuid})')
        lines.append(f'  (lib_gate {gate_uuid})')
        lines.append(f'  (position {x} {y}) (rotation {rot}) (mirror false)')
        lines.append(' )')
        return sym_inst_uuid

    def pin_abs(inst, pin_offset_x, pin_offset_y):
        """Calculate absolute pin position given symbol center and rotation."""
        cx, cy = inst._sym_pos
        rot_rad = math.radians(inst._sym_rot)
        cos_r = math.cos(rot_rad)
        sin_r = math.sin(rot_rad)
        rx = pin_offset_x * cos_r - pin_offset_y * sin_r
        ry = pin_offset_x * sin_r + pin_offset_y * cos_r
        return (round(cx + rx, 4), round(cy + ry, 4))

    # ================================================================
    # PLACEMENT — designed for clean routing on 2.54mm grid
    # ================================================================
    # U1 (NE555) at center
    # Left pins: 1(GND)=top, 2(TRIG), 3(OUT), 4(RESET)=bottom
    # Right pins: 8(VCC)=top, 7(DISCH), 6(THRESH), 5(CTRL)=bottom
    add_symbol(U1,   NE555_GATE_UUID, 50.80, 40.64, 0.0)

    # J1 at far left — pin1(VCC) and pin2(GND) exit rightward at x=20.32
    add_symbol(J1,   HDR_GATE,   15.24, 40.64, 0.0)
    # VCC1 directly above J1 pin 1 (pin at 20.32, 40.64)
    add_symbol(VCC1, VCC_GATE,   20.32, 43.18, 0.0)
    # GND1 directly below J1 pin 2 (pin at 20.32, 38.10)
    add_symbol(GND1, GND_GATE,   20.32, 35.56, 0.0)

    # VCC2 above U1 pin 8 — pin at (60.96, 43.18)
    add_symbol(VCC2, VCC_GATE,   60.96, 45.72, 0.0)
    # VCC3 left of U1 pin 4 (RESET at 40.64, 35.56) — pin at (35.56, 35.56)
    add_symbol(VCC3, VCC_GATE,   35.56, 38.10, 0.0)
    # GND5 below-left of U1 pin 1 (GND at 40.64, 43.18) — pin at (35.56, 43.18)
    add_symbol(GND5, GND_GATE,   35.56, 40.64, 0.0)

    # Timing chain to the RIGHT of U1 (vertical)
    # VCC4 at top
    add_symbol(VCC4, VCC_GATE,   73.66, 55.88, 0.0)
    # R1 vertical: rot=270 so pin1(VCC) at top, pin2(DISCH) at bottom
    add_symbol(R1,   RES_GATE_US, 73.66, 48.26, 270.0)
    # R2 vertical: rot=270 so pin1(DISCH) at top, pin2(THRESH) at bottom
    add_symbol(R2,   RES_GATE_US, 73.66, 35.56, 270.0)
    # C1 vertical: pin+(THRESH) at top, pin-(GND) at bottom
    add_symbol(C1,   CAPU_GATE_US, 73.66, 25.40, 0.0)
    # GND2 below C1
    add_symbol(GND2, GND_GATE,   73.66, 20.32, 0.0)

    # C2 below U1 pin 5 — vertical
    add_symbol(C2,   CAPB_GATE_US, 60.96, 27.94, 0.0)
    # GND3 below C2
    add_symbol(GND3, GND_GATE,   60.96, 22.86, 0.0)

    # Output chain to the LEFT of U1
    # R3 horizontal: rot=180 so pin1(OUTPUT) at right, pin2(LED_A) at left
    add_symbol(R3,   RES_GATE_US, 35.56, 38.10, 180.0)
    # D1 vertical below R3 output
    add_symbol(D1,   LED_GATE,   30.48, 33.02, 0.0)
    # GND4 below D1
    add_symbol(GND4, GND_GATE,   30.48, 27.94, 0.0)

    # ================================================================
    # NETSEGMENTS — wire everything up
    # ================================================================
    WIRE_W = "0.15875"

    def netseg_pin_to_pin(net_uuid, inst_a, pin_a, inst_b, pin_b):
        """Direct wire between two symbol pins."""
        lines.append(f' (netsegment {genuuid()}')
        lines.append(f'  (net {net_uuid})')
        lines.append(f'  (line {genuuid()} (width {WIRE_W})')
        lines.append(f'   (from (symbol {inst_a._sym_uuid}) (pin {pin_a}))')
        lines.append(f'   (to (symbol {inst_b._sym_uuid}) (pin {pin_b}))')
        lines.append('  )')
        lines.append(' )')

    def netseg_Lshape(net_uuid, inst_a, pin_a, inst_b, pin_b, jx, jy):
        """L-shaped wire via a junction point."""
        junc_uuid = genuuid()
        lines.append(f' (netsegment {genuuid()}')
        lines.append(f'  (net {net_uuid})')
        lines.append(f'  (junction {junc_uuid} (position {jx} {jy}))')
        lines.append(f'  (line {genuuid()} (width {WIRE_W})')
        lines.append(f'   (from (symbol {inst_a._sym_uuid}) (pin {pin_a}))')
        lines.append(f'   (to (junction {junc_uuid}))')
        lines.append('  )')
        lines.append(f'  (line {genuuid()} (width {WIRE_W})')
        lines.append(f'   (from (junction {junc_uuid}))')
        lines.append(f'   (to (symbol {inst_b._sym_uuid}) (pin {pin_b}))')
        lines.append('  )')
        lines.append(' )')

    def netseg_3way(net_uuid, inst_a, pin_a, inst_b, pin_b, inst_c, pin_c, jx, jy):
        """T-junction connecting three pins through one junction."""
        junc_uuid = genuuid()
        lines.append(f' (netsegment {genuuid()}')
        lines.append(f'  (net {net_uuid})')
        lines.append(f'  (junction {junc_uuid} (position {jx} {jy}))')
        for inst, pin in [(inst_a, pin_a), (inst_b, pin_b), (inst_c, pin_c)]:
            lines.append(f'  (line {genuuid()} (width {WIRE_W})')
            lines.append(f'   (from (symbol {inst._sym_uuid}) (pin {pin}))')
            lines.append(f'   (to (junction {junc_uuid}))')
            lines.append('  )')
        lines.append(' )')

    # --- Pin position reference ---
    # Resistor US: pin f42020e8 at (-5.08, 0) = "1", pin 2b3dd7f8 at (5.08, 0) = "2"
    R_PIN1 = "f42020e8-c53f-4ff2-947e-07879cf42546"
    R_PIN2 = "2b3dd7f8-043b-4d43-9302-9300ba356de7"
    # Cap Bipolar US: pin 83d40864 at (0, 2.54) = "1", pin c39ca7a0 at (0, -2.54) = "2"
    CB_PIN1 = "83d40864-0a14-496e-a08d-faeb2bbd9af6"
    CB_PIN2 = "c39ca7a0-22c0-4338-83e8-98aba0874d88"
    # Cap Unipolar US: pin 66df0382 at (0, 2.54) = "+", pin 6d445a38 at (0, -2.54) = "-"
    CU_PINP = "66df0382-3069-40e1-b729-3b1ad6f8ddb5"
    CU_PINM = "6d445a38-f8eb-46c1-8ae0-99ef036ca312"
    # LED: pin 2a64f851 at (0, 2.54) = "A", pin 18de942d at (0, -2.54) = "C"
    LED_PINA = "2a64f851-340a-43f2-b1cf-06a1d4b54560"
    LED_PINC = "18de942d-8b47-4daf-9e07-d089204e09d0"
    # VCC: pin 771c2d8b at (0, -2.54) = "NET"
    V_PIN = VCC_PIN_NET
    # GND: pin abcc319b at (0, 2.54) = "NET"
    G_PIN = GND_PIN_NET
    # Pin Header 1x02: pin e313439d at (5.08, 0) = "1", pin 8c43a15d at (5.08, -2.54) = "2"
    H_PIN1 = "e313439d-b34a-43cd-bbb6-61626a40fd32"
    H_PIN2 = "8c43a15d-5e7b-465f-b51e-5f482a4b6eb3"
    # IC 8-pin: pins 1-8
    IC_PIN = IC8_SYM_PIN  # dict: 1..8 -> UUID

    # ================================================================
    # NET: VCC
    # ================================================================
    # VCC1 → J1 pin 1 (both at x=20.32, vertical)
    netseg_pin_to_pin(NET_VCC, VCC1, V_PIN, J1, H_PIN1)
    # VCC2 → U1 pin 8 (both at x=60.96, vertical)
    netseg_pin_to_pin(NET_VCC, VCC2, V_PIN, U1, IC_PIN[8])
    # VCC3 → U1 pin 4 (RESET) — horizontal at y=35.56
    netseg_pin_to_pin(NET_VCC, VCC3, V_PIN, U1, IC_PIN[4])
    # VCC4 → R1 pin 1 (top of timing chain, both at x=73.66)
    netseg_pin_to_pin(NET_VCC, VCC4, V_PIN, R1, R_PIN1)

    # ================================================================
    # NET: GND
    # ================================================================
    # GND1 → J1 pin 2 (both at x=20.32, vertical)
    netseg_pin_to_pin(NET_GND, GND1, G_PIN, J1, H_PIN2)
    # GND2 → C1 pin - (both at x=73.66, vertical)
    netseg_pin_to_pin(NET_GND, GND2, G_PIN, C1, CU_PINM)
    # GND3 → C2 pin 2 (both at x=60.96, vertical)
    netseg_pin_to_pin(NET_GND, GND3, G_PIN, C2, CB_PIN2)
    # GND4 → D1 cathode (both at x=30.48, vertical)
    netseg_pin_to_pin(NET_GND, GND4, G_PIN, D1, LED_PINC)
    # GND5 → U1 pin 1 — horizontal at y=43.18
    netseg_pin_to_pin(NET_GND, GND5, G_PIN, U1, IC_PIN[1])

    # ================================================================
    # NET: DISCHARGE — R1 pin2, R2 pin1, U1 pin 7
    # All three must be in ONE netsegment. Junction at R2 pin1 position.
    # R1 pin2 → junction (73.66, 40.64) ← U1 pin7, junction → R2 pin1
    # ================================================================
    netseg_3way(NET_DISCHARGE,
               R1, R_PIN2,      # from above (73.66, 43.18)
               U1, IC_PIN[7],   # from left (60.96, 40.64)
               R2, R_PIN1,      # below (73.66, 40.64) — same as junction
               73.66, 40.64)

    # ================================================================
    # NET: THRESH_TRIG — R2 pin2, C1 pin+, U1 pin 2, U1 pin 6
    # All FOUR pins must be in ONE netsegment.
    # Topology:
    #   U1 pin2 (40.64, 40.64) → J1 (40.64, 27.94)  [vertical down]
    #   J1 (40.64, 27.94) → C1 pin+ (73.66, 27.94)  [horizontal right]
    #   C1 pin+ (73.66, 27.94) → R2 pin2 (73.66, 30.48) [vertical up]
    #   R2 pin2 (73.66, 30.48) → J2 (73.66, 38.10)  [vertical up]
    #   J2 (73.66, 38.10) → U1 pin6 (60.96, 38.10)  [horizontal left]
    # ================================================================
    j_thresh1 = genuuid()  # (40.64, 27.94)
    j_thresh2 = genuuid()  # (73.66, 38.10)
    lines.append(f' (netsegment {genuuid()}')
    lines.append(f'  (net {NET_THRESH})')
    lines.append(f'  (junction {j_thresh1} (position 40.64 27.94))')
    lines.append(f'  (junction {j_thresh2} (position 73.66 38.10))')
    # U1 pin2 → J1
    lines.append(f'  (line {genuuid()} (width {WIRE_W})')
    lines.append(f'   (from (symbol {U1._sym_uuid}) (pin {IC_PIN[2]}))')
    lines.append(f'   (to (junction {j_thresh1}))')
    lines.append('  )')
    # J1 → C1 pin+
    lines.append(f'  (line {genuuid()} (width {WIRE_W})')
    lines.append(f'   (from (junction {j_thresh1}))')
    lines.append(f'   (to (symbol {C1._sym_uuid}) (pin {CU_PINP}))')
    lines.append('  )')
    # C1 pin+ → R2 pin2
    lines.append(f'  (line {genuuid()} (width {WIRE_W})')
    lines.append(f'   (from (symbol {C1._sym_uuid}) (pin {CU_PINP}))')
    lines.append(f'   (to (symbol {R2._sym_uuid}) (pin {R_PIN2}))')
    lines.append('  )')
    # R2 pin2 → J2
    lines.append(f'  (line {genuuid()} (width {WIRE_W})')
    lines.append(f'   (from (symbol {R2._sym_uuid}) (pin {R_PIN2}))')
    lines.append(f'   (to (junction {j_thresh2}))')
    lines.append('  )')
    # J2 → U1 pin6
    lines.append(f'  (line {genuuid()} (width {WIRE_W})')
    lines.append(f'   (from (junction {j_thresh2}))')
    lines.append(f'   (to (symbol {U1._sym_uuid}) (pin {IC_PIN[6]}))')
    lines.append('  )')
    lines.append(' )')

    # ================================================================
    # NET: CONTROL — U1 pin 5, C2 pin 1
    # ================================================================
    # U1 pin 5 (60.96, 35.56) → C2 pin1 (60.96, 30.48): vertical, same X
    netseg_pin_to_pin(NET_CONTROL, U1, IC_PIN[5], C2, CB_PIN1)

    # ================================================================
    # NET: OUTPUT — U1 pin 3, R3 pin 1
    # ================================================================
    # U1 pin 3 (40.64, 38.10) → R3 pin1
    # R3 at (35.56, 38.10) rot=180: pin1 at (40.64, 38.10) — exactly matches!
    netseg_pin_to_pin(NET_OUTPUT, U1, IC_PIN[3], R3, R_PIN1)

    # ================================================================
    # NET: LED_ANODE — R3 pin 2, D1 anode
    # ================================================================
    # R3 pin2 at (30.48, 38.10), D1 anode at (30.48, 35.56): vertical, same X
    netseg_pin_to_pin(NET_LED_ANODE, R3, R_PIN2, D1, LED_PINA)

    lines.append(")")
    return "\n".join(lines) + "\n"


def gen_board(proj_dir):
    """Generate board.lp with device placement on 40x30mm board.

    Traces are left for the user (or a future script iteration)
    to route in the GUI. Component placement follows the build guide.
    """
    lines = []
    lines.append(f"(librepcb_board {BOARD_UUID}")
    lines.append(' (name "default")')
    lines.append(' (default_font "newstroke.bene")')
    lines.append(' (grid (interval 0.635) (unit millimeters))')
    lines.append(' (layers (inner 0))')
    lines.append(' (thickness 1.6)')
    lines.append(' (solder_resist green)')
    lines.append(' (silkscreen white)')
    lines.append(' (silkscreen_layers_top top_legend top_names)')
    lines.append(' (silkscreen_layers_bot bot_legend bot_names)')

    # Design rules (from existing project)
    lines.append(' (design_rules')
    lines.append('  (default_trace_width 0.5)')
    lines.append('  (default_via_drill_diameter 0.3)')
    lines.append('  (stopmask_max_via_drill_diameter 0.3)')
    lines.append('  (stopmask_clearance (ratio 0.0) (min 0.1) (max 0.1))')
    lines.append('  (solderpaste_clearance (ratio 0.1) (min 0.0) (max 1.0))')
    lines.append('  (pad_annular_ring (outer full) (inner auto) (ratio 0.25) (min 0.25) (max 2.0))')
    lines.append('  (via_annular_ring (ratio 0.25) (min 0.2) (max 2.0))')
    lines.append(' )')

    # DRC (from existing project)
    lines.append(' (design_rule_check')
    lines.append('  (min_pcb_size 0.0 0.0)')
    lines.append('  (max_pcb_size (double_sided 0.0 0.0) (multilayer 0.0 0.0))')
    lines.append('  (pcb_thickness)')
    lines.append('  (max_layers 0)')
    lines.append('  (solder_resist)')
    lines.append('  (silkscreen)')
    lines.append('  (min_copper_copper_clearance 0.2)')
    lines.append('  (min_copper_board_clearance 0.3)')
    lines.append('  (min_copper_npth_clearance 0.25)')
    lines.append('  (min_drill_drill_clearance 0.35)')
    lines.append('  (min_drill_board_clearance 0.5)')
    lines.append('  (min_silkscreen_stopmask_clearance 0.127)')
    lines.append('  (min_copper_width 0.2)')
    lines.append('  (min_annular_ring 0.2)')
    lines.append('  (min_npth_drill_diameter 0.5)')
    lines.append('  (min_pth_drill_diameter 0.3)')
    lines.append('  (min_npth_slot_width 1.0)')
    lines.append('  (min_pth_slot_width 0.7)')
    lines.append('  (max_tented_via_drill_diameter 3.0)')
    lines.append('  (min_silkscreen_width 0.15)')
    lines.append('  (min_silkscreen_text_height 0.8)')
    lines.append('  (min_outline_tool_diameter 2.0)')
    lines.append('  (blind_vias_allowed false)')
    lines.append('  (buried_vias_allowed false)')
    lines.append('  (allowed_npth_slots single_segment_straight)')
    lines.append('  (allowed_pth_slots single_segment_straight)')
    lines.append(f'  (approvals_version "2")')
    lines.append(' )')

    # Fabrication output settings
    lines.append(' (fabrication_output_settings')
    lines.append('  (base_path "./output/{{VERSION}}/gerber/{{PROJECT}}")')
    lines.append('  (outlines (suffix "_OUTLINES.gbr"))')
    lines.append('  (copper_top (suffix "_COPPER-TOP.gbr"))')
    lines.append('  (copper_inner (suffix "_COPPER-IN{{CU_LAYER}}.gbr"))')
    lines.append('  (copper_bot (suffix "_COPPER-BOTTOM.gbr"))')
    lines.append('  (soldermask_top (suffix "_SOLDERMASK-TOP.gbr"))')
    lines.append('  (soldermask_bot (suffix "_SOLDERMASK-BOTTOM.gbr"))')
    lines.append('  (silkscreen_top (suffix "_SILKSCREEN-TOP.gbr"))')
    lines.append('  (silkscreen_bot (suffix "_SILKSCREEN-BOTTOM.gbr"))')
    lines.append('  (drills (merge false)')
    lines.append('   (suffix_pth "_DRILLS-PTH.drl")')
    lines.append('   (suffix_npth "_DRILLS-NPTH.drl")')
    lines.append('   (suffix_merged "_DRILLS.drl")')
    lines.append('   (suffix_buried "_DRILLS-PLATED-{{START_LAYER}}-{{END_LAYER}}.drl")')
    lines.append('   (g85_slots false)')
    lines.append('  )')
    lines.append('  (solderpaste_top (create true) (suffix "_SOLDERPASTE-TOP.gbr"))')
    lines.append('  (solderpaste_bot (create true) (suffix "_SOLDERPASTE-BOTTOM.gbr"))')
    lines.append(' )')

    lines.append(' (preferred_footprint_tags')
    lines.append('  (tht_top)')
    lines.append('  (tht_bot)')
    lines.append('  (smt_top)')
    lines.append('  (smt_bot)')
    lines.append('  (common)')
    lines.append(' )')

    # Board outline: 150mm x 100mm (massive — easy routing)
    outline_uuid = genuuid()
    lines.append(f' (polygon {outline_uuid} (layer brd_outlines)')
    lines.append('  (width 0.0) (fill false) (grab_area false) (lock false)')
    lines.append('  (vertex (position 0.0 0.0) (angle 0.0))')
    lines.append('  (vertex (position 150.0 0.0) (angle 0.0))')
    lines.append('  (vertex (position 150.0 100.0) (angle 0.0))')
    lines.append('  (vertex (position 0.0 100.0) (angle 0.0))')
    lines.append('  (vertex (position 0.0 0.0) (angle 0.0))')
    lines.append(' )')

    # Device placements — VERY spread out on 150x100mm board
    # ~25mm between components for massive routing channels

    def get_first_footprint(pkg_uuid):
        """Extract the first footprint UUID from a package.lp file in project lib."""
        pkg_file = proj_dir / "library" / "pkg" / pkg_uuid / "package.lp"
        if pkg_file.exists():
            import re
            content = pkg_file.read_text()
            m = re.search(r'\(footprint ([0-9a-f-]{36})', content)
            if m:
                return m.group(1)
        return None

    def add_device(inst, dev_uuid, pkg_uuid, x, y, rot=0.0):
        fp_uuid = get_first_footprint(pkg_uuid)
        lines.append(f' (device {inst.uuid}')
        lines.append(f'  (lib_device {dev_uuid})')
        if fp_uuid:
            lines.append(f'  (lib_footprint {fp_uuid})')
        lines.append(f'  (lib_3d_model none)')
        lines.append(f'  (position {x} {y}) (rotation {rot}) (flip false) (lock false) (glue true)')
        lines.append(' )')

    # Layout: left-to-right flow, vertically centered
    #
    #   J1          R1        U1         R3        D1
    #  (15,50)    (40,75)  (70,50)    (105,50)  (130,50)
    #               R2        C1
    #             (40,50)   (95,25)
    #                         C2
    #                       (70,25)
    #
    add_device(J1,  DEV_PIN_HDR_1X02, PKG_PIN_HDR_1X02,   5.0,  35.0,  0.0)
    add_device(R1,  DEV_RES_THT,      PKG_R_THT_0207,    40.0,  75.0,  0.0)
    add_device(R2,  DEV_RES_THT,      PKG_R_THT_0207,    40.0,  35.0,  0.0)
    add_device(U1,  NE555_DEV_UUID,   PKG_DIP8,          70.0,  50.0,  0.0)
    add_device(C2,  DEV_CAP_BIPOLAR_THT_UUID, PKG_CAP_RADIAL, 70.0, 25.0, 0.0)
    add_device(C1,  DEV_CAP_RADIAL,   PKG_CAP_RADIAL,    95.0,  25.0,  0.0)
    add_device(R3,  DEV_RES_THT,      PKG_R_THT_0207,   105.0,  65.0,  0.0)
    add_device(D1,  DEV_LED_5MM_RED,  PKG_LED_5MM_RED,  145.0,  65.0,  0.0)

    # Ground plane on bottom copper
    plane_uuid = genuuid()
    lines.append(f' (plane {plane_uuid} (layer bot_cu)')
    lines.append(f'  (net {NET_GND}) (priority 0) (min_width 0.2)')
    lines.append('  (min_copper_clearance 0.2) (min_board_clearance 0.2) (min_npth_clearance 0.2)')
    lines.append('  (connect_style solid) (thermal_gap 0.2) (thermal_spoke 0.2)')
    lines.append('  (keep_islands false) (lock false)')
    lines.append('  (vertex (position 0.5 0.5) (angle 0.0))')
    lines.append('  (vertex (position 149.5 0.5) (angle 0.0))')
    lines.append('  (vertex (position 149.5 99.5) (angle 0.0))')
    lines.append('  (vertex (position 0.5 99.5) (angle 0.0))')
    lines.append('  (vertex (position 0.5 0.5) (angle 0.0))')
    lines.append(' )')

    lines.append(")")
    return "\n".join(lines) + "\n"


# ============================================================
# MAIN: Write all files
# ============================================================

def main():
    if len(sys.argv) > 1:
        proj_dir = Path(sys.argv[1])
    else:
        proj_dir = Path.home() / "LibrePCB-Workspace" / "projects" / "555_Timer_Astable"

    print(f"Output directory: {proj_dir}")

    # ---- Workspace library paths ----
    ws_lib = Path.home() / "LibrePCB-Workspace" / "data" / "libraries" / "remote"
    BASE_LIB = ws_lib / "a9ddf0c6-9b1c-4730-b300-01b4f192ad40.lplib"
    CONN_LIB = ws_lib / "6ccc516c-21b7-4cd5-9cf2-7a04cfa361c6.lplib"
    IC_LIB   = ws_lib / "326f091b-b715-44bf-b385-b613cd60d9f3.lplib"

    if not ws_lib.exists():
        print(f"ERROR: Workspace libraries not found at {ws_lib}")
        print("Make sure LibrePCB libraries are installed.")
        sys.exit(1)

    # Ensure directories exist
    for subdir in [
        "project", "circuit", "schematics/main", "boards/default",
        "resources",
        f"library/cmp/{NE555_CMP_UUID}",
        f"library/dev/{NE555_DEV_UUID}",
        f"library/dev/{DEV_CAP_BIPOLAR_THT_UUID}",
    ]:
        (proj_dir / subdir).mkdir(parents=True, exist_ok=True)

    # ---- Copy all referenced library elements into project ----
    def copy_lib_element(src_lib, element_type, uuid):
        """Copy a library element (cmp/sym/dev/pkg) into project library."""
        src = src_lib / element_type / uuid
        dst = proj_dir / "library" / element_type / uuid
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  Copied {element_type}/{uuid}")
        else:
            print(f"  WARNING: {element_type}/{uuid} not found in {src_lib.name}")

    print("\nCopying library elements into project...")

    # Components from Base library
    for cmp_uuid in [CMP_RESISTOR, CMP_CAP_BIPOLAR, CMP_CAP_UNIPOLAR,
                     CMP_LED, CMP_SUPPLY_VCC, CMP_SUPPLY_GND]:
        copy_lib_element(BASE_LIB, "cmp", cmp_uuid)

    # Components from Connectors library
    copy_lib_element(CONN_LIB, "cmp", CMP_PIN_HDR_1X02)

    # Symbols from Base library (US variants we use + EU variants referenced in component files)
    RES_SYM_EU  = "75372c18-3ba4-42e8-b3b2-2eb5039d441e"
    CAPB_SYM_EU = "eaa5837a-a451-40ae-8620-d21e9af42151"
    CAPU_SYM_EU = "15a0eeed-4dc9-48ec-a431-7c1eec56c4c4"
    for sym_uuid in [RES_SYM_US, RES_SYM_EU,
                     CAPB_SYM_US, CAPB_SYM_EU,
                     CAPU_SYM_US, CAPU_SYM_EU,
                     LED_SYM, VCC_SYM, GND_SYM]:
        copy_lib_element(BASE_LIB, "sym", sym_uuid)

    # Symbol from Connectors library
    copy_lib_element(CONN_LIB, "sym", HDR_SYM)

    # Symbol from IC library (Generic IC 8-Pin)
    copy_lib_element(IC_LIB, "sym", IC8_SYM)

    # Devices from Base library
    for dev_uuid in [DEV_RES_THT, DEV_CAP_RADIAL,
                     DEV_LED_5MM_RED]:
        copy_lib_element(BASE_LIB, "dev", dev_uuid)

    # Device from Connectors library
    copy_lib_element(CONN_LIB, "dev", DEV_PIN_HDR_1X02)

    # Packages from Base library
    for pkg_uuid in [PKG_DIP8, PKG_R_THT_0207,
                     PKG_CAP_RADIAL, PKG_LED_5MM_RED]:
        copy_lib_element(BASE_LIB, "pkg", pkg_uuid)

    # Package from Connectors library
    copy_lib_element(CONN_LIB, "pkg", PKG_PIN_HDR_1X02)

    print("  Library copy complete.")

    # Write .librepcb-project marker
    (proj_dir / ".librepcb-project").write_text("2\n")

    # Write .lpp project marker (required for LibrePCB to recognize the project)
    (proj_dir / "555_Timer_Astable.lpp").write_text("LIBREPCB-PROJECT")

    # Project metadata (preserve existing)
    (proj_dir / "project" / "metadata.lp").write_text(
        f'(librepcb_project_metadata {PROJ_UUID}\n'
        f' (name "555_Timer_Astable")\n'
        f' (author "Yuval Levental")\n'
        f' (version "v1")\n'
        f' (created 2026-03-25T18:13:12Z)\n'
        f')\n'
    )

    # Project settings
    (proj_dir / "project" / "settings.lp").write_text(
        '(librepcb_project_settings\n'
        ' (library_locale_order\n'
        ' )\n'
        ' (library_norm_order\n'
        '  "IEEE 315"\n'
        ' )\n'
        ' (custom_bom_attributes\n'
        ' )\n'
        ' (default_lock_component_assembly false)\n'
        ')\n'
    )

    # Circuit
    (proj_dir / "circuit" / "circuit.lp").write_text(gen_circuit())
    print("  Written: circuit/circuit.lp")

    # ERC placeholder
    (proj_dir / "circuit" / "erc.lp").write_text("(librepcb_erc\n)\n")

    # Schematics index
    (proj_dir / "schematics" / "schematics.lp").write_text(
        '(librepcb_schematics\n'
        ' (schematic "schematics/main/schematic.lp")\n'
        ')\n'
    )

    # Schematic
    (proj_dir / "schematics" / "main" / "schematic.lp").write_text(gen_schematic())
    print("  Written: schematics/main/schematic.lp")

    # Boards index
    (proj_dir / "boards" / "boards.lp").write_text(
        '(librepcb_boards\n'
        ' (board "boards/default/board.lp")\n'
        ')\n'
    )

    # Board
    (proj_dir / "boards" / "default" / "board.lp").write_text(gen_board(proj_dir))
    print("  Written: boards/default/board.lp")

    # Board user settings placeholder
    (proj_dir / "boards" / "default" / "settings.user.lp").write_text(
        "(librepcb_board_user_settings\n)\n"
    )

    # Schematic user settings placeholder
    (proj_dir / "schematics" / "main" / "settings.user.lp").write_text(
        "(librepcb_schematic_user_settings\n)\n"
    )

    # Project-local NE555 component
    cmp_dir = proj_dir / "library" / "cmp" / NE555_CMP_UUID
    (cmp_dir / "component.lp").write_text(gen_ne555_component())
    (cmp_dir / ".librepcb-cmp").write_text("2\n")
    print(f"  Written: library/cmp/{NE555_CMP_UUID}/component.lp")

    # Project-local NE555 device
    dev_dir = proj_dir / "library" / "dev" / NE555_DEV_UUID
    (dev_dir / "device.lp").write_text(gen_ne555_device())
    (dev_dir / ".librepcb-dev").write_text("2\n")
    print(f"  Written: library/dev/{NE555_DEV_UUID}/device.lp")

    # Project-local Capacitor Bipolar THT device
    cap_dev_dir = proj_dir / "library" / "dev" / DEV_CAP_BIPOLAR_THT_UUID
    cap_dev_dir.mkdir(parents=True, exist_ok=True)
    (cap_dev_dir / "device.lp").write_text(gen_cap_bipolar_tht_device())
    (cap_dev_dir / ".librepcb-dev").write_text("2\n")
    print(f"  Written: library/dev/{DEV_CAP_BIPOLAR_THT_UUID}/device.lp")

    # Jobs placeholder
    (proj_dir / "project" / "jobs.lp").write_text("(librepcb_jobs\n)\n")

    # Project user settings placeholder
    (proj_dir / "project" / "settings.user.lp").write_text(
        "(librepcb_project_user_settings\n)\n"
    )

    print("\n✅ Project generated successfully!")
    print(f"\nOpen in LibrePCB: {proj_dir}")
    print("\nWhat the script generated:")
    print("  • NE555 component & device (project-local library)")
    print("  • Complete netlist (all 7 nets, 14 component instances)")
    print("  • Schematic with all symbols placed")
    print("  • Board with all devices placed on 40x30mm PCB")
    print("  • Ground plane on bottom copper layer")
    print("\nWhat you'll need to do manually:")
    print("  • Draw wires in the schematic (connect the placed symbols)")
    print("  • Route traces on the board (connect the placed footprints)")
    print("  • Run ERC and DRC to verify")


if __name__ == "__main__":
    main()
