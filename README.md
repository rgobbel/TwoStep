# Two-step Task

This program runs a two-step decision task, as described in Daw et al., as well as the simplified version described in xxxx.

Results are output to a CSV file.

```
usage: two-step-simulation.py [-h] [--n-trials N_TRIALS] [--generator {brownian,blocked}]
                              [--step1-timeout STEP1_TIMEOUT]
                              [--step2-timeout STEP2_TIMEOUT] [--output OUTPUT] [--quiet]

optional arguments:
  -h, --help            show this help message and exit
  --n-trials N_TRIALS   Number of trials to run
  --generator {brownian,blocked}
                        Generator type for step 2 reward probabilities
  --step1-timeout STEP1_TIMEOUT
                        Timeout for step 1
  --step2-timeout STEP2_TIMEOUT
                        Timeout for step 2
  --output OUTPUT       Name of output CSV file
  --quiet               Do not print history or running totals

```