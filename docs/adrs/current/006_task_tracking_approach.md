# ADR 006: Task Tracking Approach

**Date:** 2025-03-04
**Status:** Accepted

## Context

As the SpeechDown project evolves, there's a need to track tasks, features, and improvements at different time horizons (short-term, mid-term, and long-term). Currently, there's no standardized location or format for documenting these plans, making it difficult to prioritize work and communicate development intentions.

## Decision

We will implement a multi-layered task tracking system:

1. Short-term TODOs:

   - Create a `TODO.md` file in the project root for immediate implementation tasks
   - Use checkbox format (`- [ ]`) for trackable completion status

2. Mid/Long-term planning:

   - Create a [planning](../../docs/planning/) directory with:
     - [roadmap.md](../../docs/planning/roadmap.md) for mid-term feature roadmaps and milestones
     - [vision.md](../../docs/planning/vision.md) for long-term development goals and architectural direction

3. Task promotion process:
   - Tasks start in `TODO.md`
   - Significant tasks move to GitHub issues when ready for implementation
   - Strategic features documented in planning documents

## Consequences

- Improved visibility of immediate tasks and future direction
- Clear separation between tactical implementation tasks and strategic planning
- Easier onboarding for new contributors who can understand both immediate work and project vision
- More structured approach to feature prioritization
- Minimal overhead while maintaining necessary documentation

## Conclusion

This task tracking approach provides a lightweight but effective means of documenting development plans across different time horizons while fitting into the existing documentation structure.
