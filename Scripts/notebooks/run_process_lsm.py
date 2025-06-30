#!/usr/bin/env python

import sys
from process_lsm_output import process_lsm_output

if __name__ == "__main__":
    lsm_name = sys.argv[1]  # e.g., LSM_IMD1
    process_lsm_output(lsm_name)

