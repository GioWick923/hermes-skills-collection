# External skill packs: adoption pattern

Use this when evaluating or installing a third-party skill repository that ships many related workflows as a pack.

## What to look for

- Prefer class-level packs over one-off narrow skills.
- Look for a root `skills/` directory and a meta-skill that explains how the pack is meant to be used.
- Expect the pack to contain multiple workflows that should be copied/adopted as a group before pruning.

## Adoption pattern used in this session

1. Clone the repo to a temporary working directory.
2. Inspect the top-level tree and count the skills under `skills/`.
3. Copy the repo's `skills/` subdirectories into Hermes' skills root under a dedicated umbrella namespace.
4. Verify the count and that the meta-skill is present.
5. Remove the temporary clone after verification.

## Verification checkpoints

- The pack should load as a coherent class-level library, not as scattered single-file fragments.
- A representative meta-skill such as `using-agent-skills` should be present.
- The target skills directory should contain the full set of workflows, not just a subset.
