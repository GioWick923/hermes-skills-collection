---
name: update_pr_description
description: "Branch name corresponds to the pull request" (Ported from OpenHands skills/ microagent.)
---

Please check the branch "{{ BRANCH_NAME }}" and look at the diff against the main branch. This branch belongs to this PR "{{ PR_URL }}".

Once you understand the purpose of the diff, please use Github API to read the existing PR description, and update it to be more reflective of the changes we've made when necessary.
