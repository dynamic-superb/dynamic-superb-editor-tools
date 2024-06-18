import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import List

from datasets import load_dataset
from datasets.features.audio import Audio
from datasets.features.features import Features
from tqdm import tqdm

MAX_AUDIO_COUNT = 10
MAX_TEXT_COUNT = 10
MAX_LABEL_COUNT = 10


def count_features(
    features: Features, prefix: str, name_list: List, max_count: int
) -> List[str]:
    for idx in range(2, max_count):
        curr_name = f"{prefix}{idx}"
        if curr_name in features:
            name_list.append(curr_name)
        else:
            break
    return name_list


def main(json_path: Path, save_path: Path) -> None:
    json_info = json.load(json_path.open(mode="r"))
    dataset = load_dataset(json_info["path"], revision=json_info["version"])

    assert "test" in dataset, "Test split was not found in the dataset."
    assert (
        len(dataset.keys()) == 1
    ), f"There are multiple splits in the dataset: {dataset.keys()}."

    test_set = dataset["test"]
    features = test_set.features

    assert "file" in features, "The file field does not exist in the dataset."
    assert (
        "instruction" in features
    ), "The instruction field does not exist in the dataset."
    assert "label" in features, "The label field does not exist in the dataset."

    assert (
        features["file"].dtype == "string"
    ), f"Expected the file to be in string format, but got {features['file'].dtype}."
    assert (
        features["instruction"].dtype == "string"
    ), f"Expected the instruction to be in string format, but got {features['instruction'].dtype}."

    assert not (
        "audio" in features and "audio1" in features
    ), "The audio and audio1 fields should not exist at the same time."
    assert not (
        "text" in features and "text1" in features
    ), "The text and text1 fields should not exist at the same time."
    assert (
        "label" in features or "label1" in features
    ), "The label (or label1) field does not exist in the dataset."
    assert not (
        "label" in features and "label1" in features
    ), "The label and label1 fields should not exist at the same time."

    if "audio" in features or "audio1" in features:
        audio_inputs = ["audio" if "audio" in features else "audio1"]
    else:
        audio_inputs = []
    if "text" in features or "text1" in features:
        text_inputs = ["text" if "text" in features else "text1"]
    else:
        text_inputs = []
    labels = ["label" if "label" in features else "label1"]

    if len(audio_inputs) > 0:
        audio_inputs = count_features(features, "audio", audio_inputs, MAX_AUDIO_COUNT)

    if len(text_inputs) > 0:
        audio_inputs = count_features(features, "text", text_inputs, MAX_TEXT_COUNT)

    labels = count_features(features, "label", labels, MAX_LABEL_COUNT)

    audio_inputs_duration_dict = defaultdict(list)
    labels_duration_dict = defaultdict(list)
    labels_text_dict = defaultdict(lambda: defaultdict(int))
    file_dict = defaultdict(int)
    instruction_dict = defaultdict(int)

    for example in tqdm(test_set):
        curr_file = example["file"]
        curr_instr = example["instruction"]
        file_dict[curr_file] += 1
        instruction_dict[curr_instr] += 1
        for audio_inp in audio_inputs:
            curr_duration = (
                len(example[audio_inp]["array"]) / example[audio_inp]["sampling_rate"]
            )
            audio_inputs_duration_dict[audio_inp].append(curr_duration)
        for label in labels:
            if isinstance(features[label], Audio):
                curr_duration = (
                    len(example[label]["array"]) / example[label]["sampling_rate"]
                )
                labels_duration_dict[label].append(curr_duration)
            elif features[label].dtype == "string":
                labels_text_dict[label][example[label]] += 1
            else:
                raise ValueError(f"Unknown data type for {label}.")

    with save_path.open(mode="w") as f:
        f.write("=" * 20)
        f.write("\n")
        f.write(f"Summary of task: {json_info['name']}\n")
        f.write("=" * 20)
        f.write("\n")
        f.write(f"- Fields of the dataset: {features.keys()}\n")
        f.write(f"- Number of examples: {len(test_set)}\n")

        for file_id in file_dict:
            if file_dict[file_id] > 1:
                f.write(
                    f"*** Repeated file ID detected: {file_id} ({file_dict[file_id]} times)\n"
                )

        f.write(f"- Number of instructions in the dataset: {len(instruction_dict)}\n")
        f.write(
            f"- The minimum required number of instructions: {max(10, len(test_set) / 20)}\n"
        )
        for index, instr in enumerate(instruction_dict):
            f.write(f"-- {(index + 1):02d}. {instr}: {instruction_dict[instr]}\n")

        for audio_inp in audio_inputs + list(labels_duration_dict.keys()):
            curr_duration = audio_inputs_duration_dict[audio_inp]
            curr_sum = sum(curr_duration) / 60.0  # minutes
            curr_avg = sum(curr_duration) / len(curr_duration)  # seconds
            curr_max = max(curr_duration)  # seconds
            curr_min = min(curr_duration)  # seconds
            curr_variance = statistics.variance(curr_duration)  # seconds
            f.write(f"- Statistics of {audio_inp} (Audio):\n")
            f.write(f"-- The total duration: {curr_sum:.3f} minutes.\n")
            f.write(f"-- The average duration: {curr_avg:.3f} seconds.\n")
            f.write(f"-- The variance: {curr_variance:.3f} seconds.\n")
            f.write(f"-- The maximum duration: {curr_max} seconds.\n")
            f.write(f"-- The minimum duration: {curr_min} seconds.\n")

        for label in labels_text_dict:
            f.write(f"- Statistics of {label} (Text):\n")
            for index, sub_label in enumerate(labels_text_dict[label]):
                f.write(
                    f"-- {(index + 1):02d}. {sub_label}: {labels_text_dict[label][sub_label]}\n"
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json_path", "-j", type=Path, required=True)
    parser.add_argument("--save_path", "-s", type=Path, required=True)
    main(**vars(parser.parse_args()))
