# Conventional references

This benchmark is intentionally built on established concurrency-control ideas.

- **SQLite isolation:** separate connections see committed transactions, and SQLite serializes writers. `BEGIN IMMEDIATE` starts the write transaction before later statements.  
  https://www.sqlite.org/isolation.html

- **Google Cloud Spanner concurrency control:** optimistic transactions validate relevant reads at commit; conflicting concurrent changes cause abort rather than committing against stale observations.  
  https://docs.cloud.google.com/spanner/docs/concurrency-control

- **Amazon DynamoDB TransactWriteItems:** condition checks and multiple writes can be grouped into an all-or-nothing transaction; a failed condition cancels the transaction.  
  https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_TransactWriteItems.html

Lycheetah does not claim these primitives as inventions. This artifact uses them to make a narrow race condition reproducible for agent-compensation engineering.
