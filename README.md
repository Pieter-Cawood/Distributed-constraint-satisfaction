# Distributed-constraint-satisfaction
Multi-Agent algorithms used to solve distributed constraint problems.

## Asyncronous-backtracking-algorithm
Uses hyper-resolution and asyncronous backtracking to send Nogood constraints to agents based on priority order.
Example solves a 4 queen problem syncronously as agents' messaging is simulated by agent-to-agent function invocation.

![N-Queen problem](https://i.ibb.co/F4pC27D/N-queen.png)

## Doman filtering algorithm
Uses Arc-consistency to reduce agent domains into smaller ones.

![Arc-cosistency](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Backtracking-arc-consistency.svg/200px-Backtracking-arc-consistency.svg.png)
