---
title: "Anatomy of a LAMMPS Input Script"
short: "Anatomy of an input script"
weight: 1
summary: "Every script in this guide shares the same skeleton. Learn it once here, then each later chapter only has to explain what is new."
learn:
  - "The seven stages of a LAMMPS input script"
  - "`metal` units, variables, and the `${...}` and `$(...)` syntax"
  - "How to run LAMMPS from a terminal"
  - "`write_data` versus `dump`, and how to open both in OVITO"
---

A LAMMPS **input script** is a plain text file of commands that LAMMPS reads from top to bottom. The five scripts in this guide look different at first glance, but they all follow the same seven stages, and only two of them (the structure and the potential) really change from system to system.

{{< svgfig src="/images/resources/md-lammps-guide/script-skeleton.svg" width="560" caption="The seven stages shared by every script in this guide. Only the highlighted stages change from one system to the next." >}}

Let's walk through them using the graphene script as the example.

## 1. Initialization

```bash
variable project string graphene
variable t equal 300.0 # temperature (K)

log           ${project}_log.txt
units           metal # grams/mole, angstroms, ps, eV, K, bars, gm/cm^3
dimension      2
boundary       p p p
atom_style     atomic
```

- **`variable`** stores a value under a name. `project` is a text label used to name output files; `t` is the temperature.
- **`log`** writes everything LAMMPS prints to a file, here `graphene_log.txt`.
- **`units metal`** sets the unit system: distance in ångströms (Å), time in picoseconds (ps), energy in eV, mass in g/mol, temperature in K, pressure in bar. Every number you type later is read in these units.
- **`dimension`** is 2 or 3. LAMMPS is built for 3D, but a single graphene sheet can be run as a 2D system.
- **`boundary p p p`** makes the box **periodic** in x, y and z: an atom that leaves through one face re-enters through the opposite face. This is how a small box can stand in for a large material. (`f` means a fixed, non-periodic boundary; you will see it in the droplet chapter.)
- **`atom_style atomic`** means each atom only has a type, a position, and a velocity, with no charges or bonds. That's enough for every system here.

### Using variables

Variables are what make a script easy to modify. There are two ways to use one:

| Syntax | Meaning | Example |
|---|---|---|
| `${name}` or `$t` | Paste the value in as text | `log ${project}_log.txt` → `log graphene_log.txt` |
| `$(expression)` | Evaluate a formula right now and paste the result | `$(sqrt(3)*v_l*v_m)` → `49.190243` |

Inside `$(...)`, refer to a variable as `v_name`. The single-letter shortcut `$t` only works for one-letter names; use `${...}` for anything longer.

## 2. Build the structure

This is the stage that changes the most, so each chapter covers it in detail. There are two routes:

- **Build it inside LAMMPS** with `lattice` → `region` → `create_atoms` (graphene, hBN–stanene, nanotube, droplet).
- **Build it elsewhere and load it** with `read_data` (silicon).

Every structure also needs a simulation box (`region` + `create_box`) and a `mass` for every atom type.

## 3. Interatomic potential

```bash
pair_style tersoff/table
pair_coeff * * SiCGe.tersoff C
```

The potential defines the energy of the atoms as a function of their positions, and the forces come from it. `pair_style` picks the functional form (Tersoff, Stillinger–Weber, EAM, Lennard-Jones…), and `pair_coeff` supplies the parameters, usually from a file. Choosing a potential is a real scientific decision. For these examples I use standard potentials that ship with LAMMPS, in its `potentials/` folder.

## 4. Settings

```bash
timestep 0.00025
neighbor 3.0 bin
neigh_modify delay 0 every 1 check yes
```

- **`timestep`**: 0.00025 ps = 0.25 fs. Each step moves time forward by this much. It must be small compared with the fastest atomic vibration, or the simulation blows up.
- **`neighbor` / `neigh_modify`**: LAMMPS keeps a list of nearby atoms so it doesn't have to check every pair at every step. These lines set how far beyond the potential cutoff the list reaches (3 Å) and tell LAMMPS to check every step whether it needs rebuilding.

## 5. Energy minimization

```bash
min_style cg
minimize 1e-10 1e-12 10000 100000
```

A structure built from ideal positions is rarely at the potential's energy minimum. `minimize` nudges the atoms downhill in energy (here with the conjugate-gradient method, `cg`) until the energy or force stops changing by more than the given tolerances, or the iteration limits are reached. This removes any large initial forces before atoms start moving.

## 6. Save a snapshot

```bash
write_data ${project}_data.txt
```

## 7. Equilibrate and record

Right after the structure is built, the script gives the atoms their starting velocities:

```bash
velocity all create $t 12345 dist gaussian
```

and at the end it runs the simulation:

```bash
fix 1 all nvt temp $t $t $(100.0*dt)
thermo 100
thermo_style custom step temp etotal press
dump 1 all custom 100 ${project}_dump.txt id type x y z vx vy vz
run 200000
```

- **`velocity ... create`** gives every atom a random velocity consistent with temperature `t`. The number `12345` is the random seed; change it to get a statistically independent run.
- **`fix nvt`** is a thermostat: it holds the **N**umber of atoms, the **V**olume, and (on average) the **T**emperature constant. The last number is the damping time, here 100 timesteps.
- **`thermo`** prints the step, temperature, total energy, and pressure every 100 steps. Watch these to see whether your system is stable.
- **`dump`** writes the positions and velocities of every atom every 100 steps.
- **`run`** advances the simulation that many timesteps. 200,000 × 0.25 fs = 50 ps.

### `write_data` versus `dump`

Both produce files you can open in OVITO, but they serve different purposes:

| | `write_data` | `dump` |
|---|---|---|
| Contents | One snapshot: positions, box, masses, and optionally velocities and coefficients | Many snapshots over time, with whatever per-atom values you list |
| Can LAMMPS read it back? | Yes, with `read_data`. It's the standard way to save and reuse a structure. | Not directly |
| Typical use | Starting point for the next simulation; checking the built structure | Animations and analysis of how the system evolves |

## Running LAMMPS

Open a terminal in the folder that contains the script and its potential file:

- **Windows:** in File Explorer, click the address bar, type `cmd`, and press Enter.
- **macOS / Linux:** open a terminal and `cd` into the folder.

Then run:

```bash
lmp -in graphene.lmp
```

`lmp` is the LAMMPS executable. Depending on how it was installed, it may be called `lmp_serial`, `lmp_mpi`, or similar. To use several CPU cores, run it through MPI, for example `mpirun -np 4 lmp -in graphene.lmp`. If your LAMMPS was built with the GPU package and you have a supported graphics card, add `-sf gpu -pk gpu 1` to use it.

Press **Ctrl+C** to stop a run early. The output files written so far are kept.

## Visualizing in OVITO

1. **Open the structure:** drag `graphene_data.txt` into OVITO. When asked, choose *LAMMPS data* as the format.
2. **Make it readable:** under *Particle types*, reduce the atom radius (about 0.6 works well here) and pick a color.
3. **Add bonds:** *Add modification* → **Create bonds**. OVITO draws a bond between any two atoms closer than the cutoff, so the honeycomb appears.
4. **Add the motion:** *Add modification* → **Load trajectory**, and pick `graphene_dump.txt`. Press play on the timeline to watch the atoms vibrate.
5. **Tidy up and export:** turn off the simulation cell display, then use *Render active viewport* to save an image or a movie.

Loading the data file first and the dump as a trajectory keeps the box and atom types from the data file while taking the positions from the dump.

With the skeleton in place, the next chapter builds our first structure from scratch.
