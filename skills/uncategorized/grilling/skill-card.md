## Description: <br>
Interview the user relentlessly about a plan or design. Use when the user wants to stress-test a plan before building, or uses any 'grill' trigger phrases. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[wufei-png](https://clawhub.ai/user/wufei-png) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users, developers, and planning teams use this skill to stress-test plans or designs through focused interview questions that surface tradeoffs, dependencies, and decisions before building. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Planning guidance can be incorrect or misleading if the skill overemphasizes a tradeoff or misses project context. <br>
Mitigation: Review recommendations before acting on them, especially before changing code, architecture, product scope, or delivery plans. <br>
Risk: The skill may inspect relevant project files when that can answer planning questions. <br>
Mitigation: Use it in workspaces where that inspection is acceptable, and review the source URL or prefer pinned marketplace installs for stronger supply-chain control. <br>


## Reference(s): <br>
- [Grilling ClawHub skill page](https://clawhub.ai/wufei-png/skills/grilling) <br>
- [Upstream grilling skill reference](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Guidance] <br>
**Output Format:** [Markdown prose with focused questions, tradeoff comparisons, and recommendations] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Asks one question at a time by default, treats a user-provided per-turn maximum as a ceiling, and may inspect relevant project files when that can answer a planning question.] <br>

## Skill Version(s): <br>
1.0.6 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
