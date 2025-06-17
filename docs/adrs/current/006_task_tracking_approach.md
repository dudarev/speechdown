# ADR 006: Task Tracking Approach

**Created:** 2025-03-04 <br/>
**Updated:** 2025-06-17 <br/>
**Status:** Accepted

## Context

As the SpeechDown project evolves, there's a need to track tasks, features, and improvements at different time horizons (short-term, mid-term, and long-term). Currently, there's no standardized location or format for documenting these plans, making it difficult to prioritize work and communicate development intentions.

## Decision

We will implement a multi-layered task tracking system:

1. Append-and-review notes:

   - Use [`docs/notes/ar.md`](../../notes/ar.md) for brainstorming, quick ideas, and ongoing thoughts
   - Inspired by [Andrej Karpathy's append-and-review note concept](https://karpathy.bearblog.dev/the-append-and-review-note/)
   - Serves as a capture space for development ideas that may later be promoted to TODO.md or planning documents

2. Short-term TODOs:

   - Use the existing [`TODO.md`](../../../TODO.md) file in the project root for immediate implementation tasks
   - Use checkbox format (`- [ ]`) for trackable completion status

3. Mid/Long-term planning:

   - Create a [planning](../../../docs/planning/) directory with:
     - [roadmap.md](../../../docs/planning/roadmap.md) for mid-term feature roadmaps and milestones
     - [vision.md](../../../docs/planning/vision.md) for long-term development goals and architectural direction

4. Task promotion process:
   - Ideas and thoughts start in `docs/notes/ar.md` for brainstorming
   - Concrete tasks move to `TODO.md` for immediate implementation
   - Significant tasks move to Linear tasks when ready for implementation
   - Strategic features documented in planning documents

## Consequences

- Improved visibility of immediate tasks and future direction
- Clear separation between tactical implementation tasks and strategic planning
- Easier onboarding for new contributors who can understand both immediate work and project vision
- More structured approach to feature prioritization
- Minimal overhead while maintaining necessary documentation

## Conclusion

This task tracking approach provides a lightweight but effective means of documenting development plans across different time horizons while fitting into the existing documentation structure.
