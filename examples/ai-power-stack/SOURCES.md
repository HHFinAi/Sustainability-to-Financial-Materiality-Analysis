# Model limitations and source register

- Original HHFinAi 16 October 2026 case: [AI infrastructure](../ai-infrastructure/README.md), with frozen [inputs](../ai-infrastructure/inputs.json) and [model](../ai-infrastructure/model.py). It is the source of **all** unchanged grid/gas parameters; every number remains an illustrative analyst assumption.
- Morgan Stanley, *Clean Tech & Data Center Infrastructure | SF Bus Tour Roundup*, dated 19 November 2026, pages 1–2: **research prompt only**, not a distributable dataset or a verified plant quotation. The report described management statements on BE demand, supply-chain expansion, CCS/CHP and Redwood's storage architecture.
- The SOFC route in this directory uses no imported bank-derived numeric assumptions. It is **not** the expected capacity, pricing, operating efficiency or economics of BE or any data center.
- The 100 MW IT workload, 70% utilization, PUE 1.15, 8% real rate, fixed USD, taxes and terminal conventions originate in the existing illustrative case. Do not extrapolate the results to an issuer's EV, ARR or share price.
- No 45Q tax credit, emissions abatement revenue, availability guarantee, grid-service revenue or site-specific price is booked. The inherited gas-engine convention allocates generation as campus-owned capex.
- The *rated capacity × assumed availability* threshold is a mechanical screening heuristic; probabilistic reliability requires a separate chronological operational model.
- Unsupported result: **NEEDS_DATA**. No human investment approval, source truth, market expectation, independent scientific validation or portfolio return is claimed.
