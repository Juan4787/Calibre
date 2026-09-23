"""Conservative boundaries for operator-chosen local output paths."""

import os
from pathlib import Path, PureWindowsPath


def checked_output_path(destination: Path) -> Path:
    """Reject ambiguous traversal and existing symlink components before writing.

    The caller still owns this local path. This protects against accidental
    redirection, not a process racing to replace directories under the same OS
    account while the write is in progress.
    """
    path = Path(destination)
    if ".." in path.parts or (os.name != "nt" and PureWindowsPath(str(path)).drive):
        raise ValueError("El destino contiene una ruta ambigua; elegir una ruta local sin '..'.")
    absolute = path.absolute()
    for component in (*reversed(absolute.parents), absolute):
        if component.is_symlink():
            raise ValueError("El destino atraviesa un enlace simbólico; elegir una ruta directa.")
    return path
