## Meta Prompt

Since Github Copilot was in the context of the research with relevant files linked I asked it with Gemini 2.5 Pro in agent mode the following meta prompt to generate a prompt:

```
I have the output as the following: I'd like you to write a prompt for another large language model that will suggest patterns for or extracting timestamp from possible patterns in the output.

Voice 250526_121004.m4a
Voice 250526_124218.m4a
```

With the following clarification:

```
in the prompt we need to highlight that there are multiple patterns so it's not a single pattern but multiple patterns
```

## Prompt for Gemini 2.5 Pro

It suggestedd the following prompt that we used in https://aistudio.google.com/:

```
Hello! I have a list of audio filenames, and I need to extract the timestamp information embedded within them. The timestamps seem to follow one or more patterns, and I'd like your help in identifying all possible patterns and suggesting ways to extract these timestamps. It's important to consider that there might not be a single, universal pattern across all filenames.
Based on these examples, please:
Describe the potential common pattern(s) you observe for the timestamp (e.g., YYMMDD_HHMMSS, or other variations). Please explicitly look for and list multiple distinct patterns if they exist.
Suggest one or more regular expressions (regex) that can be used to reliably extract the date and time components from these filenames, covering all identified patterns.
If there are multiple patterns, please list them clearly and provide corresponding extraction methods (e.g., different regex or parsing logic) for each.
Explain how to parse the extracted string(s) into a standard date/time format, considering the different potential input patterns.
My goal is to be able to programmatically extract the year, month, day, hour, minute, and second from each filename, accommodating any variations in the timestamp format.
Thank you!
```

## Further Iterations

Further iterations with GitHub Copilot were needed because edge cases were not parsed correctly.

