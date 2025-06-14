# Test Assets

This directory contains test audio files and other assets used for integration tests.

## Audio Files

Directory structure:
```
data/
├── .speechdown/
├── subfolder/
│   ├── test-1_20240315_143022.m4a - English: "Test 1"
├── README.md
├── test-2 20240316 101530.m4a - English: "Test 2"
├── test-ru.m4a - Russian: "Заметка по-русски"
├── test-ua.m4a - Ukrainian: "Запис українською"
```

## Adding New Test Assets

When adding new test assets:

1. Keep them small and minimal to maintain a reasonable repository size
2. Document their source and purpose in this README
3. If the files are generated, consider adding the generation script to the repository
