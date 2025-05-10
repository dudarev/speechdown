\
# src/speechdown/infrastructure/adapters/markdown_merger.py
import re

class MarkdownMerger:
    """
    Handles the logic of merging new transcription sections into existing
    Markdown content, respecting user edits as per the design document.
    """

    def __init__(self, user_corrected_marker: str = "[USER EDITED] "):
        """
        Initializes the merger.
        Args:
            user_corrected_marker: The string to prepend to a transcript line
                                   that has been identified as user-edited.
        """
        self.user_corrected_marker = user_corrected_marker
        # Regex to match H2 headers with the specified timestamp format
        self._h2_timestamp_pattern = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})")

    def _parse_markdown_to_sections(self, markdown_content: str) -> dict[str, list[str]]:
        """
        Parses a Markdown string into a dictionary of H2 sections.
        The key is the H2 header string (e.g., "## 2025-05-10 14:30:00"),
        and the value is a list of content lines under that header.
        """
        sections: dict[str, list[str]] = {}
        current_header: str | None = None
        current_content_lines: list[str] = []

        for line in markdown_content.splitlines():
            match = self._h2_timestamp_pattern.match(line)
            if match:
                if current_header is not None:
                    sections[current_header] = current_content_lines
                current_header = line # Store the full header line as key
                current_content_lines = []
            elif current_header is not None: # Line belongs to the current section
                current_content_lines.append(line)
        
        if current_header is not None: # Add the last section
            sections[current_header] = current_content_lines
            
        return sections

    def _serialize_sections_to_markdown(self, sections: dict[str, list[str]]) -> str:
        """
        Serializes a dictionary of sections back into a Markdown string.
        Sections are sorted chronologically based on their H2 timestamp headers.
        Ensures exactly one blank line between sections, regardless of section content.
        """
        def sort_key(header_str: str):
            match = self._h2_timestamp_pattern.match(header_str)
            if match:
                return match.group(1)
            return header_str

        sorted_headers = sorted(sections.keys(), key=sort_key)
        output_parts: list[str] = []
        for idx, header in enumerate(sorted_headers):
            output_parts.append(header)
            # Remove trailing empty lines from section content
            content = list(sections[header])
            while content and content[-1] == "":
                content.pop()
            output_parts.extend(content)
            # Add a blank line between sections, except after the last section
            if idx < len(sorted_headers) - 1:
                output_parts.append("")
        return "\n".join(output_parts)

    def merge_content(self, existing_markdown: str, new_transcriptions_markdown: str) -> str:
        """
        Merges new transcription sections (formatted as Markdown H2 sections) 
        into existing Markdown content.

        Args:
            existing_markdown: The content of the existing Markdown file as a string.
            new_transcriptions_markdown: A string containing new H2 sections 
                                         (timestamps and transcriptions) to be added/merged.
        
        Returns:
            The merged Markdown content as a string.
        """
        if not new_transcriptions_markdown.strip():
            return existing_markdown # No new content to merge

        existing_sections = self._parse_markdown_to_sections(existing_markdown)
        new_sections = self._parse_markdown_to_sections(new_transcriptions_markdown)

        # Start with existing sections; new/modified ones will update this dictionary.
        merged_sections = existing_sections.copy()

        for new_header, new_content_lines in new_sections.items():
            if not new_content_lines: # Skip if the new section has no content lines
                continue
            
            new_first_transcript_line = new_content_lines[0]

            if new_header in merged_sections:
                # Timestamp collision: Apply "Handling Existing Files" logic from the design.
                existing_section_content = merged_sections[new_header]
                
                if not existing_section_content: 
                    # Existing section for this timestamp was empty (e.g., just a header). Replace with new.
                    merged_sections[new_header] = new_content_lines
                    continue

                existing_first_transcript_line = existing_section_content[0]
                
                # Design: "If they [first lines] are identical, no changes are made"
                if new_first_transcript_line == existing_first_transcript_line:
                    # The new transcription's first line matches the existing one.
                    # Per design, user's subsequent lines are preserved. No change needed here.
                    pass
                else:
                    # Design: "If they differ, the existing line is stored as a 
                    # 'user-corrected transcript' and marked as such in the output."
                    # The new transcription for THIS specific timestamp is effectively superseded
                    # by the user's existing, now marked, version.
                    
                    # Mark the existing first line if it's not already marked.
                    if not existing_first_transcript_line.startswith(self.user_corrected_marker):
                        marked_line = self.user_corrected_marker + existing_first_transcript_line
                        # Create a new list for the modified section content
                        updated_existing_content = [marked_line] + existing_section_content[1:]
                        merged_sections[new_header] = updated_existing_content
            else:
                # This timestamp is new; simply add the new section.
                merged_sections[new_header] = new_content_lines
        
        return self._serialize_sections_to_markdown(merged_sections)

