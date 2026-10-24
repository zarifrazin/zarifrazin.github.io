---
title: "New to LAMMPS? A Beginner's Guide to Molecular Dynamics"
short: "Beginner's Guide to MD with LAMMPS"
date: 2026-10-24
summary: "A hands-on, step-by-step guide to building atomic structures and running your first molecular dynamics simulations in LAMMPS, with OVITO for visualization. Five worked systems, from a graphene sheet to a liquid droplet on a surface."
category: "Tutorials & Guides"
tags:
  - "LAMMPS"
  - "Molecular Dynamics"
  - "OVITO"
  - "Tutorial"
featured: true
type: "md-guide"
math: true
cascade:
  type: "md-guide"
  math: true
downloads:
  - name: "All scripts (.zip)"
    path: "/documents/md-lammps-guide/md-lammps-guide-all.zip"
    icon: "fa-file-archive"
    download: true
  - name: "Lecture slides (PDF)"
    path: "/documents/md-lammps-guide/md-demonstration-slides.pdf"
    icon: "fa-file-pdf"
  - name: "Code notes (PDF)"
    path: "/documents/md-lammps-guide/code-notes.pdf"
    icon: "fa-file-pdf"
---

Molecular dynamics (MD) simulates how atoms move. You place atoms in a box, choose a model for the forces between them (the **interatomic potential**), and then step Newton's equations of motion forward in time, a fraction of a femtosecond per step. From those trajectories you can measure things like temperature, pressure, structure, wetting, and heat flow.

The hardest part for most beginners isn't the physics; it's **getting the first structure built and the first simulation running**. This guide focuses on exactly that.

*This guide was converted from my lecture materials into a website by AI. [How it was made ↓](#about-this-guide)*

## Who this is for

Students and researchers who have heard of MD and want to run it, but have never written a LAMMPS input script. You don't need any programming experience. If you can edit a text file and type a command into a terminal, you can follow along.

## What you will build

{{< guide-roadmap >}}

Each system introduces a few new ideas, so it's best to go in order. Every chapter follows the same pattern: what we are building, the idea behind it, the commands that are new, how to run and visualize it, and a few things to try on your own.

## Before you start

You need three free programs:

| Software | What it does | Get it |
|---|---|---|
| **LAMMPS** | The MD simulator that reads your input script and runs the simulation | [lammps.org](https://www.lammps.org/download.html) (Windows installers, conda, or build from source) |
| **OVITO** | Visualizes the atoms, makes images and movies, and can convert file formats | [ovito.org](https://www.ovito.org/) (the free *Basic* version is enough) |
| **A text editor** | For writing input scripts | Any editor works; [VS Code](https://code.visualstudio.com/) is a comfortable choice |

Other tools you may come across: **VMD** (visualization), **Avogadro** (graphical structure builder), **Atomsk** and **EMC** (command-line structure builders), and commercial packages such as **Materials Studio** and **MedeA**.

Download the scripts with the **All scripts** button above. Each system is in its own folder, together with the potential file it needs.

## About this guide

This guide is based on a two-part guest lecture I delivered in **MAE 720: Molecular Level Modeling for Engineering Applications** at North Carolina State University in Fall 2025.

The lecture and its materials are my own: the slides, the code notes, the LAMMPS input scripts, and the simulation movies. **Converting these lecture materials into this website was done by AI.** Working from the lecture recording's transcript, the slides, the code notes and the scripts, the AI wrote the chapter text and drew the diagrams. The scripts on this site are the same as in the code notes, and each one was run in LAMMPS to check that it works. The written explanations may still contain minor mistakes.

If you spot an error or something unclear, please [let me know](mailto:zrazinb@ncsu.edu).
