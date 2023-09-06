# Two-step Task

This program runs a two-step decision task, as described in (Daw et al., 2011), as well as the simplified version described in (Akam et al., 2015).

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

Daw, N. D., Gershman, S. J., Seymour, B., Dayan, P., & Dolan, R. J. (2011). Model-based influences on humans’ choices and striatal prediction errors. Neuron, 69(6), 1204–1215. https://doi.org/10.1016/j.neuron.2011.02.027

Akam, T., Costa, R., & Dayan, P. (2015). Simple plans or sophisticated habits? State, transition and learning interactions in the two-step task. PLOS Computational Biology, 11(12), e1004648. https://doi.org/10.1371/journal.pcbi.1004648
