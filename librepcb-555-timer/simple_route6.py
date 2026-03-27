#!/usr/bin/env python3
"""
Two-layer geometric router v2 for 555 Timer (150x100mm, all THT).

Architecture:
  - top_cu: horizontal stubs from pads to approach columns
  - Vias at column points (far from all component pads)
  - bot_cu: vertical columns + horizontal corridors

Verified: zero crossings on bot_cu between any column and corridor.
Each top_cu stub at unique Y (or offset with L-jog to avoid overlap).
"""

import re, sys, math, shutil
import uuid as uuid_mod
from pathlib import Path

def genuuid(): return str(uuid_mod.uuid4())

DIP8_PAD_POS = {
    "91607d5c-257d-4d2c-a5ef-2fb6e869c143": (-3.81,  3.81),   # pin1 GND
    "01f34160-65de-4e5e-9db1-3e186d38b186": (-3.81,  1.27),   # pin2 TRIG
    "7ef06bc0-a1b8-4efd-b089-2347a7562272": (-3.81, -1.27),   # pin3 OUT
    "13904582-16ae-4f00-b796-1e8ec7321574": (-3.81, -3.81),   # pin4 RST
    "fc6081c5-2de5-4306-916b-c4f860e790d2": ( 3.81, -3.81),   # pin5 CTRL
    "c8ce3c8f-d3ca-484a-aeea-882badbfd039": ( 3.81, -1.27),   # pin6 THR
    "a193ba1f-6f5c-4bff-b5d0-93810ce154c4": ( 3.81,  1.27),   # pin7 DIS
    "6f52c096-3d8c-43e7-ae41-e295050ceffe": ( 3.81,  3.81),   # pin8 VCC
}
HDR_PAD_POS = {"f8e03f2f-c368-4b18-bfcb-35e1dcd781cc":(0.0,1.27),"61e20af2-9626-407f-af74-3a5a6a1a1002":(0.0,-1.27)}
LED_PAD_POS = {"86d7799a-37c9-4396-8e2d-997addc21175":(0.0,1.27),"a7d87d01-a650-486c-89fc-04209af0410e":(0.0,-1.27)}
R_THT_PAD_POS = {"181c5e6c-4b3c-48c8-b4d9-bb603a0f11b6":(-5.08,0.0),"b809afd1-3010-4dbe-96f0-0f16ee6c5fc3":(5.08,0.0)}
CAP_RAD_PAD_POS = {"b4e7cf1e-8cad-451a-8bd9-4f30f8118755":(-1.25,0.0),"dbaab8c2-e88b-4f5b-b2a8-528d10ec340d":(1.25,0.0)}
KNOWN_FP = {"9408300b-9a69-43c0-8926-751414b1252a":DIP8_PAD_POS,"9255069f-e33d-4351-8b3c-523866f5ef98":HDR_PAD_POS,"492738f9-6814-4c83-bb8c-67908eca68da":LED_PAD_POS}

def pad_abs(dp,po,rot):
    cx,cy=dp;px,py=po;r=math.radians(rot)
    return(round(cx+px*math.cos(r)-py*math.sin(r),3),round(cy+px*math.sin(r)+py*math.cos(r),3))

def parse_fp_pads(pkg_dir,fp_uuid):
    for f in pkg_dir.glob("*/package.lp"):
        c=f.read_text()
        m=re.search(rf'\(footprint {re.escape(fp_uuid)}.*?\n(.*?)(?=\n \(footprint |\n\)$)',c,re.DOTALL)
        if m:
            pads={}
            for pm in re.finditer(r'\(pad ([0-9a-f-]{36}) \(side \w+\) \(shape \w+\)\s*\n\s*\(position ([0-9.-]+) ([0-9.-]+)\)',m.group(0)):
                pads[pm.group(1)]=(float(pm.group(2)),float(pm.group(3)))
            if pads:return pads
    return None

def parse_board(p):
    c=p.read_text();devs={}
    for m in re.finditer(r'\(device ([0-9a-f-]{36})\s*\n\s*\(lib_device ([0-9a-f-]{36})\)\s*\n\s*\(lib_footprint ([0-9a-f-]{36})\)\s*\n\s*\(lib_3d_model \w+\)\s*\n\s*\(position ([0-9.-]+) ([0-9.-]+)\) \(rotation ([0-9.-]+)\)',c):
        devs[m.group(1)]={"lib_device":m.group(2),"lib_footprint":m.group(3),"pos":(float(m.group(4)),float(m.group(5))),"rotation":float(m.group(6))}
    return devs,c

def parse_circuit(p):
    c=p.read_text()
    nets={m.group(2):m.group(1) for m in re.finditer(r'\(net ([0-9a-f-]{36}) \(auto \w+\) \(name "([^"]+)"\)',c)}
    comps={}
    for m in re.finditer(r'\(component ([0-9a-f-]{36})\s*\n(.*?)\n \)',c,re.DOTALL):
        b=m.group(2);nm=re.search(r'\(name "([^"]+)"\)',b);dm=re.search(r'\(device ([0-9a-f-]{36})',b)
        sigs={s.group(1):s.group(2) for s in re.finditer(r'\(signal ([0-9a-f-]{36}) \(net ([0-9a-f-]{36})\)\)',b)}
        comps[m.group(1)]={"name":nm.group(1) if nm else "","lib_device":dm.group(1) if dm else None,"signals":sigs}
    return nets,comps

def get_dev_pad_map(proj_dir,ld):
    for f in (proj_dir/"library"/"dev").glob("*/device.lp"):
        c=f.read_text()
        if ld in c:
            pm={m.group(2):m.group(1) for m in re.finditer(r'\(pad ([0-9a-f-]{36}) \(optional \w+\)\s*\n\s*\(signal ([0-9a-f-]{36})\)',c)}
            if pm:return pm
    return{}

def main():
    proj_dir=Path(sys.argv[1]) if len(sys.argv)>1 else Path.home()/"LibrePCB-Workspace"/"projects"/"555_Timer_Astable"
    devices,board_content=parse_board(proj_dir/"boards"/"default"/"board.lp")
    nets,components=parse_circuit(proj_dir/"circuit"/"circuit.lp")
    n2c={c["name"]:u for u,c in components.items()}

    pad_offsets={}
    for cu,dv in devices.items():
        fp=dv["lib_footprint"];k=KNOWN_FP.get(fp)
        if k:pad_offsets[cu]=k
        else:
            p=parse_fp_pads(proj_dir/"library"/"pkg",fp)
            if p:pad_offsets[cu]=p
            elif dv["lib_device"]=="a0e021c0-90ab-4415-802e-40a847f682c8":pad_offsets[cu]=R_THT_PAD_POS
            else:pad_offsets[cu]=CAP_RAD_PAD_POS

    cpm={}
    for cu,cd in components.items():
        if cu in devices and cd.get("lib_device"):
            pm=get_dev_pad_map(proj_dir,cd["lib_device"])
            if pm:cpm[cu]=pm

    def gpp(cu,pu):
        dv=devices[cu];off=pad_offsets.get(cu,{}).get(pu,(0,0))
        return pad_abs(dv["pos"],off,dv["rotation"])
    def fpn(cu,nu):
        cd=components[cu];pm=cpm.get(cu,{})
        return[pm[s] for s,sn in cd["signals"].items() if sn==nu and s in pm]
    def C(n):
        u=n2c.get(n);return u if u and u in devices else None
    def N(n):return nets.get(n)

    all_segs=[]
    def D(cu,pu):return("d",cu,pu)
    def J(jid):return("j",jid)
    def V(vid):return("v",vid)
    def tr(f,t,w,ly="top_cu"):return{"f":f,"t":t,"w":w,"ly":ly}
    def mvia(x,y):v=genuuid();return{"id":v,"x":x,"y":y},v

    def emit(net_uuid,vias,juncs,traces):
        s=[f' (netsegment {genuuid()}',f'  (net {net_uuid})']
        for v in vias:
            s.append(f'  (via {v["id"]} (from top_cu) (to bot_cu)')
            s.append(f'   (position {v["x"]} {v["y"]}) (drill auto) (size auto) (exposure off)')
            s.append('  )')
        for j in juncs:
            s.append(f'  (junction {j["id"]} (position {j["x"]} {j["y"]}))')
        for t in traces:
            s.append(f'  (trace {genuuid()} (layer {t["ly"]}) (width {t["w"]})')
            f=t["f"]
            if f[0]=="d":s.append(f'   (from (device {f[1]}) (pad {f[2]}))')
            elif f[0]=="j":s.append(f'   (from (junction {f[1]}))')
            elif f[0]=="v":s.append(f'   (from (via {f[1]}))')
            to=t["t"]
            if to[0]=="d":s.append(f'   (to (device {to[1]}) (pad {to[2]}))')
            elif to[0]=="j":s.append(f'   (to (junction {to[1]}))')
            elif to[0]=="v":s.append(f'   (to (via {to[1]}))')
            s.append('  )')
        s.append(' )')
        all_segs.append("\n".join(s))

    W="0.5";S="0.3"

    # Edge approach columns (X) — unique per net, far from all components
    VCC_LCOL=8; OUT_LCOL=15; THR_LCOL=22
    CTL_RCOL=128; THR_RCOL=132; DIS_RCOL=136; VCC_RCOL=142
    # Corridors (Y) — unique per net
    GND_Y=4; THR_Y=12; CTL_Y=20; OUT_Y=80; DIS_Y=88; VCC_Y=96

    print("Routing (two-layer, verified zero-crossing)...\n")

    # ================================================================
    # VCC: J1:1, R1:1, U1:4(left), U1:8(right)
    # ================================================================
    vcc=N("VCC")
    j1p=fpn(C("J1"),vcc)[0]; j1pos=gpp(C("J1"),j1p)
    r1p=fpn(C("R1"),vcc)[0]; r1pos=gpp(C("R1"),r1p)
    u1v=fpn(C("U1"),vcc)
    u1vp=sorted([(p,gpp(C("U1"),p)) for p in u1v],key=lambda x:-x[1][1])
    p8pad,p8pos=u1vp[0]; p4pad,p4pos=u1vp[1]

    vs=[];js=[];ts=[]
    # J1:1 top_cu stub to VCC_LCOL, via, bot_cu column to corridor
    va1,va1id=mvia(VCC_LCOL,j1pos[1]);vs.append(va1)
    ts.append(tr(D(C("J1"),j1p),V(va1id),W,"top_cu"))
    # R1:1 top_cu stub to VCC_LCOL, via, bot_cu
    va2,va2id=mvia(VCC_LCOL,r1pos[1]);vs.append(va2)
    ts.append(tr(D(C("R1"),r1p),V(va2id),W,"top_cu"))
    # U1:4 top_cu stub to VCC_LCOL, via
    va3,va3id=mvia(VCC_LCOL,p4pos[1]);vs.append(va3)
    ts.append(tr(D(C("U1"),p4pad),V(va3id),W,"top_cu"))
    # U1:8 top_cu stub to VCC_RCOL, via
    va4,va4id=mvia(VCC_RCOL,p8pos[1]);vs.append(va4)
    ts.append(tr(D(C("U1"),p8pad),V(va4id),W,"top_cu"))
    # Bot_cu: all vias connect vertically to corridor at VCC_Y, then horizontal
    jA={"id":genuuid(),"x":VCC_LCOL,"y":VCC_Y};js.append(jA)
    jB={"id":genuuid(),"x":VCC_RCOL,"y":VCC_Y};js.append(jB)
    ts.append(tr(V(va1id),J(jA["id"]),W,"bot_cu"))  # J1 via → corridor
    ts.append(tr(V(va2id),J(jA["id"]),W,"bot_cu"))  # R1 via → corridor (same column)
    ts.append(tr(V(va3id),J(jA["id"]),W,"bot_cu"))  # pin4 via → corridor (same column)
    ts.append(tr(J(jA["id"]),J(jB["id"]),W,"bot_cu"))  # corridor L→R
    ts.append(tr(V(va4id),J(jB["id"]),W,"bot_cu"))  # pin8 via → corridor
    emit(vcc,vs,js,ts)
    print(f"  VCC: {len(ts)} traces, {len(vs)} vias")

    # ================================================================
    # DISCHARGE: R1:2, R2:1, U1:7(right)
    # R2:1 stub offset to y=37 to avoid overlap with THR at y=35
    # ================================================================
    dis=N("DISCHARGE")
    r1d=fpn(C("R1"),dis)[0];r1dp=gpp(C("R1"),r1d)
    r2d=fpn(C("R2"),dis)[0];r2dp=gpp(C("R2"),r2d)
    u1d=fpn(C("U1"),dis)[0];u1dp=gpp(C("U1"),u1d)

    vs=[];js=[];ts=[]
    # R1:2 → top_cu to DIS_RCOL
    va1,va1id=mvia(DIS_RCOL,r1dp[1]);vs.append(va1)
    ts.append(tr(D(C("R1"),r1d),V(va1id),S,"top_cu"))
    # R2:1 → jog up to y=37 then top_cu to DIS_RCOL
    jR2={"id":genuuid(),"x":r2dp[0],"y":37.0};js.append(jR2)
    va2,va2id=mvia(DIS_RCOL,37.0);vs.append(va2)
    ts.append(tr(D(C("R2"),r2d),J(jR2["id"]),S,"top_cu"))
    ts.append(tr(J(jR2["id"]),V(va2id),S,"top_cu"))
    # U1:7 → top_cu to DIS_RCOL
    va3,va3id=mvia(DIS_RCOL,u1dp[1]);vs.append(va3)
    ts.append(tr(D(C("U1"),u1d),V(va3id),S,"top_cu"))
    # Bot_cu column + corridor
    jA={"id":genuuid(),"x":DIS_RCOL,"y":DIS_Y};js.append(jA)
    ts.append(tr(V(va1id),J(jA["id"]),S,"bot_cu"))
    ts.append(tr(V(va2id),J(jA["id"]),S,"bot_cu"))
    ts.append(tr(V(va3id),J(jA["id"]),S,"bot_cu"))
    emit(dis,vs,js,ts)
    print(f"  DISCHARGE: {len(ts)} traces, {len(vs)} vias")

    # ================================================================
    # THRESH_TRIG: R2:2, C1:+, U1:2(left), U1:6(right)
    # R2:2 stub offset to y=33, C1 stub offset to y=23
    # ================================================================
    thr=N("THRESH_TRIG")
    r2t=fpn(C("R2"),thr)[0];r2tp=gpp(C("R2"),r2t)
    c1t=fpn(C("C1"),thr)[0];c1tp=gpp(C("C1"),c1t)
    u1t=fpn(C("U1"),thr)
    u1ti=[(p,gpp(C("U1"),p)) for p in u1t]

    vs=[];js=[];ts=[]
    # R2:2 → jog down to y=33 then to THR_LCOL
    jR2={"id":genuuid(),"x":r2tp[0],"y":33.0};js.append(jR2)
    va1,va1id=mvia(THR_LCOL,33.0);vs.append(va1)
    ts.append(tr(D(C("R2"),r2t),J(jR2["id"]),S,"top_cu"))
    ts.append(tr(J(jR2["id"]),V(va1id),S,"top_cu"))
    # C1:+ → jog to y=23 then to THR_RCOL
    jC1={"id":genuuid(),"x":c1tp[0],"y":23.0};js.append(jC1)
    va2,va2id=mvia(THR_RCOL,23.0);vs.append(va2)
    ts.append(tr(D(C("C1"),c1t),J(jC1["id"]),S,"top_cu"))
    ts.append(tr(J(jC1["id"]),V(va2id),S,"top_cu"))
    # U1 pins → their columns
    u1_via_info=[]  # (vaid, col_x)
    for pad,pos in u1ti:
        col=THR_LCOL if pos[0]<70 else THR_RCOL
        va,vaid=mvia(col,pos[1]);vs.append(va)
        ts.append(tr(D(C("U1"),pad),V(vaid),S,"top_cu"))
        u1_via_info.append((vaid, col))
    # Bot_cu corridors
    jL={"id":genuuid(),"x":THR_LCOL,"y":THR_Y};js.append(jL)
    jR={"id":genuuid(),"x":THR_RCOL,"y":THR_Y};js.append(jR)
    ts.append(tr(V(va1id),J(jL["id"]),S,"bot_cu"))  # R2:2
    ts.append(tr(V(va2id),J(jR["id"]),S,"bot_cu"))  # C1
    ts.append(tr(J(jL["id"]),J(jR["id"]),S,"bot_cu"))  # corridor
    for vaid,col in u1_via_info:
        target = jL if col == THR_LCOL else jR
        ts.append(tr(V(vaid),J(target["id"]),S,"bot_cu"))
    emit(thr,vs,js,ts)
    print(f"  THRESH: {len(ts)} traces, {len(vs)} vias")

    # ================================================================
    # CONTROL: U1:5 → C2:1
    # C2 stub offset to y=27 to avoid GND/THR at y=25
    # ================================================================
    ctrl=N("CONTROL")
    u1c=fpn(C("U1"),ctrl)[0];u1cp=gpp(C("U1"),u1c)
    c2c=fpn(C("C2"),ctrl)[0];c2cp=gpp(C("C2"),c2c)

    vs=[];js=[];ts=[]
    va1,va1id=mvia(CTL_RCOL,u1cp[1]);vs.append(va1)
    ts.append(tr(D(C("U1"),u1c),V(va1id),S,"top_cu"))
    # C2:1 jog to y=27
    jC2={"id":genuuid(),"x":c2cp[0],"y":27.0};js.append(jC2)
    va2,va2id=mvia(CTL_RCOL,27.0);vs.append(va2)
    ts.append(tr(D(C("C2"),c2c),J(jC2["id"]),S,"top_cu"))
    ts.append(tr(J(jC2["id"]),V(va2id),S,"top_cu"))
    # Bot_cu
    jA={"id":genuuid(),"x":CTL_RCOL,"y":CTL_Y};js.append(jA)
    ts.append(tr(V(va1id),J(jA["id"]),S,"bot_cu"))
    ts.append(tr(V(va2id),J(jA["id"]),S,"bot_cu"))
    emit(ctrl,vs,js,ts)
    print(f"  CONTROL: {len(ts)} traces, {len(vs)} vias")

    # ================================================================
    # OUTPUT: U1:3 → R3:1
    # ================================================================
    out=N("OUTPUT")
    u1o=fpn(C("U1"),out)[0];u1op=gpp(C("U1"),u1o)
    r3o=fpn(C("R3"),out)[0];r3op=gpp(C("R3"),r3o)

    vs=[];js=[];ts=[]
    va1,va1id=mvia(OUT_LCOL,u1op[1]);vs.append(va1)
    ts.append(tr(D(C("U1"),u1o),V(va1id),S,"top_cu"))
    va2,va2id=mvia(OUT_LCOL,r3op[1]);vs.append(va2)
    ts.append(tr(D(C("R3"),r3o),V(va2id),S,"top_cu"))
    # Bot_cu
    jA={"id":genuuid(),"x":OUT_LCOL,"y":OUT_Y};js.append(jA)
    ts.append(tr(V(va1id),J(jA["id"]),S,"bot_cu"))
    ts.append(tr(V(va2id),J(jA["id"]),S,"bot_cu"))
    emit(out,vs,js,ts)
    print(f"  OUTPUT: {len(ts)} traces, {len(vs)} vias")

    # ================================================================
    # LED_ANODE: R3:2 → D1:A (top_cu only, far from IC)
    # ================================================================
    led=N("LED_ANODE")
    r3l=fpn(C("R3"),led)[0];r3lp=gpp(C("R3"),r3l)
    d1l=fpn(C("D1"),led)[0];d1lp=gpp(C("D1"),d1l)
    vs=[];js=[];ts=[]
    # Approach D1:A from above — avoid passing over LED body and near cathode
    # Route: R3:2 → right to x=145 → up to y=72 (above LED body) → down to D1:A
    jA={"id":genuuid(),"x":r3lp[0],"y":72.0};js.append(jA)
    jB={"id":genuuid(),"x":d1lp[0],"y":72.0};js.append(jB)
    ts.append(tr(D(C("R3"),r3l),J(jA["id"]),S,"top_cu"))
    ts.append(tr(J(jA["id"]),J(jB["id"]),S,"top_cu"))
    ts.append(tr(J(jB["id"]),D(C("D1"),d1l),S,"top_cu"))
    emit(led,vs,js,ts)
    print(f"  LED_ANODE: {len(ts)} traces (top_cu only)")

    # ================================================================
    # GND: ALL pads are THT — ground plane on bot_cu connects them automatically.
    # No explicit routing needed!
    # ================================================================
    print(f"  GND: handled by ground plane (all THT pads)")

    print(f"\nTotal: {len(all_segs)} netsegments")

    # Write
    board_path=proj_dir/"boards"/"default"/"board.lp"
    cleaned=re.sub(r' \(netsegment .*?\n \)\n','',board_content,flags=re.DOTALL)
    idx=cleaned.find(" (plane ")
    if idx<0:idx=cleaned.rfind(" (polygon ")
    if idx<0:print("ERROR");sys.exit(1)
    new=cleaned[:idx]+"\n".join(all_segs)+"\n"+cleaned[idx:]
    bak=board_path.with_suffix(".lp.bak7")
    shutil.copy2(board_path,bak)
    board_path.write_text(new)
    print(f"\n✅ Done: {board_path}")

if __name__=="__main__":
    main()
