# Two-step Task

This program runs a two-step decision task, as described in (Daw et al., 2011), as well as the simplified version described in (Akam et al., 2015).

## How to run it:

By default, the program runs with the parameters described in (Daw et al., 2011). It first puts up a small window with a gray background. After a delay of a few seconds, two Tibetan characters are displayed, in small cards with a teal-colored background. Once these symbols are displayed, the user has 2 seconds to choose either the left or the right symbol, using the arrow keys on the keyboard. When one symbol is chosen, its card floats to the top of the window, as other symbol fades out. A second pair of Tibetan characters are then displayed, with either a blue or a pink background, and again the user has 2 seconds to make a choice. Based on which symbol is chosen, the user then receives a reward, or not. As described in the paper, choosing a symbol on the first step _probabilistically_ leads to one or the other of the pink-backed or blue-backed pairs of second-step symbols. The probability of moving to one or the other step-2 state is not revealed to the user, but it remains the same througout the run. Each of the four step-2 symbols has a probability of leading to a reward, independent of the other three, and slowly and randomly varying between 0.25 and 0.75 throughout the run.

Stimuli, responses, reward probabilities and rewards are recorded, and the results are output to a CSV file at the end of a run for analysis.

Choosing "blocked" at the start of a run changes the probability of transitioning to a particular step-2 state, and simplifies the reward probabilities for step 2, so that either symbol in a particular step-2 pair (i.e., either pink or blue) has the same probability of leading to a reward, and these probabilities remain fixed until the end of a block, at which time likely and unlikely rewards are swapped. This reproduces the setup described in (Akam et al., 2015).

Read the papers for details. This program has no purpose other than to help me understand the experience of being a subject in one of these experiments.

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
