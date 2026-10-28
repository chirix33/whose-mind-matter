# Baseline fidelity

No baseline is implemented yet. For every baseline, this file will record:
- the source paper, code repository, commit and license;
- the adaptation to OfficeMinds action selection;
- known differences from the original;
- compute knobs and the tuning budget used on Val.

Style-based adaptations are labeled as such. OfficeMinds dense modeling (A3) will be described as "MWM-style dense allocation", **never** as a verbatim Mentis reproduction.

| ID | Source to pin | Fidelity class (planned) | Notes |
|---|---|---|---|
| A3 | MWM / Mentis (github.com/mental-world/Mentis) | style-based adaptation | use Mentis's variable set where it maps to Knowledge/Reliability |
| B1 | A-ToM (arXiv 2603.16264) | approximate reimplementation | Hedge over ToM-0/1/2 |
| C1 | SimToM | approximate | target from the task text |
| C2 | RecToM (arXiv 2606.11724) | approximate | |
| D1 | AutoToM objective | same architecture, different target | AutoToM's objective is uncertainty about the **query's target variable** minus model complexity, not uncertainty over every mind. Our D1 must define the queried target per step |
| D2 | AutoToM code (github.com/SCAI-JHU/AutoToM) | released code + action-selection adapter | pin the commit and license before use |
| D5 | prompted router incl. Zing-style variable gate | prompted | count all prompt tokens |
