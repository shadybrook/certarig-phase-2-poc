# Phase 2 validation record

Validation date: 25 August 2026

Validation command:

    npm run check

## Result

| Validation area | Result |
|---|---|
| Browser engine tests | 6 passed, 0 failed |
| Supplementary reference software tests | 8 passed, 0 failed |
| Static website build | Completed |
| Synthetic evidence generation | 4 bundles generated |
| Total automated tests | 14 passed, 0 failed |

The API workflow test used an ephemeral localhost port and verified authentication, plan validation, approval, mock execution, and evidence retrieval.

The static build produced index.html, styles.css, and the browser modules in the ignored dist directory. Evidence generation produced the four checked in JSON case files and manifest under evidence/phase2.

## Claim boundary

These results validate the software and synthetic data path on the development computer. They do not validate physical sensors, GPIO wiring, an ADC, an output driver, a valve, a pressure boundary, an emergency stop, or independent electrical protection.

The same command is used by the repository validation workflow so the local result can be reproduced on a GitHub hosted runner when repository Actions are available.
