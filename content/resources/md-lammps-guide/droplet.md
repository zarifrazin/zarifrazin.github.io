---
title: "Argon Droplet on Copper: Carving Shapes and Mixing Phases"
short: "Droplet on a surface"
weight: 6
summary: "Place a liquid argon droplet on a copper plate surrounded by argon vapor, and watch it settle into its equilibrium shape. A first look at wetting and contact angles."
learn:
  - "Lattice constants from density, so a liquid starts at the right density"
  - "Carving a hole with `delete_atoms` and refilling it"
  - "Mixing EAM and Lennard-Jones potentials; tuning how much a liquid likes a surface"
  - "A non-periodic direction, a reflecting wall, and a frozen layer of atoms"
  - "Why a thermostat should only act on atoms that are free to move"
image: "/videos/md-lammps-guide/droplet-poster.jpg"
---

When a droplet sits on a surface, its shape tells you how strongly the liquid is attracted to the solid. A liquid that "likes" the surface spreads out into a flat puddle (**hydrophilic**), and one that doesn't beads up (**hydrophobic**). The angle where the liquid surface meets the solid, the **contact angle**, measures this. MD lets you compute it directly from the atoms. In this chapter we build the classic setup: liquid argon on a copper plate, surrounded by its own vapor.

{{< guide-video src="/videos/md-lammps-guide/droplet.mp4" alt="Side view of a cube of liquid argon on a copper plate, surrounded by argon vapor, relaxing into a rounded droplet" caption="The goal: a cube of liquid argon on a copper plate, surrounded by argon vapor, relaxes into a rounded droplet." >}}

## The plan: fill, carve, refill

Building three different regions (solid, vapor, liquid) sounds complicated, but `delete_atoms` makes it easy:

{{< svgfig src="/images/resources/md-lammps-guide/droplet-workflow.svg" width="700" caption="Build the copper plate, fill everything above it with argon vapor, delete the vapor where the droplet will go, then fill that hole with liquid argon." >}}

## Lattice constants from density

Argon at 90 K is a liquid, and a liquid has no crystal lattice. But MD only needs a sensible **starting** arrangement: as soon as the simulation runs, the atoms move around and the order disappears. So we place the argon on an FCC lattice whose spacing gives the correct **density**. For an FCC cell of side $a$ holding $n = 4$ atoms of molar mass $M$:

$$\rho = \frac{nM}{N_A\,a^3} \quad\Longrightarrow\quad a = \left(\frac{nM}{\rho\,N_A}\right)^{1/3}$$

| Phase | Density | Lattice constant $a$ |
|---|---|---|
| Copper (solid FCC) | 8.96 g/cm³ | 3.610 Å |
| Liquid argon at 90 K | 1.33 g/cm³ | 5.85 Å |
| Argon vapor at 90 K | 0.0168 g/cm³ | 25.07 Å |

The vapor spacing is so large that the vapor atoms are far apart, exactly as a gas should be.

## Building it

The droplet starts as a cube of side $l = 50$ Å, and the box is sized from it:

```bash
variable l equal 50.0 # length of a the cubic droplet side
variable L equal $(4*v_l) # length of the simulation box in x direction
variable W equal $(v_l) # length of the simulation box in y direction
variable H equal $(5*v_l) # length of the simulation box in z direction

region box block 0 ${L} 0 ${W} 0 ${H} units box
create_box 2 box
mass 1 39.948 # mass of argon atom
mass 2 63.546 # mass of copper atom
```

Then the three building steps:

```bash
# Generating copper plate
lattice fcc 3.610
region plate block 0 ${L} 0 ${W} 0 5 units box
create_atoms 2 region plate

# Generating argon vapor
lattice fcc 25.068
region vapor block 0 ${L} 0 ${W} 5 ${H} units box
create_atoms 1 region vapor

# Generating cubic droplet
region droplet block $(v_L/2.0-v_l/2.0) $(v_L/2.0+v_l/2.0) &
 $(v_W/2.0-v_l/2.0) $(v_W/2.0+v_l/2.0) &
 5 $(5+v_l) units box
delete_atoms region droplet
lattice fcc 5.85
create_atoms 1 region droplet
```

The copper plate is 5 Å thick, and the vapor fills everything above it. To center a cube of side $l$ in a box of length $L$, it has to start at $\tfrac{L}{2}-\tfrac{l}{2}$ and end at $\tfrac{L}{2}+\tfrac{l}{2}$. In z it starts on top of the plate at 5 Å and is $l$ tall. Note that `units box` matters here: without it, LAMMPS would measure these distances in multiples of whatever lattice was defined last.

**[`delete_atoms`](https://docs.lammps.org/delete_atoms.html)** `region droplet` removes every atom inside that region. Atoms can also be deleted by group, by overlap, or at random.

### Why "cylindrical"?

The box is exactly as wide in y as the droplet ($W = l$), and y is periodic. So the "cube" of liquid touches its own periodic images in y and forms an **infinitely long bar** of liquid, which relaxes into a cylinder lying on the plate (its cross-section is a circle cut off by the surface) instead of a spherical cap. That's deliberate: a cylindrical droplet has a straight contact line, which removes the line-tension effects that make small spherical droplets harder to analyze, and you can measure the contact angle from a simple 2D side view.

## Two potentials, one tunable knob

```bash
pair_style hybrid eam lj/cut 10.0 
pair_coeff  2 2  eam Cu_u3.eam
pair_coeff	1 1 lj/cut 0.0103 3.405 8.5
pair_coeff	1 2 lj/cut $(0.03*0.06489) 2.872 11.9
```

- **Cu–Cu:** an **embedded-atom method** (EAM) potential (Foiles et al., *Phys. Rev. B* 33, 7983, 1986), the standard model for metals.
- **Ar–Ar:** Lennard-Jones with the classic argon parameters, $\varepsilon = 0.0103$ eV and $\sigma = 3.405$ Å.
- **Ar–Cu:** Lennard-Jones with a well depth of $\varepsilon = w \times 0.06489$ eV. The factor $w$ (0.03 here) is the **wettability knob**: it scales how strongly argon is attracted to copper. A small $w$ gives a weakly attracting, hydrophobic surface. Raise it and the droplet spreads.

## Boundaries, walls and a frozen layer

```bash
boundary       p p f

# applying reflective boundary condtions at the top of the box
fix wall1 all wall/reflect zhi EDGE
# fixing the bottome layer of the copper plate
region bottom block 0 ${L} 0 ${W} 0 1 units box
group bottom region bottom
fix  bwall bottom setforce 0.0 0.0 0.0
velocity bottom  set 0.0 0.0 0.0
group mobile subtract all bottom
```

- **`boundary p p f`**: z isn't periodic. If it were, the vapor at the top of the box would interact with the underside of the copper plate.
- **[`fix wall/reflect`](https://docs.lammps.org/fix_wall_reflect.html)** puts a mirror at the top of the box: vapor atoms that reach it bounce back instead of being lost.
- The bottom layer of copper is collected into a group (`group bottom region bottom`), and then its forces and velocities are set to zero. This anchors the plate so it can't drift away or bend.
- **`group mobile subtract all bottom`** makes a group of every atom *except* that frozen layer. It's used for the thermostat below.

## Thermostat only what moves

```bash
compute Tmobile mobile temp
fix 1 mobile nvt temp $t $t $(100.0*dt)
thermo 1000
thermo_style custom step temp etotal press
thermo_modify temp Tmobile
```

A thermostat controls the **average** temperature of the group it is given. The frozen copper layer never moves, so it always counts as 0 K. If it were included, the thermostat would make up for those zeros by heating everything else above 90 K. So the thermostat acts only on the `mobile` group.

The same goes for what gets printed. `compute Tmobile mobile temp` calculates the temperature of the mobile atoms only, and `thermo_modify temp Tmobile` tells `thermo` to report that instead of the all-atom value. (LAMMPS prints a warning that the pressure now uses this temperature too; that's expected.)

## Run it

```bash
lmp -in droplet.lmp
```

This is the biggest system in the guide (about 7,800 atoms) and the longest run: 200,000 steps, or 50 ps. Expect around 12 minutes on 6 cores. It's a good candidate for trying out a [cluster](../running-on-a-cluster/) (the folder includes a job script, `run_lmp.sh`).

In OVITO, open `droplet_data.txt`, load `droplet_dump.txt` as a trajectory, and look along the y axis (the *Front* view). Make the vapor atoms smaller or semi-transparent so the droplet stands out.

{{< lmpfile src="/documents/md-lammps-guide/droplet/droplet.lmp" title="Full script: droplet.lmp" >}}

[Download the droplet folder (.zip)](/documents/md-lammps-guide/droplet.zip): the script, `Cu_u3.eam` and `run_lmp.sh`.

## Try this

1. Change the wettability factor from `0.03` to `0.1`, `0.5` and `1.0`, and compare the final shapes. How does the contact angle change as copper attracts argon more strongly?
2. Make the box shorter in x ($L = 3l$). Does the droplet now reach its periodic image?
3. The `mobile` group mixes argon and copper. Add `group ar type 1` and `compute tAr ar temp`, and print `c_tAr` next to `temp` in `thermo_style`. Do the argon and the copper stay at the same temperature?

## Going further

My [LAMMPS code samples](/resources/skill-lammps/) include a script that measures the **contact angle of an argon droplet on a copper surface**, which is the analysis this chapter builds up to.
