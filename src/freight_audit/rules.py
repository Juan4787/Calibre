"""Bounded declarative interpreter. No eval, clock, I/O, network or Python plugins."""

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, localcontext

from .canonical import decimal_text, number, rounded
from .models import BandRow, Expr, LookupRow, Shipment, Trace, Value, Version

type Scalar = Decimal | str | bool


class EvaluationError(Exception):
    def __init__(self, message: str, trace: Trace | None = None):
        display_message = (
            message if len(message) <= 1800 else message[:1800] + "… (ver el detalle completo en la traza)."
        )
        super().__init__(display_message)
        self.trace = trace or Trace(op="unresolved", details={"reason": message})


def dimensions(unit: str | None) -> dict[str, int]:
    """Small explicit unit algebra: ARS/kg, kg, m3. No implicit conversions."""
    if not unit:
        return {}
    result: dict[str, int] = {}
    parts = unit.split("/")
    if len(parts) > 2:
        raise EvaluationError(f"Unidad no admitida: {unit}. Usar una unidad o un cociente simple.")
    for i, part in enumerate(parts):
        for token in part.split("*"):
            if not token or not token.replace("_", "").isalnum():
                raise EvaluationError(f"Unidad no válida: {unit}.")
            result[token] = result.get(token, 0) + (1 if i == 0 else -1)
    return {key: value for key, value in result.items() if value}


@dataclass(frozen=True)
class Atom:
    value: Scalar
    units: dict[str, int]

    @classmethod
    def of(cls, value: Value):
        return cls(
            number(str(value.value)) if value.type == "decimal" else value.value, dimensions(value.unit)
        )

    def text(self):
        return decimal_text(self.value) if isinstance(self.value, Decimal) else self.value

    def decimal(self) -> Decimal:
        if not isinstance(self.value, Decimal):
            raise EvaluationError("La operación requiere un número; revisar el tipo del atributo.")
        return self.value

    def boolean(self) -> bool:
        if not isinstance(self.value, bool):
            raise EvaluationError("La condición debe devolver verdadero o falso.")
        return self.value


def shipment_value(shipment: Shipment, field: str) -> Value:
    if field in {"id", "reference", "carrier"}:
        return Value(type="text", value=getattr(shipment, field))
    key = field.removeprefix("attributes.")
    if key not in shipment.attributes:
        raise EvaluationError(f"Falta el dato '{key}' en la operación '{shipment.reference}'.")
    return shipment.attributes[key]


class Evaluator:
    def __init__(self, shipments: list[Shipment], version: Version, lookup_indexes: dict | None = None):
        self.shipments = sorted(shipments, key=lambda x: x.id)
        self.version = version
        self.lookup_indexes = lookup_indexes if lookup_indexes is not None else {}

    def evaluate(self, expr: Expr) -> tuple[Atom, Trace]:
        children: list[Trace] = []
        details: dict = {}
        try:
            result = self._evaluate(expr, children, details)
            details["units"] = result.units
            return result, Trace(op=expr.op, output=result.text(), details=details, children=children)
        except EvaluationError as exc:
            raise EvaluationError(
                str(exc),
                Trace(op=expr.op, details={**details, "reason": str(exc)}, children=[*children, exc.trace]),
            ) from exc
        except ArithmeticError as exc:
            raise EvaluationError(
                "El cálculo excede la precisión admitida o divide por cero; revisar la regla y su redondeo.",
                Trace(op=expr.op, details={"error": type(exc).__name__}, children=children),
            ) from exc

    def _evaluate(self, expr: Expr, children: list[Trace], details: dict) -> Atom:
        def ev(arg):
            value, trace = self.evaluate(arg)
            children.append(trace)
            return value

        if expr.op == "const":
            assert expr.value is not None
            return Atom.of(expr.value)
        if expr.op == "count":
            details["shipment_ids"] = [s.id for s in self.shipments]
            return Atom(Decimal(len(self.shipments)), {})
        if expr.op in {"attr", "sum"}:
            assert expr.field is not None
            values = []
            details["field"] = expr.field
            details["sources"] = []
            for shipment in self.shipments:
                value = shipment_value(shipment, expr.field)
                atom = Atom.of(value)
                values.append(atom)
                details["sources"].append(
                    {"shipment_id": shipment.id, "field": expr.field, "value": atom.text()}
                )
                if expr.unit is not None and atom.units != dimensions(expr.unit):
                    raise EvaluationError(
                        f"La unidad de '{expr.field}' no coincide con '{expr.unit}'. No se aplican conversiones implícitas."
                    )
            if not values:
                raise EvaluationError("No hay operaciones para ejecutar la regla.")
            if expr.op == "attr":
                if any(v != values[0] for v in values):
                    raise EvaluationError(
                        f"El grupo tiene valores diferentes para '{expr.field}'; definir una agregación explícita."
                    )
                return values[0]
            if any(v.units != values[0].units for v in values):
                raise EvaluationError("No se pueden sumar cantidades de unidades distintas.")
            return Atom(sum((v.decimal() for v in values), Decimal(0)), values[0].units)
        if expr.op == "if":
            condition = ev(expr.args[0]).boolean()
            details["branch"] = "then" if condition else "else"
            return ev(expr.args[1] if condition else expr.args[2])
        values = [ev(arg) for arg in expr.args]
        if expr.op in {"lookup", "band"}:
            table = self.version.tables.get(str(expr.table))
            details["table"] = expr.table
            if table is None or table.kind != expr.op:
                raise EvaluationError(f"No existe una tabla compatible '{expr.table}' en esta versión.")
            matches: list[LookupRow] | list[BandRow]
            if expr.op == "lookup":
                keys = [v.text() for v in values]
                details["keys"] = keys
                if expr.table not in self.lookup_indexes:
                    index: dict = defaultdict(list)
                    for row in table.rows:
                        index[tuple(row.keys)].append(row)
                    self.lookup_indexes[expr.table] = index
                matches = self.lookup_indexes[expr.table].get(tuple(keys), [])
            else:
                n = values[0].decimal()
                if values[0].units != dimensions(table.unit):
                    raise EvaluationError("La unidad del tramo no coincide con la cantidad evaluada.")
                # Explicit half-open bounds: lower inclusive, upper exclusive.
                matches = [
                    r
                    for r in table.bands
                    if (r.lower is None or n >= number(r.lower)) and (r.upper is None or n < number(r.upper))
                ]
                details["bounds_policy"] = "[lower, upper)"
            if len(matches) != 1:
                raise EvaluationError(
                    f"La tabla '{expr.table}' devolvió {len(matches)} coincidencias; se requiere exactamente una."
                )
            details["selected"] = matches[0].model_dump(mode="json")
            return Atom.of(matches[0].value)
        if expr.op in {"and", "or", "not"}:
            flags = [v.boolean() for v in values]
            return Atom(
                not flags[0] if expr.op == "not" else all(flags) if expr.op == "and" else any(flags), {}
            )
        if expr.op in {"eq", "gt", "gte", "lt", "lte"}:
            a, b = values
            if type(a.value) is not type(b.value) or a.units != b.units:
                raise EvaluationError("La comparación mezcla tipos o unidades diferentes.")
            if expr.op == "eq":
                result = a.value == b.value
            else:
                left, right = a.decimal(), b.decimal()
                result = {"gt": left > right, "gte": left >= right, "lt": left < right, "lte": left <= right}[
                    expr.op
                ]
            return Atom(result, {})
        nums = [value.decimal() for value in values]
        units = values[0].units.copy()
        if expr.op in {"add", "sub", "min", "max"}:
            if any(v.units != units for v in values):
                raise EvaluationError("La operación mezcla unidades incompatibles.")
            result = {
                "add": lambda: sum(nums, Decimal(0)),
                "sub": lambda: nums[0] - nums[1],
                "min": lambda: min(nums),
                "max": lambda: max(nums),
            }[expr.op]()
        elif expr.op in {"mul", "div"}:
            result = nums[0]
            for value, n in zip(values[1:], nums[1:], strict=True):
                for unit, power in value.units.items():
                    units[unit] = units.get(unit, 0) + power * (1 if expr.op == "mul" else -1)
                if expr.op == "mul":
                    result *= n
                else:
                    # Division is explicitly rounded. Extra precision avoids ordinary double rounding;
                    # exact rational quantization below avoids boundary ties entirely.
                    result = divide_quantized(result, n, int(expr.scale or 0), str(expr.rounding))
            units = {key: value for key, value in units.items() if value}
            if expr.op == "div":
                details.update(scale=expr.scale, rounding=expr.rounding)
        elif expr.op == "round":
            result = rounded(nums[0], int(expr.scale or 0), str(expr.rounding))
            details.update(scale=expr.scale, rounding=expr.rounding)
        else:
            raise EvaluationError(f"Operación no implementada: {expr.op}.")
        return Atom(result, units)


def divide_quantized(a: Decimal, b: Decimal, scale: int, mode: str) -> Decimal:
    """Exact integer ratio, including tie-breaking: no hidden context rounding."""
    if b == 0:
        raise EvaluationError("El divisor es cero; revisar los parámetros del acuerdo.")
    from fractions import Fraction

    ratio = Fraction(a) / Fraction(b) * (10**scale)
    negative = ratio < 0
    numerator, denominator = abs(ratio.numerator), ratio.denominator
    quotient, remainder = divmod(numerator, denominator)
    if mode == "ROUND_UP":
        increment = remainder != 0
    elif mode == "ROUND_DOWN":
        increment = False
    elif mode == "ROUND_HALF_UP":
        increment = 2 * remainder >= denominator
    elif mode == "ROUND_HALF_EVEN":
        increment = 2 * remainder > denominator or (2 * remainder == denominator and quotient % 2 == 1)
    else:
        raise EvaluationError("Política de redondeo desconocida.")
    integer = (-1 if negative else 1) * (quotient + int(increment))
    with localcontext() as context:
        context.prec = max(80, len(str(abs(integer))) + scale + 2)
        return Decimal(integer).scaleb(-scale)
