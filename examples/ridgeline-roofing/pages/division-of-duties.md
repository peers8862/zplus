# Division of duties

How a typical back-office task routes across people, AI agents, and machines. The goal:
anyone can see at a glance what's **handled**, **supervised**, or still **manual**.

```mermaid
flowchart TD
    T[Incoming task] --> D{Routine & well-defined?}
    D -->|Yes| A[AI agent drafts / handles]
    D -->|No| H[Human handles]
    A --> R{Confidence high & within policy?}
    R -->|Yes| M[Automation runs it]
    R -->|No| S[Human supervises / approves]
    H --> L[Log outcome; look for automation]
    M --> L
    S --> L
```

**Examples at Ridgeline**

| Task | Human | AI agent | Machine |
|---|---|---|---|
| Invoice import | Office Manager approves | Invoice Triage Bot | Invoice Import automation |
| Lead intake | Estimator reviews | Lead Concierge | Lead Intake Router |
| Review requests | — (autonomous) | Reputation Agent | Review Request Sender |
| Payroll | Bookkeeper approves | — | Payroll Run |
