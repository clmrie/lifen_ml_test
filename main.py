import json
from typing import List, Dict, Tuple, Optional


JSON_PATH = "JSON/doc1.json"


def sort_file(words: List[Dict], y_tol: float = 0.005) -> List[List[Dict]]:
    """
    Sorts and groups words by their approximate horizontal alignment.

    For each word, calculates the average y and x positions from the bounding
    box. Then groups words that are roughly on the same horizontal line (within
    y_tol) and sorts each group from left to right based on the x position.

    Args:
        words (List[Dict]): List of word dictionaries, each with a 'bbox' key.
        y_tol (float, optional): Tolerance for grouping words by vertical
            position. Defaults to 0.005.

    Returns:
        List[List[Dict]]: A list of lines where each line is a list of word
            dictionaries.
    """
    # calculating average positions
    for word in words:
        word['y_avg'] = (word['bbox']['y_min'] +
                         word['bbox']['y_max']) / 2
        word['x_avg'] = (word['bbox']['x_min'] +
                         word['bbox']['x_max']) / 2

    # grouping words roughly on same horizontal line
    buckets = {}
    for word in words:
        # words with similar y_avg values will get the same key
        key = round(word['y_avg'] / y_tol)
        buckets.setdefault(key, []).append(word)

    # sort lines by x value (left to right)
    sorted_lines = []
    for key in sorted(buckets.keys()):
        line = sorted(buckets[key], key=lambda w: w['x_avg'])
        sorted_lines.append(line)

    return sorted_lines


def extract_patient_name(
    lines_text: List[str],
    markers: List[str] = ["Monsieur", "Madame"]
) -> Tuple[Optional[str], Optional[str]]:
    """
    Scans each line for markers and returns the first two capitalized words
    that follow the marker as first and last names.

    Args:
        lines_text (List[str]): List of strings representing lines of text.
        markers (List[str], optional): List of marker strings to search for.
            Defaults to ["Monsieur", "Madame"].

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the first name
            and last name if found; otherwise (None, None).
    """
    for line in lines_text:
        for marker in markers:
            if marker in line:
                # split line into 2 parts: before and after marker
                parts = line.split(marker)
                # make sure marker wasn't at the end of line
                if len(parts) > 1:
                    # takes what's after the marker
                    after_marker = parts[1].strip().split()
                    # capitalization pattern
                    candidate_names = [
                        word for word in
                        after_marker if word and word[0].isupper()
                    ]
                    if len(candidate_names) >= 2:
                        # keep first one if several
                        return candidate_names[0], candidate_names[1]
    # Fallback if no marker is found
    return None, None


def format_json(json_path: str) -> List[str]:
    """
    Reads a JSON file, extracts words from the first page, groups them into
    lines, and joins each line into a single string.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        List[str]: A list of text lines extracted from the JSON file.
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    # we assume a single page for simplicity
    pages = data.get("pages", [])
    if not pages:
        raise ValueError("No pages found in JSON file.")
    page = pages[0]
    words = page.get("words", [])
    if not words:
        return []

    lines = sort_file(words)

    lines_text = []
    for line in lines:
        joined_line = " ".join(word["text"] for word in line)
        lines_text.append(joined_line)

    return lines_text


def main() -> None:
    """
    Reads the JSON file, extracts text lines, and retrieves the patient name.
    """
    try:
        lines_text = format_json(JSON_PATH)
    except (IOError, ValueError) as e:
        print(f"Error processing JSON file: {e}")
        return

    first_name, last_name = extract_patient_name(lines_text)
    if first_name and last_name:
        print(first_name, last_name)
    else:
        print("Patient name not found.")


if __name__ == "__main__":
    main()
