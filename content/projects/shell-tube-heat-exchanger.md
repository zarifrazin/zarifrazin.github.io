---
title: "Shell & Tube Heat Exchanger"
date: 2022-05-01
summary: "Group project for ME 310 (Thermo-fluid System Design) at BUET: thermal and mechanical design of a shell and tube oil cooler for a marine application, using MATLAB, HTRI and the ASME pressure vessel code."
badges:
  - "Thermal Design"
  - "MATLAB"
  - "HTRI"
  - "ASME Code"
links:
  - icon: "fab fa-google-drive"
    url: "https://drive.google.com/drive/folders/1isUNptMfIfzrmEBA_NuTvyEoEGGuvSUR?usp=sharing"
image: "/images/projects/shell-tube-heat-exchanger.png"
category: "Engineering"
featured: true
---

### Project Overview
Design of a shell and tube oil cooler for a marine application, completed by our four-member group (Group C3) for the course ME 310: Thermo-fluid System Design at BUET. SAE 30 oil is cooled from 65 °C to 56 °C by sea water heated from 20 °C to 32 °C, within pressure drop limits of 140 kPa on the tube side and 40 kPa on the shell side. Oil flows through the tubes and sea water through the shell, since oil is the costlier fluid and the shell side is easier to clean.

### Design Stages
1. **Thermo-hydraulic design**:
   - Parametric analysis over the number of tube passes, tube sizes (5/8" and 3/4", 16 BWG) and tube lengths (3.66 m to 6.1 m), checking the overall heat transfer coefficient, shell diameter, tube count and pressure drops.
   - Economic analysis of materials: mild steel tubes and a wrought iron shell, chosen for local availability and cost.
   - Hand calculation in MATLAB (LMTD method): overall heat transfer coefficient of 61.45 W/m²K with 602 tubes, a pitch ratio of 1.25 and a 30° tube layout.
   - Verification with HTRI software.
2. **Mechanical design** (following the ASME Boiler and Pressure Vessel Code, Section VIII, Division 1):
   - Shell, tube sheet, nozzles, baffles, tie rods and flanges.
   - Technical drawings of the final design.

### Documentation & Deliverables
The project report, HTRI design report, MATLAB code and HTRI file are available on Google Drive [here](https://drive.google.com/drive/folders/1isUNptMfIfzrmEBA_NuTvyEoEGGuvSUR?usp=sharing).
