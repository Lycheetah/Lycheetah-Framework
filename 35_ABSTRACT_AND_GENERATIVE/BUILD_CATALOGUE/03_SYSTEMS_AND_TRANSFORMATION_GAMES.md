# Systems and transformation games

**Status: PROPOSED product and game briefs; no prototype implied.**

Lycheetah becomes interesting as a game when a principle changes what the player can do. These are fictional mechanics, including numerical laws chosen for play; they do not validate a theory about human beings.

[Catalogue home](README.md) · [Build contract](07_BUILD_CONTRACT_AND_SEQUENCE.md)

## LYC-B014 · Permission Heist

**Form:** game · **Build status:** PROPOSED

Solve a fictional infiltration by obtaining narrow permissions and noticing when they expire.

- **Source to inspect:** [papers/agent-safety/README.md](../../papers/agent-safety/README.md). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** A level seed, visible permission scopes, simulated guards and action tokens.
- **Interaction:** Scout → request or earn a scope → act within it → handle revocation → improvise through a different authorised route. Overbroad permission has a visible fictional cost.
- **Artifact:** A replay explaining each action and the authority that enabled it.
- **First build:** One vault, two routes, a revoked token and a clean escape; no real hacking targets.
- **Acceptance:** Revocation affects the intended game boundary; every action can be explained from game state; a player can win without using an overbroad token.
- **Limits:** This teaches a simplified fictional model, not real exploit techniques or certification of agent security.

## LYC-B015 · Clockwork Colony

**Form:** game · **Build status:** PROPOSED

Keep a little city alive by constructing feedback loops instead of babysitting every machine.

- **Source to inspect:** [34_CYBERNETICS/README.md](../../34_CYBERNETICS/README.md). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** A fictional plant state: heat, power, water, supplies and disturbances.
- **Interaction:** Build sensor → choose target → connect controller and actuator → disturb the colony → repair oscillation or bottlenecks → earn another subsystem.
- **Artifact:** A working colony layout and replayable disturbance seed.
- **First build:** One district with three interacting stocks and one boss disturbance.
- **Acceptance:** Disconnecting a sensor or actuator has a readable effect; stable play admits more than one layout; losses explain the causal chain rather than hiding random punishment.
- **Limits:** All dynamics are game laws. Real cybernetic stability claims require a separate model and proof or measurement.

## LYC-B016 · Resonance Forge

**Form:** game · **Build status:** PROPOSED

Forge a device by bringing unstable oscillators into an interesting relationship.

- **Source to inspect:** [12_IMPLEMENTATIONS/core/harmonia_calculator.py](../../12_IMPLEMENTATIONS/core/harmonia_calculator.py). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** A small oscillator network, a fictional target pattern and earned coupling tools.
- **Interaction:** Listen or watch → connect nodes → tune frequencies → survive a disturbance → lock the resulting pattern into an artifact → discover a different recipe.
- **Artifact:** A forged artifact with a replayable numerical recipe.
- **First build:** Ten short challenges, three coupling tools and two valid solution families; sound is optional.
- **Acceptance:** A new player can change one control and understand its effect; no challenge requires hearing alone; solutions survive a defined disturbance rather than a single lucky frame.
- **Limits:** Use synchronisation as play. Do not market the audio as therapeutic, neurological or spiritually necessary.

## LYC-B017 · Alchemical Foundry

**Form:** game · **Build status:** PROPOSED

Discover production chains where operation order changes the material you make.

- **Source to inspect:** [09_CHRYSOPOEIA_L4/](../../09_CHRYSOPOEIA_L4/). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** Fictional materials, explicit recipes, machine capacity and a limited resource budget.
- **Interaction:** Gather → separate → combine → stabilise → test an item → unlock a branching recipe. A failed batch yields useful salvage and a visible cause.
- **Artifact:** A recipe book and a foundry whose machines reflect the chosen build.
- **First build:** Six materials, seven operations and twelve deliberately distinct recipes.
- **Acceptance:** At least two operation orders yield strategically different results; failed experiments retain a readable trail; progression does not require an idle timer or payment.
- **Limits:** The recipe algebra is authored fiction. Its usefulness as a game does not validate chemical or psychological transmutation.

## LYC-B018 · Ember Engine

**Form:** game · **Build status:** PROPOSED

Make explosive combinations from a finite action reserve, then decide when to bank the flame.

- **Source to inspect:** [06_EARNED_LIGHT_L0/](../../06_EARNED_LIGHT_L0/). This is a lineage pointer, not a statement that the proposed product already exists.
- **Inputs:** Fictional heat, fuel, damage, reserve capacity and build modifiers.
- **Interaction:** Spend to attack → convert a successful sequence into recovery → push a risky combo → bank or overheat → reshape the next run.
- **Artifact:** A compact build sheet showing how the large numbers were produced.
- **First build:** One arena, five upgrade branches and a readable overheat rule.
- **Acceptance:** Every displayed multiplier traces to a named modifier; a defensive reserve build is viable; huge values remain legible and numerically stable.
- **Limits:** Ember is a game resource. It must not be framed as an assessment of a player’s consciousness or worth.
