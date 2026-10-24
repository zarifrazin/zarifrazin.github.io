---
title: "Try It Yourself: Liquid Argon Confined Between Copper Plates"
short: "Try it yourself"
weight: 8
summary: "A practice problem that uses everything from the guide: build a thin film of liquid argon trapped between two copper walls, run it, and check it in OVITO."
learn:
  - "Planning a structure on paper before writing commands"
  - "Combining the building blocks from earlier chapters on your own"
---

You now have every tool you need to build a new system from scratch. Here is one to practice on: a **nano-confined liquid**, a few nanometers of liquid argon trapped between two copper plates. It's a classic setup for studying how liquids behave near walls, for example how they conduct and store heat.

<figure>
  <img src="/images/resources/md-lammps-guide/nano-confined-argon.jpg" alt="Schematic of liquid argon atoms between a bottom and top copper plate, 6.14 nm wide with a gap height h" style="max-width: 460px;">
  <figcaption>Liquid argon between two copper plates. The plates are 6.14 nm wide, and the gap height $h$ is up to you.</figcaption>
</figure>

## The task

Write an input script that:

1. Creates a **bottom copper plate**, a **layer of liquid argon** on top of it, and a **top copper plate** above that, with the argon filling the gap of height $h$.
2. Is periodic in the two directions **along** the plates, and not periodic across them.
3. Keeps the plates in place while the argon is free to move.
4. Minimizes the energy and then runs at 90 K, writing a dump file you can open in OVITO.

## Hints

Try it without these first. Each hint points back to the chapter where the idea came from.

<details>
<summary><strong>Which chapter is closest?</strong></summary>

The [droplet on copper](../droplet/) script. It already has a copper plate, liquid argon, the right lattice constants and potentials, and a frozen bottom layer. You mostly need to change the geometry.
</details>

<details>
<summary><strong>How do I make two plates?</strong></summary>

Define two regions with the copper lattice (`lattice fcc 3.610`), one at the bottom and one at the top, and call `create_atoms 2` for each. Remember `units box` on every region.
</details>

<details>
<summary><strong>How do I fill the gap with liquid?</strong></summary>

Switch to the liquid argon lattice (`lattice fcc 5.85`), define a region between the two plates, and `create_atoms 1` in it. Leave a small gap (about 2–3 Å) between the argon and each plate so no atoms start overlapping.
</details>

<details>
<summary><strong>How wide should the box be?</strong></summary>

As in [Chapter 2](../graphene/), the periodic directions should hold a whole number of unit cells, and here that has to work for **both** lattices. 6.14 nm is $10.5 \times 5.85$ Å for argon, and very close to $17 \times 3.61 = 61.37$ Å for copper.

"Very close" isn't enough, though. If the copper regions span the full 61.43 Å box, LAMMPS creates an extra row of copper 0.05 Å from its periodic image, and because the plates are frozen, that overlap never relaxes: the energy starts in the millions of eV. Stop the copper regions just short of 17 cells, for example at `$(17*3.61-0.01)`, so the last row of copper isn't created on top of its own periodic image.
</details>

<details>
<summary><strong>How do I hold the plates still?</strong></summary>

Put the plate atoms in a group and use `fix setforce 0.0 0.0 0.0` and `velocity ... set 0.0 0.0 0.0`, as the droplet script does for its bottom layer. Then apply the `nvt` thermostat only to the argon group instead of to `all`.

The `temp` printed by `thermo` averages over **all** atoms, including the frozen copper, so it will read far below 90 K. To see the liquid's temperature, add `compute tAr ar temp` and print `c_tAr` in `thermo_style`.
</details>

## Check your result

- Count the atoms. Does the number match what you expect from the volume and the density?
- In OVITO, look at the argon from the side. Next to the walls, the liquid packs into distinct **layers** instead of being uniformly disordered. This ordering of a liquid at a solid surface is real, and it's one of the reasons confined liquids behave differently from bulk ones.
- If an empty gap opens up inside the liquid, there isn't enough argon to fill the space at liquid density (the dense layers on the walls use up some of it). Make the gap $h$ or the spacing to the walls a little smaller.
- Change the Ar–Cu interaction strength (the `0.03` factor in the droplet script's `pair_coeff 1 2` line) and see how the layering changes.

## Where this leads

This exact system, with walls that have patterned wettability, is what I use in my research on [heat transfer in nano-confined liquids](/projects/thermal-properties-entrapped-liquid/). My [specific heat script](../../lammps-specific-heat/) builds it in a slightly different way, in lattice units, and computes the liquid's heat capacity. Compare it with your version once you're done.

## Where to go next

You've finished the guide. To keep going with LAMMPS:

- **More scripts:** my [specific heat script](../../lammps-specific-heat/) and my [LAMMPS code samples](/resources/skill-lammps/) (thermal rectification in graphene, and the contact angle of a droplet).
- **Research that uses these methods:** [Thermal Properties of Entrapped Liquid](/projects/thermal-properties-entrapped-liquid/), [Specific Heat Capacity of Nano-Confined Liquids](/projects/specific-heat-capacity-nano-confined/), and the paper [*Thermal properties of liquid entrapped between hybrid wettability surface*](/publications/thermal-properties-of-liquid-entrapped-between-hybrid-wettability-surface/).
- **Find all of it in one place:** use the **LAMMPS** filter on the [Resources](/resources/) page.
