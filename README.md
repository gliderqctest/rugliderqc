# rugliderqc
Test repository for real-time implementation

## Installation

`git clone https://github.com/rucool/rugliderqc.git`

`cd rugliderqc`

`conda env create -f environment.yml`

`conda activate rugliderqc`

**Requires replacing qartod.py in the ioos_qc package with ./ioos_qc_mods/qartod.py. Need to add this step**

## Steps

'python run_glider_qc.py glider-YYYYmmddTHHMM'

This wrapper script runs:

1. check_duplicate_timestamps.py
2. qartod_qc.py
3. ctd_hysteresis_test.py
4. <summarize_qc_flags - not written yet>
5. move_nc_files.py
