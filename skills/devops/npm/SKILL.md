---
name: npm
description: npm package install/management guidance for non-interactive shells, including piping 'yes' to confirm actions and avoiding interactive prompts. Trigger keywords: npm, install package, node_modules, package.json. (Ported from OpenHands skills/ microagent.)
---

When using npm to install packages, you will not be able to use an interactive shell, and it may be hard to confirm your actions.
As an alternative, you can pipe in the output of the unix "yes" command to confirm your actions.
