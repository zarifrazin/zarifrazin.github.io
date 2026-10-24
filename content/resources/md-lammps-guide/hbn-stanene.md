---
title: "hBN–Stanene Bilayer: Two Materials, Three Atom Types"
short: "hBN–stanene bilayer"
weight: 4
summary: "Stack a buckled stanene sheet on hexagonal boron nitride. Assign different atom types to different basis atoms, build a non-flat lattice, and combine several potentials in one simulation."
learn:
  - "Assigning atom types per basis atom: `create_atoms ... basis M itype`"
  - "A buckled lattice with a third lattice vector `a3`"
  - "Hybrid potentials: Tersoff within each layer, Lennard-Jones between them"
image: "/videos/md-lammps-guide/hbn-stanene-poster.jpg"
---

{{< guide-video src="/videos/md-lammps-guide/hbn-stanene.mp4" alt="A buckled stanene layer of tin atoms stacked above a flat hexagonal boron nitride layer" caption="The goal: a stanene (Sn) layer stacked on hexagonal boron nitride (hBN), 788 atoms in total." >}}

Stacking different 2D materials on top of each other (a **heterostructure**) is a common research topic, and you usually can't download one ready-made. So we build each layer with the graphene recipe from [Chapter 2](../graphene/), then stack them.

This stanene/hBN bilayer is a real research system. For example, Das et al. used molecular dynamics to study heat flow across the interface between the two layers: P. Das, P. Paul, M. Hassan, A. K. M. M. Morshed and T. C. Paul, "Interfacial thermal resistance in stanene/hexagonal boron nitride van der Waals heterostructures: A molecular dynamics study," *Computational Materials Science* 246, 113359 (2025), [doi:10.1016/j.commatsci.2024.113359](https://doi.org/10.1016/j.commatsci.2024.113359). The script in this chapter builds the starting structure for that kind of study.

## Layer 1: hexagonal boron nitride (hBN)

hBN has the same honeycomb as graphene, but its atoms alternate between boron and nitrogen, and its bond length is slightly longer ($l_{BN} = 1.45$ Å). Using the same four-atom orthogonal cell, basis atoms 1 and 3 are boron and 2 and 4 are nitrogen:

{{< svgfig src="/images/resources/md-lammps-guide/hbn-unit-cell.svg" width="520" caption="The same orthogonal cell as graphene, but with two atom types: boron on basis 1 and 3, nitrogen on basis 2 and 4." >}}

First, a 40 × 40 Å box with three atom types:

```bash
variable L equal 40.0# length of the hbn-sn sheet
variable W equal 40.0 # width of the hbn-sn sheet

region box block 0 ${L} 0 ${W} -10 10 units box
create_box 3 box
mass 1 10.811 # mass of boron atom
mass 2 14.007 # mass of nitrogen atom
mass 3 118.71 # mass of tin atom
```

Then the lattice. This time `scale` is 1, and the bond length goes directly into the vectors. That makes it easy to use two different bond lengths in one script:

```bash
variable lbn equal 1.45 # bond length in angstroms
lattice custom 1 &
  a1 $(sqrt(3)*v_lbn) 0.0 0.0 &
  a2 0.0 $(3.0*v_lbn) 0.0 &
  a3 0.0 0.0 1.0 &
  basis 0.0 0.0 0.0 &
  basis $(1/2) $(1/6) 0.0 &
  basis $(1/2) $(1/2) 0.0 &
  basis 0.0 $(2/3) 0.0
region bnbox block 0 ${L} 0 ${W} -0.5 0.0  units box
create_atoms 1 region bnbox basis 2 2 basis 4 2
```

The new part is at the end of the last line. `create_atoms 1` would make **every** basis atom type 1 (boron). Each `basis M itype` pair then overrides one of them: `basis 2 2` says "basis atom 2 becomes type 2", and `basis 4 2` does the same for basis atom 4. The result is boron on 1 and 3 and nitrogen on 2 and 4.

The system is now 3D (`dimension 3`), so the lattice needs a third vector, `a3`. Its value doesn't matter for a single flat layer.

## Layer 2: buckled stanene (Sn)

Stanene is a honeycomb of tin atoms, but it isn't flat. Alternate atoms sit in two planes separated by a **buckling height** $h = 0.88$ Å:

{{< svgfig src="/images/resources/md-lammps-guide/stanene-buckling.svg" width="560" caption="Side view of stanene. Seen from above it is a honeycomb, like graphene; from the side, alternate atoms sit in two planes $h$ apart." >}}

Seen from above, stanene is the same honeycomb, with an in-plane bond length of $l_{Sn} = 2.69$ Å. To build in the buckling, we add a vertical lattice vector $\vec a_3 = (0, 0, -2h)$ and give basis atoms 2 and 4 a z-fraction of ½, which puts them $h$ away from atoms 1 and 3:

```bash
variable lsn equal 2.69 # planar bond length in angstroms
variable hsn equal 0.88 # buckling height of sn atom in angstroms
lattice custom 1 &
  a1 $(sqrt(3)*v_lsn) 0.0 0.0 &
  a2 0.0 $(3.0*v_lsn) 0.0 &
  a3 0.0 0.0 $(-2*v_hsn) &
  basis 0.0 0.0 0.0 &
  basis $(1/2) $(1/6) $(1/2) &
  basis $(1/2) $(1/2) 0.0 &
  basis 0.0 $(2/3) $(1/2)
region snbox block 0 ${L} 0 ${W} 3.0 5.0 units box
create_atoms 3 region snbox
```

A lattice repeats in all three directions, so it has atomic planes every 1.76 Å in z. The region selects which ones we keep: z from 3.0 to 5.0 Å captures exactly two planes (at 3.52 and 4.40 Å), which together make one buckled layer sitting about 3.5 Å above the hBN.

## Combining potentials with `pair_style hybrid`

Different interactions need different models. Strong covalent bonds **within** each layer use Tersoff potentials, and the weak van der Waals attraction **between** the layers uses Lennard-Jones (LJ):

```bash
pair_style hybrid tersoff tersoff lj/cut 10.0
pair_coeff * * tersoff 1 BNC.tersoff B N NULL
pair_coeff * * tersoff 2 Sn.tersoff NULL NULL Sn
pair_coeff	1 3 lj/cut 0.0138 4.23 10
pair_coeff	2 3 lj/cut 0.00857 4.026 10
```

- `hybrid` lists every sub-style. `tersoff` appears twice because each instance reads its own parameter file; the `1` and `2` in the `pair_coeff` lines say which instance you mean.
- For many-body styles like Tersoff, `pair_coeff * *` maps **every** atom type, in order, to an element in the file, and `NULL` means "this type isn't handled here". So instance 1 handles types 1 and 2 (B, N), and instance 2 handles type 3 (Sn).
- The LJ lines cover the van der Waals attraction between the layers, B–Sn (`1 3`) and N–Sn (`2 3`): `epsilon` (well depth, eV), `sigma` (Å), and an optional cutoff (Å).

Potential files: `BNC.tersoff` (Kınacı et al., *Phys. Rev. B* 86, 115410, 2012) and `Sn.tersoff` (Mahdizadeh and Akhlamadi, *J. Mol. Graph. Model.* 72, 1, 2017), both from the LAMMPS `potentials/` folder.

## Run it

```bash
lmp -in hbn_sn.lmp
```

After minimization, the layers settle about 4 Å apart. In OVITO, color the three types differently and use a side view to see the buckling.

{{< lmpfile src="/documents/md-lammps-guide/hbn-stanene/hbn_sn.lmp" title="Full script: hbn_sn.lmp" >}}

[Download the hBN–stanene folder (.zip)](/documents/md-lammps-guide/hbn-stanene.zip): the script, `BNC.tersoff` and `Sn.tersoff`.

## Try this

1. Remove `basis 2 2 basis 4 2` and look at the result in OVITO. What happens to the nitrogen?
2. Change the Sn region's z range to `1.0 3.0`, which starts the tin only 1.76 Å above the hBN, and compare the first line of thermo output.
3. Look closely at the edges of the box in OVITO. 40 Å isn't a whole number of hBN cells (2.511 Å) or stanene cells (4.659 Å), so the honeycomb doesn't join up perfectly across the periodic boundary. Can you find box sizes that fit both lattices better?
