# Shark - Experiments
This repository contains the instructions to reproduce the experiments performed in the shark paper:
* [paramtest](#paramtest): experiments to test shark parameters (simulated data)
* [panelsize](#panelsize): experiments with different sized gene panels (simulated data)
* [genel_samples](#genel_samples): experiments with different sample sizes and clustering the gene by length (simulated data)
* [asquant](#asquant): experiments on alternative splicing events quantification (real data)

### Setup

To facilitate the replicability of our experiments, we provide a conda environment (`environment.yml`). To activate it, clone the repo, move to it, and run:
```bash
git clone https://github.com/AlgoLab/shark_experiments.git
cd shark_experiments
conda env create -f environment.yml
```
This environment contains all the needed softwares and libraries except for the [spladder](https://github.com/ratschlab/spladder) tool (it's not available on conda). To install it:
```bash
git clone https://github.com/ratschlab/spladder.git
cd spladder
git checkout 324d45c # This is the version we used
make install
# add spladder bin to you $PATH variable
```
**Note:** adding spladder to your `$PATH` is really important. If you don't do that, the asquant experiments will fail.

### paramtest
Download the archive from [...], unzip it and set the root in the `paramtest/config.yaml` using the path to the extracted folder (should be something like `/.../paramtest/`). Run `snakemake -n` and you should see something like:
```
Job counts:
        count   jobs
        1200    check_shark
        10      combine_results
        1       comp_average
        10      index_gtf
        1       run
        1200    shark
        2422
```

Then run `snakemake -j {threads}` to produce:
* `{root_fold}/output/average_results.csv`

### panelsize
Download the archive from [...], unzip it and set the root in the `panelsize/config.yaml` using the path to the extracted folder (should be something like `/.../panelsize/`). Run `snakemake -n` and you should see something like:
```
Job counts:
        count   jobs
        14      check_shark
        2       combine_results
        7       index_gtf
        1       run
        14      shark
        38
```

Then run `snakemake -j {threads}` to produce:
* `{root_fold}/output/single.csv`
* `{root_fold}/output/multi.csv`

### genel_samples
Download the archive from [...], unzip it and set the root in the `genel_samples/config.yaml` using the path to the extracted folder (should be something like `/.../genel_samples/`). Run `snakemake -n` and you should see something like:
```
Job counts:
        count   jobs
        360     check_shark
        1       combine_results
        40      index_gtf
        1       run
        360     shark
        9       split_sample
        771
```

Then run `snakemake -j {threads}` to produce:
* `{root_fold}/output/results.csv`

### asquant
Download the archive from [...], unzip it and set the root in the `asquant/config.yaml` using the path to the extracted folder (should be something like `/.../asquant/`). Run `snakemake -n` and you should see something like:
```
Job counts:
        count   jobs
        1       create_rtpcr_annotation
        1       extract_rtpcr_seqs
        1       fix_transcripts_for_suppa
        6       gzip_shark_fq_1
        6       gzip_shark_fq_2
        4       prepare_rmats_ctrlbam_list
        4       prepare_rmats_kdbam_list
        4       prepare_sharked_rmats_ctrlbam_list
        4       prepare_sharked_rmats_kdbam_list
        4       prepare_sharked_spladder_bam_list
        4       prepare_sharked_spladder_ctrlbam_list
        4       prepare_sharked_spladder_kdbam_list
        4       prepare_spladder_bam_list
        4       prepare_spladder_ctrlbam_list
        4       prepare_spladder_kdbam_list
        4       rmats
        1       run
        1       salmon_index
        6       salmon_quant
        6       shark
        4       sharked_rmats
        6       sharked_salmon_quant
        4       sharked_spladder_difftest_step1
        4       sharked_spladder_difftest_step2
        24      sharked_star_align
        1       sharked_suppa_compute_tmp
        1       sharked_suppa_dpsi
        1       sharked_suppa_generate_events
        1       sharked_suppa_psiperevent
        1       sharked_suppa_split_psi
        1       sharked_suppa_split_tpm
        4       spladder_difftest_step1
        4       spladder_difftest_step2
        82      split_gtf
        24      star_align
        4       star_index
        1       suppa_compute_tmp
        1       suppa_dpsi
        1       suppa_generate_events
        1       suppa_psiperevent
        1       suppa_split_psi
        1       suppa_split_tpm
        245
```

Then run `snakemake -j {threads}` to produce:
* `{root_fold}/output/resources.txt`
* `{root_fold}/output/results.005.txt`
* `{root_fold}/output/results.100.txt`

### uniqness analysis

Either load the environment from the binder folder and execute the notebook under the uniqness_analysis directory or click on the following link to run the notebook on mybinder.org [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/AlgoLab/shark_experiments/master)
