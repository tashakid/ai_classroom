import logging
import os
import json
from typing import Any, Dict

def load_json(file_path):
    """
    Loads JSON data from a file.

    :param file_path: Path to the JSON file.
    :return: Parsed JSON data.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        return {}

    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            print(f"Error: File {file_path} contains invalid JSON.")
            return {}

def save_json(data: Dict[str, Any], file_path: str):
    """
    Saves a dictionary as a JSON file.

    Args:
        data (Dict[str, Any]): The data to save.
        file_path (str): The path where the JSON file will be saved.
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f"Data successfully saved to {file_path}.")
    except Exception as e:
        logging.error(f"Failed to save JSON to {file_path}: {e}")
        raise e