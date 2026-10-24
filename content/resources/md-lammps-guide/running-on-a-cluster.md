---
title: "Running LAMMPS on a Computing Cluster"
short: "Running on a cluster"
weight: 7
summary: "When a simulation outgrows your laptop: log in to a cluster, move your files over, write a job script, submit it, and check on it, using only a handful of commands."
learn:
  - "Logging in with `ssh` and moving files with WinSCP, FileZilla or `scp`"
  - "The six Linux commands you actually need"
  - "Writing a job script and submitting it to a scheduler (LSF and Slurm)"
  - "Checking, reading and cancelling jobs"
---

Everything in this guide runs on a laptop in minutes. Research systems are usually much larger or longer, and that's where a **high-performance computing (HPC) cluster** comes in: many computers (**nodes**), each with dozens of CPU cores, shared by many users. You don't run programs on a cluster directly. Instead, you describe what you need in a **job script**, hand it to a **scheduler**, and the scheduler runs it when resources are free.

Most universities have a cluster; ask your research computing office for an account. The commands below use **NC State's Hazel cluster**, which runs the **LSF** scheduler, as the worked example. Many other clusters use **Slurm**, and the equivalent commands are shown alongside.

## 1. Log in

From a terminal (Command Prompt or PowerShell on Windows, Terminal on macOS/Linux):

```bash
ssh your_username@login.your-cluster.edu
```

For example, `ssh unityid@login.hpc.ncsu.edu` at NC State. Type your password (nothing appears on screen while you type; that's normal) and complete any two-factor prompt. Logins sometimes fail on the first attempt because of security checks, so just try again.

## 2. Move your files over

You need the input script, the potential file, any data files, and the job script on the cluster.

- **With a graphical tool:** [WinSCP](https://winscp.net/) (Windows) or [FileZilla](https://filezilla-project.org/) (any OS). Create a new site with protocol SFTP, the login host above, port 22, and your username and password. You'll see your computer on one side and the cluster on the other; drag files across.
- **From the command line:** `scp -r droplet/ your_username@login.your-cluster.edu:~/` copies the whole `droplet` folder to your home directory.

> **Mind your disk quota.** Home directories on clusters are usually small (often under a few GB) and are meant for scripts, not simulation output. A long run with frequent `dump` output can fill them quickly. Run real jobs from the larger **scratch** or **project** space your cluster provides (at NC State, `/share/<group>/<user>`). Ask your administrators which directory to use.

## 3. The Linux commands you need

Clusters run Linux and have no graphical desktop. These six commands cover nearly everything:

| Command | What it does |
|---|---|
| `pwd` | **P**rint **w**orking **d**irectory: where am I? |
| `ls` | **L**i**s**t the files here |
| `cd droplet` | **C**hange **d**irectory into `droplet` |
| `cd ..` | Go up one level (`.` is the current folder, `..` the parent) |
| `mkdir lmp_test` | **M**a**k**e a new **dir**ectory |
| `less file.txt` | Read a file one screen at a time (arrow keys to scroll, **q** to quit) |

## 4. Write a job script

The job script tells the scheduler what resources you need and what to run. This is the one used in the lecture (`run_lmp.sh` in the droplet folder):

```bash
#!/bin/bash
#BSUB -n 32
#BSUB -R "span[hosts=1]"
#BSUB -W 60
#BSUB -J droplet
#BSUB -o stdout.%J
#BSUB -e stderr.%J

module load lammps/2022Jun23/intel/cpu
mpirun lmp_hazel -in droplet.lmp
```

The `#BSUB` lines are instructions to the scheduler, not comments:

| LSF line | Meaning | Slurm equivalent |
|---|---|---|
| `#BSUB -n 32` | Use 32 CPU cores (MPI tasks) | `#SBATCH --ntasks=32` |
| `#BSUB -R "span[hosts=1]"` | Put all of them on one node | `#SBATCH --nodes=1` |
| `#BSUB -W 60` | Wall-time limit: 60 minutes, after which the job is killed | `#SBATCH --time=01:00:00` |
| `#BSUB -J droplet` | A job name you'll recognize in the queue | `#SBATCH --job-name=droplet` |
| `#BSUB -o stdout.%J` | File for normal output (`%J` = job ID) | `#SBATCH --output=stdout.%j` |
| `#BSUB -e stderr.%J` | File for error messages | `#SBATCH --error=stderr.%j` |

The last two lines are the actual work. `module load` makes the cluster's installed LAMMPS available (run `module avail lammps` to see the versions on your cluster). `mpirun` then launches it in parallel on the cores you requested. The executable name (`lmp_hazel` here) varies from cluster to cluster, so check your cluster's documentation.

> **Ask for what you need, not the maximum.** The bigger the request, the longer the job may wait in the queue. For small and medium systems, 16 cores on one node is often a good starting point, and a realistic wall time also helps the scheduler fit your job in sooner.

## 5. Submit and check on the job

| Task | LSF | Slurm |
|---|---|---|
| Submit | `bsub < run_lmp.sh` | `sbatch run_lmp.sh` |
| List my jobs | `bjobs` | `squeue -u $USER` |
| Cancel one job | `bkill <jobid>` | `scancel <jobid>` |
| Cancel all my jobs | `bkill 0` | `scancel -u $USER` |

Note the `<` in the LSF submit command: the script is *fed into* `bsub`. In `bjobs`, a status of `PEND` means the job is waiting for resources and `RUN` means it's running.

There's no progress bar. Everything LAMMPS would normally print to your screen goes into `stdout.<jobid>` instead, so `less stdout.12345` (or the LAMMPS log file) shows how far the run has got: compare the latest step number with the `run` length in your script.

## 6. Bring the results home

When the job finishes, copy the output files (`*_data.txt`, `*_dump.txt`, `*_log.txt`) back to your computer with WinSCP, FileZilla or `scp`, and open them in OVITO as usual.

## Do you need a cluster at all?

Not always. Every system in this guide runs comfortably on a modern laptop, and laptops now have several cores; `mpirun -np 4 lmp -in ...` will use them. A cluster becomes worth the overhead once a run takes hours instead of minutes, or when you need many runs at once (for example, sweeping a parameter). Get your cluster account set up early, though: sorting out access and directories always takes longer than you expect.
