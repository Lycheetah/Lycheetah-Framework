# Lycheetah External Threat Boundary Auditor v1.4

**Status:** `SYNTHETIC_ENGINEERING_VALIDATED`  
**Deployment:** none

## Why this direction

v1.3 showed that a self-authored test suite can be green while declared safety
mutants survive.

v1.4 therefore imports challenge families from outside the Lycheetah lineage.

The source lens includes:
- OWASP Top 10 for Agentic Applications 2026;
- OWASP MCP Security guidance;
- OWASP memory/context-poisoning guidance;
- AgentDojo;
- AgentDyn;
- Microsoft FIDES as a concrete defensive architecture.

The source ideas are prior art. The artifact is a transmutation/crosswalk into a
portable agent-boundary manifest.

## Concrete use case

A coding agent can:
- read repository/issues/web/tool output;
- invoke shell/MCP-style tools;
- use credentials;
- persist memory;
- request approval;
- trigger deployment-like effects.

The auditor asks whether the declared control boundary covers each externally
sourced challenge family.

## Important meaning of FULL

`FULL` means only:

> every control primitive declared as required by that challenge packet appears
> in the manifest.

It does NOT mean:
- the implementation works;
- the attack is empirically blocked;
- the control mapping is complete;
- the external source endorses this mapping.

## Why this is useful today

Run:

```bash
python3 boundary_auditor.py examples/current_lycheetah_coding_agent.json
```

Then replace the example manifest with a real agent architecture's enabled
controls.

The output names missing primitives per threat family and gives the union of
controls needed to reach full *declared* coverage.

This turns an abstract security review into an explicit engineering backlog.

## External challenge packets

The packet currently includes:
1. indirect prompt injection / goal hijack;
2. MCP tool poisoning;
3. MCP rug pull / tool-definition mutation;
4. confused deputy / over-scoped credentials;
5. exfiltration through legitimate tool arguments;
6. persistent memory/context poisoning;
7. unexpected code execution / hostile local tool;
8. insecure inter-agent communication / spoof/replay;
9. cascading failure / retry amplification;
10. human-agent trust exploitation;
11. identity and privilege abuse;
12. rogue/strategically deceptive agent behavior.

## Next move

The auditor identifies several primitives that should not remain paper-only:
- memory lifecycle mediation;
- MCP/tool-definition attestation;
- real execution sandboxing;
- authenticated inter-agent messages;
- trusted human confirmation surfaces;
- systemic blast-radius/circuit-breaker controls.

The highest-value next implementation should be chosen from the largest
externally grounded gap, not from internal aesthetic preference.
