"""
Unit tests for DatasetLoader: discovering files, handling missing directory/files,
column normalization, and missing value handling.
"""

import os
import pytest
import pandas as pd
from src.dataset_loader import DatasetLoader, DatasetLoaderError


def test_missing_data_directory(tmp_path):
    non_existent = str(tmp_path / "non_existent_folder")
    loader = DatasetLoader(data_dir=non_existent)
    with pytest.raises(DatasetLoaderError, match="does not exist"):
        loader.load_dataset()


def test_empty_data_directory(tmp_path):
    empty_dir = str(tmp_path / "empty_dir")
    os.makedirs(empty_dir, exist_ok=True)
    loader = DatasetLoader(data_dir=empty_dir)
    with pytest.raises(DatasetLoaderError, match="No .parquet files found"):
        loader.load_dataset()


def test_dataset_column_normalization_and_loading(tmp_path):
    # Test loading with custom alternative column names
    test_parquet = str(tmp_path / "custom_data.parquet")
    df = pd.DataFrame([
        {
            "query": "What is an IP address?",
            "response": "An Internet Protocol address is a unique numerical identifier assigned to each device connected to a network.",
            "key_terms": "IP address, numerical identifier, network",
            "key_concepts": "Unique identifier; Network device addressing",
            "marks": 5.0,
            "rubric": "Full marks for identifier and network role."
        },
        {
            # Row with missing optional columns
            "query": "What is DHCP?",
            "response": "Dynamic Host Configuration Protocol automatically assigns IP addresses.",
            "key_terms": None,
            "key_concepts": None,
            "marks": None,
            "rubric": None
        }
    ])
    df.to_parquet(test_parquet, index=False)

    loader = DatasetLoader(data_dir=str(tmp_path))
    records = loader.load_dataset()

    assert len(records) == 2
    r1 = records[0]
    assert r1.question == "What is an IP address?"
    assert "Internet Protocol" in r1.answer
    assert r1.max_marks == 5.0
    assert r1.source_id.startswith("custom_data.parquet:row-0")

    r2 = records[1]
    assert r2.question == "What is DHCP?"
    assert r2.expected_concepts is None
    assert r2.source_id.startswith("custom_data.parquet:row-1")
