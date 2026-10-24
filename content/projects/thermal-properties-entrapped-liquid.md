---
title: "Thermal Properties of Entrapped Liquid"
date: 2024-09-01
summary: "Open-source LAMMPS simulation code for nano-confined liquids with hybrid wettability [Computational Materials Science Q1, IF: 3.1]."
badges:
  - "Molecular Dynamics"
  - "LAMMPS"
  - "Thermal Properties"
  - "Wettability"
links:
  - icon: "fas fa-link"
    name: "Journal Article (DOI)"
    url: "https://doi.org/10.1016/j.commatsci.2024.113232"
  - icon: "fab fa-github"
    name: "GitHub Repository"
    url: "https://github.com/zarifrazin/ncl_hybrid_wettability"
image: "/images/research/hybrid_ncl.png"
image_caption: "Molecular dynamics simulation domain showing liquid argon nano-confined between solid copper walls with hybrid wettability."
category: "Research"
featured: true
math: true
preview_open: true
---

### Project Overview

When liquids are confined within nanoscale gaps such as in advanced micro/nanochannel heat sinks, thermal interface materials, and nanofluidic cooling devices, their thermophysical behavior deviates fundamentally from bulk fluid dynamics. Interfacial effects, solid-liquid interaction potentials, and atomic density layering dominate the energy storage and transport characteristics of the entrapped fluid.

While previous studies focused primarily on uniformly hydrophilic or uniformly hydrophobic surfaces, practical engineering surfaces inherently exhibit chemical heterogeneity. This research investigated the **thermal properties of nano-confined liquid (NCL)** entrapped between solid copper surfaces engineered with **hybrid wettability**, utilizing equilibrium molecular dynamics (EMD) simulations performed with **LAMMPS**.

---

### Key Scientific Findings

1. **Enhanced Specific Heat Capacity**: Demonstrated that the constant volume molar heat capacity ($C_v$) of liquid argon entrapped between hybrid wettability surfaces is significantly higher than its bulk counterpart ($20\text{ J/(mol}\cdot\text{K)}$).
2. **Tunability via Surface Fraction**: Identified how the hydrophilic area fraction ($f$) governs specific heat capacity, thermal conductivity, interfacial fluid layering, localized mass density profiles, and total system energy fluctuations.

---

### 💻 Open-Source LAMMPS Code & GitHub Repository

To promote reproducible computational research, the complete LAMMPS simulation script, parametric loops, and data post-processing routines are openly shared on GitHub:

👉 **[GitHub Repository: zarifrazin/ncl_hybrid_wettability](https://github.com/zarifrazin/ncl_hybrid_wettability)**

The repository includes:
- **`in.ncl_hybrid`**: The master LAMMPS input deck containing the system initialization, lattice creation, region partitioning, and velocity distribution.
- **Parametric Loops**: Automated nested scripts looping over wettability combinations ($w_I, w_O$) and area fractions ($f$).
- **Property Calculations**: Fluctuation formulas for calculating $C_v$, mean squared displacement (MSD) for diffusion, radial distribution functions (RDF), and density profiles across the channel.
- **Log & Output Parsers**: Guidance on parsing thermodynamic outputs and extracting publication-grade datasets.

---

### 📊 Presentation Slides

Below are the presentation slides from my talk on this research, outlining the molecular dynamics framework, interfacial phenomena, and thermal property results:

{{< preview src="documents/research_projects/hybrid_ncl.pdf" title="hybrid_ncl_presentation.pdf" >}}

