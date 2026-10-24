---
title: "Graphene: Building a Structure from Scratch"
short: "Graphene"
weight: 2
summary: "Build a graphene sheet atom by atom with LAMMPS's own lattice, region and create_atoms commands, then run it at room temperature."
learn:
  - "Describing a crystal as **lattice vectors + basis atoms**"
  - "The three building commands: `lattice`, `region`, `create_atoms`"
  - "Sizing the box from variables so it fits a whole number of unit cells"
---

{{< guide-video src="/videos/md-lammps-guide/graphene.mp4" alt="A 20 by 20 cell graphene sheet rendered in OVITO, a honeycomb of carbon atoms" caption="The goal: a 1600-atom graphene sheet (20 × 20 unit cells) at 300 K." >}}

Graphene is a single layer of carbon atoms arranged in a honeycomb, with a C–C bond length of $l = 1.42$ Å. LAMMPS has no built-in "graphene" lattice, so we describe it ourselves. That is the most useful skill in this whole guide, because the same recipe builds almost any crystal.

## The idea: a unit cell that tiles the plane

Any crystal can be described by a **unit cell** (a box defined by lattice vectors $\vec a_1, \vec a_2, \vec a_3$) and the **basis atoms** inside it. Copy the cell over and over and you get the whole crystal.

For graphene, I use an **orthogonal** (rectangular) cell. It's not the smallest possible cell, but its sides line up with x and y, so it fits neatly into a rectangular simulation box.

{{< svgfig src="/images/resources/md-lammps-guide/graphene-unit-cell.svg" width="520" caption="The orthogonal graphene cell (dashed): $\vec a_1 = (\sqrt3, 0)\,l$ and $\vec a_2 = (0, 3)\,l$, with four basis atoms." >}}

In a textbook you would usually write basis positions in Cartesian coordinates. LAMMPS instead wants **fractional coordinates**: each position written as a fraction of the lattice vectors.

| Basis atom | Cartesian position | Fractional (what LAMMPS wants) |
|---|---|---|
| 1 | $(0,\ 0)\,l$ | $0\,\vec a_1 + 0\,\vec a_2$ → `0 0 0` |
| 2 | $(\tfrac{\sqrt3}{2},\ \tfrac12)\,l$ | $\tfrac12\,\vec a_1 + \tfrac16\,\vec a_2$ → `1/2 1/6 0` |
| 3 | $(\tfrac{\sqrt3}{2},\ \tfrac32)\,l$ | $\tfrac12\,\vec a_1 + \tfrac12\,\vec a_2$ → `1/2 1/2 0` |
| 4 | $(0,\ 2)\,l$ | $0\,\vec a_1 + \tfrac23\,\vec a_2$ → `0 2/3 0` |

To convert, divide each Cartesian coordinate by the length of the matching lattice vector. For atom 2: $\tfrac{\sqrt3/2}{\sqrt3} = \tfrac12$ and $\tfrac{1/2}{3} = \tfrac16$.

## Step 1: size the box

```bash
variable l equal 1.42 # bond length in angstroms
variable m  equal 20 # number of unit cells along length
variable n  equal 20 # number of unit cells along width
variable L equal $(sqrt(3)*v_l*v_m) # length of the graphene sheet
variable W equal $(3*v_l*v_n) # width of the graphene sheet

region box block 0 ${L} 0 ${W} -10 10 units box
create_box 1 box
mass 1 12.01 # mass of carbon atom
```

The box length is the number of cells times the cell length: $L = m\sqrt3\,l$ and $W = 3n\,l$. This matters more than it looks. Because the box is periodic, the right edge of the sheet must connect perfectly to the left edge. If the box doesn't hold a **whole number** of unit cells, atoms at the edges end up too close together or too far apart, and the sheet has a defect line running along the boundary.

`region box block xlo xhi ylo yhi zlo zhi` defines a rectangular block, and `create_box 1 box` turns it into the simulation box with **1** atom type. `units box` means the numbers are in Å. Without it, LAMMPS would multiply them by the lattice spacing.

The z range (−10 to 10) doesn't matter here, because this is a 2D simulation (`dimension 2`).

## Step 2: the three building commands

```bash
lattice custom ${l} &
  a1 $(sqrt(3)) 0.0 0.0 &
  a2 0.0 3.0 0.0 &
  basis 0.0 0.0 0.0 &
  basis $(1/2) $(1/6) 0.0 &
  basis $(1/2) $(1/2) 0.0 &
  basis 0.0 $(2/3) 0.0

region mybox block 0 ${L} 0 ${W} -0.1 0.1 units box
create_atoms 1 region mybox
```

**[`lattice`](https://docs.lammps.org/lattice.html)** `style scale keyword values...` defines the unit cell.
- `custom` because graphene isn't one of the built-in styles (`sc`, `bcc`, `fcc`, `hcp`, `diamond`…).
- `scale` = 1.42: every vector below is multiplied by this, so `a1 $(sqrt(3)) 0 0` becomes $(\sqrt3\,l, 0, 0)$.
- `a1`, `a2` (and `a3`) are the lattice vectors; each `basis` line adds one atom in fractional coordinates.
- A long command can be split over several lines by ending each line with `&`.

**[`region`](https://docs.lammps.org/region.html)** `ID style args` marks out the space to fill. Regions can be blocks, cylinders, spheres, cones and more. Here, a thin slab around z = 0.

**[`create_atoms`](https://docs.lammps.org/create_atoms.html)** `type style args` fills that region with the lattice, using atom type `1` (carbon) and style `region`.

The order matters: lattice first (what to tile), then region (where), then create_atoms (do it).

## Step 3: everything else

The rest of the script is the standard skeleton from the [previous chapter](../script-skeleton/), using the **Tersoff** potential for carbon:

```bash
pair_style tersoff/table
pair_coeff * * SiCGe.tersoff C
```

`SiCGe.tersoff` holds Tersoff parameters for Si, C and Ge (Tersoff, *Phys. Rev. B* 39, 5566, 1989). The `C` at the end maps atom type 1 to the carbon entry. `tersoff/table` is a faster, tabulated version of the standard `tersoff` style.

## Run it

```bash
lmp -in graphene.lmp
```

The sheet has 1600 atoms ($20 \times 20$ cells $\times$ 4 atoms per cell); if you see a different number, check your `L` and `W`. The full run is 200,000 steps (50 ps) and takes about a minute on a few cores. The temperature should settle around 300 K.

Open `graphene_data.txt` in OVITO, add **Create bonds**, and load `graphene_dump.txt` as a trajectory to watch the sheet vibrate.

{{< lmpfile src="/documents/md-lammps-guide/graphene/graphene.lmp" title="Full script: graphene.lmp" >}}

[Download the graphene folder (.zip)](/documents/md-lammps-guide/graphene.zip): the script and `SiCGe.tersoff`.

## Try this

1. Change `m` and `n` to make a long, narrow ribbon. Check that the atom count is $4mn$.
2. Set `m` to a non-integer value, such as 20.5. Look at the edge of the sheet in OVITO, and compare the starting energy in the log.
3. Change `dimension 2` to `dimension 3` and the box z range to −20 to 20. In 3D, the sheet is free to ripple out of plane.

## Going further

This sheet is the starting point for real graphene studies. My [LAMMPS code samples](/resources/skill-lammps/) include a script for **thermal rectification in graphene**, where heat flows more easily in one direction than the other.
