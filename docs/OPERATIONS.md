# Executable operation catalogue

Every operation requires supplied assumptions/provenance. No market or issuer data are inferred.

## `cashflow_bridge`
```python
cashflow_bridge(revenue: 'float', volume_change: 'float', price_change: 'float', contribution_margin: 'float', incremental_opex: 'float', incremental_capex: 'float', incremental_working_capital: 'float', tax_rate: 'float') -> 'dict'
```
One-period sensitivity. Positive cost/capex/WC changes consume cash; tax shield is assumed usable.

Input units: `{"revenue": "$money", "volume_change": "decimal", "price_change": "decimal", "contribution_margin": "decimal", "incremental_opex": "$money", "incremental_capex": "$money", "incremental_working_capital": "$money", "tax_rate": "decimal"}`. Output unit/type: `cashflow_bridge`.

## `dscr`
```python
dscr(cash_available: 'float', debt_service: 'float') -> 'float'
```
See source code and domain methodology for assumptions.

Input units: `{"cash_available": "$money", "debt_service": "$money"}`. Output unit/type: `multiple`.

## `equity_bridge`
```python
equity_bridge(enterprise_value: 'float', cash: 'float', debt: 'float', minority_claims: 'float', shares: 'float') -> 'dict'
```
See source code and domain methodology for assumptions.

Input units: `{"enterprise_value": "$money", "cash": "$money", "debt": "$money", "minority_claims": "$money", "shares": "shares"}`. Output unit/type: `equity_value_bridge`.

## `holding_period_return`
```python
holding_period_return(initial_dirty_price: 'float', exit_dirty_price: 'float', cash_income: 'float', funding_cost: 'float', transaction_cost: 'float') -> 'float'
```
See source code and domain methodology for assumptions.

Input units: `{"initial_dirty_price": "$money", "exit_dirty_price": "$money", "cash_income": "$money", "funding_cost": "$money", "transaction_cost": "$money"}`. Output unit/type: `decimal_return`.

## `incremental_dcf`
```python
incremental_dcf(annual_delta_cashflows: 'list[float]', discount_rate: 'float', terminal_growth: 'float', include_terminal: 'bool') -> 'dict'
```
Year-1 onward deltas. Terminal perpetuity uses last delta*(1+g), only when explicitly requested.

Input units: `{"annual_delta_cashflows": "$money", "discount_rate": "decimal", "terminal_growth": "decimal", "include_terminal": "boolean"}`. Output unit/type: `incremental_valuation`.

## `npv`
```python
npv(cashflows: 'list[float]', annual_discount: 'float') -> 'float'
```
Periodic NPV; cashflows[0] is at time zero, then annual periods.

Input units: `{"cashflows": "$money", "annual_discount": "decimal"}`. Output unit/type: `$money`.

## `scale`
```python
scale(value: 'float', factor: 'float') -> 'float'
```
Explicit arithmetic conversion; external unit semantics need human review.

Input units: `{"value": "$input_unit", "factor": "conversion_factor"}`. Output unit/type: `$output_unit`.

## `scenario_expected_value`
```python
scenario_expected_value(scenario_values: 'list[float]', probabilities: 'list[float]') -> 'float'
```
See source code and domain methodology for assumptions.

Input units: `{"scenario_values": "$money", "probabilities": "decimal"}`. Output unit/type: `$money`.
