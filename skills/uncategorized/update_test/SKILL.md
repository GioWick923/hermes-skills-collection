---
name: update_test
description: update_test (Ported from OpenHands skills/ microagent.)
---

Can you check out branch "{{ BRANCH_NAME }}", and run {{ TEST_COMMAND_TO_RUN }}.

The current implementation of the code is correct BUT the test functions {{ FUNCTION_TO_FIX }} in file {{ FILE_FOR_FUNCTION }} are failing.

Please update the test file so that they pass with the current version of the implementation.
