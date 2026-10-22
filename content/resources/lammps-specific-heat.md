---
title: "LAMMPS Script for Specific Heat Calculation"
date: 2026-06-04
summary: "An input script for LAMMPS to calculate specific heat capacity of confined argon under solid copper walls."
category: "Simulation Scripts"
tags:
  - "LAMMPS"
  - "Molecular Dynamics"
  - "Specific Heat"
github: "https://github.com/zarifrazin/ncl_hybrid_wettability"
download: ""
pdf: ""
featured: true
math: true
---

### Simulation Description
This resource contains a sample LAMMPS input script to compute the constant volume specific heat capacity ($C_v$) of liquid argon confined between solid copper walls with hybrid wettability (the script loops over the fraction of hydrophilic area and the two wettability strengths), using equilibrium molecular dynamics (EMD). The solid-liquid interaction is modeled using the Lennard-Jones (LJ) potential.

### LAMMPS Input Script

```lammps
#----------------------------------Initialization-----------------------------------
variable		Ocount loop 3
variable		wO index 0.02 0.06 0.1

label		Ichange

variable		Icount loop 3
variable		wI index 1.0 0.5 0.1

shell		mkdir wettability_wO_${wO}_wI_${wI}
shell		cd wettability_wO_${wO}_wI_${wI}

label		fchange

variable		fcount loop 18
variable		f index 0.1 0.15 0.2 0.25 0.3 0.35 0.4 0.45 0.5 0.55 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95	#Percentage of hydrophilic area

log			log_ncl_$f.txt
#processors		* * * grid numa
#package		intel 0 omp 1
units			metal
dimension		3
boundary		p f p
atom_style		atomic


variable		t equal 100
variable		h equal 5.00
#variable		wI equal 1.0
#variable		wO equal 0.02
variable		l equal 10.5
variable		fI equal $f	#Percentage of hydrophilic area
variable		volume equal $(v_l*v_l*(v_h+1)*5.85*5.85*5.85)

#---------------------------------System Definition---------------------------------

#Simulation Box

lattice		fcc 5.85
region			box block -0.25 10.5 -1 $(v_h+3.0) 0 10.5
create_box		3 box 

#Set up atoms 

region			B block 0 INF 1.0 $(v_h+1.0) 0 INF
region			A1 block 0 INF -0.5 0.5 0 INF
region			A2 block 0 INF $(v_h+1.51) $(v_h+2.5) 0 INF
region			A1I block 0 $(v_f*v_l) -0.5 0.5 0 INF
region			A1O block $(v_f*v_l) INF -0.5 0.5 0 INF
region			A2I block 0 $(v_f*v_l) $(v_h+1.51) $(v_h+2.5) 0 INF
region			A2O block $(v_f*v_l) INF $(v_h+1.51) $(v_h+2.5) 0 INF
region			fluid block 0 INF 0.5 $(v_h+1.5) 0 INF

create_atoms		1 region B
lattice		fcc 3.615
create_atoms		2 region A1I
create_atoms		2 region A2I
create_atoms		3 region A1O
create_atoms		3 region A2O

group			ar type 1
group			cuI type 2		#hydrophIllic
group			cuO type 3		#hydrophObic
group			cu union cuI cuO

mass			1 39.95
mass			2 63.55
mass			3 63.55

velocity		all create $t 4928459

#---------------------------------Simulation Settings---------------------------------------

#force field

pair_style	lj/cut 8.5
pair_coeff	1 1 0.0103 3.405 8.5
pair_coeff	2 2 0.41148 2.34 6.5
pair_coeff	3 3 0.41148 2.34 6.5
pair_coeff	2 3 0.41148 2.34 6.5
pair_coeff	1 2 $(v_wI*0.06489) 2.872 11.9
pair_coeff	1 3 $(v_wO*0.06489) 2.872 11.9

neighbor	0.35 bin
neigh_modify	delay 1

#settings

timestep	0.005

#Apply fix

fix		1 cu spring/self 4.3

shell		mkdir trajectory_ncl_$f
shell		cd trajectory_ncl_$f

fix		2 ar nvt temp $t $t $(10*dt)
fix		myfix cu nvt temp $t $t $(10*dt)
thermo		100
thermo_modify	lost ignore
#dump		1 all custom 100 tarj.all_atom.*.txt id type x y z
dump			1 all atom 1000 traj_all_atom_*.txt
run		3000  

shell		cd ..
undump		1

compute	arTemp ar temp
compute	cuTemp cu temp 
thermo		1000
thermo_style	custom step temp c_arTemp c_cuTemp etotal press  
run		1500000

write_data	pp_data_ncl_$f.txt
write_restart	pp_restart_ncl_$f.bin

#output 

#Energy Calculation
compute		pe ar pe/atom
compute		PE ar reduce sum c_pe
compute		KE ar ke
variable	E equal c_PE+c_KE
variable	Esq equal v_E*v_E
variable	KEsq equal c_KE*c_KE
variable	PEsq equal c_PE*c_PE
variable	N equal count(ar)

#MSD
compute		arMSD ar msd
fix		MSD ar ave/time 100 1 100 c_arMSD[1] c_arMSD[2] c_arMSD[3] c_arMSD[4] file msd_ar_ncl_$f.txt

#RDF
compute		arRDF ar rdf 500 1 1
fix		RDF ar ave/time 1000 1 1000 c_arRDF[*] file rdf_ar_ncl_$f.txt mode vector

#Pressure 
compute		peratomS ar stress/atom arTemp
compute		stress ar reduce sum c_peratomS[1] c_peratomS[2] c_peratomS[3]
variable	arPress equal -(c_stress[1]+c_stress[2]+c_stress[3])/(3*v_volume)

fix		5 ar ave/time 2 500 1000 v_N v_fI c_arTemp v_arPress v_Esq v_E c_PE v_PEsq c_KE v_KEsq file cv_data_ncl_$f.txt

#Density Profile

#compute		allChunk all chunk/atom bin/3d x lower INF y lower 5.85 z lower INF
compute		arChunk all chunk/atom bin/1d y lower 0.01 region fluid units reduced
fix		arDensity all ave/chunk 2 500 1000 arChunk density/mass density/number file ardensity_ncl_$f.txt 
  
thermo		1000
thermo_style	custom step f_5[*]
run		100000

unfix		MSD
unfix		RDF
unfix		arDensity
run		1500000


clear

next		f
next		fcount
jump		SELF fchange

shell	cd ..

next		wI
next		Icount
jump		SELF Ichange

next		wO
next		Ocount
jump		SELF
```
