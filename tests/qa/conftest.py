"""Exclude QA tests from normal pytest runs.

QA tests are interactive walkthroughs meant to be run individually
with the -s flag. They are NOT part of the regular test suite.

Usage:
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__1__create_twin_fleet -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__2__create_instance -s
"""
import sys

collect_ignore_glob = ['test_QA__*.py']


def pytest_collect_file(parent, file_path):
    if 'tests/qa' in str(file_path):
        return None
