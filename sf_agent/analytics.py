"""Bounded incremental financial sensitivities; no inferred ESG valuation premium."""
from __future__ import annotations
from .maths import COMMON_OPERATIONS, checked, fraction, number, operation, positive, require, series, npv

@operation({'revenue':'$money','volume_change':'decimal','price_change':'decimal','contribution_margin':'decimal','incremental_opex':'$money','incremental_capex':'$money','incremental_working_capital':'$money','tax_rate':'decimal'},'cashflow_bridge')
def cashflow_bridge(revenue: float, volume_change: float, price_change: float, contribution_margin: float,
                    incremental_opex: float, incremental_capex: float, incremental_working_capital: float,
                    tax_rate: float) -> dict:
    """One-period sensitivity. Positive cost/capex/WC changes consume cash; tax shield is assumed usable."""
    base=checked(revenue,'revenue',0)
    v=checked(volume_change,'volume_change',-1);p=checked(price_change,'price_change',-1)
    margin=fraction(contribution_margin,'contribution_margin');tax=fraction(tax_rate,'tax_rate')
    dr=base*((1+v)*(1+p)-1)
    de=dr*margin-number(incremental_opex,'incremental_opex')
    return {'revenue_change':dr,'ebit_change':de,'after_tax_operating_change':de*(1-tax),
            'free_cashflow_change':de*(1-tax)-number(incremental_capex,'incremental_capex')-number(incremental_working_capital,'incremental_working_capital')}

@operation({'annual_delta_cashflows':'$money','discount_rate':'decimal','terminal_growth':'decimal','include_terminal':'boolean'},'incremental_valuation')
def incremental_dcf(annual_delta_cashflows: list[float], discount_rate: float, terminal_growth: float,
                    include_terminal: bool) -> dict:
    """Year-1 onward deltas. Terminal perpetuity uses last delta*(1+g), only when explicitly requested."""
    cfs=series(annual_delta_cashflows,'annual_delta_cashflows');r=number(discount_rate,'discount_rate');g=number(terminal_growth,'terminal_growth')
    require(type(include_terminal) is bool,'include_terminal must be boolean');require(r>-1,'invalid discount rate')
    pv=npv([0]+cfs,r);tv=0.0
    if include_terminal:
        require(r>g and g>-1,'terminal growth must be below discount rate and above -100%')
        tv=cfs[-1]*(1+g)/(r-g)/(1+r)**len(cfs)
    return {'explicit_period_pv':pv,'terminal_pv':tv,'enterprise_value_delta':pv+tv}

@operation({'enterprise_value':'$money','cash':'$money','debt':'$money','minority_claims':'$money','shares':'shares'},'equity_value_bridge')
def equity_bridge(enterprise_value: float,cash: float,debt: float,minority_claims: float,shares: float) -> dict:
    residual=number(enterprise_value,'enterprise_value')+checked(cash,'cash',0)-checked(debt,'debt',0)-checked(minority_claims,'minority_claims',0)
    return {'equity_residual':residual,'per_share_residual':residual/positive(shares,'shares')}

@operation({'scenario_values':'$money','probabilities':'decimal'},'$money')
def scenario_expected_value(scenario_values: list[float], probabilities: list[float]) -> float:
    vals=series(scenario_values,'scenario_values');ps=[fraction(p,'probability') for p in series(probabilities,'probabilities')]
    require(len(vals)==len(ps),'scenario lengths differ');require(abs(sum(ps)-1)<1e-10,'probabilities must sum to one')
    return sum(v*p for v,p in zip(vals,ps))
OPERATIONS=dict(COMMON_OPERATIONS)
OPERATIONS.update({f.__name__:f for f in (cashflow_bridge,incremental_dcf,equity_bridge,scenario_expected_value)})
