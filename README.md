# singularity-technical-seminar
Technical seminar on containerizing bioinformatics pipelines 📦 🧬 💻 👩🏻‍💻 🧪

> [!IMPORTANT]
> If you want to clone this repository containing the submodules with the examples, use the following command:
> `git clone --recurse-submodules -j4 https://github.com/Gabaldonlab/singularity-technical-seminar`

# Table of content
- [What is Singularity](#what-is-singularity)
- [Key Features of Singularity-CE](#key-features-of-singularity-ce)
- [Singularity-CE vs. Docker](#singularity-ce-vs.-docker)
- [Install Singularity on Debian based Linux](#install-singularity-on-debian-based-linux)
- [Singularity definition files](#singularity-definition-files)
    - [File structure](#file-structure)
    - [Convert Dockerfile into Singularity .def files](#convert-dockerfile-into-singularity-.def-files)
- [Useful commands](#useful-commands)
    - [Basic Commands](#basic-commands)
    - [Building & Managing Containers](#building--managing-containers)
    - [Inspect metadata](#inspect-metadata)
    - [Filesystem & Bind Mounting](#filesystem--bind-mounting)
    - [Networking & Permissions](#networking--permissions)
    - [Advanced Usage](#advanced-usage)
- [Building singularity images for pipelines: Two Approaches](#building-singularity-images-for-pipelines-two-approaches)
    - [Approach 1: Image Contains Only Runtime & Dependencies](#approach-1-image-contains-only-runtime--dependencies)
    - [Approach 2: Fully Self-Contained Image](#approach-2-fully-self-contained-image)
    - [Comparison](#comparison)
    - [Which Approach Should You Choose?](#which-approach-should-you-choose)
- [Development with incremental build Build in "chunks"](#development-with-incremental-build-build-in-chunks)
    - [Why Build Singularity Images Incrementally?](#why-build-singularity-images-incrementally)
    - [How to build incrementally in "chunks"?](#how-to-build-incrementally-in-chunks)
        - [1. Use a base image](#1-use-a-base-image)
        - [2. Build and save a partial image](#2-build-and-save-a-partial-image)
        - [3. Extend the base image](#3-extend-the-base-image)
- [Example for "black box first" strategy to containerize a pipeline](#example-for-black-box-first-strategy-to-containerize-a-pipeline)
    - [1. Identify the programming languages](#1-identify-the-programming-languages)
    - [2. Start with the skeleton of the Singularity definition file.](#2-start-with-the-skeleton-of-the-singularity-definition-file)
    - [3. Look for libraries by languages](#4-create-the-second-chunk-file-in-the-image-build)
    - [4. Create the second "chunk file" in the image build.](#4-create-the-second-chunk-file-in-the-image-build)
    - [5. Install rest of the dependencies through runtime error](#5-install-rest-of-the-dependencies-through-runtime-error)
    - [6. Join the chunk files into your final definition file](#6-join-the-chunk-files-into-your-final-definition-file)
- [Debugging with Singularity images](#debugging-with-singularity-images)
- [EXAMPLES - Projects already converted to Singularity](#examples---projects-already-converted-to-singularity)
---

# What is Singularity-CE (Community Edition)?

**Singularity-CE** is an open-source container platform designed for high-performance computing (HPC), AI, and scientific workloads. It allows users to package applications and their dependencies into portable, reproducible containers.

# Key Features of Singularity-CE
- **Security-Focused**: Unlike Docker, Singularity-CE doesn’t require root privileges to run, making it safer for HPC environments.
- **Reproducibility**: Ensures that software runs consistently across different systems.
- **Mobility of Compute**: Packages applications and dependencies into a single file (`.sif` - Singularity Image Format), making it easy to move across different environments.
- **Seamless Integration with HPC**: Works well with SLURM, MPI, and other HPC frameworks.
- **Support for GPUs & AI Workloads**: Compatible with NVIDIA and AMD GPUs for deep learning and scientific computing.

---

# Singularity-CE vs. Docker

| Feature          | Singularity-CE | Docker |
|-----------------|---------------|--------|
| **User Privileges** | Runs as non-root | Typically requires root |
| **Security**       | More secure for HPC | Needs extra security measures |
| **Compatibility**  | Works with HPC schedulers | Designed for cloud and microservices |
| **Container Format** | `.sif` (single file) | Layered filesystem |


![docker vs singularity](https://github.com/Gabaldonlab/singularity-technical-seminar/blob/main/assets/singularity-vs-docker.png?raw=true)

---

# Install Singularity on Debian based Linux
**IMPORTANT: If you are going to run the pipeline in an HPC environment, skip this section!**

*Note: you will always have to build the singularity images on your local machine, because it requires sudo and that you won't have in your remote hpc environment!*

To be able to build the Singularity image of MeTAline, you will need to install Singularity first:

1. Download from [HERE](https://github.com/sylabs/singularity/releases/tag/v4.1.5) the corresponding installation package (_.deb or _.rpm) to your operating system. (E.G.: Ubuntu 24.04 needs the "singularity-ce_4.1.5-noble_amd64.deb" file).
2. Install it from the downloaded package. Example command for the above mentioned version:

```bash
sudo apt install ./singularity-ce_4.1.5-noble_amd64.deb
```

3. Test if the installation is OK.

```bash
singularity --version
```

---

# Singularity definition files

### File structure
```sh
Bootstrap: docker  # Use Docker as the base image
From: ubuntu:22.04  # Pull Ubuntu 20.04 as the base OS

%setup
    # - Executes before the container is built.
    # - Used for tasks like creating directories or downloading external dependencies.

    # Create a directory for storing data
    mkdir -p /data

%files
    # - Copies files from the host into the container.

    # Copy a script from the host into the container
    myscript.sh /usr/local/bin/myscript.sh

%environment
    # - Defines environment variables that persist in the container.

    # Set environment variables
    export PATH="/usr/local/bin:$PATH"
    export MY_VAR="Hello, Singularity!"

%post
    # - Runs after the base image is set up.
    # - Used for installing software and making system changes.

    # Update the package list
    apt-get update
    # Install Python
    apt-get install -y python3
    echo "Installation complete!" > /etc/motd  # Set a message

%runscript
    # - Defines the default command when running the container with singularity run (or singularity exec).

    # This script runs when `singularity run` is executed
    echo "Welcome to my Singularity container!"

%test
    # - Defines a test script to verify that the container works.

    # Check if Python is installed
    python3 --version

%labels
    # - Adds metadata (key-value pairs) to the container.

    # Metadata for the container
    Author "John Doe"
    Version "1.0"

%help
    # - Provides documentation for the container.

    # Help message for users
    This container is built for running Python applications.
```

---

### Convert Dockerfile into Singularity .def files

To convert Dockerfiles into Singularity .def files we can use the [Spython - Singularity Python Recipes](https://singularityhub.github.io/singularity-cli/recipes).

```sh
spython recipe --entrypoint /bin/sh ./<path to Dockerfile> > <path to output .def file>

# Example: spython recipe --entrypoint /bin/sh ./Dockerfile > metaline-singularity.def
```

**Watchouts!** The tool does a great job indeed with the conversion, but there are couple things that you would want to modify after running the tool.
1. Fix the translation error due the difference between how Singularity and Docker copies the files.

    ```
    Docker's file copy command: COPY ./external-sources /bin/
    Singularity's file copy command: ./external-sources/* /bin/
    ```

    As you can see we need to use the /* wildcard for any sub files and directories to be copied properly into our target directory.

2. Remove the default runscript and startscript sections.

    `sed -i '/^%runscript$/,$d' metaline-singularity.def`

    Sometimes we don't want a %runscript section, because we will use the Singularity image as a container for the dependencies and use the language interpreter only for our scripts outside of the container / image.
    *E.G.: singularity run --cleanenv python3 ./my_script.py*

---

# Useful commands

These commands cover installation, execution, image management, filesystem mounting, networking, and security.

### Basic Commands

1. Check Singularity version

    `singularity --version`

2. Pull an image from a container registry (e.g., DockerHub, Sylabs Cloud)

    `singularity pull ubuntu.sif docker://ubuntu:latest`

3. Run a container interactively

    `singularity shell ubuntu.sif`

4. Execute a command inside a container

    `singularity exec ubuntu.sif ls /`

5. Run a container (equivalent to executing its default command)

    `singularity run ubuntu.sif`

### Building & Managing Containers

6.1. Build a Singularity Image File (SIF) from a definition file

    `sudo singularity build my_container.sif my_definition.def`

6.2. Build an image from a Docker source

    `sudo singularity build my_container.sif docker://ubuntu:latest`

### Inspect metadata

7.1. Base inspect command
    `singularity inspect my_container.sif`

7.2. View environment variables inside a container

    `singularity inspect --environment my_container.sif`

### Filesystem & Bind Mounting

8.1. Bind a host directory into the container

    `singularity exec --bind /host/path:/container/path my_container.sif ls /container/path`

8.2. Use a writable temporary overlay filesystem

    `singularity shell --overlay temp_overlay.img my_container.sif`

### Networking & Permissions

9.1. Run a container with a fake root user (useful for installing software inside the container)

    `singularity exec --fakeroot my_container.sif apt-get install -y vim`

9.2. Enable networking inside a container (for use with MPI, etc.)

    `singularity exec --net my_container.sif ping google.com`

### Advanced Usage

10.1. Convert an image to a sandbox for modification

    `sudo singularity build --sandbox my_sandbox/ my_container.sif`

10.2. Push an image to a remote Singularity registry

    `singularity push my_container.sif library://user/collection/container`

10.3. Sign a container image

    `singularity sign my_container.sif`

10.4. Verify a signed container

    `singularity verify my_container.sif`

10.5. Delete a local container cache

    `singularity cache clean`

---

# Building singularity images for pipelines: Two Approaches

When creating a Singularity image for a computational pipeline, you have two main approaches:

1. **The image only contains the runtime and dependencies**, while the scripts remain on the host.
2. **A fully self-contained image**, where the runtime, dependencies, and scripts are all included inside the image.


![approach 1-2](https://github.com/Gabaldonlab/singularity-technical-seminar/blob/main/assets/approaches-1-2.png?raw=true)

---

### Approach 1: Image Contains Only Runtime & Dependencies

In this approach, the `Singularity image` contains only the runtime (e.g., Python, R, or other required software) and all necessary dependencies (e.g., Python libraries, system libraries). The pipeline scripts remain `on the host machine` and are executed by calling the container.

#### Example

```bash
singularity exec --bind /host/scripts:/container/scripts my_pipeline.sif python /container/scripts/run_pipeline.py
```

✅ **Benefits**

- **Smaller image size**: Since the scripts are not included, the image remains lightweight.
- **Easier to update scripts**: You can modify or debug the pipeline scripts without rebuilding the container.
- **Better integration with host filesystem**: Useful when working with shared directories or frequent script changes.
- **Faster iteration**: Avoids rebuilding the image every time a script is updated.

❌ **Disadvantages**

- **Potential dependency mismatch**: If scripts rely on different versions of dependencies over time, you may run into compatibility issues.
- **Risk of breaking changes**: If the scripts are changed but are no longer compatible with the containerized runtime, issues can arise.
- **Less reproducibility**: Since scripts remain on the host, different environments may lead to inconsistencies in results.

---

### Approach 2: Fully Self-Contained Image

In this approach, **everything** (runtime, dependencies, and scripts/tools) is installed inside the Singularity image. The pipeline can run independently of the host system.

#### Example

```bash
singularity run my_pipeline.sif
```

(where the `%runscript` in the Singularity definition file automatically executes the pipeline)

✅ **Benefits**

- **Full reproducibility**: Ensures that the exact same environment is used every time, preventing dependency mismatches.
- **Portability**: The image can be moved to different systems (HPC clusters, cloud, local machines) and still function identically.
- **No external dependencies**: Scripts do not rely on the host system, reducing external failure points.

❌ **Disadvantages**

- **Larger image size**: Including scripts and tools inside the image increases its size.
- **Harder to modify scripts**: If a script needs updating, the entire image must be rebuilt.
- **Slower iteration**: Requires rebuilding and redistributing the image every time a change is made to the pipeline scripts.

---

### Comparison

| Feature                | Runtime + Dependencies Only              | Fully Self-Contained Image                  |
| ---------------------- | ---------------------------------------- | ------------------------------------------- |
| **Image Size**         | Smaller                                  | Larger                                      |
| **Script Flexibility** | Scripts can be modified anytime          | Scripts are fixed inside the image          |
| **Reproducibility**    | Lower (depends on external scripts)      | High (everything is inside)                 |
| **Ease of Updates**    | Easier (no need to rebuild the image)    | Harder (requires rebuilding for any change) |
| **Portability**        | Requires scripts to be copied separately | Fully portable                              |

---

### Which Approach Should You Choose?

- If you **frequently update scripts** and need fast iteration, go with **Approach 1** (runtime + dependencies only).
- If you need **maximum reproducibility and portability**, choose **Approach 2** (fully self-contained).
- A hybrid approach can also be used: keeping scripts on the host for development but packaging them inside the image for final deployment.

---

# Development with incremental build Build in "chunks"

### Why Build Singularity Images Incrementally?
Building a Singularity container incrementally (in "chunks") helps:
1. **Reduce Build Time** – Avoids rebuilding everything from scratch when making small changes.
2. **Improve Debugging** – Easier to identify issues in specific layers.
3. **Increase Reproducibility** – Each step is well-defined, making updates predictable
4. **Enable Caching** – If a step hasn’t changed, it can be reused.

Unlike Docker, Singularity does not have built-in layer caching, but we can still **structure the build incrementally**.

---

### How to build incrementally in "chunks"?

![Incremental chunk build strategy](https://github.com/Gabaldonlab/singularity-technical-seminar/blob/main/assets/incremental-chunk-build-strategy.png?raw=true)

#### 1. Use a base image
Start with a minimal base to avoid unnecessary dependencies.
```singularity
Bootstrap: docker
From: ubuntu:22.04

This ensures that future changes don’t require pulling the OS again.
```

#### 2. Build and save a partial image
Instead of writing all installation steps in one Singularity.def file, split the process.

**Step 1: Install Basic Dependencies**

**Create Singularity.base.def:**

```singularity
Bootstrap: docker
From: ubuntu:22.04

%post
    apt-get update && apt-get install -y \
        wget \
        curl \
        git

%runscript
    echo "Base container ready!"
```

**Build the base image:**

```sh
sudo singularity build base.sif Singularity.base.def
```

Now you have a reusable base.sif.

#### 3. Extend the base image

Instead of modifying base.sif, create another definition file for extra software.
**Step 2: Add tools**

`Create Singularity.tools.def:`

```singularity
Bootstrap: localimage
From: base.sif

%post
    apt-get install -y blast ncbi-blast+
    echo "BLAST installed!"

%runscript
    echo "BLAST is ready to use!"
```

**Build the extended image:**

```sh
sudo singularity build tools.sif Singularity.tools.def
```

Now tools.sif is an incremental build that extends base.sif.
Advantages of This Approach

✅ Faster rebuilds – If you only update tools, you don’t have to re-download Ubuntu or reinstall basic dependencies.

✅ Modular structure – You can swap out different modules (e.g., add R in a separate step).

✅ Easier debugging – If something breaks in tools.sif, base.sif is still intact.


**Final image definition file from joining all the "chunks"**
![Incremental chunk build strategy](https://github.com/Gabaldonlab/singularity-technical-seminar/blob/main/assets/final-build-from-chunks.png?raw=true)

---

# Example for "black box first" strategy to containerize a pipeline
Sometimes you will have to work with pipelines, where all you have is the source code, and you have to containerize it with Singularity so you can run it in your HPC cluster.

**Imagine the following scenery:**

`You get the source code in a dusty repository, but cannot find any documentation about dependencies, just some example commands, small input data, unit tests. As usual, you would want to contact with the author of the pipeline, but unfortunately the person who has written it has quit from the group, has left academy, gone to be a farmer in Norway, and doesn't respond to any calls, messages or e-mail.`

**So, this is a scenery, where you will treat the process as "black box first" strategy. Which is not 100% true, because we have the source code, but in some sense we do not know anything about how it works, what it needs, etc ...**

Of course, you could take your time and read line by line every single file in the repository, but that can take quiet some time to parse through everything.

With the following steps we can speed up the process:

### 1. Identify the programming languages

```bash
# Note that in the find command we filter out the binary files. We do not need them.
find ./my_dummy_pipeline -type f -exec grep -I -q . {} \; -print | awk -F"." '{print $NF}' | sort | uniq -c | sort -rn
```

**OUTPUT:**

```sh
(venv) danielmajer@danielmajer-Latitude-7420:~/workspace/singularity-technical-seminar$
find ./my_dummy_pipeline -type f -exec grep -I -q . {} \; -print | awk -F"." '{print $NF}' | sort | uniq -c | sort -rn
      3 faa
      2 py  # <- Mostly Python files are used.
      1 R   # <- But also there is 1 R file.
      1 /my_dummy_pipeline/Makefile
      1 md
      1 gitignore
```

So from the above output we can guess that mostly `Python` and `R` are used as scripting languages.

**But** some of the files can be named without extensions, so we need to check for the `shebangs` (E.G.: #!/usr/bin/env python3; #!/usr/bin/env Rscript ) headers too!

```bash
head -2 $(find ./my_dummy_pipeline -type f -exec grep -I -q . {} \; -print) | grep -P "^#!"
```

**OUTPUT:**

```sh
(venv) danielmajer@danielmajer-Latitude-7420:~/workspace/singularity-technical-seminar$
head -2 $(find ./my_dummy_pipeline -type f -exec grep -I -q . {} \; -print) | grep -P "^#!" | sort | uniq
#!/usr/bin/env python3
```

Okay, this time we are lucky, and we don't have any surprises. We can considere that only `Python and R` interpreters and libraries will be needed for starting.

### 2. Start with the skeleton of the Singularity definition file.

`1_my_dummy_pipeline.def` <- Note, that we are enumerating the files. It is because of the ["incremental build"](#development-with-incremental-build-build-in-chunks) tactic for development.
```singularity
Bootstrap: docker  # Use Docker as the base image
From: python:3.12.9-slim-bookworm  # Use a minimal Debian based Python image, because we are using mainly Python, and it is compatible with separete R installs.

%setup
    # We can leave this section empty for now.

%files
    # We can leave this section empty for now.

%environment
    # We can leave this section empty for now.

%post
    # Usually, we will almost certianly need these basic libraries / tool.
    apt-get update
    apt-get install -y \
    wget \
    curl \
    libcurl4-openssl-dev \
    software-properties-common
    # =================================

    # Add apt-fast repository to install apt-fast,
    # which will make the package installation faster and concurrent.
    /bin/bash -c "$(curl -sL https://git.io/vokNn)"
    # =================================

    apt-get update
    # Set non-interactive installation mode and timezone to avoid prompts
    DEBCONF_NOWARNINGS="yes" \
    TZ="Europe/Madrid" \
    DEBIAN_FRONTEND=noninteractive \

    # Install R packages
    # NOTE: Python is already installed in the base image.
    # NOTE: Pin down versions to improve reproducibility.
    apt-fast install -y \
        r-base=4.2.2.20221110-2 \
        r-base-dev=4.2.2.20221110-2
```

Build the "chunk" image
```sh
sudo singularity build ./1_my_dummy_pipeline.sif ./1_my_dummy_pipeline.def
```

### 3. Look for libraries by languages

Now we will try to look for the Python and R libraries that we need to install.

```bash
# Look for all Python imports.
grep -rinP "^from .* import .*|^import .*" ./my_dummy_pipeline/ --include=*.py
```

**OUTPUT:**
```sh
(venv) danielmajer@danielmajer-Latitude-7420:~/workspace/singularity-technical-seminar$
grep -rinP "^from .* import .*|^import .*" ./my_dummy_pipeline/ --include=*.py
./my_dummy_pipeline/tests/test_main.py:3:import os
./my_dummy_pipeline/tests/test_main.py:4:import shutil
./my_dummy_pipeline/tests/test_main.py:5:from uuid import UUID, uuid4
./my_dummy_pipeline/tests/test_main.py:6:from pathlib import Path
./my_dummy_pipeline/tests/test_main.py:7:from main import prepare_blastdb
./my_dummy_pipeline/main.py:2:from __future__ import annotations
./my_dummy_pipeline/main.py:4:import os
./my_dummy_pipeline/main.py:5:import shutil
./my_dummy_pipeline/main.py:6:from argparse import ArgumentParser
./my_dummy_pipeline/main.py:7:from dataclasses import dataclass
./my_dummy_pipeline/main.py:8:from pathlib import Path
./my_dummy_pipeline/main.py:9:from subprocess import getstatusoutput
./my_dummy_pipeline/main.py:10:from uuid import UUID, uuid4
./my_dummy_pipeline/main.py:12:import numpy as np # <- BINGO
./my_dummy_pipeline/main.py:13:import pandas as pd # <- BINGO
```

```bash
# Look for all R imports.
grep -rinP "^library\(.*\)|^require\(.*\)" ./my_dummy_pipeline/ --include=*.{R,Rscript}
```

**OUTPUT:**
```sh
(venv) danielmajer@danielmajer-Latitude-7420:~/workspace/singularity-technical-seminar$
grep -rinP "^library\(.*\)|^require\(.*\)" ./my_dummy_pipeline/ --include=*.{R,Rscript}
./my_dummy_pipeline/create_result_plot.R:1:library(ggplot2) # <- BINGO
```


### 4. Create the second "chunk file" in the image build.

`2_my_dummy_pipeline.def` <- Note, that we are enumerating the files. It is because of the ["incremental build"](#development-with-incremental-build-build-in-chunks) tactic for development.

```singularity
Bootstrap: docker  # Use Docker as the base image
From: 1_my_dummy_pipeline.sif # We use the previous chunk as the continuation.

%post
    # Install ggplot2 via the already available and compiled APT repository.
    apt-fast install -y \
        r-cran-ggplot2=3.4.1+dfsg-1

    # Install the Python packages through the official Python PyPI repository
    pip install pandas numpy
```

Build the "chunk" image
```sh
sudo singularity build ./2_my_dummy_pipeline.sif ./2_my_dummy_pipeline.def
```

---

### 5. Install rest of the dependencies through runtime error

Now that we consider having all the libraries and runtimes installed, we need to finish up the first iteration of the definition file and try to run our pipeline.
Probably some more error will occur, because there are external dependencies, like binaries and other tools, that are called through child processes and are still missing.
So the best way to find out, to follow the "edit-compile-debug cycle".

`3_my_dummy_pipeline.def`
```singularity
Bootstrap: localimage  # Use a locally compiled image as the base image
From: 2_my_dummy_pipeline.sif # We use the previous chunk as the continuation.

%files
    ./* /my_dummy_pipeline/
```

Build the "chunk" image
```sh
sudo singularity build ./3_my_dummy_pipeline.sif ./3_my_dummy_pipeline.def
```

Try to run the pipeline
```sh
# Note that we are referencing the pipeline's path INSIDE the Singularity image, but the argument file paths are relative and FROM THE HOST machine's filesystem!
singularity run --cleanenv ./3_my_dummy_pipeline.sif python3 /my_dummy_pipeline/main.py \
                --reference-fasta-gz "./_test_data/input_data/reference_proteomes/7165.fasta.gz" \
                --blast-db-output-dir "./_test_data/output_data/blast_db_7165/" \
                --target-fasta-path "./_test_data/input_data/target_proteomes/0.7165.reduced.faa" \
                --blast-result-tsv-path "./_test_data/output_data/blast_result_0.7165.reduced.tsv" \
                --plot-output  "./_test_data/output_data/0.7165.res.png"
```

**OUTPUT:**
```sh
(venv) danielmajer@danielmajer-Latitude-7420:~/workspace/singularity-technical-seminar/my_dummy_pipeline$
singularity run --cleanenv ./3_my_dummy_pipeline.sif python3 /my_dummy_pipeline/main.py                 --reference-fasta-gz "./_test_data/input_data/reference_proteomes/7165.fasta.gz"                 --blast-db-output-dir "./_te
st_data/output_data/blast_db_7165/"                 --target-fasta-path "./_test_data/input_data/target_proteomes/0.7165.reduced.faa"                 --blast-result-tsv-path "./_test_data/output_data/blast_result_0.7165.reduced.t
sv"                 --plot-output  "./_test_data/output_data/0.7165.res.png"
Traceback (most recent call last):
  File "/my_dummy_pipeline/main.py", line 148, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/my_dummy_pipeline/main.py", line 120, in main
    blast_db = prepare_blastdb(
               ^^^^^^^^^^^^^^^^
  File "/my_dummy_pipeline/main.py", line 91, in prepare_blastdb
    _exec_shell(makeblastdb_cmd)
  File "/my_dummy_pipeline/main.py", line 63, in _exec_shell
    raise ChildProcessError(f"[ERROR] Failed cmd: [{cmd}]!\n" f"OUTPUT:\n{output}")
ChildProcessError: [ERROR] Failed cmd: [makeblastdb -in _test_data/output_data/blast_db_7165/7165.fasta -dbtype 'prot' -title b61b56c3-fb3c-4aba-980a-bf3939e70188]!
OUTPUT:
/bin/sh: 1: makeblastdb: not found
```

Okay, so we can see that the pipeline fails, because we are missing the `makeblastdb` tool. We can assume that the entire Blast+ is missing the image. So let's install it.
[How to install Blast+](https://blast.ncbi.nlm.nih.gov/doc/blast-help/downloadblastdata.html)

Let's start the 4th "chunk" definition file and add the missing Blast+ dependency.

`4_my_dummy_pipeline.def`
```singularity
Bootstrap: localimage  # Use a locally compiled image as the base image
From: 3_my_dummy_pipeline.sif # We use the previous chunk as the continuation.

%post
    wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.16.0+-x64-linux.tar.gz
    tar -zxvf ncbi-blast-2.16.0+-x64-linux.tar.gz
    cp -r ncbi-blast-2.16.0+/bin/* /bin/
```

Build the "chunk" image
```sh
sudo singularity build ./4_my_dummy_pipeline.sif ./4_my_dummy_pipeline.def
```

Try to run the pipeline after we have installed the Blast+ dependency.
```sh
# Note that we are referencing the pipeline's path INSIDE the Singularity image, but the argument file paths are relative and FROM THE HOST machine's filesystem!
singularity run --cleanenv ./4_my_dummy_pipeline.sif python3 /my_dummy_pipeline/main.py \
                --reference-fasta-gz "./_test_data/input_data/reference_proteomes/7165.fasta.gz" \
                --blast-db-output-dir "./_test_data/output_data/blast_db_7165/" \
                --target-fasta-path "./_test_data/input_data/target_proteomes/0.7165.reduced.faa" \
                --blast-result-tsv-path "./_test_data/output_data/blast_result_0.7165.reduced.tsv" \
                --plot-output  "./_test_data/output_data/0.7165.res.png"
```

**OUTPUT:**
```sh
```

---

### 6. Join the chunk files into your final definition file

So, our pipeline works as expected, then we can join our "chunk" .def files into one. All we have to do is `following the orders of the files` we need to join the `sections` (%files, %post, etc..)

`my_dummy_pipeline.def`
```singularity
Bootstrap: docker  # Use Docker as the base image
From: python:3.12.9-slim-bookworm  # Use a minimal Debian based Python image, because we are using mainly Python, and it is compatible with separete R installs.

%files
    ./* /my_dummy_pipeline/

%post
    # Usually, we will almost certianly need these basic libraries / tool.
    apt-get update
    apt-get install -y \
    wget \
    curl \
    libcurl4-openssl-dev \
    software-properties-common
    # =================================

    # Add apt-fast repository to install apt-fast,
    # which will make the package installation faster and concurrent.
    /bin/bash -c "$(curl -sL https://git.io/vokNn)"
    # =================================

    apt-get update
    # Set non-interactive installation mode and timezone to avoid prompts
    DEBCONF_NOWARNINGS="yes" \
    TZ="Europe/Madrid" \
    DEBIAN_FRONTEND=noninteractive \

    # Install R packages
    # NOTE: Python is already installed in the base image.
    # NOTE: Pin down versions to improve reproducibility.
    # Install ggplot2 via the already available and compiled APT repository.
    apt-fast install -y \
        r-base=4.2.2.20221110-2 \
        r-base-dev=4.2.2.20221110-2 \
        r-cran-ggplot2=3.4.1+dfsg-1

    # Install the Python packages through the official Python PyPI repository
    pip install pandas numpy

    wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.16.0+-x64-linux.tar.gz
    tar -zxvf ncbi-blast-2.16.0+-x64-linux.tar.gz
    cp -r ncbi-blast-2.16.0+/bin/* /bin/

%test
    python3 /my_dummy_pipeline/main.py --help
```

**Build the base image:**

```sh
sudo singularity my_dummy_pipeline.sif my_dummy_pipeline.def
```

---

# Debugging with Singularity images

Debugging can be tricky, because it would require a fast iteration cycle between "write-compile-run" and with the build time of the singularity images it is quiet cumbersome.
Exactly that is why we have written our container in the example above in such way, so the runtime is separated from the scripts.

After placing our print statements inside the files, what we can do is instead of running the copied script files from inside the container, we will run the ones which are in our host machine.

**EXAMPLE:**

> [!NOTE]
> We are calling the "./main.py" from our HOST machine, and not the /my_dummy_pipeline/main.py
```sh
singularity run --cleanenv ./my_dummy_pipeline.sif python3 ./main.py \
                --reference-fasta-gz "./_test_data/input_data/reference_proteomes/7165.fasta.gz" \
                --blast-db-output-dir "./_test_data/output_data/blast_db_7165/" \
                --target-fasta-path "./_test_data/input_data/target_proteomes/0.7165.reduced.faa" \
                --blast-result-tsv-path "./_test_data/output_data/blast_result_0.7165.reduced.tsv" \
                --plot-output  "./_test_data/output_data/0.7165.res.png"
```
**OR!**

> [!NOTE]
> We are binding the current working directory (./my_dummy_pipeline) with the container's one located at the root of the internal filesystem, then calling the "/my_dummy_pipeline/main.py" from the CONTAINER as usual.
```sh
singularity run --cleanenv --bind .:/my_dummy_pipeline ./my_dummy_pipeline.sif python3 /my_dummy_pipeline/main.py \
                --reference-fasta-gz "./_test_data/input_data/reference_proteomes/7165.fasta.gz" \
                --blast-db-output-dir "./_test_data/output_data/blast_db_7165/" \
                --target-fasta-path "./_test_data/input_data/target_proteomes/0.7165.reduced.faa" \
                --blast-result-tsv-path "./_test_data/output_data/blast_result_0.7165.reduced.tsv" \
                --plot-output  "./_test_data/output_data/0.7165.res.png"
```

Using dedicated debuggers is always a good idea, because it let us step through the execution with more insight.
Unfortunately, IDEs like Vscode, haven't got good integration in terms of debuggers with Singularity, not like with Docker, so we have to use the built-in REPL debuggers of the languages.

**EXAMPLE:**
Python allows you to utilize pdb (Python Debugger) for interactive debugging sessions.

To set a breakpoint in a Python script, use the **breakpoint()** function:

```bash
x = 10
y = 'Hi'
z = 'Hello'
print(y)

breakpoint()

print(z)
```

For further information about pdb refer to the [official Python 3 documentation](https://docs.python.org/3/library/pdb.html).

---

# EXAMPLES - Projects already converted to Singularity
In this repository you can find 2 linked submodules if you are interested in how they are structured to run with Singularity:

- [metaline](https://github.com/Gabaldonlab/meTAline)
- [phylomizer-2024](https://github.com/gabaldonlab/phylomizer-2024)

---
