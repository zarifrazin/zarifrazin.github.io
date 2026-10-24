---
title: "Silicon: Importing a Structure from a Database"
short: "Silicon"
weight: 3
summary: "For common crystals you don't need to write the lattice yourself. Download the unit cell from Materials Project, build a supercell in OVITO, and load it with read_data."
learn:
  - "Getting a crystal structure from Materials Project as a `.cif` file"
  - "Building a supercell and exporting a LAMMPS data file with OVITO"
  - "Loading a structure with `read_data`"
  - "The Stillinger–Weber potential for silicon"
---

{{< guide-video src="/videos/md-lammps-guide/silicon.mp4" alt="A cube of 1000 silicon atoms in the diamond structure rendered in OVITO" caption="The goal: a 5 × 5 × 5 supercell of diamond-cubic silicon (1000 atoms) at 300 K." >}}

Writing out the lattice vectors and basis worked well for graphene, but for a common crystal it's unnecessary work. Silicon has the diamond structure, and its unit cell is already in public databases. This chapter shows the **import route**, which is usually the fastest way to get a well-known crystal into LAMMPS.

## The workflow

1. **Download the unit cell** as a `.cif` file from a crystal database.
2. **Convert** it to an `.xyz` file.
3. **Open** the `.xyz` in OVITO.
4. **Replicate** it into a supercell.
5. **Export** a LAMMPS data file.
6. **Load** it in the input script with `read_data`.

### 1. Download the `.cif` file

[Materials Project](https://next-gen.materialsproject.org/) has computed structures for well over 100,000 materials (a free account is required). Search for **Si**, open the diamond-cubic entry (`mp-149`), and choose **Export → CIF**. Pick the **conventional standard** cell: it's a cube, which is much easier to work with than the smaller primitive cell.

The conventional silicon cell is a cube with side $a = 5.444$ Å containing 8 atoms (`Si.cif` in the download folder).

### 2. Convert to `.xyz`

Several tools can do this: a small Python script with [ASE](https://wiki.fysik.dtu.dk/ase/) or pymatgen, or one of the free online CIF-to-XYZ converters. Choose **extended XYZ** as the output, because it keeps the cell dimensions; plain `.xyz` stores only the atom positions. The result is `Si.extxyz` in the download folder.

### 3–5. Build the supercell in OVITO

1. Drag `Si.extxyz` into OVITO. You'll see the 8-atom cube.
2. *Add modification* → **Replicate**, and set 5 × 5 × 5 to get $8 \times 125 = 1000$ atoms.
3. *File* → **Export File**, choose **LAMMPS Data File**, and name it `si_supercell.data`.
4. In the export options, set the **atom style** to `atomic` so it matches the input script.

The data file lists the box size, the masses, and one line per atom:

```text
1000 atoms
1 atom types

-10.88740474 16.33110711 xlo xhi
-10.88740474 16.33110711 ylo yhi
-10.88740474 16.33110711 zlo zhi

Masses

1 28.0855  # Si

Atoms  # atomic

1 1 -6.80462796 -6.80462796 -9.52647915
2 1 -10.88740474 -8.16555356 -8.16555356
...
```

The box is $5 \times 5.444 = 27.22$ Å on each side, a whole number of cells, so the periodic boundaries match up perfectly.

### 6. Load it with `read_data`

In the input script, the entire "build the structure" stage becomes a single line:

```bash
read_data si_supercell.data
```

[`read_data`](https://docs.lammps.org/read_data.html) creates the box, the atom types, the masses and the atoms all at once, so there is no `region`, `create_box`, `mass` or `create_atoms`. It can also load several data files into one simulation (with the `add`, `offset` and `shift` keywords), which is a handy way to combine separately built pieces.

## The potential

```bash
pair_style sw
pair_coeff * * Si.sw Si
```

The **Stillinger–Weber** potential (Stillinger and Weber, *Phys. Rev. B* 31, 5262, 1985) is the classic model for silicon. Along with pairwise terms, it includes a three-body term that favors the 109.5° tetrahedral bond angle of the diamond structure.

## Run it

```bash
lmp -in si.lmp
```

20,000 steps (5 ps) takes well under a minute. In OVITO, add **Create bonds** with a cutoff of about 2.6 Å to see each atom bonded to its four neighbors.

{{< lmpfile src="/documents/md-lammps-guide/silicon/si.lmp" title="Full script: si.lmp" >}}

[Download the silicon folder (.zip)](/documents/md-lammps-guide/silicon.zip): the script, `si_supercell.data`, `Si.sw`, and the original `Si.cif` and `Si.extxyz`.

## When this route doesn't work

The import route needs a structure that someone has already published. For a stacked bilayer of two different 2D materials, a nanotube, or a droplet sitting on a surface, there's usually no file to download, so you are back to building it yourself. The next three chapters do exactly that.

## Try this

1. Replicate 3 × 3 × 3 instead of 5 × 5 × 5. How many atoms do you get? How much faster is the run?
2. Raise `t` to 1500 K. Silicon melts at 1687 K in experiments; does the structure stay crystalline in 5 ps?
3. Repeat the workflow for germanium, another diamond-structure crystal. The `SiCGe.tersoff` file from the graphene folder has Ge parameters: use `pair_style tersoff` and `pair_coeff * * SiCGe.tersoff Ge`.
