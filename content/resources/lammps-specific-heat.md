---
title: "LAMMPS Script for specific heat calculation"
date: 2026-06-04
summary: "An input script for LAMMPS to calculate specific heat capacity of confined argon under solid copper walls."
category: "Simulation Scripts"
tags:
  - "LAMMPS"
  - "Molecular Dynamics"
  - "Specific Heat"
github: "https://github.com/abzarif/lammps-cv"
download: ""
pdf: ""
featured: true
---

### Simulation Description
This resource contains a sample LAMMPS input script to compute the constant volume specific heat capacity ($C_v$) of liquid argon confined between solid copper walls using equilibrium molecular dynamics (EMD). The solid-liquid interaction is modeled using the Lennard-Jones (LJ) potential.

### LAMMPS Input Script

```lammps
# LAMMPS input script: Specific Heat Calculation
units           lj
atom_style      atomic
boundary        p p f

# Define simulation space
lattice         fcc 0.844
region          box block 0 10 0 10 0 15
create_box      2 box
create_atoms    1 box

# Define solid walls at boundaries
region          lower block INF INF INF INF 0 1.5
region          upper block INF INF INF INF 13.5 15
group           lower_wall region lower
group           upper_wall region upper
group           liquid subtract all lower_wall upper_wall

# Potentials and coefficients
pair_style      lj/cut 2.5
pair_coeff      1 1 1.0 1.0 2.5   # Argon-Argon
pair_coeff      2 2 1.0 1.0 2.5   # Copper-Copper
pair_coeff      1 2 0.5 1.0 2.5   # Argon-Copper (hydrophobic interface)

# Equilibrium run
velocity        liquid create 1.0 87287
fix             1 liquid nvt temp 1.0 1.0 0.1
fix             2 lower_wall setforce 0.0 0.0 0.0
fix             3 upper_wall setforce 0.0 0.0 0.0

thermo          100
run             5000
```
