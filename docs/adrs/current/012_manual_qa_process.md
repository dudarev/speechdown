# ADR 012: Manual QA Process

**Date:** 2025-05-25
**Status:** Accepted

## Context

Currently, the project relies on unit and integration tests for automated quality assurance. Automated tests protect core logic, but SpeechDown still ships UI changes, CLI ergonomics, and docs updates that automated tests do not fully cover. Regressions can occur when branches are merged without structured human checks. There is a need for a structured manual QA process to validate end-to-end scenarios, user experience, and overall application stability.

## Decision

We will implement the following manual QA process:

1.  **Create a dedicated directory for manual QA checklists:** A new directory named `tests/manual` will be used (already created).
2.  **Structure manual QA checklists:** Inside `tests/manual`, checklists will initially be stored directly. As the number of checklists grows, they can be organized into subdirectories based on features or application modules (e.g., `tests/manual/cli_commands/`, `tests/manual/output_formats/`). Each checklist will be a markdown file (e.g., `tests/manual/checklist_001_show_help.md`).
3.  **Checklist Template:** A template file named `tests/manual/templates/checklist_template.md` (already created) will be used as a base for all new checklists.
4.  **Checklist Content:** Each checklist file, based on the template, will include:
    *   A title indicating the feature/scenario being tested.
    *   Space for brief notes or a Bug ID can be added below each item if needed.
5.  **Execution:**
    *   For non-trivial feature branches, the author is responsible for creating or updating relevant checklists.
    *   The PR author runs the checklist(s) locally.
    *   The filled-in checklist(s) should be reviewed as part of the PR, potentially with a screenshare with the reviewer if needed.
    *   The release manager (or designated QA person) runs a combined set of relevant checklists on release candidates before publishing.
6.  **Documentation:** Filled-in checklists (checked or unchecked boxes and any notes) serve as documentation of the manual QA performed. Any failed checks (unchecked boxes with explanatory notes) should be linked to a bug report or issue.

### Checklist Template (`tests/manual/templates/checklist_template.md`)

```markdown
# Manual QA Checklist – <Feature/Scenario Name>

- **Test Step 1:** Description of the action to perform.
  - Expected: (Optional: Expected result of this action.)
  - Notes: (Optional: any observations or Bug ID)

- **Test Step 2:** Another action.
  - Expected: Expected result.
  - Notes:

- **Test Step ...:** And so on.
  - Expected: ...
  - Notes:
```

## Consequences

### Positive

*   Improved confidence in releases by validating end-to-end user flows and UI/CLI aspects.
*   Early detection of usability issues and bugs not covered by automated tests.
*   Clear, documented, and repeatable process for manual testing using checklists.
*   Centralized location for all manual test checklists.
*   PR authors take initial responsibility for QA of their features.

### Negative

*   Manual QA can be time-consuming.
*   Requires discipline to create, update, and consistently execute checklists.
*   Potential for human error during test execution, though checklists aim to minimize this.
*   Overhead in maintaining the checklist template and individual checklists.

## Conclusion

Introducing a structured manual QA process using checklists, organized by feature/scenario, will enhance the overall quality and reliability of the SpeechDown project. This process complements our automated testing strategies by focusing on user-centric validation and aspects not easily covered by automation.
