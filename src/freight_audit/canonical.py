"""Canonical serialization and bounded, exact decimal arithmetic."""

import hashlib
import json
from contextlib import contextmanager
from decimal import Context, Decimal, Inexact, InvalidOperation, localcontext
from typing import Any

from pydantic import BaseModel

ROUNDINGS = {name: name for name in ("ROUND_HALF_UP", "ROUND_HALF_EVEN", "ROUND_DOWN", "ROUND_UP")}


def number(value: str) -> Decimal:
    if not isinstance(value, str):
        raise ValueError("Los decimales deben representarse como texto, nunca como float.")
    import re

    if not re.fullmatch(r"-?(?:0|[1-9]\d*)(?:\.\d+)?", value) or len(value) > 50:
        raise ValueError("Número decimal inválido; usar punto decimal, sin agrupadores ni exponentes.")
    result = Decimal(value)
    if len(result.as_tuple().digits) > 36 or abs(int(result.as_tuple().exponent)) > 12:
        raise ValueError("El número excede 36 dígitos o 12 decimales admitidos.")
    return result


def decimal_text(value: Decimal) -> str:
    if not value.is_finite():
        raise ValueError("Resultado numérico no finito.")
    result = format(value, "f")
    if "." in result:
        result = result.rstrip("0").rstrip(".")
    return "0" if value == 0 else result


@contextmanager
def exact_context():
    context = Context(prec=80, Emin=-999, Emax=999)
    context.traps[Inexact] = True
    with localcontext(context):
        yield


def rounded(value: Decimal, scale: int, mode: str) -> Decimal:
    with localcontext() as context:
        context.traps[Inexact] = False
        return value.quantize(Decimal(1).scaleb(-scale), rounding=ROUNDINGS[mode])


def _json_default(value: Any) -> Any:
    if isinstance(value, BaseModel):
        # Shallow field extraction lets JSON walk nested models once. A full model_dump
        # followed by a recursive copy doubled trace memory for large audit batches.
        return {name: getattr(value, name) for name in type(value).model_fields}
    if isinstance(value, Decimal):
        return decimal_text(value)
    raise TypeError(f"Unsupported canonical type: {type(value).__name__}")


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        default=_json_default,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def bytes_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(text: str | bytes) -> Any:
    def no_duplicates(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Clave repetida en el documento: {key}.")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"Valor no permitido: {value}.")

    return json.loads(text, object_pairs_hook=no_duplicates, parse_constant=reject_constant)


ARITHMETIC_ERRORS = (ArithmeticError, InvalidOperation)
