from airflow.models import Variable
from pathlib import Path


def add_base_dir_if_exists(path: str) -> str:
    """Add base dir from environmental variables.
    Used to for testing to direct I/O operations to tmp directories."""
    if Variable.get("base_dir", None) is not None:
        return str(
            Path(Variable.get("base_dir")) / Path(path).relative_to(Path(path).anchor)
        )
    else:
        return path
