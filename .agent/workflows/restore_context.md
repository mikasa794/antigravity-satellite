---
description: Restore Project Context & Memory
---

# 🧠 Memory Restoration Protocol

**Trigger**: Run this at the start of every new session or when the user mentions "memory loss".

1.  **Read Task History**:
    -   `cat .gemini/brain/*/task.md` (Check the current status of all tasks)
2.  **Check Environment & Keys**:
    -   `cat .env` (Verify API keys and endpoints in use)
3.  **Scan Recent Execution Logs**:
    -   `ls -lt assets/antigravity_design_output | head -n 10` (See what was last generated)
4.  **Recall Key Decisions**:
    -   Search for `implementation_plan.md` to review architectural decisions.
5.  **Acknowledge**:
    -   Tell the user you have synced with the project history.
