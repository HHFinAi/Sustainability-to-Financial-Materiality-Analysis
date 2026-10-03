# Cooling investment: reproducible sensitivities

**Illustrative project arithmetic, not a Microsoft site forecast or share-price valuation.**
All monetary values below are USD million unless stated otherwise.

Annual IT electricity: 613,200 MWh. Additional electricity: 12,264 MWh.
Assumed avoided direct cooling water: 183,960 m3/year.
Water bill saving: 0.551880; additional electricity cost: 0.981120 per year.

| Scenario | Annual incremental FCF | NPV | Break-even additional pre-tax benefit/year |
|---|---:|---:|---:|
| Reference: direct bills only | -0.1344 | -15.9020 | 3.1598 |
| Additional benefit $3m/year | 2.1156 | -0.8044 | 3.1598 |
| Electricity $120/MWh | -0.5023 | -18.3708 | 3.6504 |
| Water $5/m3 | 0.1415 | -14.0505 | 2.7919 |
| Incremental PUE 0.04 | -0.8703 | -20.8396 | 4.1409 |
| Capex +25%; commissioning +1 year | -0.0407 | -19.0027 | 4.0780 |
| No tax relief | -0.6792 | -19.5578 | 2.9147 |

Each row changes only the stated reference inputs. The hurdle is the total recurring additional pre-tax operating benefit needed for zero NPV, not an extra amount on top of any assumed benefit.
Tax relief assumes immediately usable deductions; the no-tax row removes both tax charges and shields. Commissioning delay postpones operating flows and depreciation, but not initial capex. No delay holding costs are modeled.

[Investment memo](README.md) · [Inputs and assumptions](inputs.json) · [Calculation](model.py)
