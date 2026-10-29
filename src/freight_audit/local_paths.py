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


def read_bounded(path, limit: int) -> bytes:
    """Bound the actual read as well as stat: do not materialize oversized inputs."""
    import stat

    path = Path(path)
    details = path.stat()
    if not stat.S_ISREG(details.st_mode):
        raise ValueError("El origen no es un archivo regular; seleccionar un archivo de datos guardado.")
    if details.st_size > limit:
        raise ValueError("El archivo supera el tamaño admitido; dividirlo o aportar una copia más pequeña.")
    with path.open("rb") as source:
        data = source.read(limit + 1)
    if len(data) > limit:
        raise ValueError("El archivo supera el tamaño admitido; dividirlo o aportar una copia más pequeña.")
    return data
