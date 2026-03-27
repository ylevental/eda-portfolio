<Qucs Schematic 24.4.0>
<Properties>
  <View=-100,-200,800,600,1,0,0>
  <Grid=10,10,1>
  <DataSet=inverting_amp.dat>
  <DataDisplay=inverting_amp.dpl>
  <OpenDisplay=1>
  <Script=inverting_amp.m>
  <RunScript=0>
  <showFrame=0>
  <FrameText0=Title>
  <FrameText1=Drawn By: Yuval Levental>
  <FrameText2=Date:>
  <FrameText3=Revision:>
</Properties>
<Symbol>
</Symbol>
<Components>
  <Vac V1 1 80 200 18 -26 0 1 "1 V" 1 "1 kHz" 1 "0" 0 "0" 0 "0" 0 "0" 0>
  <GND * 1 80 260 0 0 0 0>
  <R R1 1 180 120 -26 15 0 0 "1 kOhm" 1 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "european" 0>
  <R Rf 1 360 120 -26 15 0 0 "10 kOhm" 1 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "european" 0>
  <OpAmp OP1 1 320 200 -26 42 0 0 "1e6" 1 "15 V" 0>
  <GND * 1 290 250 0 0 0 0>
  <.ac AC1 1 80 360 0 46 0 0 "log" 1 "100 Hz" 1 "10 MHz" 1 "100" 1 "no" 0>
  <.tr TR1 1 300 360 0 46 0 0 "1 ms" 1 "5 ms" 1 "10 us" 0 "0" 0 "0" 0 "0" 0 "0" 0 "0" 0 "0" 0>
</Components>
<Wires>
  <80 120 80 170 "" 0 0 0 "">
  <80 120 150 120 "Vin" 90 100 15 "">
  <210 120 260 120 "" 0 0 0 "">
  <260 120 260 180 "" 0 0 0 "">
  <260 180 290 180 "" 0 0 0 "">
  <290 220 290 250 "" 0 0 0 "">
  <260 120 330 120 "" 0 0 0 "">
  <390 120 440 120 "" 0 0 0 "">
  <440 120 440 200 "" 0 0 0 "">
  <350 200 440 200 "Vout" 400 180 15 "">
  <80 230 80 260 "" 0 0 0 "">
</Wires>
<Diagrams>
</Diagrams>
<Paintings>
  <Text 60 30 12 #000000 0 "Inverting Op-Amp Amplifier\nGain = -Rf/R1 = -10 kOhm / 1 kOhm = -10 (20 dB)\nAuthor: Yuval Levental">
</Paintings>
