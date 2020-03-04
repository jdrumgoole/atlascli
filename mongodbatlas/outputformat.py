from enum import Enum

class OutputFormat(Enum):

    SUMMARY = "summary"
    PYTHON = "python"
    JSON = "json"
    def __str__(self):
        return self.value
