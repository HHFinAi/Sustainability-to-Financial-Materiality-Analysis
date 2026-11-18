# Climate resilience — from potential need to cash and entry-price hurdle

**Research package, 18 Nov 2026. Three original hypothetical exercises; all valuations NEEDS_DATA.**

This adds the **funding → awarded share → delivery conversion → incremental revenue → FCF → reverse price hurdle** bridge to existing HHFinAI financial-materiality work. It complements the separate climate-agent's supplier/operator/insurer model rather than replacing its evidence workflow.

Run from repository root:
```bash
python examples/climate-resilience/model.py --check
python -m unittest discover -s tests -p 'test_climate_resilience.py' -v
```

## Three comparison studies

| Sector study | Candidates | Why the difference between need and paid orders matters |
| --- | --- | --- |
| Cooling / HVAC | TT, JCI, CARR | Heat and cooling requirements ≠ funded retrofits; service mix, contractor capacity, electricity bills and order conversion matter. |
| Grid hardening | GEV, HUBB, FLNC | Utilities need regulator-approved budgets and contracts; AI load, grid modernization and climate resilience overlap and must not be summed. |
| Flood-defense cement | HEI.DE | Tender awards, capacity, geography and delivered concrete pricing determine incremental demand. Keep separate from existing Brevik CCS **mitigation** case. |

The inputs are **synthetic** and represent no expected current orders, market consensus, revenues or entry prices. The contribution/DCF arithmetic is an **illustrative cash-flow proxy**, with constant annual flows, no terminal value and simplified tax treatment. A synthetic hypothetical premium is used to calculate **reverse required annual FCF**, not a market-implied price observed from any exchange.

## Required primary evidence and falsifiers

1. Geographic hazard and buyer payer: exact facility or utility service geography, valid published weather/hazard data and adaptation need.
2. Bankability: approved budget, finance source, award date, procurement ability, contract cancellation rights and distribution through the value chain.
3. Issuer: segment revenue and backlog, order timing, contribution earnings, cash taxes, working capital, capex, debt/dilution and cross-region exposure.
4. Market: timestamped executable price, enterprise-to-equity bridge, consensus embedded growth and reverse valuation.
5. Challenge: backlog growth without cash conversion; grid project delays or competition; cement freight/market-share restrictions. **Stop at NEEDS_DATA** if a material field is missing.

For near-term prospective discipline, see [EL_NINO_MONITOR.md](EL_NINO_MONITOR.md); no local weather impact or company EPS forecast is inferred from NOAA ENSO strength.


## Q3 2026 primary-source observation monitor

See [OBSERVATIONS.md](OBSERVATIONS.md) and run `python examples/climate-resilience/monitor.py` for descriptive TT/GEV/Heidelberg operating indicators from current issuer disclosures. Accounting scopes differ; there is no verified climate-driven revenue or security valuation.
