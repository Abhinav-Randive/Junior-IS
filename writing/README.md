# Architecture Tradeoffs in Low-Latency Algorithmic Trading

Written thesis sources (`main.tex`, `proposal.tex`, bibliography). Compile with `latexmk -pdf main.tex` from this folder.

## Feature Calendar

| **Feature** | **Due date** | **Notes**|
| --------- | ------------ | -- |
| [Market data ingestion and replay](https://github.com/Abhinav-Randive/Junior-IS/issues/1#issue-3929584763) | Week 1 | Loading historical data and replay events in timestamp order |
| [Event-driven processing loop with dispatcher](https://github.com/Abhinav-Randive/Junior-IS/issues/2#issue-3929588434) | Week 1 | Core infrastructure milestone |
| [Core limit order book implementation](https://github.com/Abhinav-Randive/Junior-IS/issues/3#issue-3929589777) | Week 2 | Maintain bid/ask structures |
| [Limit, market, and cancel order support ](https://github.com/Abhinav-Randive/Junior-IS/issues/4#issue-3929591905)| Week 2 | Basic execution functionality |
| [Execution simulator (partial fills, queue position)](https://github.com/Abhinav-Randive/Junior-IS/issues/5#issue-3929595713) | Week 3 | Realistic execution behavior |
| [Market microstructure feature extraction](https://github.com/Abhinav-Randive/Junior-IS/issues/6#issue-3929598515) | Week 4 | Spread, depth, imbalance metrics |
| [Baseline predictive model](https://github.com/Abhinav-Randive/Junior-IS/issues/7#issue-3929599639) (logistic regression)| Week 5 | First prediction integration |
| [Strategy model using predictions](https://github.com/Abhinav-Randive/Junior-IS/issues/8#issue-3929601119) | Week 6 | Prediction-informed decisions |
| Latency instrumentation and logging | Week 7 | Measure component delays |
| Visualisation of latency distributions and execution metrics | Week 8 | Plotting for analysis |
| Prediction Accuracy vs Latency | Week 9 | Main Question |
| Final Documentation | Week 10 | Results (Hopefully!!!!) |


