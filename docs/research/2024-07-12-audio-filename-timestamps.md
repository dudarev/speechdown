# Extracting Timestamps from Audio File Names
*Status*: Active
*Date*: 2024-07-12

## Problem
Audio files often have timestamps embedded in their file names, but the formats can vary widely. We need a systematic way to extract these timestamps. This research aims to explore methods for reliably parsing timestamps from file names, including leveraging existing tools and potentially using machine learning for categorization.

## Approach
1. **Gather Audio File Names:** Develop a script to collect a diverse set of audio file names from various sources.
2. **Analyze Naming Patterns:** Manually inspect the collected file names to identify common timestamp formats and patterns.
3. **Categorize Formats:** Explore using an LLM or rule-based methods to categorize the different timestamp formats found.
4. **Integrate Existing Parser:** Adapt and evaluate the timestamp parsing function from the `voice.cli` project.
5. **Develop New Parsers:** Create new parsing logic for formats not covered by the existing function.
6. **Evaluate Performance:** Measure the accuracy and coverage of the developed timestamp extraction methods.

## Findings
(To be filled as research progresses)

## Next steps
- Begin by developing the script to gather audio file names.
- Research and experiment with LLM-based categorization of file name patterns.
