---
title: "Carbon Nanotube: Rolling a Sheet with a Loop"
short: "Carbon nanotube"
weight: 5
summary: "Build a graphene sheet, then roll it into a nanotube by moving every atom with a coordinate transformation, using LAMMPS loops and displace_atoms."
learn:
  - "Turning geometry into a coordinate transformation"
  - "Loops in LAMMPS: `variable ... loop`, `label`, `next`, `jump`"
  - "Moving atoms with `displace_atoms`"
  - "Immediate evaluation `$(...)` versus a formula variable"
image: "/videos/md-lammps-guide/cnt-poster.jpg"
---

{{< guide-video src="/videos/md-lammps-guide/cnt.mp4" alt="A carbon nanotube rendered in OVITO, a hollow cylinder of carbon atoms in a honeycomb pattern" caption="The goal: a (15, 0) zigzag carbon nanotube, 11.7 Å in diameter, made by rolling up a graphene sheet." >}}

A carbon nanotube (CNT) is a graphene sheet rolled into a seamless cylinder. Dedicated nanotube builders exist, but doing it in LAMMPS teaches two tools you'll use again and again: **loops** and **moving atoms**. The plan has just two steps: make a flat graphene sheet, then move every atom onto a cylinder.

## Step 1: a flat sheet in the x–z plane

This is the graphene recipe from [Chapter 2](../graphene/), with one change: the sheet lies in the **x–z** plane instead of x–y, so that z can become the tube's axis. In the lattice, the vector that was along y now points along z:

```bash
lattice custom ${l} &
  a1 $(sqrt(3)) 0.0 0.0 &
  a2 0.0 1.0 0.0 &
  a3 0.0 0.0 3.0 &
  basis 0.0 0.0 0.0 &
  basis $(1/2) 0.0 $(1/6) &
  basis $(1/2) 0.0 $(1/2) &
  basis 0.0 0.0 $(2/3)
region graphenebox block 0 ${L} -0.1 0.1 0 ${W} units box
create_atoms 1 region graphenebox
```

With $m = 15$ cells around and $n = 20$ cells along the axis, the sheet is $L = 36.9$ Å by $W = 85.2$ Å, with 1200 atoms. The box is periodic along z, so the finished tube is effectively infinitely long.

## Step 2: the coordinate transformation

Roll the sheet so that its length $L$ (along x) becomes the circumference of the tube. An atom at position $x_i$ along the sheet ends up at angle $\theta$ around a circle of radius $R$:

{{< svgfig src="/images/resources/md-lammps-guide/cnt-rolling.svg" width="620" caption="Each atom's distance along the sheet, $x_i$, becomes an angle $\theta$ around a circle whose circumference is the sheet length $L$." >}}

$$R = \frac{L}{2\pi}, \qquad \theta_i = \frac{2\pi x_i}{L}$$

$$x_i' = R\cos\theta_i + a, \qquad y_i' = R\sin\theta_i + b, \qquad z_i' = z_i$$

Here $(a, b)$ is the center of the tube. The z coordinate doesn't change. Each atom just needs to be moved by

$$\Delta x = x_i' - x_i, \qquad \Delta y = y_i' - y_i, \qquad \Delta z = 0$$

## Step 3: loop over every atom

The transformation has to be applied to each atom in turn. Most programming languages use a `for` loop for this; LAMMPS has its own version, built from four commands:

```bash
variable a loop N          # counter a runs 1, 2, ..., N
label    my_loop           # where each pass begins
#   ... commands that use $a ...
next     a                 # advance the counter (exits the loop after N)
jump     SELF my_loop      # go back to the label (SELF = this same script)
```

Here is the CNT loop. The counter `id` runs over every atom ID:

```bash
variable R  equal ${L}/(2*3.14159265359)  # radius of the CNT
variable cx  equal (xlo+xhi)/2.0 # center of the CNT
variable cy  equal (ylo+yhi)/2.0 # center of the CNT

# setting up loop for displacing atoms
variable natoms  equal count(all)
variable id loop ${natoms}
label loop

group anatom id ${id}
variable x equal xcm(anatom,x)
variable y equal xcm(anatom,y)

variable theta  equal $(v_x*2*3.1416/lx)

variable newx equal $(v_R*cos(v_theta)+v_cx)
variable newy equal $(v_R*sin(v_theta)+v_cy)

variable dx  equal $(v_newx-v_x)
variable dy  equal $(v_newy-v_y)

displace_atoms anatom move v_dx v_dy 0.0 units box
group anatom delete
next id
jump SELF loop
```

Line by line:

- **`R`, `cx`, `cy`** are the radius $L/2\pi$ and the center $(a, b)$ of the tube. `xlo`, `xhi`, `ylo`, `yhi` are the box bounds, so the tube sits in the middle of the box.
- **`count(all)`** is a built-in function that returns the number of atoms (1200).
- **`group anatom id ${id}`** makes a group containing only the current atom. **`xcm(anatom,x)`** is the group's center of mass, which for a one-atom group is simply that atom's position.
- **`$(...)`** evaluates each formula **immediately** and stores the number. This matters: an `equal`-style variable written without `$( )` is a *formula*, re-evaluated every time it's used. Since the atom is about to move, we want its position frozen *before* moving it.
- **[`displace_atoms`](https://docs.lammps.org/displace_atoms.html)** `group move dx dy dz` shifts the group by the given amounts.
- **`group anatom delete`** matters too: LAMMPS allows at most 32 groups, so without it the loop would fail after about 30 atoms.

## The result

The 15 graphene cells around the circumference make a **(15, 0) zigzag** nanotube: the $\vec a_1$ direction we rolled along is graphene's zigzag direction. Its radius is $R = 36.89/2\pi = 5.87$ Å (11.74 Å diameter), which matches the textbook value for a (15, 0) tube. After that, the script continues with the standard skeleton: the Tersoff potential, minimization, and an NVT run at 298 K.

```bash
lmp -in cnt.lmp
```

The loop over 1200 atoms takes less than a second. In OVITO, add **Create bonds** and rotate the view to look down the tube axis (z).

{{< lmpfile src="/documents/md-lammps-guide/cnt/cnt.lmp" title="Full script: cnt.lmp" >}}

[Download the CNT folder (.zip)](/documents/md-lammps-guide/cnt.zip): the script and `SiCGe.tersoff`.

## Going further: one command instead of a loop

The loop is the clearest way to see what happens to each atom, but LAMMPS can also move every atom at once using **atom-style variables**, which hold one value per atom. There is one trap: `displace_atoms` applies the x shift *before* it evaluates the y variable, so $\theta$ has to be saved before anything moves:

```bash
variable theta atom 2*PI*x/lx
fix freeze all store/state 0 v_theta   # snapshot theta before any atom moves
run 0                                  # initializes the stored values
variable dx atom v_R*cos(f_freeze)+v_cx-x
variable dy atom v_R*sin(f_freeze)+v_cy-y
displace_atoms all move v_dx v_dy 0.0 units box
```

These lines replace everything from `variable natoms` to `jump SELF loop` and produce the same tube. Without the `fix store/state` snapshot, the result is a squashed tangle of atoms. That's a good reminder to always look at your structure in OVITO before running anything long.

## Try this

1. Change `m` to 10 and 20. How does the radius change? Is it what $R = m\sqrt3\,l / 2\pi$ predicts?
2. Swap the roles of the two directions (roll along the $3l$ direction instead). You'll get an **armchair** nanotube.
3. Increase `t` to 1000 K and watch whether the tube stays round.
