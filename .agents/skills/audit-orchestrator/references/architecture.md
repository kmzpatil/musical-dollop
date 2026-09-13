# Architecture Rationale

## Distributed Skills Model
The audit pipeline uses a decentralized "skills" architecture. Instead of a monolithic codebase, each heuristic domain (discoverability, engagement, answerability) runs as a standalone, stateless script. 

## Fault Tolerance
The orchestrator aggregates outputs via a best-effort merge. If a skill crashes or times out, the orchestrator proceeds with whatever valid JSON it successfully ingested, ensuring the end-user still receives a partial report rather than a catastrophic pipeline failure.
