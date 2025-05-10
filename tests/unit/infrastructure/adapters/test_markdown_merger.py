import pytest
from speechdown.infrastructure.adapters.markdown_merger import MarkdownMerger

# Helper to create consistent timestamps for testing
TS1 = "2025-05-10 10:00:00"
TS2 = "2025-05-10 11:00:00"
TS3 = "2025-05-09 12:00:00" # For sorting tests

H_TS1 = f"## {TS1}"
H_TS2 = f"## {TS2}"
H_TS3 = f"## {TS3}"

USER_EDITED_MARKER = "[USER EDITED] "

@pytest.fixture
def merger() -> MarkdownMerger:
    """Returns a MarkdownMerger instance with the default marker."""
    return MarkdownMerger()

@pytest.fixture
def custom_merger() -> MarkdownMerger:
    """Returns a MarkdownMerger instance with a custom marker."""
    return MarkdownMerger(user_corrected_marker="[CUSTOM] ")

def test_merge_content_empty_existing_empty_new(merger: MarkdownMerger):
    # Arrange
    existing_markdown = ""
    new_transcriptions_markdown = ""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    assert result == ""

def test_merge_content_empty_existing_with_new(merger: MarkdownMerger):
    # Arrange
    existing_markdown = ""
    new_transcriptions_markdown = f"""{H_TS1}
New transcript line 1.
*Language: en*"""
    expected_markdown = f"""{H_TS1}
New transcript line 1.
*Language: en*
"""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    # Normalize by splitting lines and rejoining to handle potential trailing newline discrepancies
    assert "\n".join(result.splitlines()) == "\n".join(expected_markdown.splitlines())


def test_merge_content_existing_with_empty_new(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}
Existing transcript line 1.
Some user comment."""
    new_transcriptions_markdown = ""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    assert "\n".join(result.splitlines()) == "\n".join(existing_markdown.splitlines())

def test_merge_content_add_new_section_no_collision(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}
Existing transcript line 1."""
    new_transcriptions_markdown = f"""{H_TS2}
New transcript line 2."""
    expected_markdown = f"""{H_TS1}
Existing transcript line 1.

{H_TS2}
New transcript line 2."""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    assert "\n".join(result.splitlines()) == "\n".join(expected_markdown.splitlines())

def test_merge_content_timestamp_collision_identical_first_line(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}
Same first line.
User added this line.
And this one."""
    new_transcriptions_markdown = f"""{H_TS1}
Same first line.
*Language: en*""" # New metadata, but first line is the same
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    # Expect no change to the existing section as per design ("If they are identical, no changes are made")
    assert "\n".join(result.splitlines()) == "\n".join(existing_markdown.splitlines())


def test_merge_content_timestamp_collision_different_first_line(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}
Original first line by user.
User comment."""
    new_transcriptions_markdown = f"""{H_TS1}
Newly transcribed first line.
*Language: en*"""
    expected_markdown = f"""{H_TS1}
{USER_EDITED_MARKER}Original first line by user.
User comment."""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    assert "\n".join(result.splitlines()) == "\n".join(expected_markdown.splitlines())

def test_merge_content_timestamp_collision_different_first_line_custom_marker(custom_merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}
Original first line by user."""
    new_transcriptions_markdown = f"""{H_TS1}
Newly transcribed first line."""
    expected_markdown = f"""{H_TS1}
[CUSTOM] Original first line by user."""
    # Act
    result = custom_merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    assert "\n".join(result.splitlines()) == "\n".join(expected_markdown.splitlines())


def test_merge_content_timestamp_collision_existing_already_marked(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}
{USER_EDITED_MARKER}Original first line by user.
User comment."""
    new_transcriptions_markdown = f"""{H_TS1}
Another new transcribed first line.
*Language: fr*"""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    # Expect no double marking, existing marked content is preserved
    assert "\n".join(result.splitlines()) == "\n".join(existing_markdown.splitlines())

def test_merge_content_timestamp_collision_existing_section_empty_content(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}""" # Header exists, but no content lines under it
    new_transcriptions_markdown = f"""{H_TS1}
New transcript for previously empty section.
*Language: de*"""
    expected_markdown = f"""{H_TS1}
New transcript for previously empty section.
*Language: de*"""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    assert "\n".join(result.splitlines()) == "\n".join(expected_markdown.splitlines())


def test_merge_content_chronological_sorting_of_sections(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS2}
Content for TS2."""
    new_transcriptions_markdown = f"""{H_TS3}
Content for TS3 (earlier).

{H_TS1}
Content for TS1 (middle)."""
    # Expected: TS3, then TS1, then TS2
    expected_markdown = f"""{H_TS3}
Content for TS3 (earlier).

{H_TS1}
Content for TS1 (middle).

{H_TS2}
Content for TS2."""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    actual = "\n".join(result.splitlines())
    expected = "\n".join(expected_markdown.splitlines())
    assert actual == expected

def test_merge_content_new_section_has_no_content_lines(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}
Existing content."""
    new_transcriptions_markdown = f"""{H_TS2}""" # New header but no content lines
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    # The new empty section should effectively be ignored or not added if it has no content.
    # The current _parse_markdown_to_sections might add it with an empty list.
    # The _serialize_sections_to_markdown might then just print the header.
    # Let's assume for now an empty section (just a header) is not added if it's from `new_transcriptions_markdown`
    # and has no content lines. The `merge_content` has a check: `if not new_content_lines: continue`
    assert "\n".join(result.splitlines()) == "\n".join(existing_markdown.splitlines())

def test_parse_markdown_to_sections_complex_content(merger: MarkdownMerger):
    # Arrange
    markdown_input = f"""
Some text before any headers.
{H_TS1}
Line 1 for TS1.
Line 2 for TS1.
> A blockquote
- A list item

{H_TS2}
Line 1 for TS2.
```python
print("hello")
```
Another line for TS2."""
    # Act
    sections = merger._parse_markdown_to_sections(markdown_input)
    # Assert
    assert H_TS1 in sections
    assert sections[H_TS1] == [
        "Line 1 for TS1.",
        "Line 2 for TS1.",
        "> A blockquote",
        "- A list item",
        "",
    ]
    assert H_TS2 in sections
    assert sections[H_TS2] == [
        "Line 1 for TS2.",
        "```python",
        'print("hello")', # Correctly formatted string
        "```",
        "Another line for TS2.",
    ]
    # Text outside sections is ignored by _parse_markdown_to_sections
    assert len(sections) == 2


def test_serialize_sections_to_markdown_empty_input(merger: MarkdownMerger):
    # Arrange
    sections = {}
    # Act
    result = merger._serialize_sections_to_markdown(sections)
    # Assert
    assert result == ""

def test_serialize_sections_ensures_blank_line_separation(merger: MarkdownMerger):
    # Arrange
    sections = {
        H_TS1: ["Line 1 for TS1."],
        H_TS2: ["Line 1 for TS2."]
    }
    expected_markdown = f"""{H_TS1}
Line 1 for TS1.

{H_TS2}
Line 1 for TS2.""" # Note: _serialize_sections_to_markdown adds a trailing newline if content exists
    # Act
    result = merger._serialize_sections_to_markdown(sections)
    # Assert
    assert "\n".join(result.splitlines()) == "\n".join(expected_markdown.splitlines())

def test_serialize_sections_no_extra_newline_for_last_empty_section(merger: MarkdownMerger):
    # Arrange
    # This tests a subtle case: if the last chronological section has content, it gets a newline after.
    # If the last chronological section is just a header (empty content list), it should not add an extra blank line.
    sections_with_content_last = {
        H_TS1: ["Content"] 
    }
    sections_empty_last = {
         H_TS1: []
    }
    expected_content_last = f"{H_TS1}\nContent" # Trailing newline added by join
    expected_empty_last = f"{H_TS1}"

    # Act
    result_content_last = merger._serialize_sections_to_markdown(sections_with_content_last)
    result_empty_last = merger._serialize_sections_to_markdown(sections_empty_last)
    
    # Assert
    # .splitlines() will remove the trailing newline, so we compare based on that behavior.
    # The key is that an empty section doesn't cause a *double* newline at the end.
    assert "\n".join(result_content_last.splitlines()) == expected_content_last 
    assert "\n".join(result_empty_last.splitlines()) == expected_empty_last


def test_merge_content_preserves_all_user_lines_on_first_line_match(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}
This is the first transcript line.
This is a user comment.
This is another user comment.
    Indented user comment.
"""
    new_transcriptions_markdown = f"""{H_TS1}
This is the first transcript line.
*Language: en*
*Confidence: 0.95*
"""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    # Since the first transcript line matches, the entire original section should be preserved.
    assert "\n".join(result.splitlines()) == "\n".join(existing_markdown.splitlines())

# TODO(AD): Modify this when existing markdown will be read for feedback. No changes expected.
def test_merge_content_preserves_all_user_lines_on_first_line_differs(merger: MarkdownMerger):
    # Arrange
    existing_markdown = f"""{H_TS1}
Original user's first line.
This is a user comment.
This is another user comment.
"""
    new_transcriptions_markdown = f"""{H_TS1}
New AI-generated first line.
*Language: en*
"""
    expected_markdown = f"""{H_TS1}
{USER_EDITED_MARKER}Original user's first line.
This is a user comment.
This is another user comment.
"""
    # Act
    result = merger.merge_content(existing_markdown, new_transcriptions_markdown)
    # Assert
    # The first line is marked, but subsequent user lines are preserved.
    assert "\n".join(result.splitlines()) == "\n".join(expected_markdown.splitlines())

def test_init_default_marker():
    # Arrange & Act
    merger = MarkdownMerger()
    # Assert
    assert merger.user_corrected_marker == "[USER EDITED] "

def test_init_custom_marker():
    # Arrange & Act
    custom_marker_text = "MODIFIED: "
    merger = MarkdownMerger(user_corrected_marker=custom_marker_text)
    # Assert
    assert merger.user_corrected_marker == custom_marker_text

