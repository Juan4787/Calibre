"""Versioned contracts. Decimal inputs are strings; unknown keys are rejected."""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

from .canonical import decimal_text, number

Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
MoneyText = Annotated[str, StringConstraints(max_length=50)]
Currency = Annotated[str, StringConstraints(pattern=r"^[A-Z]{3}$")]
Hash = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
Status = Literal["PASS", "FAIL", "REVIEW", "UNDETERMINABLE"]
Rounding = Literal["ROUND_HALF_UP", "ROUND_HALF_EVEN", "ROUND_DOWN", "ROUND_UP"]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, str_max_length=10000)


class Value(Model):
    type: Literal["decimal", "text", "date", "boolean"]
    value: str | bool
    unit: str | None = None

    @model_validator(mode="after")
    def validate_value(self) -> Self:
        if self.type == "boolean":
            if not isinstance(self.value, bool):
                raise ValueError("Un booleano requiere true o false.")
        elif not isinstance(self.value, str):
            raise ValueError("El valor debe ser texto.")
        elif self.type == "decimal":
            object.__setattr__(self, "value", decimal_text(number(self.value)))
        elif self.type == "date":
            if date.fromisoformat(self.value).isoformat() != self.value:
                raise ValueError("La fecha debe usar AAAA-MM-DD.")
        if self.unit is not None and self.type != "decimal":
            raise ValueError("Sólo un decimal puede declarar unidad.")
        return self


class SourceRef(Model):
    document: Hash
    filename: str
    sheet: str
    row: int = Field(ge=1)
    column: str
    raw: str
    transform: str


class Shipment(Model):
    id: Identifier
    reference: Identifier
    carrier: Identifier
    attributes: dict[Identifier, Value] = Field(default_factory=dict)
    provenance: dict[str, SourceRef] = Field(default_factory=dict)


class Charge(Model):
    id: Identifier
    settlement: Identifier
    carrier: Identifier
    agreement: Identifier
    reference: str
    concept: Identifier
    amount: MoneyText
    currency: Currency
    attributes: dict[Identifier, Value] = Field(default_factory=dict)
    provenance: dict[str, SourceRef] = Field(default_factory=dict)

    @field_validator("amount")
    @classmethod
    def monetary(cls, value):
        return decimal_text(number(value))


class Evidence(Model):
    id: Identifier
    kind: Identifier
    shipment_ids: list[Identifier] = Field(default_factory=list)
    charge_ids: list[Identifier] = Field(default_factory=list)
    note: str
    document_hash: Hash | None = None


class Expr(Model):
    op: Literal[
        "const",
        "attr",
        "sum",
        "count",
        "add",
        "sub",
        "mul",
        "div",
        "min",
        "max",
        "round",
        "lookup",
        "band",
        "if",
        "eq",
        "gt",
        "gte",
        "lt",
        "lte",
        "and",
        "or",
        "not",
    ]
    args: list["Expr"] = Field(default_factory=list, max_length=100)
    value: Value | None = None
    field: str | None = None
    unit: str | None = None
    table: str | None = None
    scale: int | None = Field(default=None, ge=0, le=12)
    rounding: Rounding | None = None

    @model_validator(mode="after")
    def shape(self) -> Self:
        arity = {
            "const": (0, 0),
            "attr": (0, 0),
            "sum": (0, 0),
            "count": (0, 0),
            "add": (2, 100),
            "mul": (2, 100),
            "min": (2, 100),
            "max": (2, 100),
            "sub": (2, 2),
            "div": (2, 2),
            "round": (1, 1),
            "band": (1, 1),
            "lookup": (1, 20),
            "if": (3, 3),
            "eq": (2, 2),
            "gt": (2, 2),
            "gte": (2, 2),
            "lt": (2, 2),
            "lte": (2, 2),
            "and": (2, 100),
            "or": (2, 100),
            "not": (1, 1),
        }
        low, high = arity[self.op]
        if not low <= len(self.args) <= high:
            raise ValueError(f"Cantidad de operandos incorrecta para {self.op}.")
        required = {
            "const": {"value"},
            "attr": {"field"},
            "sum": {"field"},
            "lookup": {"table"},
            "band": {"table"},
            "div": {"scale", "rounding"},
            "round": {"scale", "rounding"},
        }.get(self.op, set())
        optional = {"attr": {"unit"}, "sum": {"unit"}}.get(self.op, set())
        present = {
            key
            for key in ("value", "field", "unit", "table", "scale", "rounding")
            if getattr(self, key) is not None
        }
        if not required <= present or not present <= required | optional:
            raise ValueError(f"Parámetros incorrectos para {self.op}: requeridos {sorted(required)}.")

        def depth(expr, level=0):
            if level > 30:
                raise ValueError("La expresión supera 30 niveles.")
            return 1 + sum(depth(arg, level + 1) for arg in expr.args)

        if depth(self) > 1000:
            raise ValueError("La expresión supera 1000 operaciones.")
        return self


class LookupRow(Model):
    keys: list[str | bool]
    value: Value


class BandRow(Model):
    lower: MoneyText | None = None
    upper: MoneyText | None = None
    value: Value

    @model_validator(mode="after")
    def bounds(self):
        low = number(self.lower) if self.lower is not None else None
        high = number(self.upper) if self.upper is not None else None
        if low is not None and high is not None and low >= high:
            raise ValueError("El límite inferior debe ser menor que el superior.")
        return self


class Table(Model):
    kind: Literal["lookup", "band"]
    rows: list[LookupRow] = Field(default_factory=list, max_length=20000)
    bands: list[BandRow] = Field(default_factory=list, max_length=1000)
    unit: str | None = None

    @model_validator(mode="after")
    def table_shape(self):
        if self.kind == "lookup" and (not self.rows or self.bands):
            raise ValueError("La tabla de búsqueda requiere filas y no tramos.")
        if self.kind == "band" and (not self.bands or self.rows):
            raise ValueError("La tabla de tramos requiere bandas y no filas.")
        return self


class Requirement(Model):
    any_of: list[Identifier] = Field(min_length=1)
    scope: Literal["group", "each_shipment", "each_charge"] = "group"
    document_required: bool = False


class Rule(Model):
    id: Identifier
    concept: Identifier
    description: str
    expression: Expr
    when: Expr | None = None
    evidence: list[Requirement] = Field(default_factory=list)
    expected: bool = False


class Version(Model):
    id: Identifier
    valid_from: str
    valid_to: str | None = None
    rules: list[Rule] = Field(min_length=1, max_length=200)
    tables: dict[Identifier, Table] = Field(default_factory=dict)
    source_note: str

    @model_validator(mode="after")
    def valid(self):
        start = date.fromisoformat(self.valid_from)
        end = date.fromisoformat(self.valid_to) if self.valid_to else None
        if start.isoformat() != self.valid_from or (end and end.isoformat() != self.valid_to):
            raise ValueError("Usar fechas AAAA-MM-DD.")
        if end and end < start:
            raise ValueError("La vigencia final precede al inicio.")
        if len({r.id for r in self.rules}) != len(self.rules):
            raise ValueError("Hay identificadores de regla repetidos.")
        return self


class MatchKey(Model):
    charge: Identifier
    shipment: Identifier
    aliases: dict[str, str] = Field(default_factory=dict)


class Matching(Model):
    keys: list[MatchKey] = Field(min_length=1)
    cardinality: Literal["one", "group"] = "one"
    explicit: dict[Identifier, list[Identifier]] = Field(default_factory=dict)
    duplicate_fields: list[Identifier] = Field(default_factory=list)


class Agreement(Model):
    id: Identifier
    name: str
    carrier: Identifier
    currency: Currency
    date_field: Identifier
    scale: int = Field(ge=0, le=8)
    rounding: Rounding
    tolerance_absolute: MoneyText
    tolerance_relative: MoneyText
    matching: Matching
    versions: list[Version] = Field(min_length=1, max_length=200)
    detect_missing: bool = False

    @field_validator("tolerance_absolute", "tolerance_relative")
    @classmethod
    def tolerance(cls, value):
        if number(value) < 0:
            raise ValueError("La tolerancia no puede ser negativa.")
        return decimal_text(number(value))

    @model_validator(mode="after")
    def unique_versions(self):
        if len({v.id for v in self.versions}) != len(self.versions):
            raise ValueError("Hay identificadores de versión repetidos.")
        return self


class DataIssue(Model):
    category: Literal["file", "mapping", "row", "warning", "coverage"]
    message: str
    document: str | None = None
    row: int | None = None
    field: str | None = None
    raw: str | None = None


class Dataset(Model):
    schema_version: Literal[1] = 1
    label: str
    shipments: list[Shipment]
    charges: list[Charge]
    agreements: list[Agreement]
    evidence: list[Evidence] = Field(default_factory=list)
    issues: list[DataIssue] = Field(default_factory=list)
    mappings: list[dict] = Field(default_factory=list)
    documents: dict[str, str] = Field(default_factory=dict)
    # Missing-charge checks require an explicit agreement-to-operation scope.
    coverage: dict[Identifier, list[Identifier]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique_ids(self):
        for field in ("shipments", "charges", "agreements", "evidence"):
            values = getattr(self, field)
            if len({item.id for item in values}) != len(values):
                raise ValueError(f"Identificadores repetidos en {field}; corregir el origen o el mapping.")
        shipment_ids = {s.id for s in self.shipments}
        charge_ids = {c.id for c in self.charges}
        for evidence in self.evidence:
            if not set(evidence.shipment_ids) <= shipment_ids or not set(evidence.charge_ids) <= charge_ids:
                raise ValueError("La evidencia referencia operaciones o cargos inexistentes.")
            if not evidence.shipment_ids and not evidence.charge_ids:
                raise ValueError("La evidencia debe vincularse a una operación o cargo.")
        agreements = {a.id for a in self.agreements}
        carrier_by_agreement = {a.id: a.carrier for a in self.agreements}
        carrier_by_shipment = {s.id: s.carrier for s in self.shipments}
        for agreement, ids in self.coverage.items():
            if agreement not in agreements or not set(ids) <= shipment_ids:
                raise ValueError("El alcance de cobertura contiene referencias inexistentes.")
            if len(set(ids)) != len(ids) or any(
                carrier_by_shipment[sid] != carrier_by_agreement[agreement] for sid in ids
            ):
                raise ValueError(
                    "El alcance de cobertura contiene operaciones repetidas o de otro transportista."
                )
        return self


class Trace(Model):
    op: str
    output: str | bool | None = None
    details: dict = Field(default_factory=dict)
    children: list["Trace"] = Field(default_factory=list)


class Finding(Model):
    id: str
    status: Status
    agreement: str
    version: str | None = None
    rule: str | None = None
    concept: str
    currency: str
    shipment_ids: list[str]
    charge_ids: list[str]
    actual: str
    expected: str | None = None
    difference: str | None = None
    confirmed_difference: str = "0"
    reasons: list[str]
    evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    trace: list[Trace] = Field(default_factory=list)


class AuditResult(Model):
    engine_version: str
    schema_version: Literal[1] = 1
    semantic_hash: str
    findings: list[Finding]
    summary: dict
    issues: list[DataIssue]


class Decision(Model):
    finding_id: Identifier
    action: Literal["APPROVED", "REJECTED", "INFORMATION_REQUESTED", "EXCEPTION_ACCEPTED", "IGNORED"]
    actor: Identifier
    note: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=10000)]
    evidence_ids: list[Identifier] = Field(default_factory=list)
    known_to_client: bool | None = None
    review_minutes: int | None = Field(default=None, ge=0, le=100000)
