# Root Cause Classifier Agent

File:

`backend/app/core/classifier.py`

## Input

- `event_type`
- `failure_code`
- `failure_description`

## Output

The classifier returns:

- `root_cause`
- `reason_detail`
- `risk_score`
- `suggested_action`

## Current detection paths

```text
payment.failed
    ├── timeout
    ├── insufficient funds
    └── generic decline

subscription.halted
    └── recurring mandate declined

checkout.abandoned
    └── cart abandonment

invoice.overdue
    └── overdue receivable

unknown
    └── generic fallback
```

This version intentionally uses deterministic rules first. The same
function interface can later be backed by an LLM without changing the
Risk → Root Cause → Intervention pipeline.
