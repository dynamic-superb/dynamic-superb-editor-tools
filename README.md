# Dynamic-SUPERB Editor Tools

This repository contains scripts and documents for editors working with the Dynamic-SUPERB dataset.

## Requirements
- Python 3.8 or higher
- datasets
- tqdm

## Reviewing Pull Requests

1. **Retrieve the JSON file from the pull request**: Each pull request should include an `instance.json` file, which contains comprehensive details about the task.

The JSON file should have the following fields:
- `name`: A concise and descriptive task name suitable for a plot legend.
- `description`: A plain text description of the task, easily understandable by non-experts.
- `keywords`: A list of keywords related to the task, each represented as a separate string.
- `metrics`: A list of evaluation metrics, specified as strings.
- `path`: The file path for the evaluation instance, formatted as `DynamicSuperb/<your instance>`.
- `version`: The commit ID of the evaluation instance on Huggingface.

2. **Gather fundamental information**: Use `gather_information.py` to perform statistical analysis of the dataset. This script verifies necessary fields and computes statistics for both audio and text data in the dataset. Key operations include counting occurrences of specific fields, verifying data types, and computing statistics like average duration and variance.

### Usage

```bash
python gather_information.py --json_path=<JSON_PATH> --save_path=<SAVE_PATH>
```

- `JSON_PATH`: Path to the JSON file with dataset details.
- `SAVE_PATH`: Path where the analysis results will be stored.

Key functionalities of this script include:
- **Validation Checks**: Ensures the presence of essential fields in the dataset such as `file`, `instruction`, and `label`.
- **Feature Counting**: Counts additional features such as `audio1`, `text1`, and `label1` if they exist.

- **Statistics Calculation**:
    - For audio features, calculates the total duration, average duration, variance, maximum, and minimum durations.
    - For text labels, counts occurrences of each unique label.

For datasets with multiple audio/text/label features, the naming convention should be "`audio`, `audio2`, `audio3`" (numbering starts from the second feature). However, it has been observed that many submitters use the format "`audio1`, `audio2`, `audio3`". This script handles this naming inconsistency, but it should be corrected during the pull request review process.

Finally, the script generates a summary file that provides comprehensive statistics of the dataset, including:
- Fields present.
- Total number of examples.
- Detailed statistics for specific audio and text data.

The script also flags repeated file IDs, indicating potential data duplication.
