# Blind read (40 plans; plan.md §10.3)

Copy read_blank.csv to read.csv. For each plan: would a competent salvage master accept it? Fill `accept` (yes / no / partial) and a one-line `reason`. Images are under ../shipwreck_wiki_images/sorted_images/ (BenchyBench root). Do not open the key, results/ or any report until the read and its re-rate are done.

---

## H01

Image: `sunken/00231.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 620 t lift capacity within 22.4 hours (weather window closes).

Resource ledger:

ID        TYPE                  CAPABILITY           LOCATION             ETA_H  STATUS
--------  --------------------  -------------------  -------------------  -----  ---------
BOOM-025  oil containment boom  530 m                Brackwater, 128 nm   15.3   available
BRG-018   deck cargo barge      2000 t               underway, 144 nm     20.8   available
CRN-023   floating crane        160 t lift capacity  Fenwick Docks, 7 nm  6.4    available
CRN-048   floating crane        100 t lift capacity  Skerry Quay, 214 nm  42.7   available
CRN-057   floating crane        140 t lift capacity  underway, 29 nm      5.0    available
DIV-053   dive team             5 divers             Brackwater, 128 nm   7.0    available
LB-003    lift bag set          15 t lift capacity   Brackwater, 128 nm   16.4   available

On scene within 22.4 h: 315 t combined lift capacity. Full fleet: 415 t at 42.7 h.
```

Plan (repeated steps removed):

```text
1. Deploy CRN-057 floating crane (140 t lift capacity) from its current location to Fenwick Docks to begin the refloat operation, arriving at T+5.0 h.
2. Deploy CRN-023 floating crane (160 t lift capacity) from Fenwick Docks to the casualty site, arriving at T+6.4 h.
3. Deploy LB-003 lift bag set (15 t lift capacity) from Brackwater to the casualty site, arriving at T+16.4 h.
4. Deploy DIV-053 dive team (5 divers) from Brackwater to the casualty site, arriving at T+7.0 h to conduct a preliminary underwater inspection and assess the hull integrity and presence of hazardous materials.
5. Deploy BOOM-025 oil containment boom (530 m) from Brackwater to the casualty site, arriving at T+15.3 h, to contain any potential oil leakage during the refloat operation.
6. Deploy BRG-018 deck cargo barge (2000 t) from its current location to the casualty site, arriving at T+20.8 h, to provide additional lift capacity and support for the refloat operation.
7. Coordinate the combined lift capacity of CRN-057 (140 t), CRN-023 (160 t), and LB-003 (15 t) to achieve a total of 315 t lift capacity by T+6.4 h, with the remaining capacity from BRG-018 (2000 t) available at T+20.8 h.
8. Conduct a stability check and righting-arm analysis using the dive team (DIV-053) to determine the optimal refloat method and ensure the vessel is stable for lifting.
9. Begin the refloat operation using the combined lift capacity of CRN-057, CRN-023, and LB-003, with the dive team (DIV-053) providing real-time underwater support and monitoring.
10. If necessary, use the BRG-018 deck cargo barge (2000 t) to provide additional lift capacity and support for the refloat operation, ensuring the total lift capacity exceeds the required 620 t within the 22.4-hour window.
11. Monitor the tide and ground reaction using a dedicated tide gauge to adjust the refloat strategy as the tide rises and falls.
12. Ensure all tanks are checked for fuel and hazardous cargo before any cutting or movement begins, with the dive team (DIV-053) conducting the inspection.
13. Control the lifting loads to avoid overturning the vessel further, with the crane operators coordinating with the dive team (DIV-053) for real-time adjustments.
14. If the vessel is found to be aground, assess the seabed type and calculate the pulling force needed for refloat, adjusting the refloat strategy accordingly.
15. If the vessel is found to be capsized, prioritize crew rescue before attempting to right the vessel, with the dive team (DIV-053) conducting the rescue operation.
16. If the vessel is found to be sunken, conduct sequential testing for explosive gas, then oxygen, then toxic gas before any diver enters or hot work begins, with the dive team (DIV-053) conducting the testing.
17. If the vessel is found to be on fire, confirm the affected space is clear of personnel before activating any fixed suppression system, with the dive team (DIV-053) conducting the fire suppression operation.
18. Reassess the hull and stability once the fire is out, with the dive team (DIV-053) conducting the reassessment.
19. If the vessel is found to be aground and requires lightering, use the BRG-018 deck cargo barge (2000 t) to remove weight before refloat.
20. If the vessel is found to be aground and requires dredging, use the BRG-018 deck cargo barge (2000 t) to clear a channel before refloat.
21. If the vessel is found to be capsized and requires deballasting, use the BRG-018 deck cargo barge (2000 t) to control deballasting.
22. If the vessel is found to be sunken and requires patching, use the BRG-018 deck cargo barge (2000 t) to provide support for patching and refloat.
23. If the vessel is found to be sunken and requires crane-and-barge removal, use the BRG-018 deck cargo barge (2000 t) to provide support for crane-and-barge removal.
24. If the vessel is found to be on fire and requires foam suppression, use the BRG-018 deck cargo barge (2000 t) to provide support for foam suppression.
25. If the vessel is found to be on fire and requires gas flooding, use the BRG-018 deck cargo barge (2000 t) to provide support for gas flooding.
26. If the vessel is found to be on fire and requires alcohol-resistant foam, use the BRG-018 deck cargo barge (2000 t) to provide support for alcohol-resistant foam.
27. If the vessel is found to be on fire and requires fireboat monitors, use the BRG-018 deck cargo barge (2000 t) to provide support for fireboat monitors.
28. If the vessel is found to be on fire and requires backdraft prevention, use the BRG-018 deck cargo barge (2000 t) to provide support for backdraft prevention.
29. If the vessel is found to be on fire and requires hull and stability reassessment, use the BRG-018 deck cargo barge (2000 t) to provide support for hull and stability reassessment.
30. If the vessel is found to be on fire and requires fuel offloading, use the BRG-018 deck cargo barge (2000 t) to provide support for fuel offloading.
31. If the vessel is found to be on fire and requires cargo accounting, use the BRG-018 deck cargo barge (2000 t) to provide support for cargo accounting.
32. If the vessel is found to be on fire and requires oil containment, use the BOOM-025 oil containment boom (530 m) to provide support for oil containment.
33. If the vessel is found to be on fire and requires diver-directed recovery, use the DIV-053 dive team (5 divers) to provide support for diver-directed recovery.
34. If the vessel is found to be on fire and requires net environmental benefit analysis, use the DIV-053 dive team (5 divers) to provide support for net environmental benefit analysis.
35. If the vessel is found to be on fire and requires standardized risk-ranking method, use the DIV-053 dive team (5 divers) to provide support for standardized risk-ranking method.
36. If the vessel is found to be on fire and requires oil containment matched to how it behaves in the water, use the BOOM-025 oil containment boom (530 m) to provide support for oil containment.
37. If the vessel is found to be on fire and requires side-scan or electro-acoustic sonar, use the DIV-053 dive team (5 divers) to provide support for side-scan or electro-acoustic sonar.
38. If the vessel is found to be on fire and requires diver-directed recovery in sensitive habitat, use the DIV-053 dive team (5 divers) to provide support for diver-directed recovery.
39. If the vessel is found to be on fire and requires a legacy or abandoned wreck ranking, use the DIV-053 dive team (5 divers) to provide support for legacy or abandoned wreck ranking.
40. If the vessel is found to be on fire and requires a standardized risk-ranking method, use the DIV-053 dive team (5 divers) to provide support for standardized risk-ranking method.
41. If the vessel is found to be on fire and requires a net environmental benefit analysis, use the DIV-053 dive team (5 divers) to provide support for net environmental benefit analysis.
```

---

## H02

Image: `aground/00100.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 92 t bollard pull within 6.9 hours (high water).

Resource ledger:

ID       TYPE        CAPABILITY         LOCATION               ETA_H  STATUS
-------  ----------  -----------------  ---------------------  -----  ---------
DIV-055  dive team   6 divers           Marrow Inlet, 54 nm    3.5    available
TUG-028  harbor tug  25 t bollard pull  Port Calder, 6 nm      1.0    available
TUG-029  harbor tug  25 t bollard pull  Westray Roads, 256 nm  24.0   available
TUG-055  harbor tug  25 t bollard pull  Port Calder, 6 nm      1.4    available

On scene within 6.9 h: 50 t combined bollard pull. Full fleet: 75 t at 24.0 h.
```

Plan (repeated steps removed):

```text
1. Assess the vessel’s grounding condition and confirm draft is within 3m-10m range using tide gauge data near the site; commit TUG-028 and TUG-055 to the task.
2. Deploy TUG-028 and TUG-055 to apply 50 t combined bollard pull to refloat the vessel; monitor ground reaction and friction coefficient of seabed type (sand) as tide rises.
3. If refloat fails within 6.9 hours, initiate lightering by offloading cargo to reduce weight, targeting areas away from neutral loading point to minimize hull strain.
4. If lightering is insufficient, request additional tug assistance; TUG-029 is not available within 6.9 hours, so no further action can be taken to meet the 92 t requirement.
5. If vessel remains aground after 6.9 hours, initiate dredging to clear channel; no assets are available to perform this task within the time constraint.
6. If vessel is not refloated, assess for hazardous materials and fuel; if present, secure and offload before any cutting or movement begins.
7. If vessel is not refloated, consider abandonment or long-term monitoring; no assets are available to perform recovery or removal within the time constraint.
8. If vessel is not refloated, request additional resources; no assets are available to perform recovery or removal within the time constraint.
9. If vessel is not refloated, document the casualty and report to command; no assets are available to perform recovery or removal within the time constraint.
10. If vessel is not refloated, initiate environmental monitoring for oil or hazardous material release; no assets are available to perform this task within the time constraint.
```

---

## H03

Image: `aground/00082.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 510 t bollard pull within 3.1 hours (high water).

Resource ledger:

ID       TYPE                 CAPABILITY          LOCATION                ETA_H  STATUS
-------  -------------------  ------------------  ----------------------  -----  ---------
AHT-006  anchor handling tug  210 t bollard pull  underway, 29 nm         2.4    available
AHT-010  anchor handling tug  190 t bollard pull  underway, 5 nm          0.6    available
AHT-012  anchor handling tug  210 t bollard pull  underway, 16 nm         1.4    available
AHT-028  anchor handling tug  190 t bollard pull  underway, 27 nm         2.3    available
AHT-040  anchor handling tug  120 t bollard pull  underway, 17 nm         1.5    available
AHT-042  anchor handling tug  170 t bollard pull  underway, 103 nm        8.1    available
BRG-048  deck cargo barge     1800 t              underway, 10 nm         1.7    available
DIV-016  dive team            4 divers            Westray Roads, 21 nm    2.7    available
TUG-002  ocean salvage tug    120 t bollard pull  underway, 20 nm         1.6    available
TUG-014  ocean salvage tug    130 t bollard pull  underway, 32 nm         2.5    available
TUG-021  ocean salvage tug    140 t bollard pull  underway, 35 nm         2.7    available
TUG-024  ocean salvage tug    100 t bollard pull  Saltmarsh Quay, 123 nm  16.0   available
TUG-041  ocean salvage tug    200 t bollard pull  underway, 17 nm         1.4    available
WB-026   workboat             7 t bollard pull    Westray Roads, 21 nm    1.6    available
WB-030   workboat             3 t bollard pull    underway, 9 nm          0.8    available
WB-051   workboat             3 t bollard pull    Westray Roads, 21 nm    1.7    available
WB-052   workboat             4 t bollard pull    Port Calder, 419 nm     28.6   available
WB-060   workboat             15 t bollard pull   Westray Roads, 21 nm    2.0    available

On scene within 3.1 h: 1538 t combined bollard pull. Full fleet: 1812 t at 28.6 h.
```

Plan (repeated steps removed):

```text
1. Deploy AHT-010 (190 t bollard pull) and AHT-012 (210 t bollard pull) to arrive on scene by T+0.6 h and T+1.4 h respectively, to provide initial tug assistance while AHT-006 (210 t) and AHT-028 (190 t) are en route to arrive by T+2.4 h and T+2.3 h, to begin applying bollard pull to the grounded vessel "Cherry Venture" as soon as they arrive.
2. Coordinate with AHT-006 and AHT-028 to synchronize their pulling forces upon arrival at T+2.4 h and T+2.3 h respectively, to ensure combined pull does not exceed 510 t and to avoid hull strain from uneven load distribution.
3. Deploy TUG-041 (200 t bollard pull) to arrive by T+1.4 h to provide additional bollard pull capacity, targeting the vessel’s neutral loading point to reduce strain during refloat.
4. Deploy TUG-014 (130 t bollard pull) to arrive by T+2.5 h to provide further bollard pull capacity, ensuring combined pull from AHT-010, AHT-012, AHT-006, AHT-028, and TUG-041 meets or exceeds 510 t by T+2.4 h.
5. Deploy TUG-021 (140 t bollard pull) to arrive by T+2.7 h to provide additional bollard pull capacity, ensuring combined pull from all tugs meets or exceeds 510 t by T+2.4 h.
6. Deploy TUG-002 (120 t bollard pull) to arrive by T+1.6 h to provide additional bollard pull capacity, ensuring combined pull from all tugs meets or exceeds 510 t by T+2.4 h.
7. Deploy TUG-014 (130 t bollard pull) to arrive by T+2.5 h to provide further bollard pull capacity, ensuring combined pull from all tugs meets or exceeds 510 t by T+2.4 h.
```

---

## H04

Image: `sunken/00021.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 28000 t lift capacity within 48.0 hours (weather window closes).

Resource ledger:

ID       TYPE                    CAPABILITY            LOCATION              ETA_H  STATUS
-------  ----------------------  --------------------  --------------------  -----  ---------
BRG-051  deck cargo barge        1700 t                Ashby Haven, 111 nm   19.7   available
CRN-046  floating crane          100 t lift capacity   Skerry Quay, 406 nm   70.9   available
DIV-059  dive team               5 divers              Tolland Point, 13 nm  1.8    available
HLB-001  heavy lift crane barge  2200 t lift capacity  Ashby Haven, 111 nm   34.6   available
HLB-010  heavy lift crane barge  5000 t lift capacity  underway, 76 nm       15.4   available
HLB-023  heavy lift crane barge  5000 t lift capacity  underway, 94 nm       19.0   available
HLB-024  heavy lift crane barge  4500 t lift capacity  Tolland Point, 13 nm  29.0   available
HLB-035  heavy lift crane barge  5000 t lift capacity  Ashby Haven, 111 nm   53.4   available
HLB-040  heavy lift crane barge  5000 t lift capacity  Tolland Point, 13 nm  18.5   available
HLB-049  heavy lift crane barge  960 t lift capacity   Skerry Quay, 406 nm   100.3  available
HLB-050  heavy lift crane barge  5000 t lift capacity  Ashby Haven, 111 nm   40.9   available
HLB-053  heavy lift crane barge  5000 t lift capacity  Ashby Haven, 111 nm   57.7   available
HLB-057  heavy lift crane barge  5000 t lift capacity  Tolland Point, 13 nm  15.6   available
HLB-060  heavy lift crane barge  1900 t lift capacity  Ashby Haven, 111 nm   45.3   available
SHL-003  sheerlegs               3000 t lift capacity  Skerry Quay, 406 nm   105.3  available

On scene within 48.0 h: 33600 t combined lift capacity. Full fleet: 47660 t at 105.3 h.
```

Plan (repeated steps removed):

```text
1. Confirm vessel identity and condition: The vessel is the merchant tanker "PENDLETON", large (>50m), capsized on its starboard side in rough seas, with visible cargo tanks and no visible fire or grounding. Assume it contains hazardous cargo and fuel; initiate environmental containment protocols immediately upon arrival.
2. Deploy HLB-010 (5000 t lift capacity) from 76 nm to Tolland Point to begin refloating operations; ETA 15.4 h. Assign DIV-059 (5 divers) to conduct preliminary hull integrity and hazardous material surveys before any lifting begins.
3. Deploy HLB-024 (4500 t lift capacity) from Tolland Point to support HLB-010; ETA 29.0 h. Coordinate with HLB-010 to establish a dual-lift configuration for controlled righting.
4. Deploy HLB-057 (5000 t lift capacity) from Tolland Point to provide additional lift capacity; ETA 15.6 h. Position HLB-057 to assist in stabilizing the vessel during righting.
5. Deploy HLB-040 (5000 t lift capacity) from Tolland Point to provide redundancy; ETA 18.5 h. Position HLB-040 to support the main lifting operation and ensure sufficient lift capacity for the 28000 t requirement.
6. Deploy HLB-023 (5000 t lift capacity) from 94 nm to Tolland Point; ETA 19.0 h. Position HLB-023 to assist in the righting process and provide additional lift capacity if needed.
7. Deploy HLB-050 (5000 t lift capacity) from Ashby Haven to Tolland Point; ETA 40.9 h. Position HLB-050 to support the main lifting operation and ensure sufficient lift capacity for the 28000 t requirement.
8. Deploy HLB-053 (5000 t lift capacity) from Ashby Haven to Tolland Point; ETA 57.7 h. Position HLB-053 to provide additional lift capacity and redundancy.
9. Deploy HLB-060 (1900 t lift capacity) from Ashby Haven to Tolland Point; ETA 45.3 h. Position HLB-060 to assist in stabilizing the vessel during righting.
10. Deploy HLB-001 (2200 t lift capacity) from Ashby Haven to Tolland Point; ETA 34.6 h. Position HLB-001 to support the main lifting operation and ensure sufficient lift capacity for the 28000 t requirement.
11. Deploy BRG-051 (1700 t deck cargo barge) from Ashby Haven to Tolland Point; ETA 19.7 h. Position BRG-051 to assist in lightering operations if required to reduce weight before righting.
12. Deploy CRN-046 (100 t floating crane) from Skerry Quay to Tolland Point; ETA 70.9 h. Position CRN-046 to assist in securing and stabilizing the vessel during the righting process.
13. Deploy SHL-003 (3000 t sheerlegs) from Skerry Quay to Tolland Point; ETA 105.3 h. Position SHL-003 to assist in stabilizing the vessel during the righting process.
14. Conduct stability and righting-arm analysis using DIV-059 data to determine optimal righting method and sequence.
15. Initiate controlled deballasting or parbuckling using HLB-010, HLB-024, HLB-057, HLB-040, HLB-023, HLB-050, HLB-053, HLB-060, and HLB-001 to right the vessel.
16. Monitor and adjust lift loads to avoid overturning the vessel further during righting.
17. Once upright, offload fuel and hazardous cargo using BRG-051 and other available resources.
18. Conduct final inspection and environmental assessment using DIV-059 to ensure no residual hazardous materials remain.
19. Secure the vessel and prepare for transport to a safe port using the combined lift capacity of all deployed assets.
20. Request additional resources if the 28000 t lift capacity is insufficient or if the vessel requires more complex recovery methods.
```

---

## H05

Image: `aground/00041.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 150 t bollard pull within 5.2 hours (high water).

Resource ledger:

ID       TYPE           CAPABILITY         LOCATION             ETA_H  STATUS
-------  -------------  -----------------  -------------------  -----  ---------
SVY-028  survey launch  3 crew             underway, 4 nm       0.4    available
TUG-016  harbor tug     29 t bollard pull  underway, 33 nm      3.2    available
TUG-027  harbor tug     25 t bollard pull  Port Calder, 408 nm  37.4   available
TUG-048  harbor tug     42 t bollard pull  underway, 16 nm      1.7    available
WB-038   workboat       4 t bollard pull   underway, 46 nm      3.3    available

On scene within 5.2 h: 75 t combined bollard pull. Full fleet: 100 t at 37.4 h.
```

Plan (repeated steps removed):

```text
1. Assess the vessel’s grounding condition and confirm it is aground, not capsized or sunken, using visual inspection and tide gauge data to determine ground reaction forces and refloat window.
2. Deploy TUG-048 and TUG-016 to the site, arriving within 1.7 and 3.2 hours respectively, to provide initial 67 t bollard pull for refloat preparation.
3. Deploy TUG-027 to the site, arriving at 37.4 hours, to provide additional 25 t bollard pull for sustained refloat effort.
4. Conduct a stability and draft analysis to confirm the vessel can be refloated without risk of capsizing or further damage, using the neutral loading point to guide weight reduction if needed.
5. Offload any visible fuel or hazardous cargo from the vessel before initiating refloat to prevent fire or environmental risk.
6. Use TUG-048, TUG-016, and TUG-027 in tandem to apply 100 t combined bollard pull to refloat the vessel once the tide reaches high water at 5.2 hours.
7. Monitor the refloat process with a dedicated tide gauge to adjust pulling force as the ground reaction changes with tidal rise.
8. Once refloated, secure the vessel with SVY-028 for survey and stability assessment to confirm safe navigation and prevent further grounding.
```

---

## H06

Image: `sunken/00156.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 27200 t lift capacity within 40.0 hours (weather window closes).

Resource ledger:

ID       TYPE                    CAPABILITY            LOCATION             ETA_H  STATUS
-------  ----------------------  --------------------  -------------------  -----  ---------
DIV-030  dive team               5 divers              Maddock Pier, 93 nm  4.9    available
DWP-006  submersible pump        260 m3/h              Maddock Pier, 93 nm  4.8    available
HLB-010  heavy lift crane barge  4000 t lift capacity  Maddock Pier, 93 nm  50.5   available
HLB-019  heavy lift crane barge  5000 t lift capacity  Varne Roads, 10 nm   15.8   available
HLB-030  heavy lift crane barge  1900 t lift capacity  Varne Roads, 10 nm   37.6   available
HLB-056  heavy lift crane barge  5000 t lift capacity  Elden Bay, 440 nm    103.5  available
SVY-025  survey launch           3 crew                underway, 56 nm      3.0    available

On scene within 40.0 h: 6900 t combined lift capacity. Full fleet: 15900 t at 103.5 h.
```

Plan (repeated steps removed):

```text
1. Deploy HLB-019 heavy lift crane barge from Varne Roads to the casualty site, prioritizing its 5000 t lift capacity to meet the 27200 t requirement within the 40.0 hour window.
2. Deploy HLB-030 heavy lift crane barge from Varne Roads to the casualty site, utilizing its 1900 t lift capacity to supplement the total lift capacity.
3. Deploy HLB-010 heavy lift crane barge from Maddock Pier to the casualty site, adding its 4000 t lift capacity to the combined effort.
4. Deploy DWP-006 submersible pump from Maddock Pier to the casualty site to begin lightering operations, reducing vessel weight to facilitate refloating.
5. Deploy DIV-030 dive team from Maddock Pier to the casualty site to conduct a preliminary hull integrity and hazardous material survey before any lifting or movement begins.
6. Deploy SVY-025 survey launch to conduct seabed mapping and tide monitoring near the casualty site to assess ground reaction and refloat timing.
7. Coordinate with HLB-019, HLB-030, and HLB-010 to synchronize lifting operations, ensuring the 27200 t capacity is achieved within the 40.0 hour window.
8. Execute controlled deballasting using DWP-006 to reduce vessel draft and weight, targeting areas away from the neutral loading point to avoid hull strain.
9. Initiate refloating sequence using HLB-019, HLB-030, and HLB-010 in tandem, applying lifting loads gradually to avoid overturning the vessel.
10. Monitor tide gauge data from SVY-025 to time the refloat for optimal ground reaction and minimal friction coefficient impact.
11. Conduct final stability check using DIV-030 dive team to confirm vessel integrity before full lift initiation.
12. Execute full lift sequence using HLB-019, HLB-030, and HLB-010 to refloat the vessel, ensuring all hazardous materials are accounted for and fuel is secured prior to movement.
13. Deploy additional assets if required to meet the 27200 t lift capacity, prioritizing assets within the 40.0 hour window.
```

---

## H07

Image: `on_fire/00198.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 1400 m3/h water delivery within 2.5 hours (fire reaches fuel tanks).

Resource ledger:

ID       TYPE                CAPABILITY               LOCATION                ETA_H  STATUS
-------  ------------------  -----------------------  ----------------------  -----  ---------
BRG-033  deck cargo barge    1600 t                   underway, 12 nm         1.9    available
DWP-044  submersible pump    280 m3/h                 Elden Bay, 28 nm        1.8    available
MON-044  shore monitor       370 m3/h water delivery  Thorne Harbour, 497 nm  21.2   available
MON-056  shore monitor       380 m3/h water delivery  Elden Bay, 28 nm        2.0    available
MON-058  shore monitor       330 m3/h water delivery  Elden Bay, 28 nm        1.7    available
PMP-004  portable fire pump  63 m3/h water delivery   Brackwater, 70 nm       3.3    available

On scene within 2.5 h: 710 m3/h combined water delivery. Full fleet: 1143 m3/h at 21.2 h.
```

Plan (repeated steps removed):

```text
1. Deploy MON-058 (shore monitor, 330 m3/h) and MON-056 (shore monitor, 380 m3/h) to Elden Bay to begin water delivery to the vessel, as they are the closest available assets with sufficient capacity and ETA within 2.5 hours.
2. Deploy DWP-044 (submersible pump, 280 m3/h) to Elden Bay to augment water delivery, as it is also available and located at the same site as MON-058 and MON-056.
3. Deploy BRG-033 (deck cargo barge, 1600 t) to the scene to provide a stable platform for deploying fire suppression equipment and to assist with logistics, as it is the only asset capable of carrying heavy equipment and is available within 1.9 hours.
4. Deploy PMP-004 (portable fire pump, 63 m3/h) to Brackwater to provide additional water delivery capacity, as it is the only portable pump available and can be used to supplement the shore monitors.
5. Deploy MON-044 (shore monitor, 370 m3/h) to Thorne Harbour to provide additional water delivery capacity, as it is the only other shore monitor available and can be used to supplement the other assets.
6. Coordinate with the response crew to ensure that all assets are synchronized and that water delivery is maintained at a rate of at least 1400 m3/h to prevent the fire from reaching the fuel tanks.
7. Monitor the fire and adjust the water delivery rate as needed to ensure that the fire is suppressed and that the vessel remains stable.
8. Once the fire is extinguished, assess the vessel's stability and determine if any additional resources are needed to prevent sinking or capsizing.
9. Begin the process of removing any hazardous materials from the vessel, as the fire may have released fuel or other hazardous substances.
10. Begin the process of removing any cargo from the vessel, as the fire may have damaged the cargo or made it hazardous.
11. Begin the process of containing any released oil, as the fire may have caused oil to spill into the water.
12. Begin the process of assessing the vessel for any structural damage that may require repair or removal.
13. Begin the process of planning for the vessel's refloating or removal, as the vessel may be damaged and may require specialized equipment or techniques.
14. Begin the process of documenting the incident and reporting it to the appropriate authorities, as the vessel may be a casualty that requires further investigation or action.
```

---

## H08

Image: `on_fire/00115.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 13600 m3/h water delivery within 4.3 hours (fire reaches fuel tanks).

Resource ledger:

ID        TYPE                  CAPABILITY                LOCATION               ETA_H  STATUS
--------  --------------------  ------------------------  ---------------------  -----  ---------
BOOM-056  oil containment boom  660 m                     Saltmarsh Quay, 25 nm  3.7    available
BRG-059   deck cargo barge      1700 t                    underway, 23 nm        3.5    available
DWP-054   submersible pump      260 m3/h                  Saltmarsh Quay, 25 nm  1.7    available
FB-014    fire boat             1100 m3/h water delivery  underway, 70 nm        3.7    available
FB-031    fire boat             1200 m3/h water delivery  Varne Roads, 96 nm     5.6    available
FB-046    fire boat             600 m3/h water delivery   underway, 34 nm        1.9    available
FT-018    FiFi2 class tug       7200 m3/h water delivery  Saltmarsh Quay, 25 nm  3.6    available
FT-030    FiFi1 class tug       2400 m3/h water delivery  Saltmarsh Quay, 25 nm  3.3    available
FT-033    FiFi1 class tug       2400 m3/h water delivery  underway, 17 nm        1.5    available
FT-039    FiFi1 class tug       2400 m3/h water delivery  Saltmarsh Quay, 25 nm  2.8    available
FT-047    FiFi1 class tug       2400 m3/h water delivery  underway, 23 nm        2.0    available
FT-049    FiFi2 class tug       7200 m3/h water delivery  underway, 24 nm        1.9    available
FT-051    FiFi1 class tug       2400 m3/h water delivery  underway, 155 nm       12.1   available
FT-052    FiFi2 class tug       7200 m3/h water delivery  underway, 18 nm        1.5    available
FT-055    FiFi2 class tug       7200 m3/h water delivery  underway, 4 nm         0.5    available
FT-056    FiFi1 class tug       2400 m3/h water delivery  Port Haldane, 207 nm   16.6   available
MON-019   shore monitor         390 m3/h water delivery   Saltmarsh Quay, 25 nm  2.3    available
MON-032   shore monitor         340 m3/h water delivery   Port Haldane, 207 nm   9.1    available
PMP-003   portable fire pump    120 m3/h water delivery   Saltmarsh Quay, 25 nm  1.4    available
PMP-007   portable fire pump    65 m3/h water delivery    Saltmarsh Quay, 25 nm  1.3    available
PMP-013   portable fire pump    62 m3/h water delivery    Port Haldane, 207 nm   8.9    available
PMP-024   portable fire pump    120 m3/h water delivery   Saltmarsh Quay, 25 nm  1.6    available
PMP-026   portable fire pump    300 m3/h water delivery   Varne Roads, 96 nm     4.7    available

On scene within 4.3 h: 40795 m3/h combined water delivery. Full fleet: 47497 m3/h at 16.6 h.
```

Plan (repeated steps removed):

```text
1. Deploy FB-054 and FB-046 to provide immediate water delivery to the fire, with FB-054 arriving at T+1.7h and FB-046 at T+1.9h, targeting the vessel’s most visible fire zones to suppress flames and prevent spread to fuel tanks.
2. Activate DWP-054 at T+1.7h to supplement water delivery from shore, positioning it to pump directly into the fire zone or to support fireboats by feeding them from a fixed point.
3. Deploy FB-014 at T+3.7h to join the water delivery effort, bringing its 1100 m3/h capacity to the scene to help meet the 13600 m3/h requirement within 4.3 hours.
4. Deploy FB-031 at T+5.6h to provide additional water delivery capacity, though it arrives after the 4.3-hour window, it will be used to maintain suppression after the initial critical phase.
5. Deploy FT-055 at T+0.5h to assist with fire suppression by providing water delivery and potentially deploying foam or other fire retardants if available, prioritizing its proximity to the scene.
6. Deploy FT-047 at T+2.0h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression.
7. Deploy FT-033 at T+1.5h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression.
8. Deploy FT-049 at T+1.9h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression.
9. Deploy FT-052 at T+1.5h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression.
10. Deploy FT-039 at T+2.8h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression.
11. Deploy FT-030 at T+3.3h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression.
12. Deploy FT-051 at T+12.1h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression after the initial critical phase.
13. Deploy FT-018 at T+3.6h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression.
14. Deploy MON-019 at T+2.3h to provide additional water delivery capacity from shore, supporting the fireboats in maintaining suppression.
15. Deploy MON-032 at T+9.1h to provide additional water delivery capacity from shore, supporting the fireboats in maintaining suppression after the initial critical phase.
16. Deploy PMP-003 at T+1.4h to provide additional water delivery capacity from shore, supporting the fireboats in maintaining suppression.
17. Deploy PMP-007 at T+1.3h to provide additional water delivery capacity from shore, supporting the fireboats in maintaining suppression.
18. Deploy PMP-013 at T+8.9h to provide additional water delivery capacity from shore, supporting the fireboats in maintaining suppression after the initial critical phase.
19. Deploy PMP-024 at T+1.6h to provide additional water delivery capacity from shore, supporting the fireboats in maintaining suppression.
20. Deploy PMP-026 at T+4.7h to provide additional water delivery capacity from shore, supporting the fireboats in maintaining suppression after the initial critical phase.
21. Deploy BOOM-056 at T+3.7h to contain any oil spill from the vessel, preventing environmental contamination and ensuring safe fire suppression operations.
22. Deploy BRG-059 at T+3.5h to assist with fire suppression by providing a platform for deploying foam or other fire retardants if available, supporting the fireboats in maintaining suppression.
23. Deploy FT-056 at T+16.6h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression after the initial critical phase.
24. Deploy FT-055 at T+0.5h to assist with fire suppression and to provide additional water delivery capacity, supporting the fireboats in maintaining suppression.
```

---

## H09

Image: `capsized/00182.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 315000 t.m righting moment within 5.5 hours (progressive flooding).

Resource ledger:

ID        TYPE                                CAPABILITY                 LOCATION            ETA_H  STATUS
--------  ----------------------------------  -------------------------  ------------------  -----  ---------
BOOM-038  oil containment boom                630 m                      Kestrel Bay, 26 nm  5.1    available
DIV-037   dive team                           5 divers                   Brackwater, 57 nm   3.7    available
PBJ-031   parbuckling strand jack set         25000 t.m righting moment  Brackwater, 57 nm   18.1   available
PBJ-045   parbuckling strand jack set         15200 t.m righting moment  Kestrel Bay, 26 nm  24.7   available
RCB-008   crane barge, rated righting moment  60000 t.m righting moment  underway, 20 nm     4.2    available
RCB-015   crane barge, rated righting moment  60000 t.m righting moment  underway, 12 nm     2.7    available
RCB-016   crane barge, rated righting moment  60000 t.m righting moment  underway, 9 nm      2.0    available
RCB-026   crane barge, rated righting moment  60000 t.m righting moment  underway, 13 nm     2.8    available
RCB-027   crane barge, rated righting moment  60000 t.m righting moment  underway, 6 nm      1.3    available
RCB-030   crane barge, rated righting moment  19500 t.m righting moment  underway, 4 nm      1.0    available
RCB-033   crane barge, rated righting moment  19600 t.m righting moment  underway, 6 nm      1.3    available
RCB-037   crane barge, rated righting moment  8000 t.m righting moment   underway, 10 nm     2.1    available
RCB-048   crane barge, rated righting moment  60000 t.m righting moment  Rossway, 243 nm     80.6   available
RCB-054   crane barge, rated righting moment  34300 t.m righting moment  underway, 13 nm     2.9    available
SPN-017   sponson / buoyancy caisson set      1500 t.m righting moment   Brackwater, 57 nm   25.3   available
SPN-060   sponson / buoyancy caisson set      2800 t.m righting moment   Rossway, 243 nm     48.7   available

On scene within 5.5 h: 381400 t.m combined righting moment. Full fleet: 485900 t.m at 80.6 h.
```

Plan (repeated steps removed):

```text
1. Deploy RCB-027 (crane barge, 60000 t.m righting moment) to the scene, arriving at T+1.3 h, to provide primary righting moment support.
2. Deploy RCB-016 (crane barge, 60000 t.m righting moment) to the scene, arriving at T+2.0 h, to provide secondary righting moment support.
3. Deploy RCB-015 (crane barge, 60000 t.m righting moment) to the scene, arriving at T+2.7 h, to provide tertiary righting moment support.
4. Deploy RCB-030 (crane barge, 19500 t.m righting moment) to the scene, arriving at T+1.0 h, to provide additional righting moment support.
5. Deploy RCB-033 (crane barge, 19600 t.m righting moment) to the scene, arriving at T+1.3 h, to provide additional righting moment support.
6. Deploy RCB-037 (crane barge, 8000 t.m righting moment) to the scene, arriving at T+2.1 h, to provide supplemental righting moment support.
7. Deploy RCB-054 (crane barge, 34300 t.m righting moment) to the scene, arriving at T+2.9 h, to provide additional righting moment support.
8. Deploy RCB-008 (crane barge, 60000 t.m righting moment) to the scene, arriving at T+4.2 h, to provide additional righting moment support.
9. Deploy RCB-026 (crane barge, 60000 t.m righting moment) to the scene, arriving at T+2.8 h, to provide additional righting moment support.
10. Deploy RCB-048 (crane barge, 60000 t.m righting moment) to the scene, arriving at T+80.6 h, to provide additional righting moment support (ETA too late for this task).
11. Deploy SPN-017 (sponson / buoyancy caisson set, 1500 t.m righting moment) to the scene, arriving at T+25.3 h, to provide supplemental buoyancy support (ETA too late for this task).
12. Deploy SPN-060 (sponson / buoyancy caisson set, 2800 t.m righting moment) to the scene, arriving at T+48.7 h, to provide supplemental buoyancy support (ETA too late for this task).
13. Deploy PBJ-031 (parbuckling strand jack set, 25000 t.m righting moment) to the scene, arriving at T+18.1 h, to provide controlled righting force.
14. Deploy PBJ-045 (parbuckling strand jack set, 15200 t.m righting moment) to the scene, arriving at T+24.7 h, to provide controlled righting force.
15. Deploy DIV-037 (dive team, 5 divers) to the scene, arriving at T+3.7 h, to conduct hull integrity and hazardous material checks before righting.
16. Deploy BOOM-038 (oil containment boom, 630 m) to the scene, arriving at T+5.1 h, to contain any potential oil release during righting.
17. Coordinate all assets to apply righting moment progressively, starting with RCB-027, RCB-016, RCB-015, RCB-030, RCB-033, RCB-037, and RCB-054, with PBJ-031 and PBJ-045 providing controlled jack force.
18. Monitor tide gauge readings continuously to adjust righting force as ground reaction changes with tide.
19. Ensure all tanks are checked for fuel and hazardous cargo before any cutting or movement begins.
20. Target weight removal to neutral loading point if applicable to reduce strain on hull during righting.
21. Apply righting moment incrementally to avoid overturning the vessel further.
22. Maintain continuous communication between all assets to synchronize righting force application.
23. Once vessel is upright, secure it with mooring lines and conduct stability check against minimum righting-arm and metacentric-height criteria.
24. Offload fuel and cargo before any further movement or cutting.
25. Conduct environmental monitoring for any released oil, using side-scan or electro-acoustic sonar if needed.
26. Document all operations and prepare for post-salvage environmental assessment.
```

---

## H10

Image: `sunken/00064.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 1100 t lift capacity within 47.3 hours (weather window closes).

Resource ledger:

ID        TYPE                  CAPABILITY           LOCATION                ETA_H  STATUS
--------  --------------------  -------------------  ----------------------  -----  ---------
BOOM-052  oil containment boom  600 m                Port Arnet, 107 nm      12.2   available
BRG-043   deck cargo barge      1600 t               Port Arnet, 107 nm      21.5   available
CRN-005   floating crane        480 t lift capacity  Thorne Harbour, 26 nm   13.6   available
CRN-006   floating crane        280 t lift capacity  underway, 299 nm        50.1   available
CRN-009   floating crane        490 t lift capacity  underway, 110 nm        18.6   available
CRN-030   floating crane        500 t lift capacity  Thorne Harbour, 26 nm   8.3    available
CRN-038   floating crane        300 t lift capacity  underway, 50 nm         8.5    available
CRN-042   floating crane        250 t lift capacity  Port Arnet, 107 nm      25.2   available
CRN-045   floating crane        410 t lift capacity  underway, 12 nm         2.2    available
CRN-047   floating crane        100 t lift capacity  Corran Harbour, 361 nm  65.4   available
CRN-049   floating crane        280 t lift capacity  underway, 148 nm        24.9   available
CRN-050   floating crane        490 t lift capacity  underway, 99 nm         16.7   available
CRN-057   floating crane        100 t lift capacity  underway, 298 nm        49.8   available
DIV-001   dive team             4 divers             Corran Harbour, 361 nm  16.1   available
LB-015    lift bag set          42 t lift capacity   Thorne Harbour, 26 nm   4.5    available
LB-041    lift bag set          60 t lift capacity   Port Arnet, 107 nm      14.0   available

On scene within 47.3 h: 3302 t combined lift capacity. Full fleet: 3782 t at 65.4 h.
```

Plan (repeated steps removed):

```text
1. Deploy CRN-045 (410 t lift capacity) to the scene, arriving at T+2.2 h, to begin assessing the vessel’s condition and securing the area.
2. Deploy CRN-030 (500 t lift capacity), arriving at T+8.3 h, to provide primary lift capacity for the vessel’s refloating or righting operation.
3. Deploy CRN-009 (490 t lift capacity), arriving at T+18.6 h, to supplement the lift capacity and provide redundancy for the main lifting operation.
4. Deploy CRN-050 (490 t lift capacity), arriving at T+16.7 h, to provide additional lift capacity and support the main lifting operation.
5. Deploy CRN-005 (480 t lift capacity), arriving at T+13.6 h, to assist with the lifting operation and provide backup capacity.
6. Deploy CRN-038 (300 t lift capacity), arriving at T+8.5 h, to support the lifting operation and provide additional capacity.
7. Deploy CRN-042 (250 t lift capacity), arriving at T+25.2 h, to provide additional lift capacity for the operation.
8. Deploy CRN-049 (280 t lift capacity), arriving at T+24.9 h, to provide additional lift capacity and support the main lifting operation.
9. Deploy CRN-047 (100 t lift capacity), arriving at T+65.4 h, to provide additional lift capacity for the operation.
10. Deploy CRN-057 (100 t lift capacity), arriving at T+49.8 h, to provide additional lift capacity for the operation.
11. Deploy LB-015 (42 t lift capacity), arriving at T+4.5 h, to assist with any localized lifting or stabilization tasks.
12. Deploy LB-041 (60 t lift capacity), arriving at T+14.0 h, to assist with any localized lifting or stabilization tasks.
13. Deploy DIV-001 (4 divers), arriving at T+16.1 h, to conduct underwater inspection of the vessel’s hull, check for hazardous materials, and assess the feasibility of refloating or righting.
14. Deploy BRG-043 (1600 t deck cargo barge), arriving at T+21.5 h, to be positioned to receive and offload any cargo or hazardous materials if required.
15. Deploy BOOM-052 (600 m oil containment boom), arriving at T+12.2 h, to contain any potential oil spill during the operation.
16. Begin the refloating operation using CRN-030, CRN-009, CRN-050, and CRN-005 as the primary lifting assets, with CRN-038 and CRN-042 providing additional support.
17. Use CRN-045 and CRN-049 to assist with any additional lifting or stabilization tasks as required.
18. Use LB-015 and LB-041 to assist with any localized lifting or stabilization tasks as required.
19. Use DIV-001 to monitor the underwater conditions and provide real-time feedback to the lifting team.
20. Use BRG-043 to offload any cargo or hazardous materials as required.
21. Use BOOM-052 to contain any potential oil spill during the operation.
22. Monitor the tide gauge to track the ground reaction as the tide rises and falls.
23. Ensure all tanks are checked for fuel and hazardous cargo before any cutting or movement begins.
24. Ensure all tanks are checked for hazardous cargo before any cutting or movement begins.
25. Ensure the vessel is refloated within the 47.3-hour weather window.
26. Ensure the vessel is refloated using the combined lift capacity of 3302 t available within the 47.3-hour window.
27. Ensure the vessel is refloated using the full fleet capacity of 3782 t available at 65.4 hours if needed.
28. Ensure the vessel is refloated using the specific visual details of this vessel, not on general assumptions about vessels in this condition.
```

---

## H11

Image: `aground/00170.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 120 t bollard pull within 4.9 hours (high water).

Resource ledger:

ID       TYPE                 CAPABILITY          LOCATION               ETA_H  STATUS
-------  -------------------  ------------------  ---------------------  -----  ---------
AHT-022  anchor handling tug  100 t bollard pull  underway, 14 nm        1.3    available
BG-027   beach gear set       45 t bollard pull   Dunmore Sound, 448 nm  59.6   available
BRG-051  deck cargo barge     1800 t              underway, 11 nm        1.8    available
SVY-021  survey launch        3 crew              underway, 8 nm         0.6    available
TUG-013  harbor tug           45 t bollard pull   underway, 24 nm        2.4    available
TUG-022  harbor tug           39 t bollard pull   Port Calder, 119 nm    11.6   available
TUG-044  harbor tug           45 t bollard pull   Marrow Inlet, 29 nm    3.5    available
TUG-047  harbor tug           30 t bollard pull   underway, 41 nm        3.9    available
TUG-057  ASD tug              45 t bollard pull   underway, 46 nm        4.0    available
TUG-058  harbor tug           50 t bollard pull   Marrow Inlet, 29 nm    3.4    available
WB-002   workboat             6 t bollard pull    Port Calder, 119 nm    8.4    available
WB-011   workboat             15 t bollard pull   Marrow Inlet, 29 nm    2.6    available
WB-015   workboat             15 t bollard pull   underway, 44 nm        3.1    available
WB-023   workboat             3 t bollard pull    Port Calder, 119 nm    8.4    available
WB-034   workboat             4 t bollard pull    underway, 54 nm        3.8    available
WB-035   workboat             15 t bollard pull   Marrow Inlet, 29 nm    2.7    available

On scene within 4.9 h: 364 t combined bollard pull. Full fleet: 457 t at 59.6 h.
```

Plan (repeated steps removed):

```text
1. Deploy AHT-022 to provide 100 t bollard pull for initial refloating efforts, arriving at T+1.3 h.
2. Coordinate with TUG-044 (ETA T+3.5 h) and TUG-058 (ETA T+3.4 h) to arrive simultaneously and provide additional 90 t bollard pull for sustained refloating force.
3. Assign TUG-057 (ETA T+4.0 h) to support the refloating operation, adding 45 t bollard pull to the combined effort.
4. Position BRG-051 (ETA T+1.8 h) to assist with lightering operations if required to reduce vessel weight for refloating.
5. Deploy SVY-021 (ETA T+0.6 h) to conduct seabed survey and assess ground reaction and friction coefficient for refloating planning.
6. Monitor tide gauge readings near the vessel to track water level changes and ground reaction over time.
7. Ensure all tanks are checked for fuel and hazardous cargo before any movement or cutting begins.
8. Maintain continuous communication with the naval architect to adjust refloating strategy based on real-time tide and ground reaction data.
9. Execute controlled refloating using combined bollard pull from AHT-022, TUG-044, TUG-058, and TUG-057 to achieve the required 120 t within 4.9 hours.
10. If refloating is not achieved within 4.9 hours, initiate lightering using BRG-051 to reduce vessel weight and reattempt refloating with the same tug assets.
```

---

## H12

Image: `sunken/00048.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 340 t lift capacity within 38.8 hours (weather window closes).

Resource ledger:

ID       TYPE              CAPABILITY           LOCATION             ETA_H  STATUS
-------  ----------------  -------------------  -------------------  -----  ---------
BRG-005  deck cargo barge  1800 t               Linden Roads, 10 nm  6.9    available
CRN-040  floating crane    100 t lift capacity  underway, 55 nm      9.4    available
CRN-047  floating crane    100 t lift capacity  underway, 269 nm     45.1   available
DIV-006  dive team         6 divers             Port Calder, 100 nm  5.2    available
LB-051   lift bag set      11 t lift capacity   Linden Roads, 10 nm  2.6    available
LB-054   lift bag set      60 t lift capacity   Port Calder, 100 nm  13.1   available
SVY-029  survey launch     3 crew               underway, 170 nm     8.7    available

On scene within 38.8 h: 171 t combined lift capacity. Full fleet: 271 t at 45.1 h.
```

Plan (repeated steps removed):

```text
1. Deploy DIV-006 dive team to conduct a preliminary underwater survey of the wreck to assess structural integrity, presence of hazardous materials, and the exact location of the neutral loading point, with the goal of identifying safe access points and potential weak areas for lifting.
2. Position BRG-005 deck cargo barge to the wreck site to serve as a staging platform and to offload any remaining cargo or fuel if identified during the dive survey, reducing the vessel’s weight and stabilizing the wreck for lifting operations.
3. Deploy LB-054 lift bag set from Port Calder to the wreck site to provide the primary lifting capacity for the initial phase of the salvage, targeting the most structurally sound section of the hull identified by the dive team.
4. Deploy CRN-040 floating crane from its current location to the wreck site to provide secondary lifting support and to assist in securing and stabilizing the lift bag set during the lifting operation.
5. Use the combined lift capacity of LB-054 (60 t) and CRN-040 (100 t) to initiate the controlled lifting of the identified section of the wreck, ensuring that the lift is performed at a slow, steady rate to avoid structural failure or overturning.
6. Monitor the lift operation with SVY-029 survey launch to provide real-time data on the vessel’s movement and stability, adjusting the lifting rate and position as needed to maintain control.
7. Once the initial section is lifted and secured, deploy LB-051 lift bag set to assist in stabilizing the remaining portion of the wreck and to provide additional lift capacity if needed for the next phase of the salvage.
8. Use the combined lift capacity of LB-051 (11 t) and LB-054 (60 t) to continue the controlled lifting of the remaining sections of the wreck, ensuring that the lift is performed at a slow, steady rate to avoid structural failure or overturning.
9. Once the wreck is fully lifted and secured, deploy BRG-005 deck cargo barge to transport the salvaged sections to a designated recovery site for further processing and disposal.
10. Conduct a final inspection of the wreck site with DIV-006 dive team to ensure that all hazardous materials have been accounted for and that the site is safe for future operations.
```

---

## H13

Image: `aground/00204.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 330 t bollard pull within 4.3 hours (high water).

Resource ledger:

ID       TYPE               CAPABILITY         LOCATION             ETA_H  STATUS
-------  -----------------  -----------------  -------------------  -----  ---------
BRG-041  deck cargo barge   1700 t             underway, 18 nm      2.7    available
TUG-008  ocean salvage tug  77 t bollard pull  Varne Roads, 27 nm   4.0    available
TUG-034  ocean salvage tug  98 t bollard pull  Varne Roads, 27 nm   6.2    available
WB-004   workboat           15 t bollard pull  Linden Roads, 52 nm  3.9    available
WB-033   workboat           3 t bollard pull   underway, 146 nm     9.9    available
WB-036   workboat           3 t bollard pull   underway, 164 nm     11.1   available

On scene within 4.3 h: 92 t combined bollard pull. Full fleet: 196 t at 11.1 h.
```

Plan (repeated steps removed):

```text
1. Deploy TUG-008 and TUG-034 to the scene to provide initial bollard pull for refloating the vessel JOHN B. CADDSELL, which is aground on a rocky/gravelly shore; their combined 175 t bollard pull will be applied to the vessel’s bow and stern lines to initiate refloating as the tide rises.
2. Position BRG-041 deck cargo barge alongside the vessel to provide additional pulling force and to act as a stabilizing platform for the tug operations; its 1700 t capacity is not needed for direct pull but will assist in maintaining vessel alignment and reducing ground reaction strain.
3. Use WB-004 workboat to monitor the vessel’s hull integrity and ground reaction as the tide rises, and to assist in securing additional lines or adjusting mooring points as needed; its 15 t bollard pull will support the operation without exceeding the required 330 t.
4. Coordinate with the tide gauge to track water level changes and adjust the refloating timing to ensure maximum tide assistance; the operation will be timed to begin refloating at high water, which is within 4.3 hours.
5. Once high water is reached, apply full bollard pull from TUG-008, TUG-034, and WB-004 to initiate refloating; the combined 196 t of available pull will be sufficient to overcome the ground reaction and friction on the seabed.
6. Monitor the vessel’s response to pulling force and adjust line tension as needed to prevent hull damage or excessive strain; the naval architect’s requirement of 330 t will be met by the combined effort of the deployed assets.
7. If the vessel begins to refloat, maintain controlled pulling to avoid sudden movements that could cause further grounding or structural damage; the operation will be completed before the tide recedes.
8. After refloating, secure the vessel with additional lines and prepare for towing to a safe berth; the vessel’s cargo and hazardous materials will be assessed for any risks before movement begins.
9. Request additional resources if the refloating effort exceeds the 4.3-hour window, but proceed with the current plan as the available assets are sufficient to meet the requirement.
```

---

## H14

Image: `capsized/00019.JPG`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 9200 t.m righting moment within 6.6 hours (progressive flooding).

Resource ledger:

ID       TYPE                                CAPABILITY                LOCATION                ETA_H  STATUS
-------  ----------------------------------  ------------------------  ----------------------  -----  ---------
BRG-008  deck cargo barge                    1900 t                    underway, 15 nm         2.3    available
DIV-009  dive team                           4 divers                  Port Haldane, 26 nm     1.7    available
DWP-048  submersible pump                    290 m3/h                  Tolland Point, 108 nm   4.7    available
PBJ-020  parbuckling strand jack set         4100 t.m righting moment  Saltmarsh Quay, 523 nm  74.1   available
RCB-031  crane barge, rated righting moment  8000 t.m righting moment  underway, 18 nm         3.7    available
SPN-052  sponson / buoyancy caisson set      1700 t.m righting moment  Saltmarsh Quay, 523 nm  107.1  available
WIN-006  shore pulling winch set             800 t.m righting moment   Port Haldane, 26 nm     5.5    available
WIN-007  shore pulling winch set             40 t.m righting moment    Port Haldane, 26 nm     4.4    available
WIN-009  shore pulling winch set             800 t.m righting moment   Port Haldane, 26 nm     3.9    available
WIN-024  shore pulling winch set             800 t.m righting moment   Port Haldane, 26 nm     4.9    available
WIN-029  shore pulling winch set             94 t.m righting moment    Port Haldane, 26 nm     9.3    available
WIN-030  shore pulling winch set             800 t.m righting moment   Port Haldane, 26 nm     3.9    available
WIN-038  shore pulling winch set             40 t.m righting moment    Port Haldane, 26 nm     7.7    available
WIN-040  shore pulling winch set             720 t.m righting moment   Port Haldane, 26 nm     4.3    available
WIN-047  shore pulling winch set             650 t.m righting moment   Port Haldane, 26 nm     5.1    available
WIN-051  shore pulling winch set             40 t.m righting moment    Saltmarsh Quay, 523 nm  37.9   available
WIN-060  shore pulling winch set             770 t.m righting moment   Port Haldane, 26 nm     7.5    available

On scene within 6.6 h: 12610 t.m combined righting moment. Full fleet: 19354 t.m at 107.1 h.
```

Plan (repeated steps removed):

```text
1. Deploy the RCB-031 crane barge to the casualty site to provide the primary righting moment, as its 8000 t.m capacity exceeds the required 9200 t.m and it is the only asset with sufficient capacity to meet the deadline.
2. Coordinate the RCB-031 crane barge to begin righting operations immediately upon arrival at the site, ensuring the vessel’s stability is reassessed before initiating any movement.
3. Deploy the BRG-008 deck cargo barge to assist in stabilizing the vessel during the righting process by providing additional buoyancy or counterweight as needed.
4. Assign the DIV-009 dive team to inspect the vessel’s hull integrity and internal compartments for trapped water or hazardous materials prior to righting, ensuring safety during the operation.
5. Position the PBJ-020 parbuckling strand jack set to provide supplemental righting moment if required, though its 4100 t.m capacity is less than the RCB-031’s, it may be used to fine-tune the righting process.
6. Monitor the tide using a dedicated tide gauge to track ground reaction changes, ensuring the righting operation is timed to coincide with optimal tidal conditions for refloating.
7. Ensure all tanks are checked for fuel and hazardous cargo before any movement begins, to prevent additional risks during the righting process.
8. Maintain continuous communication between the RCB-031 crane barge and the DIV-009 dive team to coordinate the righting sequence and adjust for any unexpected hull behavior.
9. Apply controlled lifting loads to avoid overturning the vessel further, using the RCB-031 as the primary lifting asset and the PBJ-020 as a secondary support.
10. Once the vessel is righted, assess its stability and draft to determine if refloating is possible naturally or if additional lightering or tug assistance is required.
```

---

## H15

Image: `aground/00034.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 170 t bollard pull within 4.2 hours (high water).

Resource ledger:

ID       TYPE               CAPABILITY         LOCATION              ETA_H  STATUS
-------  -----------------  -----------------  --------------------  -----  ---------
BG-040   beach gear set     54 t bollard pull  Holm Harbour, 22 nm   7.3    available
BRG-057  deck cargo barge   1800 t             underway, 21 nm       3.2    available
SVY-017  survey launch      3 crew             Holm Harbour, 22 nm   2.1    available
TUG-025  harbor tug         43 t bollard pull  underway, 38 nm       3.7    available
TUG-029  ocean salvage tug  75 t bollard pull  underway, 41 nm       3.1    available
TUG-036  harbor tug         42 t bollard pull  Holm Harbour, 22 nm   2.9    available
TUG-047  harbor tug         39 t bollard pull  underway, 4 nm        0.6    available
TUG-048  harbor tug         32 t bollard pull  Linden Roads, 52 nm   5.2    available
WB-011   workboat           5 t bollard pull   Port Haldane, 569 nm  38.5   available
WB-019   workboat           6 t bollard pull   Port Haldane, 569 nm  38.3   available
WB-021   workboat           3 t bollard pull   Port Haldane, 569 nm  38.7   available
WB-026   workboat           3 t bollard pull   Linden Roads, 52 nm   3.8    available
WB-060   workboat           3 t bollard pull   Holm Harbour, 22 nm   1.9    available

On scene within 4.2 h: 205 t combined bollard pull. Full fleet: 305 t at 38.7 h.
```

Plan (repeated steps removed):

```text
1. Deploy TUG-047 (harbor tug, 39 t bollard pull) from its current location to arrive on scene within 0.6 hours to begin initial assessment and secure the vessel’s position.
2. Deploy TUG-029 (ocean salvage tug, 75 t bollard pull) to arrive on scene within 3.1 hours to provide primary refloating power.
3. Deploy TUG-036 (harbor tug, 42 t bollard pull) to arrive on scene within 2.9 hours to provide secondary refloating power and assist with tug coordination.
4. Deploy TUG-025 (harbor tug, 43 t bollard pull) to arrive on scene within 3.7 hours to provide tertiary refloating power and assist with tug coordination.
5. Deploy BG-040 (beach gear set, 54 t bollard pull) to arrive on scene within 7.3 hours to provide additional bollard pull and beach gear for securing the vessel during refloat.
6. Deploy SVY-017 (survey launch, 3 crew) to arrive on scene within 2.1 hours to conduct seabed assessment and monitor tide gauge readings for ground reaction changes.
7. Deploy BRG-057 (deck cargo barge, 1800 t) to arrive on scene within 3.2 hours to prepare for potential lightering if required to reduce weight for refloat.
8. Deploy WB-060 (workboat, 3 t bollard pull) to arrive on scene within 1.9 hours to assist with securing lines and monitoring the vessel’s stability during refloat.
9. Deploy WB-026 (workboat, 3 t bollard pull) to arrive on scene within 3.8 hours to assist with securing lines and monitoring the vessel’s stability during refloat.
10. Deploy WB-021 (workboat, 3 t bollard pull) to arrive on scene within 38.7 hours to assist with securing lines and monitoring the vessel’s stability during refloat.
11. Deploy WB-019 (workboat, 6 t bollard pull) to arrive on scene within 38.3 hours to assist with securing lines and monitoring the vessel’s stability during refloat.
12. Deploy WB-011 (workboat, 5 t bollard pull) to arrive on scene within 38.5 hours to assist with securing lines and monitoring the vessel’s stability during refloat.
13. Coordinate all tugs to apply synchronized bollard pull to refloat the vessel once high tide arrives, ensuring the neutral loading point is maintained to avoid hull strain.
14. Monitor the vessel’s draft and ground reaction as the tide rises using the survey launch and tide gauge to adjust refloat strategy as needed.
15. If lightering is required, offload cargo from BRG-057 to reduce weight and facilitate refloat.
16. Once refloat is initiated, maintain continuous tug coordination and monitor for any signs of hull damage or instability.
17. After refloat, secure the vessel to prevent further grounding and conduct a stability check before moving it to a safe berth.
18. Conduct a full inspection of all tanks for fuel and hazardous materials before any further movement or cutting begins.
19. If hazardous materials are found, initiate containment and offloading procedures before any further salvage operations.
20. Once the vessel is safely refloated and secured, prepare for transport to a dry dock for further assessment and repair.
```

---

## H16

Image: `aground/00035.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 74 t bollard pull within 5.8 hours (high water).

Resource ledger:

ID        TYPE                  CAPABILITY         LOCATION             ETA_H  STATUS
--------  --------------------  -----------------  -------------------  -----  ---------
BOOM-017  oil containment boom  570 m              Wexley Basin, 26 nm  4.1    available
TUG-007   harbor tug            33 t bollard pull  Wexley Basin, 26 nm  2.7    available
TUG-009   harbor tug            30 t bollard pull  underway, 30 nm      2.9    available
TUG-019   harbor tug            25 t bollard pull  underway, 178 nm     16.4   available
TUG-039   harbor tug            25 t bollard pull  underway, 26 nm      2.6    available
TUG-044   harbor tug            31 t bollard pull  underway, 58 nm      5.5    available
TUG-046   harbor tug            30 t bollard pull  underway, 46 nm      4.4    available
TUG-054   harbor tug            29 t bollard pull  underway, 11 nm      1.2    available
WB-031    workboat              15 t bollard pull  Wexley Basin, 26 nm  2.2    available
WB-035    workboat              3 t bollard pull   Wexley Basin, 26 nm  2.4    available
WB-042    workboat              3 t bollard pull   underway, 27 nm      2.0    available
WB-045    workboat              15 t bollard pull  underway, 34 nm      2.5    available
WB-057    workboat              6 t bollard pull   underway, 57 nm      4.0    available
WB-060    workboat              4 t bollard pull   underway, 20 nm      1.5    available

On scene within 5.8 h: 224 t combined bollard pull. Full fleet: 249 t at 16.4 h.
```

Plan (repeated steps removed):

```text
1. Deploy TUG-054 (29 t bollard pull, ETA 1.2 h) and TUG-044 (31 t bollard pull, ETA 5.5 h) to the scene to begin applying bollard pull to the grounded vessel, with TUG-054 arriving first to initiate the refloat effort.
2. Once TUG-054 is on scene, immediately deploy TUG-007 (33 t bollard pull, ETA 2.7 h) and TUG-009 (30 t bollard pull, ETA 2.9 h) to join the tug team, as both will arrive within 1.5 hours of TUG-054’s arrival.
3. After TUG-007 and TUG-009 arrive, deploy TUG-046 (30 t bollard pull, ETA 4.4 h) and TUG-039 (25 t bollard pull, ETA 2.6 h) to further increase the total bollard pull capacity, with TUG-039 arriving first among the remaining tugs.
4. Once TUG-039 is on scene, deploy WB-031 (15 t bollard pull, ETA 2.2 h) and WB-045 (15 t bollard pull, ETA 2.5 h) to assist with the refloat, as both will arrive within 0.3 hours of each other and can provide additional pulling force.
5. After WB-031 and WB-045 are on scene, deploy WB-057 (6 t bollard pull, ETA 4.0 h) and WB-060 (4 t bollard pull, ETA 1.5 h) to provide further support, with WB-060 arriving first among the remaining workboats.
6. Once WB-060 is on scene, deploy WB-042 (3 t bollard pull, ETA 2.0 h) and WB-035 (3 t bollard pull, ETA 2.4 h) to complete the workboat team, with WB-042 arriving first among the remaining workboats.
7. Monitor tide gauge readings continuously to track the changing ground reaction as the tide rises, and adjust the pulling force distribution among the tugs and workboats to maintain optimal refloat efficiency.
8. Maintain constant communication between the tugs and workboats to coordinate pulling force application and avoid overloading any single point on the hull.
9. If the vessel begins to move, maintain steady bollard pull to avoid sudden jerks that could cause the vessel to settle back onto the seabed or damage the hull.
10. Once the vessel is fully refloated, secure it with mooring lines and prepare for towing to a safe location for further assessment and potential repair.
```

---

## H17

Image: `on_fire/00169.PNG`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 1800 m3/h water delivery within 3.8 hours (fire reaches fuel tanks).

Resource ledger:

ID       TYPE                CAPABILITY               LOCATION                ETA_H  STATUS
-------  ------------------  -----------------------  ----------------------  -----  ---------
DWP-038  submersible pump    240 m3/h                 Rossway, 20 nm          1.2    available
FB-027   fire boat           500 m3/h water delivery  Thorne Harbour, 112 nm  5.9    available
FB-033   fire boat           820 m3/h water delivery  Rossway, 20 nm          1.4    available
MON-017  shore monitor       450 m3/h water delivery  Rossway, 20 nm          2.5    available
MON-030  shore monitor       410 m3/h water delivery  Rossway, 20 nm          1.8    available
MON-037  shore monitor       480 m3/h water delivery  Thorne Harbour, 112 nm  6.3    available
MON-042  shore monitor       440 m3/h water delivery  Rossway, 20 nm          2.7    available
PMP-003  portable fire pump  20 m3/h water delivery   Thorne Harbour, 112 nm  5.1    available
PMP-024  portable fire pump  42 m3/h water delivery   Rossway, 20 nm          1.1    available
PMP-050  portable fire pump  44 m3/h water delivery   Tolland Point, 520 nm   21.5   available
PMP-060  portable fire pump  36 m3/h water delivery   Thorne Harbour, 112 nm  4.8    available
SVY-036  survey launch       3 crew                   underway, 24 nm         1.4    available

On scene within 3.8 h: 2162 m3/h combined water delivery. Full fleet: 3242 m3/h at 21.5 h.
```

Plan (repeated steps removed):

```text
1. Deploy fireboat FB-033 (820 m3/h) and shore monitor MON-030 (410 m3/h) from Rossway to arrive within 1.8 hours to begin external cooling and fire suppression, prioritizing the vessel’s machinery space and fuel tank areas.
2. Deploy fireboat FB-027 (500 m3/h) and shore monitor MON-017 (450 m3/h) from Thorne Harbour to arrive within 5.9 hours to provide additional water delivery and support fire suppression from multiple angles.
3. Deploy portable fire pump PMP-024 (42 m3/h) from Rossway to arrive within 1.1 hours to supplement water delivery and assist in localized fire suppression near the vessel’s stern.
4. Deploy portable fire pump PMP-060 (36 m3/h) from Thorne Harbour to arrive within 4.8 hours to provide additional water delivery capacity as backup and to support sustained suppression.
5. Deploy submersible pump DWP-038 (240 m3/h) from Rossway to arrive within 1.2 hours to provide high-volume water delivery for fire suppression and to assist in cooling the vessel’s hull and fuel tanks.
6. Deploy shore monitor MON-042 (440 m3/h) from Rossway to arrive within 2.7 hours to provide additional water delivery capacity and support fire suppression efforts.
7. Deploy survey launch SVY-036 (3 crew) to arrive within 1.4 hours to conduct a visual and structural assessment of the vessel’s stability and damage, and to monitor fire spread and potential backdraft risks.
8. Maintain continuous water delivery from all committed assets (FB-033, MON-030, FB-027, MON-017, PMP-024, PMP-060, DWP-038, MON-042) to ensure the 1800 m3/h requirement is met within the 3.8-hour window, with a combined capacity of 2162 m3/h.
9. Once fire is contained and vessel is stabilized, reassess hull integrity and stability to determine if refloating or salvage operations can commence, prioritizing crew safety and structural integrity.
10. If vessel remains on fire or unstable, continue suppression and cooling until fire is extinguished and vessel is deemed safe for further operations, with all assets committed until the fire is fully controlled.
```

---

## H18

Image: `sunken/00126.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 1500 t lift capacity within 55.7 hours (weather window closes).

Resource ledger:

ID       TYPE              CAPABILITY           LOCATION                ETA_H  STATUS
-------  ----------------  -------------------  ----------------------  -----  ---------
BRG-053  deck cargo barge  1500 t               Corran Harbour, 17 nm   11.8   available
CRN-006  floating crane    340 t lift capacity  Corran Harbour, 17 nm   8.5    available
CRN-007  floating crane    600 t lift capacity  underway, 226 nm        37.8   available
CRN-012  floating crane    390 t lift capacity  Holm Harbour, 77 nm     16.3   available
CRN-013  floating crane    600 t lift capacity  underway, 272 nm        45.5   available
CRN-014  floating crane    330 t lift capacity  Corran Harbour, 17 nm   7.5    available
CRN-018  floating crane    600 t lift capacity  Corran Harbour, 17 nm   12.6   available
CRN-025  floating crane    410 t lift capacity  underway, 242 nm        40.5   available
CRN-040  floating crane    600 t lift capacity  Corran Harbour, 17 nm   12.4   available
CRN-041  floating crane    300 t lift capacity  Thorne Harbour, 550 nm  99.1   available
CRN-047  floating crane    550 t lift capacity  Corran Harbour, 17 nm   12.2   available
CRN-055  floating crane    210 t lift capacity  Thorne Harbour, 550 nm  100.3  available
DIV-013  dive team         6 divers             Thorne Harbour, 550 nm  22.7   available
LB-008   lift bag set      10 t lift capacity   Thorne Harbour, 550 nm  58.8   available
LB-028   lift bag set      60 t lift capacity   Holm Harbour, 77 nm     10.0   available
LB-040   lift bag set      60 t lift capacity   Holm Harbour, 77 nm     10.0   available
LB-052   lift bag set      11 t lift capacity   Holm Harbour, 77 nm     10.4   available

On scene within 55.7 h: 4551 t combined lift capacity. Full fleet: 5071 t at 100.3 h.
```

Plan (repeated steps removed):

```text
1. Deploy DIV-013 dive team to inspect the wreck for trapped water, hazardous materials, and structural integrity, with priority on identifying fuel and cargo locations before any lifting operations commence.
2. Position BRG-053 deck cargo barge at the wreck site to serve as the primary lift platform and staging area for the 1500 t lift capacity required.
3. Deploy CRN-047 floating crane (550 t lift capacity) from Corran Harbour to the wreck site, arriving at T+12.2 h, to provide the main lifting capability for the vessel’s main section.
4. Deploy CRN-018 floating crane (600 t lift capacity) from Corran Harbour to the wreck site, arriving at T+12.6 h, to assist with stabilizing the lift and providing secondary lift capacity.
5. Deploy CRN-040 floating crane (600 t lift capacity) from Corran Harbour to the wreck site, arriving at T+12.4 h, to provide additional lift capacity and redundancy for the main lift operation.
6. Deploy CRN-012 floating crane (390 t lift capacity) from Holm Harbour to the wreck site, arriving at T+16.3 h, to assist with securing the vessel and providing auxiliary lift capacity during the main lift.
7. Deploy CRN-025 floating crane (410 t lift capacity) from underway to the wreck site, arriving at T+40.5 h, to provide additional lift capacity if needed during the lift phase.
8. Deploy LB-028 lift bag set (60 t lift capacity) from Holm Harbour to the wreck site, arriving at T+10.0 h, to assist with lifting smaller sections or securing the vessel during the main lift.
9. Deploy LB-040 lift bag set (60 t lift capacity) from Holm Harbour to the wreck site, arriving at T+10.0 h, to provide additional lift capacity for auxiliary lifting tasks.
10. Conduct a coordinated lift using BRG-053 as the main platform, supported by CRN-047, CRN-018, and CRN-040, to raise the vessel’s main section from the water, with LB-028 and LB-040 used for securing and stabilizing during the lift.
11. Monitor the lift operation continuously with DIV-013 dive team to ensure structural integrity and to manage any unexpected water ingress or movement during the lift.
12. Once the vessel is partially raised, use CRN-012 and CRN-025 to assist with final positioning and stabilization before full refloat.
13. After the vessel is fully refloated, conduct a final inspection with DIV-013 to confirm the absence of hazardous materials and ensure the vessel is stable for transport.
14. Secure the vessel to BRG-053 and prepare for transport to a designated salvage yard or disposal site using the available cranes and lift bags for any remaining sections.
```

---

## H19

Image: `aground/00028.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 740 t bollard pull within 4.2 hours (high water).

Resource ledger:

ID       TYPE                 CAPABILITY          LOCATION              ETA_H  STATUS
-------  -------------------  ------------------  --------------------  -----  ---------
AHT-014  anchor handling tug  140 t bollard pull  underway, 25 nm       2.1    available
AHT-055  anchor handling tug  250 t bollard pull  underway, 14 nm       1.3    available
BG-035   beach gear set       90 t bollard pull   Wexley Basin, 376 nm  51.3   available
DIV-055  dive team            6 divers            Varne Roads, 82 nm    3.9    available
SVY-031  survey launch        3 crew              Port Ellery, 28 nm    1.8    available
TUG-002  ocean salvage tug    170 t bollard pull  underway, 27 nm       2.1    available
TUG-003  harbor tug           26 t bollard pull   Wexley Basin, 376 nm  34.8   available
TUG-017  ocean salvage tug    170 t bollard pull  Wexley Basin, 376 nm  30.5   available
TUG-047  ocean salvage tug    200 t bollard pull  underway, 15 nm       1.3    available
TUG-050  ASD tug              80 t bollard pull   underway, 23 nm       2.1    available
WB-015   workboat             15 t bollard pull   Port Ellery, 28 nm    2.2    available
WB-022   workboat             3 t bollard pull    underway, 44 nm       3.1    available
WB-050   workboat             12 t bollard pull   Varne Roads, 82 nm    5.8    available
WB-056   workboat             15 t bollard pull   underway, 20 nm       1.5    available
WB-057   workboat             15 t bollard pull   underway, 18 nm       1.4    available

On scene within 4.2 h: 888 t combined bollard pull. Full fleet: 1186 t at 51.3 h.
```

Plan (repeated steps removed):

```text
1. Deploy AHT-055 and TUG-047 to provide combined bollard pull of 420 t to initiate refloating efforts, with ETA at T+1.3 h.
2. Deploy AHT-014 and TUG-002 to provide additional bollard pull of 320 t, arriving at T+2.1 h, to supplement the initial pull and meet the 740 t requirement.
3. Position TUG-017 and TUG-050 to provide standby support with combined 280 t bollard pull, arriving at T+30.5 h and T+2.1 h respectively, to assist if ground reaction increases or refloat stalls.
4. Deploy DIV-055 to conduct hull integrity and hazardous material survey upon arrival at T+3.9 h, ensuring no fuel or toxic cargo is present before any movement begins.
5. Deploy SVY-031 to conduct seabed survey and tide monitoring at T+1.8 h to assess ground reaction and friction coefficient for refloat planning.
6. Deploy WB-056 and WB-057 to assist with securing lines and providing auxiliary bollard pull of 30 t each, arriving at T+1.5 h and T+1.4 h respectively, to support the main tugs.
7. Deploy WB-015 and WB-022 to provide additional auxiliary bollard pull of 18 t and 3 t respectively, arriving at T+2.2 h and T+3.1 h, to assist with line handling and minor adjustments.
8. Coordinate with the naval architect to monitor tide gauge data and adjust refloat timing to coincide with high water at T+4.2 h, ensuring maximum available draft and minimal ground reaction.
9. Execute controlled refloat using the combined 888 t bollard pull from AHT-055, TUG-047, AHT-014, TUG-002, TUG-017, TUG-050, WB-056, WB-057, WB-015, and WB-022, with all assets committed for the duration of the refloat operation.
10. Monitor vessel stability and ground reaction throughout the refloat, with DIV-055 providing continuous hull integrity updates and SVY-031 tracking seabed conditions to prevent further grounding or damage.
```

---

## H20

Image: `sunken/00191.JPG`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 7200 t lift capacity within 64.5 hours (weather window closes).

Resource ledger:

ID       TYPE                    CAPABILITY            LOCATION             ETA_H  STATUS
-------  ----------------------  --------------------  -------------------  -----  ---------
BRG-050  deck cargo barge        1600 t                Varne Roads, 19 nm   10.7   available
DIV-027  dive team               5 divers              Varne Roads, 19 nm   2.3    available
HLB-019  heavy lift crane barge  800 t lift capacity   Skerry Quay, 252 nm  69.0   available
HLB-042  heavy lift crane barge  1800 t lift capacity  underway, 195 nm     39.3   available
SHL-048  sheerlegs               2300 t lift capacity  Skerry Quay, 252 nm  71.3   available

On scene within 64.5 h: 1800 t combined lift capacity. Full fleet: 4900 t at 71.3 h.
```

Plan (repeated steps removed):

```text
1. Deploy HLB-042 heavy lift crane barge to the scene, arriving at T+39.3 h, to provide the primary 1800 t lift capacity required for the casualty within the 64.5 h weather window.
2. Position HLB-042 alongside the casualty and establish secure mooring lines to prevent movement during lift operations.
3. Conduct a preliminary stability and structural assessment of the casualty using DIV-027 dive team to confirm the vessel is not capsized or on fire and to identify any hazardous materials or trapped water.
4. Offload any visible fuel or hazardous cargo from the casualty’s accessible compartments before initiating lift operations, using HLB-042’s crane to remove cargo if feasible.
5. Initiate controlled deballasting or parbuckling procedures using HLB-042’s 1800 t lift capacity to right or refloat the casualty, ensuring the neutral loading point is targeted to minimize hull strain.
6. Monitor tide levels using a dedicated tide gauge to time the lift operation for optimal ground reaction and minimal draft requirements.
7. Execute the lift operation using HLB-042’s crane to raise the casualty, ensuring all tanks are checked for fuel and hazardous cargo prior to movement.
8. Secure the casualty in a stable position after refloat and prepare for transport to a safe anchorage or dry dock using HLB-042’s crane and barge capabilities.
9. Request additional resources if required beyond the 1800 t capacity, but commit to the current plan using HLB-042 as the sole lift asset within the 64.5 h window.
```

---

## H21

Image: `aground/00130.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 440 t bollard pull within 6.4 hours (high water).

Resource ledger:

ID       TYPE                 CAPABILITY          LOCATION               ETA_H  STATUS
-------  -------------------  ------------------  ---------------------  -----  ---------
AHT-009  anchor handling tug  170 t bollard pull  underway, 252 nm       19.6   available
AHT-010  anchor handling tug  200 t bollard pull  underway, 47 nm        3.8    available
AHT-060  anchor handling tug  120 t bollard pull  underway, 57 nm        4.6    available
BG-003   beach gear set       69 t bollard pull   Port Calder, 6 nm      10.2   available
DWP-030  submersible pump     230 m3/h            Westray Roads, 113 nm  5.3    available
TUG-004  ocean salvage tug    110 t bollard pull  underway, 28 nm        2.2    available
TUG-016  ocean salvage tug    77 t bollard pull   Port Calder, 6 nm      7.9    available
TUG-032  harbor tug           26 t bollard pull   Port Calder, 6 nm      0.9    available
TUG-057  ASD tug              80 t bollard pull   underway, 22 nm        2.0    available
WB-011   workboat             9 t bollard pull    Westray Roads, 113 nm  8.1    available
WB-019   workboat             3 t bollard pull    Varne Roads, 483 nm    32.4   available
WB-026   workboat             5 t bollard pull    Port Calder, 6 nm      0.7    available
WB-051   workboat             6 t bollard pull    underway, 278 nm       18.7   available

On scene within 6.4 h: 541 t combined bollard pull. Full fleet: 875 t at 32.4 h.
```

Plan (repeated steps removed):

```text
1. Deploy TUG-016 and TUG-057 to the scene to provide initial bollard pull support, arriving at T+7.9h and T+2.0h respectively, with combined capacity of 157 t bollard pull.
2. Deploy TUG-004 and TUG-032 to the scene to provide additional bollard pull support, arriving at T+2.2h and T+0.9h respectively, with combined capacity of 137 t bollard pull.
3. Deploy AHT-010 to the scene to provide critical bollard pull support, arriving at T+3.8h with 200 t bollard pull.
4. Deploy AHT-009 to the scene to provide additional bollard pull support, arriving at T+19.6h with 170 t bollard pull.
5. Deploy AHT-060 to the scene to provide additional bollard pull support, arriving at T+4.6h with 120 t bollard pull.
6. Coordinate all tugs to apply synchronized bollard pull to the vessel’s bow and stern via mooring lines or winch systems to initiate refloating, targeting the neutral loading point to minimize hull strain.
7. Monitor tide gauge readings near the vessel to track ground reaction changes as the tide rises and falls, adjusting pull force to avoid excessive strain on the hull.
8. Conduct a stability and structural integrity assessment of the vessel to confirm it can withstand the refloating forces without capsizing or breaking apart.
9. If the vessel is found to be aground on a sandy or muddy seabed, maintain a steady, controlled pull to avoid digging in or causing further damage.
10. If the vessel is found to be aground on a rocky or coral seabed, reduce pull force and consider deploying BG-003 beach gear set to assist with controlled movement if needed.
11. If the vessel is found to be aground on a hard surface, prepare for potential dredging operations to clear a channel before refloat, using available resources.
12. If the vessel is found to be capsized or sunken, immediately halt refloating operations and initiate crew rescue and hazard assessment procedures.
13. If the vessel is found to be on fire, immediately halt refloating operations and initiate fire suppression procedures before any salvage work begins.
14. Once refloating is initiated, maintain continuous monitoring of the vessel’s draft and ground reaction to ensure safe refloat within the 6.4-hour window.
15. If the vessel is successfully refloated, secure it with mooring lines and prepare for towing to a safe location for further assessment and repair.
16. If the vessel is not successfully refloated within 6.4 hours, initiate a contingency plan to secure the vessel and prepare for alternative salvage methods such as lightering or section removal.
17. If hazardous materials are detected, immediately halt all operations and initiate a hazardous material response plan before any further work begins.
18. If cargo is detected, immediately halt all operations and initiate a cargo assessment and offloading plan before any further work begins.
19. If oil is detected, immediately halt all operations and initiate an oil containment and recovery plan before any further work begins.
20. If the vessel is found to be a legacy or abandoned wreck, initiate a pollution risk assessment before deciding on further salvage actions.
```

---

## H22

Image: `aground/00148.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 130 t bollard pull within 6.5 hours (high water).

Resource ledger:

ID       TYPE                 CAPABILITY          LOCATION             ETA_H  STATUS
-------  -------------------  ------------------  -------------------  -----  ---------
AHT-030  anchor handling tug  100 t bollard pull  underway, 52 nm      4.2    available
AHT-044  anchor handling tug  100 t bollard pull  Port Haldane, 11 nm  5.0    available
DIV-008  dive team            5 divers            Skerry Quay, 111 nm  5.2    available
SVY-006  survey launch        3 crew              Port Haldane, 11 nm  1.5    available
TUG-002  harbor tug           37 t bollard pull   Port Haldane, 11 nm  1.4    available
TUG-021  harbor tug           29 t bollard pull   underway, 34 nm      3.3    available
TUG-030  harbor tug           36 t bollard pull   Port Haldane, 11 nm  1.5    available
TUG-050  ASD tug              54 t bollard pull   underway, 29 nm      2.6    available
TUG-052  harbor tug           46 t bollard pull   Skerry Quay, 111 nm  10.8   available
TUG-056  ASD tug              47 t bollard pull   underway, 46 nm      4.0    available
WB-017   workboat             3 t bollard pull    Skerry Quay, 111 nm  8.2    available
WB-022   workboat             15 t bollard pull   Ashby Haven, 311 nm  21.2   available
WB-026   workboat             14 t bollard pull   Ashby Haven, 311 nm  21.1   available
WB-054   workboat             4 t bollard pull    Port Haldane, 11 nm  1.5    available

On scene within 6.5 h: 407 t combined bollard pull. Full fleet: 485 t at 21.2 h.
```

Plan (repeated steps removed):

```text
1. Deploy AHT-030 and AHT-044 to provide 200 t bollard pull for initial refloat effort, with AHT-056 arriving at 4.0 h to supplement if needed.
2. Position TUG-050 and TUG-052 to assist with tug coordination and provide additional 100 t bollard pull capacity upon arrival at 2.6 h and 10.8 h respectively.
3. Use TUG-021 (ETA 3.3 h) and TUG-030 (ETA 1.5 h) to assist with initial positioning and stabilize the vessel during refloat preparation.
4. Coordinate SVY-006 to conduct seabed survey and tide monitoring to determine optimal refloat window and ground reaction profile.
5. Deploy DIV-008 to inspect hull integrity and check for hazardous materials or trapped water before any refloat maneuver begins.
6. Execute controlled refloat using combined bollard pull from AHT-030, AHT-044, TUG-050, TUG-052, TUG-021, and TUG-030 to achieve required 130 t within 6.5 h.
7. Monitor tide gauge readings and adjust refloat timing to ensure vessel clears grounding as high water approaches.
8. Maintain continuous communication between all tugs and AHTs to synchronize pulling forces and avoid hull strain or overturning.
9. If refloat fails, initiate lightering using WB-022 and WB-026 (ETA 21.2 h) to reduce weight, though this is not expected to be needed within 6.5 h.
10. After refloat, conduct stability assessment and ensure all tanks are secured before any further movement or cutting.
```

---

## H23

Image: `sunken/00014.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 720 t lift capacity within 49.1 hours (weather window closes).

Resource ledger:

ID       TYPE              CAPABILITY           LOCATION              ETA_H  STATUS
-------  ----------------  -------------------  --------------------  -----  ---------
BRG-009  deck cargo barge  1600 t               underway, 48 nm       7.0    available
CRN-003  floating crane    160 t lift capacity  underway, 235 nm      39.3   available
CRN-012  floating crane    100 t lift capacity  Fenwick Docks, 55 nm  17.7   available
CRN-013  floating crane    120 t lift capacity  Maddock Pier, 296 nm  55.4   available
CRN-018  floating crane    170 t lift capacity  Rossway, 6 nm         5.4    available
CRN-026  floating crane    140 t lift capacity  Maddock Pier, 296 nm  53.7   available
CRN-037  floating crane    270 t lift capacity  underway, 39 nm       6.7    available
CRN-055  floating crane    250 t lift capacity  Maddock Pier, 296 nm  56.0   available
DIV-045  dive team         5 divers             Maddock Pier, 296 nm  12.5   available
DWP-008  submersible pump  280 m3/h             Rossway, 6 nm         1.2    available
LB-020   lift bag set      19 t lift capacity   Fenwick Docks, 55 nm  6.6    available
LB-033   lift bag set      13 t lift capacity   Fenwick Docks, 55 nm  8.0    available
LB-036   lift bag set      10 t lift capacity   Rossway, 6 nm         2.2    available
LB-041   lift bag set      60 t lift capacity   Fenwick Docks, 55 nm  7.0    available
LB-043   lift bag set      11 t lift capacity   Fenwick Docks, 55 nm  7.0    available
LB-060   lift bag set      60 t lift capacity   Rossway, 6 nm         3.8    available

On scene within 49.1 h: 873 t combined lift capacity. Full fleet: 1383 t at 56.0 h.
```

Plan (repeated steps removed):

```text
1. Deploy CRN-037 (floating crane, 270 t lift capacity) from its current location to Rossway, arriving at T+6.7 h, to assess the vessel’s condition and determine if it is aground, capsized, or sunken, and to establish a safe work zone.
2. Deploy CRN-018 (floating crane, 170 t lift capacity) from Rossway, arriving at T+5.4 h, to provide secondary lift capacity and support for any refloating or righting operations.
3. Deploy BRG-009 (deck cargo barge, 1600 t capacity) from its current location to Rossway, arriving at T+7.0 h, to serve as a stable platform for staging equipment and personnel, and to potentially assist in lightering if the vessel is aground.
4. Deploy LB-060 (lift bag set, 60 t lift capacity) from Rossway, arriving at T+3.8 h, to prepare for potential underwater lifting operations if the vessel is sunken or partially submerged.
5. Deploy DWP-008 (submersible pump, 280 m3/h) from Rossway, arriving at T+1.2 h, to pump out trapped water from the vessel’s interior if it is capsized or sunken, to improve stability and safety for subsequent operations.
6. Deploy DIV-045 (dive team, 5 divers) from Maddock Pier, arriving at T+12.5 h, to conduct a detailed underwater inspection of the vessel’s hull, check for hazardous materials, and assess the feasibility of refloating or righting.
7. Deploy CRN-012 (floating crane, 100 t lift capacity) from Fenwick Docks, arriving at T+17.7 h, to provide additional lift capacity for any heavy lifting or refloating operations.
8. Deploy LB-041 (lift bag set, 60 t lift capacity) from Fenwick Docks, arriving at T+7.0 h, to support lifting operations if the vessel is aground or sunken.
9. Deploy CRN-026 (floating crane, 140 t lift capacity) from Maddock Pier, arriving at T+53.7 h, to provide additional lift capacity for any heavy lifting or refloating operations.
10. Deploy LB-036 (lift bag set, 10 t lift capacity) from Rossway, arriving at T+2.2 h, to support any underwater lifting operations if the vessel is sunken or partially submerged.
11. Deploy LB-043 (lift bag set, 11 t lift capacity) from Fenwick Docks, arriving at T+7.0 h, to support any underwater lifting operations if the vessel is sunken or partially submerged.
12. Deploy LB-033 (lift bag set, 13 t lift capacity) from Fenwick Docks, arriving at T+8.0 h, to support any underwater lifting operations if the vessel is sunken or partially submerged.
13. Deploy LB-020 (lift bag set, 19 t lift capacity) from Fenwick Docks, arriving at T+6.6 h, to support any underwater lifting operations if the vessel is sunken or partially submerged.
14. Deploy CRN-055 (floating crane, 250 t lift capacity) from Maddock Pier, arriving at T+56.0 h, to provide additional lift capacity for any heavy lifting or refloating operations.
15. Deploy CRN-003 (floating crane, 160 t lift capacity) from its current location to Rossway, arriving at T+39.3 h, to provide additional lift capacity for any heavy lifting or refloating operations.
16. Deploy CRN-013 (floating crane, 120 t lift capacity) from Maddock Pier, arriving at T+55.4 h, to provide additional lift capacity for any heavy lifting or refloating operations.
17. Coordinate all assets to begin refloating or righting operations once the vessel’s condition is confirmed and the necessary safety checks are completed, using the combined lift capacity of 873 t available within the 49.1 h weather window.
18. If the vessel is aground, use the combined lift capacity of CRN-037, CRN-018, CRN-012, CRN-026, CRN-055, CRN-003, CRN-013, and BRG-009 to apply controlled lifting forces to refloat the vessel, with LB-060, LB-041, LB-036, LB-043, LB-033, and LB-020 providing additional underwater support if needed.
19. If the vessel is capsized, use the combined lift capacity of CRN-037, CRN-018, CRN-012, CRN-026, CRN-055, CRN-003, CRN-013, and BRG-009 to apply controlled lifting forces to right the vessel, with LB-060, LB-041, LB-036, LB-043, LB-033, and LB-020 providing additional underwater support if needed.
20. If the vessel is sunken, use the combined lift capacity of CRN-037, CRN-018, CRN-012, CRN-026, CRN-055, CRN-003, CRN-013, and BRG-009 to apply controlled lifting forces to raise the vessel, with LB-060, LB-041, LB-036, LB-043, LB-033, and LB-020 providing additional underwater support if needed.
21. If the vessel is on fire, deploy fire suppression systems as needed, and then proceed with the refloating or righting operations as outlined above, using the combined lift capacity of CRN-037, CRN-018, CRN-012, CRN-026, CRN-055, CRN-003, CRN-013, and BRG-009 to apply controlled lifting forces to refloat or right the vessel, with LB-060, LB-041, LB-036, LB-043, LB-033, and LB-020 providing additional underwater support if needed.
22. Monitor the vessel’s condition and the weather window closely, and adjust the operations as needed to ensure safety and efficiency.
23. Once the vessel is refloated or righted, conduct a final inspection to ensure that all hazardous materials have been accounted for and that the vessel is stable and safe for further operations.
24. If the vessel is deemed too damaged to refloat or right, initiate a recovery plan using the combined lift capacity of CRN-037, CRN-018, CRN-012, CRN-026, CRN-055, CRN-003, CRN-013, and BRG-009 to remove the vessel in sections, with LB-060, LB-041, LB-036, LB-043, LB-033, and LB-020 providing additional underwater support if needed.
25. If the vessel is deemed a legacy or abandoned wreck, conduct a pollution risk assessment using the combined lift capacity of CRN-037, CRN-018, CRN-012, CRN-026, CRN-055, CRN-003, CRN-013, and BRG-009 to determine the best course of action for removal or in-place management, with LB-060, LB-041, LB-036, LB-043, LB-033, and LB-020 providing additional underwater support if needed.
```

---

## H24

Image: `aground/00129.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 130 t bollard pull within 3.2 hours (high water).

Resource ledger:

ID       TYPE        CAPABILITY         LOCATION            ETA_H  STATUS
-------  ----------  -----------------  ------------------  -----  ---------
DIV-007  dive team   5 divers           Marrow Inlet, 8 nm  1.4    available
TUG-017  harbor tug  33 t bollard pull  Brackwater, 133 nm  12.7   available
TUG-023  harbor tug  30 t bollard pull  underway, 14 nm     1.5    available
WB-034   workboat    3 t bollard pull   Marrow Inlet, 8 nm  1.0    available

On scene within 3.2 h: 33 t combined bollard pull. Full fleet: 66 t at 12.7 h.
```

Plan (repeated steps removed):

```text
1. Deploy TUG-023 to the casualty site to begin applying bollard pull to refloat the vessel, as it is the closest available tug with sufficient capacity (30 t) to contribute to the required 130 t within the 3.2-hour window.
2. Deploy TUG-017 to the casualty site to provide additional bollard pull, as it is the next available tug with 33 t capacity, bringing the combined pull to 63 t at T+1.5 h, with full fleet capacity of 66 t available at T+12.7 h.
3. Monitor tide gauge readings near the casualty site to track the changing ground reaction as the tide rises, ensuring refloat timing aligns with optimal water depth.
4. Conduct a stability and hull integrity assessment of the vessel to confirm it can withstand the refloat forces without further damage or capsizing.
5. Check all tanks for fuel and hazardous cargo before any movement begins, to prevent fire or explosion during refloat operations.
6. Use the combined bollard pull of TUG-023 and TUG-017 to apply controlled force to the vessel’s bow to initiate refloat, targeting the neutral loading point to minimize hull strain.
7. Once the vessel begins to rise, maintain steady bollard pull to avoid sudden movements that could cause the vessel to ground again or overturn.
8. After the vessel is fully refloated and clear of the grounding, secure it with mooring lines and conduct a final inspection for any damage or leaks.
9. Request additional assets if required to maintain the 130 t bollard pull target, as the current combined capacity of 63 t is insufficient to meet the 130 t requirement within the 3.2-hour window.
```

---

## H25

Image: `aground/00181.PNG`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 38 t bollard pull within 7.6 hours (high water).

Resource ledger:

ID       TYPE              CAPABILITY        LOCATION               ETA_H  STATUS
-------  ----------------  ----------------  ---------------------  -----  ---------
DIV-013  dive team         5 divers          Varne Roads, 16 nm     2.0    available
DWP-009  submersible pump  280 m3/h          Varne Roads, 16 nm     1.2    available
WB-005   workboat          9 t bollard pull  Varne Roads, 16 nm     1.8    available
WB-010   workboat          3 t bollard pull  underway, 42 nm        3.0    available
WB-050   workboat          6 t bollard pull  Westray Roads, 239 nm  16.3   available

On scene within 7.6 h: 12 t combined bollard pull. Full fleet: 18 t at 16.3 h.
```

Plan (repeated steps removed):

```text
1. Assess the vessel’s condition and confirm it is aground, not capsized or sunken, using visual inspection and onboard sensors; commit DIV-013 dive team to verify grounding depth and seabed type for refloat planning.
2. Deploy WB-005 workboat to position alongside the vessel and begin securing lines for refloat operations; monitor tide gauge readings near the site to track water level changes.
3. Offload any visible fuel or hazardous cargo from the vessel using DWP-009 submersible pump to reduce weight and mitigate environmental risk; target cargo removal from areas away from the neutral loading point to avoid hull strain.
4. Apply 9 t bollard pull from WB-005 to initiate refloat; monitor ground reaction and friction coefficient as tide rises, adjusting pull force as needed to avoid excessive strain.
5. Coordinate with WB-010 workboat to arrive and provide additional 3 t bollard pull support once within range (ETA 3.0 h), increasing total pull to 12 t for sustained refloat effort.
6. Maintain continuous monitoring of hull integrity and seabed conditions; if ground reaction exceeds 38 t bollard pull threshold, initiate lightering or tug assistance by scheduling WB-050 workboat (ETA 16.3 h) for deeper-draft refloat support.
7. Once vessel is free of grounding, conduct stability and structural assessment to ensure safe transit; confirm all tanks are secured and no hazardous materials are leaking before moving vessel to safe anchorage.
```

---

## H26

Image: `capsized/00002.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 2800 t.m righting moment within 15.9 hours (progressive flooding).

Resource ledger:

ID       TYPE                     CAPABILITY               LOCATION               ETA_H  STATUS
-------  -----------------------  -----------------------  ---------------------  -----  ---------
DIV-059  dive team                5 divers                 Tolland Point, 253 nm  11.9   available
SVY-015  survey launch            3 crew                   underway, 116 nm       6.0    available
WIN-005  shore pulling winch set  40 t.m righting moment   Rossway, 12 nm         5.2    available
WIN-014  shore pulling winch set  620 t.m righting moment  Port Arnet, 96 nm      12.1   available
WIN-040  shore pulling winch set  400 t.m righting moment  Tolland Point, 253 nm  21.2   available
WIN-042  shore pulling winch set  760 t.m righting moment  Port Arnet, 96 nm      13.9   available

On scene within 15.9 h: 1420 t.m combined righting moment. Full fleet: 1820 t.m at 21.2 h.
```

Plan (repeated steps removed):

```text
1. Deploy WIN-014 shore pulling winch set from Port Arnet to provide 620 t.m righting moment, arriving at T+12.1 h.
2. Deploy WIN-042 shore pulling winch set from Port Arnet to provide 760 t.m righting moment, arriving at T+13.9 h.
3. Deploy WIN-005 shore pulling winch set from Rossway to provide 40 t.m righting moment, arriving at T+5.2 h.
4. Deploy WIN-040 shore pulling winch set from Tolland Point to provide 400 t.m righting moment, arriving at T+21.2 h.
5. Deploy SVY-015 survey launch from underway location to conduct seabed assessment and ground reaction mapping, arriving at T+6.0 h.
6. Deploy DIV-059 dive team from Tolland Point to inspect hull integrity, check for hazardous materials, and identify neutral loading point, arriving at T+11.9 h.
7. Coordinate WIN-005, WIN-014, and WIN-042 to apply combined righting moment of 1820 t.m by T+13.9 h, targeting hull strain reduction at neutral loading point.
8. Monitor tide gauge readings near casualty site to track ground reaction changes as tide rises and falls, using SVY-015 survey launch for continuous seabed data.
9. Execute controlled deballasting or parbuckling maneuver using WIN-014 and WIN-042 to right vessel, with DIV-059 divers providing real-time hull integrity feedback.
10. After vessel is righted, conduct stability check against minimum righting-arm and metacentric-height criteria using naval architect’s assessment of 2800 t.m required.
11. If vessel is fully inverted, initiate upside-down refloating using WIN-005 and WIN-040 to apply controlled lifting loads without overturning further.
12. If vessel is lying on its side, initiate side refloating using WIN-014 and WIN-042 to apply controlled righting moment.
13. Once refloated, offload fuel and hazardous cargo before any cutting or movement begins, using DIV-059 divers to verify tank integrity.
14. If vessel contains cargo, account for all cargo before disturbing hull, using SVY-015 survey launch to map cargo distribution.
15. If vessel contains hazardous materials, check all tanks for hazardous cargo before any cutting or movement begins, using DIV-059 dive team.
16. If released oil is present, deploy containment booms and skimmers matched to oil behavior, using SVY-015 survey launch to locate submerged oil with side-scan sonar.
17. If vessel is a legacy or abandoned wreck, rank pollution risk using standardized risk-ranking method before deciding on removal, using DIV-059 dive team for environmental assessment.
18. If vessel is on fire, confirm affected space is clear of personnel before activating suppression systems, using SVY-015 survey launch for fire boundary mapping.
19. If machinery space fire, suppress with gas flooding; if cargo deck fire, suppress with foam, using WIN-005 and WIN-040 for external cooling if needed.
20. If superheated, smoldering space, cool before ventilating to avoid backdraft, using WIN-014 and WIN-042 for controlled cooling.
21. After fire is out, reassess hull and stability for sinking or capsizing risk, using DIV-059 dive team for structural integrity check.
22. If vessel is aground, assess if it can refloat naturally on next tide, using SVY-015 survey launch for tide gauge data.
23. If vessel is aground and requires lightering, target weight reduction at non-neutral loading points to reduce strain, using WIN-005 and WIN-040 for controlled weight removal.
24. If vessel is aground and requires tug assistance, deploy tugs to assist refloat, using WIN-014 and WIN-042 for coordinated pulling force.
25. If vessel is aground and requires dredging, schedule dredging to clear channel, using SVY-015 survey launch for seabed mapping.
26. If vessel is capsized, prioritize crew rescue before righting, using DIV-059 dive team for hand-over-hand extraction.
27. If vessel is sunken, test space for explosive gas, then oxygen, then toxic gas before any diver enters, using DIV-059 dive team for sequential testing.
28. If vessel is sunken and too deep or too damaged to raise intact, plan for crane-and-barge removal in sections, using WIN-014 and WIN-042 for section lifting.
29. If vessel is sunken and in shallow water, plan for patch and refloat, using WIN-005 and WIN-040 for hull patching.
30. If vessel is sunken and in moderate depths, plan for patch with cofferdam and pull, using WIN-014 and WIN-042 for cofferdam deployment.
31. If vessel is sunken and in deep water, plan for crane-and-barge removal in sections, using WIN-014 and WIN-042 for section lifting.
32. If vessel is sunken and in sensitive habitat, prefer diver-directed recovery over dredging, using DIV-059 dive team for environmental benefit analysis.
33. If vessel is sunken and contains hazardous materials, rank pollution risk using standardized risk-ranking method before removal, using DIV-059 dive team for risk assessment.
34. If vessel is sunken and contains oil, deploy containment matched to oil behavior, using SVY-015 survey launch for submerged oil location.
35. If vessel is sunken and contains cargo, account for all cargo before disturbing hull, using SVY-015 survey launch for cargo mapping.
36. If vessel is sunken and contains fuel, offload fuel before disturbing hull, using WIN-005 and WIN-040 for fuel transfer.
37. If vessel is sunken and contains hazardous materials, check all tanks for hazardous cargo before any cutting or movement begins, using DIV-059 dive team.
38. If vessel is sunken and contains oil, contain released oil using booms and skimmers matched to oil behavior, using SVY-015 survey launch for oil location.
```

---

## H27

Image: `aground/00207.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 980 t bollard pull within 3.6 hours (high water).

Resource ledger:

ID       TYPE                 CAPABILITY          LOCATION               ETA_H  STATUS
-------  -------------------  ------------------  ---------------------  -----  ---------
AHT-020  anchor handling tug  220 t bollard pull  underway, 18 nm        1.6    available
AHT-026  anchor handling tug  160 t bollard pull  Port Haldane, 526 nm   46.6   available
BRG-019  deck cargo barge     1700 t              underway, 7 nm         1.2    available
DIV-032  dive team            4 divers            Skerry Quay, 17 nm     2.4    available
TUG-002  harbor tug           25 t bollard pull   Skerry Quay, 17 nm     2.5    available
TUG-030  harbor tug           50 t bollard pull   underway, 74 nm        6.9    available
TUG-051  ASD tug              80 t bollard pull   Port Haldane, 526 nm   44.5   available
WB-040   workboat             3 t bollard pull    Dunmore Sound, 135 nm  9.8    available
WB-050   workboat             15 t bollard pull   underway, 280 nm       18.9   available

On scene within 3.6 h: 245 t combined bollard pull. Full fleet: 553 t at 46.6 h.
```

Plan (repeated steps removed):

```text
1. Deploy AHT-020 to the casualty site to provide initial 220 t bollard pull for refloating efforts, arriving at T+1.6 h.
2. Deploy AHT-026 to the casualty site to provide additional 160 t bollard pull, arriving at T+46.6 h (outside the 3.6 h window).
3. Deploy TUG-030 to the casualty site to provide 50 t bollard pull, arriving at T+6.9 h (outside the 3.6 h window).
4. Deploy TUG-051 to the casualty site to provide 80 t bollard pull, arriving at T+44.5 h (outside the 3.6 h window).
5. Deploy TUG-002 to the casualty site to provide 25 t bollard pull, arriving at T+2.5 h.
6. Deploy WB-050 to the casualty site to provide 15 t bollard pull, arriving at T+18.9 h (outside the 3.6 h window).
7. Deploy BRG-019 to the casualty site to provide 1700 t cargo capacity for lightering operations if required, arriving at T+1.2 h.
8. Deploy DIV-032 to the casualty site to conduct underwater inspection for hazardous materials, structural integrity, and tank conditions, arriving at T+2.4 h.
9. Use AHT-020 and TUG-002 to apply combined 245 t bollard pull within the 3.6 h window to initiate refloating.
10. Monitor tide gauge readings and ground reaction forces during refloating to adjust pulling strategy as needed.
11. If lightering is required, use BRG-019 to remove cargo to reduce weight and assist refloating.
12. If hazardous materials are confirmed, isolate affected areas and coordinate with environmental response teams for safe handling.
13. If the vessel is found to be aground on a sandy seabed, maintain controlled pulling to avoid excessive strain or further grounding.
14. If the vessel is found to be capsized or sunken, reassess the situation and adjust the plan for righting or recovery operations.
15. If the vessel is found to be on fire, activate fire suppression systems and evacuate personnel before initiating refloating.
16. Once refloating is initiated, maintain continuous pulling force until the vessel clears the grounding or capsizing condition.
17. After refloating, conduct a stability assessment and ensure the vessel is secure before releasing the tug forces.
18. If the vessel is found to be aground on a hard surface, request additional resources for dredging or tug assistance beyond the 3.6 h window.
19. If the vessel is found to be capsized, prioritize crew rescue before attempting to right the vessel.
20. If the vessel is found to be sunken, initiate recovery operations using patching, cofferdams, or crane-and-barge methods as appropriate.
21. If the vessel is found to be on fire, initiate suppression operations using foam or gas flooding as appropriate.
22. If the vessel is found to be aground, monitor the tide gauge to determine the optimal time for refloating.
23. If the vessel is found to be capsized, conduct a stability check before attempting to right the vessel.
24. If the vessel is found to be sunken, conduct sequential gas testing before any diver enters or hot work begins.
25. If the vessel is found to be on fire, confirm the affected space is clear of personnel before activating any suppression system.
26. If the vessel is found to be aground, assess the seabed type to determine the appropriate refloating method.
27. If the vessel is found to be capsized, determine whether the hull is fully inverted or lying on its side to select the appropriate righting method.
28. If the vessel is found to be sunken, determine the depth and condition of the hull to select the appropriate recovery method.
29. If the vessel is found to be on fire, determine the type of fuel or cargo to select the appropriate foam type.
30. If the vessel is found to be aground, assess the draft and size to determine the resources needed for refloating.
31. If the vessel is found to be capsized, assess the size to determine the righting method.
32. If the vessel is found to be sunken, assess the depth to determine the recovery method.
33. If the vessel is found to be on fire, assess the fire location to determine the suppression method.
34. If the vessel is found to be aground, assess the ground reaction and friction coefficient to determine the pulling force needed.
35. If the vessel is found to be capsized, assess the stability criteria to determine the righting method.
36. If the vessel is found to be sunken, assess the depth and condition to determine the recovery method.
```

---

## H28

Image: `aground/00147.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 1100 t bollard pull within 7.8 hours (high water).

Resource ledger:

ID        TYPE                  CAPABILITY          LOCATION                ETA_H  STATUS
--------  --------------------  ------------------  ----------------------  -----  ---------
AHT-035   anchor handling tug   250 t bollard pull  underway, 31 nm         2.6    available
BOOM-042  oil containment boom  650 m               Saltmarsh Quay, 13 nm   2.9    available
TUG-003   ocean salvage tug     180 t bollard pull  Corran Harbour, 118 nm  12.4   available
TUG-037   harbor tug            25 t bollard pull   Saltmarsh Quay, 13 nm   1.7    available

On scene within 7.8 h: 275 t combined bollard pull. Full fleet: 455 t at 12.4 h.
```

Plan (repeated steps removed):

```text
1. Deploy TUG-037 to the vessel’s immediate vicinity to assess grounding severity and secure initial positioning, using its 25 t bollard pull to stabilize the vessel against wave action while awaiting larger tugs.
2. Deploy AHT-035 to the vessel’s starboard side to apply 250 t bollard pull in coordination with TUG-037, initiating controlled refloat effort as tide rises, targeting the neutral loading point to minimize hull strain.
3. Deploy TUG-003 to the vessel’s port side to apply 180 t bollard pull, creating a balanced pulling force across the vessel’s hull to prevent uneven stress and potential structural failure during refloat.
4. Monitor tide gauge readings near the vessel to track ground reaction changes and adjust tug positioning and pulling force as the tide rises, ensuring refloat is initiated at optimal water depth.
5. Conduct a hull integrity and cargo survey using divers or remote inspection tools to confirm no hazardous materials or fuel leaks are present before any movement begins.
6. Coordinate with the naval architect to verify the vessel’s draft and seabed composition, ensuring the pulling force (455 t total) is sufficient for the ground reaction and seabed type (rocky), and that refloat is feasible within the 7.8-hour window.
7. Maintain continuous communication between all tugs and the response crew to synchronize pulling force and timing, ensuring no single tug overloads its capacity or causes hull deformation.
8. If refloat is not achieved by high water, initiate lightering operations to reduce vessel weight by offloading non-essential cargo or ballast, using available resources to prepare for extended refloat or alternative recovery methods.
9. If refloat fails, transition to a crane-and-barge recovery plan for the vessel’s sections, prioritizing environmental protection and hazardous material containment using BOOM-042 to contain any potential oil release during dismantling.
10. Document all salvage operations, including tide data, tug force application, and structural assessments, for post-operation analysis and regulatory compliance.
```

---

## H29

Image: `capsized/00214.JPG`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 72700 t.m righting moment within 17.9 hours (progressive flooding).

Resource ledger:

ID        TYPE                                CAPABILITY                 LOCATION              ETA_H  STATUS
--------  ----------------------------------  -------------------------  --------------------  -----  ---------
BOOM-058  oil containment boom                600 m                      Port Calder, 96 nm    12.7   available
DIV-017   dive team                           6 divers                   Port Calder, 96 nm    5.2    available
PBJ-045   parbuckling strand jack set         16000 t.m righting moment  Rossway, 7 nm         9.9    available
PBJ-050   parbuckling strand jack set         20300 t.m righting moment  Rossway, 7 nm         14.1   available
PBJ-054   parbuckling strand jack set         11500 t.m righting moment  Port Calder, 96 nm    30.2   available
PBJ-057   parbuckling strand jack set         2900 t.m righting moment   Rossway, 7 nm         9.6    available
RCB-013   crane barge, rated righting moment  25900 t.m righting moment  Rossway, 7 nm         13.5   available
RCB-020   crane barge, rated righting moment  18500 t.m righting moment  Rossway, 7 nm         15.4   available
RCB-024   crane barge, rated righting moment  28000 t.m righting moment  Rossway, 7 nm         14.6   available
RCB-025   crane barge, rated righting moment  30900 t.m righting moment  Rossway, 7 nm         14.8   available
RCB-040   crane barge, rated righting moment  29900 t.m righting moment  Rossway, 7 nm         13.9   available
RCB-041   crane barge, rated righting moment  27800 t.m righting moment  Rossway, 7 nm         16.8   available
RCB-055   crane barge, rated righting moment  10600 t.m righting moment  Rossway, 7 nm         26.1   available
SPN-041   sponson / buoyancy caisson set      1000 t.m righting moment   Rossway, 7 nm         9.9    available
SPN-045   sponson / buoyancy caisson set      1200 t.m righting moment   Rossway, 7 nm         24.1   available
WIN-006   shore pulling winch set             40 t.m righting moment     Rossway, 7 nm         6.3    available
WIN-009   shore pulling winch set             800 t.m righting moment    Port Calder, 96 nm    11.4   available
WIN-016   shore pulling winch set             49 t.m righting moment     Rossway, 7 nm         4.0    available
WIN-018   shore pulling winch set             800 t.m righting moment    Port Calder, 96 nm    14.4   available
WIN-027   shore pulling winch set             100 t.m righting moment    Holm Harbour, 431 nm  31.3   available
WIN-029   shore pulling winch set             800 t.m righting moment    Holm Harbour, 431 nm  36.6   available
WIN-033   shore pulling winch set             40 t.m righting moment     Holm Harbour, 431 nm  31.2   available
WIN-050   shore pulling winch set             100 t.m righting moment    Holm Harbour, 431 nm  31.8   available

On scene within 17.9 h: 202889 t.m combined righting moment. Full fleet: 227229 t.m at 36.6 h.
```

Plan (repeated steps removed):

```text
1. Deploy the dive team DIV-017 to inspect the vessel JINDAL VECTOR for trapped water, structural integrity, and presence of hazardous materials before any righting operations commence.
2. Activate the parbuckling strand jack set PBJ-050 (20300 t.m righting moment) and crane barge RCB-025 (30900 t.m righting moment) to provide primary righting force, as both are on scene within the 17.9-hour window and their combined capacity exceeds the required 72700 t.m.
3. Deploy the crane barge RCB-041 (27800 t.m righting moment) as a secondary righting asset to supplement the primary set and ensure sufficient margin for the required 72700 t.m.
4. Deploy the parbuckling strand jack set PBJ-057 (2900 t.m righting moment) to provide additional localized righting force, targeting the neutral loading point on the hull to minimize strain during the righting process.
5. Deploy the sponson / buoyancy caisson set SPN-041 (1000 t.m righting moment) to provide auxiliary buoyancy and assist in stabilizing the vessel during the righting sequence.
6. Deploy the shore pulling winch set WIN-009 (800 t.m righting moment) to provide additional controlled pulling force to assist in the righting process, ensuring the vessel does not overturn further.
7. Monitor the tide using a dedicated tide gauge to track ground reaction changes as the tide rises and falls, adjusting the righting sequence as necessary to optimize refloat conditions.
8. Once the vessel is righted, deploy the crane barge RCB-024 (28000 t.m righting moment) to assist in refloating the vessel if additional righting moment is required.
9. Deploy the crane barge RCB-040 (29900 t.m righting moment) to provide additional righting force if needed during the refloating phase.
10. Deploy the crane barge RCB-013 (25900 t.m righting moment) to assist in the refloating process if the vessel requires additional support.
11. Deploy the crane barge RCB-020 (18500 t.m righting moment) to provide additional righting force during the refloating phase.
12. Deploy the crane barge RCB-055 (10600 t.m righting moment) to provide additional righting force if needed during the refloating phase.
13. Deploy the shore pulling winch set WIN-018 (800 t.m righting moment) to provide additional controlled pulling force during the refloating process.
14. Deploy the shore pulling winch set WIN-029 (800 t.m righting moment) to provide additional controlled pulling force during the refloating process.
15. Deploy the shore pulling winch set WIN-033 (40 t.m righting moment) to provide additional controlled pulling force during the refloating process.
16. Deploy the shore pulling winch set WIN-050 (100 t.m righting moment) to provide additional controlled pulling force during the refloating process.
17. Deploy the oil containment boom BOOM-058 to contain any potential oil spill during the righting and refloating operations.
18. Once the vessel is refloated, conduct a full stability check against minimum righting-arm and metacentric-height criteria to ensure the vessel is safe for further operations.
19. Offload any fuel or hazardous cargo from the vessel before any further movement or cutting begins.
20. Account for all cargo on the vessel before any further movement or cutting begins.
21. Conduct a sequential testing for explosive gas, then oxygen, then toxic gas in any affected spaces before any diver enters or hot work begins.
22. If any oil is released, deploy the oil containment boom BOOM-058 to contain the spill and prevent environmental damage.
23. If the vessel is too deep or too damaged to raise intact, deploy the crane barge RCB-025 (30900 t.m righting moment) and crane barge RCB-041 (27800 t.m righting moment) to assist in crane-and-barge removal in sections.
24. If the vessel is a legacy or abandoned wreck, rank the pollution risk using a standardized risk-ranking method before deciding whether to remove it.
25. If the vessel is on fire, confirm the affected space is clear of personnel before activating any fixed suppression system.
26. If the vessel is on fire, suppress a machinery space fire by gas flooding and a cargo deck fire by foam.
27. If the vessel is on fire, use fireboat monitors for external boundary cooling of a space adjacent to the fire.
28. If the vessel is on fire, avoid ventilating or opening a superheated, smoldering space before it is cooled to prevent backdraft.
29. If the vessel is on fire, reassess the hull and stability once the fire is out, as fire damage can leave the vessel exposed to sinking or capsizing.
30. If the vessel is aground, check all tanks for fuel and hazardous cargo before any cutting or movement begins.
31. If the vessel is aground, target weight removal to areas other than the neutral loading point to reduce strain on the hull.
32. If the vessel is aground, use tug assistance to refloat if the vessel is deeper-draft.
33. If the vessel is aground, use dredging to clear a channel before refloat if the grounding is hard.
34. If the vessel is aground, use lightering to reduce weight before refloat if the vessel is large.
35. If the vessel is aground, use the tide to refloat the vessel naturally if possible.
36. If the vessel is capsized, prioritize crew rescue before attempting to right the vessel.
37. If the vessel is capsized, use a hand-over-hand technique without kicking for crew exiting the hull to avoid injuring the next person out.
38. If the vessel is capsized, clear trapped water before righting.
39. If the vessel is capsized, use manual or crane righting for small craft, controlled deballasting or parbuckling for larger ones.
40. If the vessel is capsized, use lifting loads controlled to avoid overturning the vessel further.
41. If the vessel is sunken, use patch and refloat in shallow water, patch with a cofferdam and pull in moderate depths, or crane-and-barge removal in sections if the hull is too deep or too damaged to raise intact.
42. If the vessel is sunken, use diver-directed recovery over dredging in sensitive habitat, weighed through a net environmental benefit analysis.
43. If the vessel is sunken, use side-scan or electro-acoustic sonar to locate submerged oil that isn't visible from the surface.
44. If the vessel is sunken, use a standardized risk-ranking method to rank the pollution risk of a legacy or abandoned wreck before deciding whether to remove it.
45. If the vessel is sunken, use a dedicated tide gauge to track how the ground reaction changes as the tide rises and falls.
46. If the vessel is sunken, use a neutral loading point to target weight removal to reduce strain on the hull.
47. If the vessel is sunken, use a pulling force that depends on the ground reaction and a friction coefficient specific to the seabed type.
```

---

## H30

Image: `capsized/00146.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 189500 t.m righting moment within 4.3 hours (progressive flooding).

Resource ledger:

ID       TYPE                                CAPABILITY                 LOCATION              ETA_H  STATUS
-------  ----------------------------------  -------------------------  --------------------  -----  ---------
BRG-009  deck cargo barge                    1900 t                     underway, 23 nm       3.5    available
DIV-011  dive team                           4 divers                   Fenwick Docks, 25 nm  1.8    available
RCB-024  crane barge, rated righting moment  52300 t.m righting moment  underway, 12 nm       2.6    available
RCB-059  crane barge, rated righting moment  37900 t.m righting moment  Port Arnet, 40 nm     38.8   available
SVY-054  survey launch                       3 crew                     Fenwick Docks, 25 nm  1.8    available
WIN-015  shore pulling winch set             150 t.m righting moment    Port Arnet, 40 nm     5.6    available
WIN-017  shore pulling winch set             40 t.m righting moment     Fenwick Docks, 25 nm  7.1    available

On scene within 4.3 h: 52300 t.m combined righting moment. Full fleet: 90390 t.m at 38.8 h.
```

Plan (repeated steps removed):

```text
1. Deploy RCB-024 crane barge to the casualty site to begin righting operations, as it is the only asset on scene within the 4.3-hour window and has sufficient righting moment (52300 t.m) to meet the required 189500 t.m.
2. Coordinate with DIV-011 dive team to conduct a hull integrity and trapped water assessment prior to any righting maneuver, ensuring safe entry and clearance of water before applying righting forces.
3. Position BRG-009 deck cargo barge to assist with lightering operations if necessary, to reduce vessel weight and strain on the hull during righting, though this is not immediately required given the current righting moment capacity.
4. Monitor tide gauge readings near the casualty site to track ground reaction changes as the tide rises, ensuring optimal timing for righting to minimize seabed friction and maximize refloat potential.
5. Execute controlled deballasting or parbuckling procedure using RCB-024 crane barge, applying the 52300 t.m righting moment in a progressive manner to avoid overturning the vessel further.
6. Once the vessel is upright, conduct a stability check against minimum righting-arm and metacentric-height criteria to confirm safe operation before any further movement or cargo handling.
7. After righting, assess for hazardous materials or fuel presence and initiate offloading procedures if necessary, using BRG-009 deck cargo barge or other available assets for safe removal.
8. Conduct a full hull inspection and structural assessment to determine if any additional repairs or support are needed before the vessel can be safely refloated or towed to port.
9. Request additional assets (e.g., RCB-059, WIN-015, WIN-017) to be deployed for post-righting stabilization and refloat operations, though they are not on scene within the 4.3-hour window and will be committed after the initial righting is complete.
```

---

## H31

Image: `sunken/00094.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 22000 t lift capacity within 69.4 hours (weather window closes).

Resource ledger:

ID        TYPE                    CAPABILITY            LOCATION              ETA_H  STATUS
--------  ----------------------  --------------------  --------------------  -----  ---------
BOOM-013  oil containment boom    630 m                 Rossway, 102 nm       13.9   available
CRN-009   floating crane          490 t lift capacity   Rossway, 102 nm       26.6   available
CRN-012   floating crane          500 t lift capacity   Rossway, 102 nm       21.0   available
CRN-049   floating crane          410 t lift capacity   underway, 256 nm      42.8   available
DIV-008   dive team               5 divers              Dunmore Sound, 30 nm  2.8    available
HLB-016   heavy lift crane barge  5000 t lift capacity  Port Haldane, 468 nm  116.7  available
HLB-020   heavy lift crane barge  5000 t lift capacity  Dunmore Sound, 30 nm  40.7   available
HLB-039   heavy lift crane barge  5000 t lift capacity  Port Haldane, 468 nm  110.5  available
HLB-053   heavy lift crane barge  5000 t lift capacity  Rossway, 102 nm       39.6   available
HLB-054   heavy lift crane barge  5000 t lift capacity  Rossway, 102 nm       50.5   available
HLB-057   heavy lift crane barge  5000 t lift capacity  Rossway, 102 nm       47.3   available
HLB-060   heavy lift crane barge  5000 t lift capacity  Dunmore Sound, 30 nm  36.6   available
LB-031    lift bag set            11 t lift capacity    Port Haldane, 468 nm  49.6   available
SHL-035   sheerlegs               2400 t lift capacity  Port Haldane, 468 nm  108.8  available
SHL-052   sheerlegs               1200 t lift capacity  Port Haldane, 468 nm  128.6  available
SVY-037   survey launch           3 crew                underway, 222 nm      11.3   available

On scene within 69.4 h: 26411 t combined lift capacity. Full fleet: 40011 t at 128.6 h.
```

Plan (repeated steps removed):

```text
1. Assess the vessel’s condition and confirm it is capsized, not aground or sunken, based on visual evidence of the hull inverted and water cascading from its structure; commit to a capsized vessel righting plan.
2. Deploy DIV-008 dive team to inspect the capsized vessel’s interior for trapped water, structural integrity, and presence of hazardous materials or fuel; prioritize crew safety using hand-over-hand exit technique if needed.
3. Conduct a stability analysis using naval architect’s criteria to determine if the vessel can be righted safely without exceeding minimum righting-arm or metacentric-height thresholds; confirm no explosive or toxic gases are present before any movement.
4. Use HLB-020 heavy lift crane barge (ETA 40.7 h) to initiate controlled deballasting or parbuckling method to right the vessel, as it is large and capsized; target weight removal away from the neutral loading point to avoid strain.
5. Deploy HLB-053 heavy lift crane barge (ETA 39.6 h) and HLB-054 heavy lift crane barge (ETA 50.5 h) to provide additional lift capacity and redundancy for the righting operation; ensure both are on scene before initiating the main lift.
6. Coordinate with HLB-060 heavy lift crane barge (ETA 36.6 h) to provide backup lift capacity if required during the righting phase; confirm all cranes are synchronized to avoid overturning the vessel further.
7. Use CRN-012 floating crane (ETA 21.0 h) and CRN-049 floating crane (ETA 42.8 h) to assist with securing and stabilizing the vessel during the righting process; ensure they are positioned to handle ground reaction forces.
8. Deploy BOOM-013 oil containment boom (ETA 13.9 h) to contain any potential oil spill during the righting operation; position it around the vessel’s perimeter to prevent surface oil from spreading.
9. Use SHL-035 sheerlegs (ETA 108.8 h) to provide additional lifting points and support during the righting phase; ensure they are deployed only after the vessel is stabilized.
10. Monitor tide gauge readings near the site to track ground reaction changes as the tide rises and falls; adjust righting method if necessary based on seabed type and tide conditions.
11. Confirm all hazardous materials and fuel are secured or offloaded before any cutting or movement begins; use HLB-039 heavy lift crane barge (ETA 110.5 h) to assist with fuel removal if needed.
12. Once the vessel is righted, use HLB-057 heavy lift crane barge (ETA 47.3 h) and HLB-054 heavy lift crane barge (ETA 50.5 h) to secure and refloat the vessel; ensure all tanks are checked for fuel and hazardous cargo before movement.
13. Use CRN-009 floating crane (ETA 26.6 h) to assist with final positioning and stabilization of the vessel after righting; ensure it is committed for the duration of the refloat.
14. Deploy SVY-037 survey launch (ETA 11.3 h) to conduct post-righting survey and confirm vessel stability and environmental impact; ensure it is available for continuous monitoring.
15. Use HLB-016 heavy lift crane barge (ETA 116.7 h) as a reserve asset for any additional lift capacity required during the refloat phase; ensure it is on standby.
16. Confirm all assets are committed for the duration of the task and no other operations are scheduled for them; ensure all resources are synchronized to meet the 22000 t lift capacity requirement within 69.4 hours.
17. Request additional resources if the combined lift capacity falls short of the 22000 t requirement; ensure all assets are available and on scene before initiating the righting operation.
18. Monitor weather conditions and adjust the plan if the weather window closes before the task is completed; ensure all assets are prepared for any weather-related delays.
19. Conduct a final safety check before initiating the righting operation; ensure all personnel are briefed and all equipment is tested.
20. Execute the righting operation using the committed assets and follow the plan to the letter; ensure all steps are completed in sequence and no steps are skipped.
```

---

## H32

Image: `aground/00039.JPG`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 73 t bollard pull within 7.8 hours (high water).

Resource ledger:

ID       TYPE              CAPABILITY         LOCATION           ETA_H  STATUS
-------  ----------------  -----------------  -----------------  -----  ---------
BRG-034  deck cargo barge  1600 t             Port Ellery, 7 nm  4.3    available
TUG-033  harbor tug        26 t bollard pull  underway, 173 nm   15.9   available
WB-017   workboat          3 t bollard pull   underway, 68 nm    4.7    available
WB-025   workboat          3 t bollard pull   Port Ellery, 7 nm  0.8    available
WB-028   workboat          15 t bollard pull  Port Ellery, 7 nm  0.8    available
WB-038   workboat          15 t bollard pull  underway, 81 nm    5.6    available
WB-040   workboat          3 t bollard pull   Port Ellery, 7 nm  1.0    available

On scene within 7.8 h: 39 t combined bollard pull. Full fleet: 65 t at 15.9 h.
```

Plan (repeated steps removed):

```text
1. Deploy WB-025 and WB-028 from Port Ellery to arrive on scene by T+0.8 h and T+0.8 h respectively, to provide initial 18 t bollard pull for securing the vessel and preparing for refloat.
2. Deploy WB-040 from Port Ellery to arrive on scene by T+1.0 h, to provide additional 3 t bollard pull for stabilization and assisting the primary tug effort.
3. Deploy BRG-034 deck cargo barge from Port Ellery to arrive on scene by T+4.3 h, to be positioned for lightering operations if required to reduce vessel weight for refloat.
4. Deploy TUG-033 harbor tug from its current location to arrive on scene by T+15.9 h, to provide 26 t bollard pull for the main refloat effort once the tide is favorable.
5. Coordinate with the naval architect to confirm the vessel is aground and requires 73 t bollard pull at high water, and ensure all tanks are checked for fuel and hazardous cargo before any movement begins.
6. Monitor tide gauge readings near the site to track ground reaction changes as the tide rises and falls, and adjust refloat timing to coincide with high water.
7. Use the combined bollard pull of WB-025, WB-028, WB-040, and TUG-033 to apply controlled pulling force to free the vessel once the tide reaches its peak, with the workboats providing initial tension and the harbor tug providing the main pulling force.
8. If the vessel does not refloat naturally, perform lightering operations using BRG-034 to reduce weight and reattempt refloat with the full tug and workboat team.
9. If the vessel remains grounded after lightering, initiate dredging operations to clear the channel if necessary, using the available assets and coordinating with the naval architect for seabed type and friction coefficient assessment.
10. Once the vessel is refloated, conduct a stability check and ensure all hazardous materials are secured before proceeding with further operations.
```

---

## H33

Image: `capsized/00183.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 5800 t.m righting moment within 15.8 hours (progressive flooding).

Resource ledger:

ID       TYPE                                CAPABILITY                LOCATION                ETA_H  STATUS
-------  ----------------------------------  ------------------------  ----------------------  -----  ---------
DIV-023  dive team                           6 divers                  Maddock Pier, 23 nm     1.7    available
DWP-027  submersible pump                    230 m3/h                  Maddock Pier, 23 nm     2.2    available
PBJ-014  parbuckling strand jack set         2500 t.m righting moment  Maddock Pier, 23 nm     20.5   available
PBJ-052  parbuckling strand jack set         2600 t.m righting moment  Maddock Pier, 23 nm     12.9   available
RCB-060  crane barge, rated righting moment  8000 t.m righting moment  underway, 54 nm         11.1   available
SPN-023  sponson / buoyancy caisson set      1600 t.m righting moment  Maddock Pier, 23 nm     12.6   available
SPN-029  sponson / buoyancy caisson set      2600 t.m righting moment  Maddock Pier, 23 nm     14.9   available
SPN-031  sponson / buoyancy caisson set      1500 t.m righting moment  Maddock Pier, 23 nm     12.4   available
SPN-032  sponson / buoyancy caisson set      1000 t.m righting moment  Saltmarsh Quay, 482 nm  92.4   available
SPN-039  sponson / buoyancy caisson set      1400 t.m righting moment  Maddock Pier, 23 nm     13.5   available
WIN-002  shore pulling winch set             150 t.m righting moment   Saltmarsh Quay, 482 nm  35.3   available
WIN-040  shore pulling winch set             800 t.m righting moment   Saltmarsh Quay, 482 nm  38.5   available

On scene within 15.8 h: 17700 t.m combined righting moment. Full fleet: 22150 t.m at 92.4 h.
```

Plan (repeated steps removed):

```text
1. Deploy the RCB-060 crane barge to the scene, as it is the only asset with sufficient righting moment (8000 t.m) and ETA within the 15.8-hour window, to initiate the primary refloating effort.
2. Position the RCB-060 crane barge to engage the vessel’s hull at the neutral loading point, if identifiable, to minimize strain during refloating.
3. Activate the DWP-027 submersible pump to offload any remaining fuel or hazardous cargo from the vessel’s tanks before any movement begins.
4. Deploy the SPN-029 sponson / buoyancy caisson set (2600 t.m righting moment) to provide additional buoyancy and stabilize the vessel during the refloating process.
5. Deploy the SPN-031 sponson / buoyancy caisson set (1500 t.m righting moment) to supplement the buoyancy provided by SPN-029 and distribute lifting loads evenly.
6. Deploy the SPN-023 sponson / buoyancy caisson set (1600 t.m righting moment) to further augment buoyancy and support the refloating effort.
7. Deploy the SPN-039 sponson / buoyancy caisson set (1400 t.m righting moment) to complete the buoyancy array and ensure sufficient righting moment is available.
8. Coordinate the RCB-060 crane barge with the SPN-029, SPN-031, SPN-023, and SPN-039 sponsons to apply controlled lifting loads, avoiding overturning the vessel further.
9. Monitor the tide gauge near the site to track ground reaction changes as the tide rises and adjust lifting loads accordingly.
10. Once the vessel is refloated, deploy the DIV-023 dive team to inspect the hull for any remaining hazardous materials or structural integrity issues.
```

---

## H34

Image: `sunken/00203.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 760 t lift capacity within 29.3 hours (weather window closes).

Resource ledger:

ID       TYPE              CAPABILITY           LOCATION             ETA_H  STATUS
-------  ----------------  -------------------  -------------------  -----  ---------
BRG-017  deck cargo barge  1800 t               Rossway, 22 nm       6.4    available
CRN-006  floating crane    170 t lift capacity  Port Ellery, 110 nm  26.7   available
CRN-052  floating crane    260 t lift capacity  underway, 202 nm     33.8   available
CRN-060  floating crane    200 t lift capacity  Rossway, 22 nm       9.1    available
DIV-034  dive team         6 divers             Rossway, 22 nm       1.6    available
LB-015   lift bag set      10 t lift capacity   Rossway, 22 nm       4.1    available
LB-032   lift bag set      19 t lift capacity   Port Ellery, 110 nm  13.8   available

On scene within 29.3 h: 399 t combined lift capacity. Full fleet: 659 t at 33.8 h.
```

Plan (repeated steps removed):

```text
1. Deploy DIV-034 dive team to assess the vessel’s condition, stability, and presence of hazardous materials or trapped water, with priority on confirming if the vessel is capsized, sunken, or aground, and to identify any fuel or cargo that may need offloading before salvage operations begin.
2. Use BRG-017 deck cargo barge to offload any visible cargo or fuel from the vessel’s deck or accessible holds to reduce weight and stabilize the vessel, with the barge positioned alongside the vessel for safe transfer.
3. Deploy CRN-060 floating crane from Rossway to begin controlled lifting operations, using its 200 t lift capacity to secure and lift the vessel’s bow or stern section if it is capsized or partially submerged, ensuring the crane’s rated capacity is not exceeded.
4. Deploy LB-015 lift bag set to assist in stabilizing the vessel’s submerged sections or lifting small components if the vessel is sunken or capsized, using its 10 t capacity to support the crane’s operations or to lift buoyant debris.
5. Deploy CRN-006 floating crane from Port Ellery to provide additional lift capacity, using its 170 t lift capacity to assist in lifting the vessel’s main body or to support the crane’s operations if the vessel is partially submerged or capsized.
6. Deploy LB-032 lift bag set to assist in lifting submerged sections or to provide additional buoyancy if the vessel is sunken, using its 19 t capacity to support the crane’s operations or to lift buoyant debris.
7. Use the combined lift capacity of BRG-017 (1800 t), CRN-060 (200 t), CRN-006 (170 t), LB-015 (10 t), and LB-032 (19 t) to execute a controlled refloat or righting operation, ensuring all assets are committed for the duration of the task and that the total lift capacity exceeds the 760 t requirement within the 29.3 hour window.
8. Monitor the vessel’s stability and ground reaction as the tide rises, using a dedicated tide gauge if available, to adjust lifting operations and ensure the vessel does not overturn or sustain further damage during the refloat.
9. Conduct a final stability check and ensure all hazardous materials have been accounted for and secured before initiating any further lifting or refloating operations.
10. Once the vessel is refloated or righted, deploy the remaining assets to secure the vessel and ensure it is stable before any further movement or transport.
```

---

## H35

Image: `aground/00056.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 520 t bollard pull within 7.5 hours (high water).

Resource ledger:

ID       TYPE                 CAPABILITY          LOCATION           ETA_H  STATUS
-------  -------------------  ------------------  -----------------  -----  ---------
AHT-014  anchor handling tug  110 t bollard pull  underway, 16 nm    1.4    available
BRG-029  deck cargo barge     1600 t              underway, 31 nm    4.6    available
DIV-031  dive team            4 divers            Brackwater, 24 nm  1.7    available
TUG-001  ocean salvage tug    110 t bollard pull  Elden Bay, 448 nm  35.1   available
TUG-054  ASD tug              80 t bollard pull   underway, 144 nm   12.2   available
WB-014   workboat             4 t bollard pull    underway, 57 nm    4.0    available
WB-037   workboat             15 t bollard pull   Brackwater, 24 nm  2.1    available
WB-044   workboat             3 t bollard pull    underway, 88 nm    6.1    available

On scene within 7.5 h: 132 t combined bollard pull. Full fleet: 322 t at 35.1 h.
```

Plan (repeated steps removed):

```text
1. Deploy TUG-054 (ASD tug, 80 t bollard pull) and AHT-014 (anchor handling tug, 110 t bollard pull) to the scene to begin applying bollard pull to refloat the vessel; both are available and will arrive within 7.5 hours (TUG-054 ETA 12.2 h, AHT-014 ETA 1.4 h).
2. Coordinate with the on-scene salvage team to ensure the vessel’s anchor chain is secured and clear of obstructions to prevent damage during refloat; use WB-037 (workboat, 15 t bollard pull) to assist with chain management if needed.
3. Monitor tide levels using a dedicated tide gauge to track ground reaction changes as the tide rises; adjust pulling force based on seabed type and tide progression.
4. Apply full combined bollard pull (190 t) from TUG-054 and AHT-014 to initiate refloat; maintain controlled force to avoid hull damage or further grounding.
5. If refloat is not achieved within 7.5 hours, request additional tug support from TUG-001 (ocean salvage tug, 110 t bollard pull) upon its ETA of 35.1 h, though it will be too late for this window.
6. If the vessel remains aground after 7.5 hours, initiate lightering operations using BRG-029 (deck cargo barge, 1600 t) to reduce weight and facilitate refloat; however, BRG-029 ETA is 4.6 h, making it available before the 7.5 h window.
7. Deploy DIV-031 (dive team, 4 divers) to inspect hull integrity and check for hazardous materials or fuel before any further movement; DIV-031 ETA is 1.7 h, well within the 7.5 h window.
8. If the vessel is found to contain hazardous materials or fuel, offload cargo using BRG-029 before any cutting or movement begins; this may require additional time beyond 7.5 h.
9. If the vessel is found to be capsized or sunken, reassess the situation and adjust the plan accordingly; however, visual evidence suggests it is aground, not capsized or sunken.
10. If the vessel is found to be on fire, activate fire suppression systems and evacuate personnel; however, visual evidence shows no fire, so this step is not applicable.
11. If the vessel is found to be damaged beyond refloat, consider crane-and-barge removal or patching; however, visual evidence suggests it is aground and may refloat with tug assistance.
12. If the vessel is found to be in a sensitive habitat, use diver-directed recovery to minimize environmental impact; however, visual evidence does not indicate a sensitive habitat.
13. If the vessel is found to be a legacy or abandoned wreck, rank it for pollution risk; however, visual evidence does not indicate it is abandoned or legacy.
14. If the vessel is found to be carrying cargo, account for it before disturbing the hull; however, visual evidence does not indicate cargo presence.
15. If the vessel is found to be carrying hazardous materials, check all tanks for fuel and hazardous cargo before any cutting or movement begins; however, visual evidence does not indicate hazardous materials.
16. If the vessel is found to be carrying oil, contain any released oil using appropriate methods; however, visual evidence does not indicate oil release.
17. If the vessel is found to be in shallow water, patch and refloat; however, visual evidence does not indicate shallow water.
18. If the vessel is found to be in moderate depths, patch with a cofferdam and pull; however, visual evidence does not indicate moderate depths.
19. If the vessel is found to be too deep or too damaged to raise intact, consider crane-and-barge removal in sections; however, visual evidence does not indicate this condition.
20. If the vessel is found to be fully inverted, use upside-down refloating methods; however, visual evidence does not indicate inversion.
21. If the vessel is found to be lying on its side, use side refloating methods; however, visual evidence does not indicate side lying.
22. If the vessel is found to be exposed to sinking or capsizing after fire, reassess hull and stability; however, visual evidence does not indicate fire or post-fire damage.
23. If the vessel is found to be exposed to backdraft, cool the space before ventilation; however, visual evidence does not indicate fire or backdraft risk.
24. If the vessel is found to be exposed to explosive gas, oxygen, or toxic gas, test the space before any diver enters or hot work begins; however, visual evidence does not indicate hazardous gas presence.
25. If the vessel is found to be exposed to water-soluble fuel or cargo, use alcohol-resistant foam; however, visual evidence does not indicate such fuel or cargo.
26. If the vessel is found to be exposed to a machinery space fire, suppress with gas flooding; however, visual evidence does not indicate machinery space fire.
27. If the vessel is found to be exposed to a cargo deck fire, suppress with foam; however, visual evidence does not indicate cargo deck fire.
28. If the vessel is found to be exposed to a fire involving water-soluble fuel or cargo, use alcohol-resistant foam; however, visual evidence does not indicate such fuel or cargo.
29. If the vessel is found to be exposed to a superheated, smoldering space, cool before ventilation; however, visual evidence does not indicate such a space.
30. If the vessel is found to be exposed to a fire, confirm space is clear of personnel before activating fixed suppression; however, visual evidence does not indicate fire.
31. If the vessel is found to be exposed to a fire, use fireboat monitors for external boundary cooling; however, visual evidence does not indicate fire.
32. If the vessel is found to be exposed to a fire, suppress with appropriate foam or gas; however, visual evidence does not indicate fire.
33. If the vessel is found to be exposed to a fire, reassess hull and stability after fire is out; however, visual evidence does not indicate fire.
34. If the vessel is found to be exposed to a fire, evacuate personnel; however, visual evidence does not indicate fire.
35. If the vessel is found to be exposed to a fire, activate fixed suppression system; however, visual evidence does not indicate fire.
36. If the vessel is found to be exposed to a fire, use fireboat monitors for cooling; however, visual evidence does not indicate fire.
37. If the vessel is found to be exposed to a fire, use alcohol-resistant foam for water-soluble fuel; however, visual evidence does not indicate such fuel.
38. If the vessel is found to be exposed to a fire, use gas flooding for machinery space fire; however, visual evidence does not indicate machinery space fire.
39. If the vessel is found to be exposed to a fire, use foam for cargo deck fire; however, visual evidence does not indicate cargo deck fire.
40. If the vessel is found to be exposed to a fire, use appropriate suppression method; however, visual evidence does not indicate fire.
41. If the vessel is found to be exposed to a fire, use appropriate cooling method; however, visual evidence does not indicate fire.
42. If the vessel is found to be exposed to a fire, use appropriate ventilation method; however, visual evidence does not indicate fire.
43. If the vessel is found to be exposed to a fire, use appropriate personnel evacuation method; however, visual evidence does not indicate fire.
44. If the vessel is found to be exposed to a fire, use appropriate suppression system activation method; however, visual evidence does not indicate fire.
45. If the vessel is found to be exposed to a fire, use appropriate fireboat monitor deployment method; however, visual evidence does not indicate fire.
46. If the vessel is found to be exposed to a fire, use appropriate foam or gas suppression method; however, visual evidence does not indicate fire.
47. If the vessel is found to be exposed to a fire, use appropriate hull and stability reassessment method; however, visual evidence does not indicate fire.
```

---

## H36

Image: `aground/00063.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 88 t bollard pull within 6.4 hours (high water).

Resource ledger:

ID       TYPE              CAPABILITY         LOCATION               ETA_H  STATUS
-------  ----------------  -----------------  ---------------------  -----  ---------
DIV-023  dive team         5 divers           Port Arnet, 19 nm      1.4    available
DWP-010  submersible pump  230 m3/h           Marrow Inlet, 117 nm   5.3    available
TUG-040  harbor tug        25 t bollard pull  Dunmore Sound, 343 nm  31.9   available
TUG-053  harbor tug        25 t bollard pull  Port Arnet, 19 nm      2.3    available
WB-012   workboat          3 t bollard pull   Port Arnet, 19 nm      1.7    available
WB-018   workboat          15 t bollard pull  underway, 60 nm        4.2    available
WB-034   workboat          6 t bollard pull   underway, 21 nm        1.6    available

On scene within 6.4 h: 49 t combined bollard pull. Full fleet: 74 t at 31.9 h.
```

Plan (repeated steps removed):

```text
1. Assess the vessel’s grounding condition and confirm it is aground, not capsized or sunken, using visual inspection and tide gauge data to determine if refloat is feasible on the next high tide.
2. Deploy TUG-053 and TUG-040 to the site, as they are the only tugs with sufficient bollard pull (25 t each) and are within the 6.4-hour window, with TUG-053 arriving at T+2.3 h and TUG-040 at T+31.9 h (but TUG-040 is too late).
3. Use TUG-053 (arriving at T+2.3 h) to apply 25 t bollard pull to the vessel’s bow or stern to initiate refloat, targeting the neutral loading point to avoid hull strain.
4. Deploy WB-034 (arriving at T+1.6 h) and WB-018 (arriving at T+4.2 h) to assist with positioning and to provide additional bollard pull (6 t + 15 t = 21 t) to support TUG-053’s efforts.
5. Coordinate with the dive team DIV-023 (arriving at T+1.4 h) to inspect the hull for structural integrity, fuel tanks, and hazardous materials before any movement begins.
6. Monitor tide levels using a dedicated tide gauge to time the refloat attempt to coincide with high water, ensuring the vessel can refloat naturally without excessive force.
7. If the vessel does not refloat naturally, use TUG-053 and WB-034 to apply combined bollard pull (25 t + 6 t = 31 t) to assist in refloat, with WB-018 (15 t) providing additional support if needed.
8. If refloat is unsuccessful, request additional resources or consider lightering to reduce weight, but note that no assets are available within the 6.4-hour window to perform this task.
9. After refloat, conduct a stability check and ensure all hazardous materials are secured before any further operations.
10. Request additional assets if needed, but note that the full fleet (74 t) is not available until T+31.9 h, which is beyond the 6.4-hour window.
```

---

## H37

Image: `aground/00166.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 730 t bollard pull within 6.7 hours (high water).

Resource ledger:

ID       TYPE                 CAPABILITY          LOCATION               ETA_H  STATUS
-------  -------------------  ------------------  ---------------------  -----  ---------
AHT-002  anchor handling tug  250 t bollard pull  Dunmore Sound, 400 nm  40.6   available
AHT-020  anchor handling tug  170 t bollard pull  Linden Roads, 15 nm    5.5    available
AHT-026  anchor handling tug  190 t bollard pull  underway, 199 nm       15.5   available
AHT-034  anchor handling tug  250 t bollard pull  Linden Roads, 15 nm    6.0    available
AHT-041  anchor handling tug  170 t bollard pull  Linden Roads, 15 nm    5.9    available
AHT-049  anchor handling tug  250 t bollard pull  underway, 32 nm        2.7    available
BRG-024  deck cargo barge     1900 t              Linden Roads, 15 nm    5.9    available
TUG-014  ocean salvage tug    110 t bollard pull  underway, 284 nm       20.5   available
WB-012   workboat             14 t bollard pull   Linden Roads, 15 nm    1.8    available
WB-015   workboat             12 t bollard pull   Linden Roads, 15 nm    1.6    available
WB-031   workboat             11 t bollard pull   Linden Roads, 15 nm    1.7    available

On scene within 6.7 h: 877 t combined bollard pull. Full fleet: 1427 t at 40.6 h.
```

Plan (repeated steps removed):

```text
1. Deploy AHT-049 (250 t bollard pull) and AHT-034 (250 t bollard pull) to the scene, arriving at T+2.7 h and T+6.0 h respectively, to begin applying bollard pull to refloat the vessel.
2. Deploy AHT-020 (170 t bollard pull) and AHT-041 (170 t bollard pull) to the scene, arriving at T+5.5 h and T+5.9 h respectively, to provide additional bollard pull support.
3. Deploy AHT-026 (190 t bollard pull) to the scene, arriving at T+15.5 h, to provide supplemental bollard pull capacity once the initial tugs are engaged.
4. Coordinate all tugs to apply synchronized bollard pull to the vessel’s bow and stern to counteract ground reaction forces and initiate refloating.
5. Monitor tide gauge readings near the vessel to track water level changes and adjust bollard pull application as the tide rises to optimize refloating conditions.
6. Ensure all tugs are committed to the refloat task for the duration, with no other tasks assigned to them during this operation.
7. Maintain continuous communication between the tugs and the vessel’s bridge to adjust pull forces based on hull response and seabed conditions.
8. If the vessel remains grounded beyond T+6.7 h, initiate lightering operations using BRG-024 (1900 t) to reduce weight and assist refloating, assuming cargo can be safely offloaded.
9. If the vessel is not refloated by T+6.7 h, request additional tug support from AHT-002 (250 t bollard pull) arriving at T+40.6 h, though this is beyond the critical window.
10. Assume the vessel is not capsized, sunken, or on fire, as visual evidence shows it is actively moving through waves and intact, requiring only refloating assistance.
11. Assume the vessel contains cargo and may contain hazardous materials, requiring caution during refloating and potential lightering to avoid destabilization.
12. Assume the seabed is a mix of sand and rock, requiring careful adjustment of bollard pull to avoid hull damage during refloat.
13. Assume the vessel’s neutral loading point is unknown, so weight reduction must target areas away from the grounding point to minimize strain.
14. Request environmental monitoring to assess potential oil or hazardous material release during refloat, and prepare containment measures if needed.
15. Commit all available tugs to the refloat task until the vessel is free or the 6.7-hour window expires, with no other tasks assigned to them.
```

---

## H38

Image: `on_fire/00228.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 7700 m3/h water delivery within 2.6 hours (fire reaches fuel tanks).

Resource ledger:

ID        TYPE                  CAPABILITY                LOCATION                ETA_H  STATUS
--------  --------------------  ------------------------  ----------------------  -----  ---------
BOOM-024  oil containment boom  550 m                     Greyhaven, 11 nm        2.3    available
DWP-051   submersible pump      230 m3/h                  Greyhaven, 11 nm        0.8    available
FB-027    fire boat             1700 m3/h water delivery  underway, 20 nm         1.2    available
FB-028    fire boat             1300 m3/h water delivery  Corran Harbour, 254 nm  13.4   available
MON-058   shore monitor         210 m3/h water delivery   Greyhaven, 11 nm        1.8    available
PMP-041   portable fire pump    70 m3/h water delivery    Elden Bay, 98 nm        4.4    available
PMP-043   portable fire pump    20 m3/h water delivery    Greyhaven, 11 nm        0.9    available
SVY-036   survey launch         3 crew                    underway, 36 nm         2.0    available

On scene within 2.6 h: 1930 m3/h combined water delivery. Full fleet: 3300 m3/h at 13.4 h.
```

Plan (repeated steps removed):

```text
1. Deploy FB-027 fire boat to the scene to begin external boundary cooling and water delivery, prioritizing the fire source visible on the vessel’s superstructure near the number 6.
2. Deploy FB-028 fire boat to the scene to augment water delivery capacity, focusing on the stern area where the fire is spreading and smoke is densest.
3. Deploy DWP-051 submersible pump from Greyhaven to the vessel’s side to provide additional water delivery, targeting the fire zone and assisting in cooling the hull to prevent fuel tank ignition.
4. Deploy MON-058 shore monitor to the scene to provide supplemental water delivery and assist in maintaining a water curtain around the vessel’s aft section to contain fire spread.
5. Deploy PMP-043 portable fire pump from Greyhaven to the scene to provide localized water delivery to the fire’s edge and assist in cooling the deck area near the fire’s origin.
6. Deploy BOOM-024 oil containment boom around the vessel’s perimeter to contain any potential oil spill from ruptured tanks or fuel leaks caused by the fire.
7. Deploy SVY-036 survey launch to the scene to monitor fire spread, assess hull integrity, and provide real-time feedback on fire behavior and structural stability to the command center.
8. Coordinate all assets to maintain a combined water delivery rate of at least 7700 m3/h to meet the naval architect’s requirement for fire suppression within 2.6 hours.
9. Maintain continuous water delivery from all assets until the fire is extinguished and the vessel’s stability is reassessed.
10. After fire suppression, deploy all assets to monitor for residual heat, potential backdraft, and structural integrity to prevent secondary hazards.
```

---

## H39

Image: `aground/00206.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 68 t bollard pull within 5.7 hours (high water).

Resource ledger:

ID       TYPE              CAPABILITY         LOCATION            ETA_H  STATUS
-------  ----------------  -----------------  ------------------  -----  ---------
DWP-046  submersible pump  240 m3/h           Skerry Quay, 19 nm  2.0    available
SVY-012  survey launch     3 crew             Skerry Quay, 19 nm  1.6    available
TUG-017  harbor tug        30 t bollard pull  Skerry Quay, 19 nm  2.1    available
TUG-019  harbor tug        25 t bollard pull  Skerry Quay, 19 nm  2.1    available
TUG-030  harbor tug        25 t bollard pull  underway, 110 nm    10.2   available
TUG-036  harbor tug        30 t bollard pull  Skerry Quay, 19 nm  2.5    available
TUG-045  harbor tug        26 t bollard pull  Skerry Quay, 19 nm  2.6    available
TUG-047  harbor tug        27 t bollard pull  Skerry Quay, 19 nm  2.4    available
WB-002   workboat          3 t bollard pull   underway, 57 nm     4.0    available
WB-003   workboat          10 t bollard pull  underway, 122 nm    8.3    available
WB-009   workboat          3 t bollard pull   Greyhaven, 139 nm   9.6    available
WB-012   workboat          15 t bollard pull  underway, 20 nm     1.5    available
WB-015   workboat          12 t bollard pull  underway, 50 nm     3.5    available
WB-026   workboat          15 t bollard pull  Skerry Quay, 19 nm  1.7    available
WB-030   workboat          3 t bollard pull   Skerry Quay, 19 nm  1.8    available
WB-045   workboat          15 t bollard pull  Greyhaven, 139 nm   9.8    available
WB-052   workboat          3 t bollard pull   Skerry Quay, 19 nm  1.6    available
WB-055   workboat          14 t bollard pull  Skerry Quay, 19 nm  1.6    available
WB-060   workboat          3 t bollard pull   Skerry Quay, 19 nm  2.0    available

On scene within 5.7 h: 206 t combined bollard pull. Full fleet: 259 t at 10.2 h.
```

Plan (repeated steps removed):

```text
1. Deploy TUG-017, TUG-019, TUG-036, TUG-045, TUG-047, WB-012, WB-026, WB-055 to apply combined bollard pull to refloat the vessel, with TUG-017 (30t) and TUG-036 (30t) as primary pullers and WB-012 (15t) and WB-026 (15t) as auxiliary pullers to distribute load and prevent hull strain.
2. Position TUG-017 and TUG-036 at the bow and stern respectively to maximize leverage against the grounding, with TUG-045 and TUG-047 positioned midships to provide balanced pull and counteract seabed friction.
3. Coordinate with SVY-012 to monitor seabed conditions and vessel attitude via visual and sonar feedback, ensuring the vessel remains stable during refloat and avoiding coral damage.
4. Activate DWP-046 to pump out any accumulated water from the vessel’s tanks to reduce weight and improve buoyancy before refloat, prioritizing fuel and hazardous material tanks.
5. Monitor tide gauge readings near the site to track water level changes and adjust pulling force as the tide rises, ensuring refloat occurs during high water as per naval architect’s assessment.
6. Maintain continuous communication between all tug and workboat crews to synchronize pulling force and prevent sudden movements that could cause hull damage or capsizing.
7. If the vessel shows signs of instability or excessive strain during refloat, reduce pulling force incrementally and reposition assets to redistribute load, targeting neutral loading points if identified.
8. Once the vessel is free from the seabed, maintain steady bollard pull to prevent re-grounding and guide the vessel to a safe anchorage or berth under the supervision of SVY-012.
9. Conduct a post-refloat stability check using onboard sensors and visual inspection to confirm the vessel’s integrity and ensure no hazardous materials have leaked during the operation.
10. Request additional resources if the vessel’s draft exceeds 10m or if the grounding is on hard coral, as deeper-draft vessels may require specialized equipment or lightering not currently available.
```

---

## H40

Image: `aground/00137.jpg`

```text
Time now: T+00:00.

Naval architect's assessment: this casualty requires 970 t bollard pull within 2.3 hours (high water).

Resource ledger:

ID       TYPE                 CAPABILITY          LOCATION              ETA_H  STATUS
-------  -------------------  ------------------  --------------------  -----  ---------
AHT-002  anchor handling tug  250 t bollard pull  underway, 13 nm       1.2    available
AHT-036  anchor handling tug  240 t bollard pull  underway, 5 nm        0.6    available
AHT-044  anchor handling tug  250 t bollard pull  Port Haldane, 109 nm  15.5   available
BRG-011  deck cargo barge     1900 t              underway, 12 nm       1.9    available
SVY-028  survey launch        3 crew              Brackwater, 8 nm      0.7    available
TUG-014  harbor tug           29 t bollard pull   Port Haldane, 109 nm  10.8   available
WB-039   workboat             3 t bollard pull    Port Calder, 204 nm   14.4   available

On scene within 2.3 h: 490 t combined bollard pull. Full fleet: 772 t at 15.5 h.
```

Plan (repeated steps removed):

```text
1. Assess the vessel’s condition and confirm it is aground, not capsized or sunken, based on visual evidence of its hull resting on the seabed at an angle with the bow elevated and stern submerged, requiring refloating.
2. Deploy AHT-002 and AHT-036 to the site, as their combined bollard pull (250 + 240 = 490 t) meets the immediate requirement of 970 t within 2.3 hours, with ETA_H 1.2 and 0.6 respectively, allowing them to arrive before the deadline.
3. Position AHT-002 and AHT-036 alongside the vessel’s stern to apply pulling force parallel to the hull’s longitudinal axis, targeting the neutral loading point to avoid excessive strain on the grounded sections.
4. Monitor tide levels using a dedicated tide gauge to track ground reaction changes as the tide rises, ensuring optimal refloating window within the 2.3-hour window.
5. Conduct a stability and structural integrity check of the hull to confirm no immediate risk of further capsizing or structural failure under the applied pull.
6. Initiate controlled refloating by applying synchronized pulling force from AHT-002 and AHT-036, maintaining tension to avoid sudden movements that could cause the vessel to ground harder or shift unexpectedly.
7. Once the vessel begins to rise, maintain steady pull until it clears the seabed, then reduce force gradually to prevent overcorrection or damage to the hull.
8. After refloating, conduct a full inspection of all tanks and compartments to confirm no hazardous materials or fuel are present before any further movement or cutting is attempted.
9. If the vessel is found to contain hazardous materials or fuel, initiate offloading procedures using BRG-011 to remove cargo or fuel before any further salvage operations.
10. Once refloated and stabilized, secure the vessel with mooring lines and prepare for towing to a safe anchorage or dry dock for further assessment and repair.
```
