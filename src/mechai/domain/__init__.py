"""MechAI automotive domain layer.

Pure business entities representing vehicles, powertrains, systems, components,
procedures, diagnostics, and technical documentation.
"""

from __future__ import annotations

from mechai.domain.base import DomainModel, DomainProvenance
from mechai.domain.diagnostics import DiagnosticCode, Inspection, Repair, Symptom
from mechai.domain.document import DocumentSection, Figure, Manual, Table
from mechai.domain.enums import (
    AspirationType,
    DiagramType,
    DifficultyLevel,
    DocumentType,
    DriveType,
    DtcCategory,
    FastenerCondition,
    FuelType,
    HazardType,
    InspectionOutcome,
    ProcedureType,
    SymptomCategory,
    TableType,
    ToolCategory,
    TorqueUnit,
    TransmissionType,
    WarningSeverity,
)
from mechai.domain.procedure import (
    Procedure,
    ProcedureStep,
    Tool,
    TorqueSpecification,
    Warning,
)
from mechai.domain.system import Component, PartNumber, System
from mechai.domain.vehicle import Engine, Transmission, Vehicle

__all__ = [
    "AspirationType",
    "Component",
    "DiagnosticCode",
    "DiagramType",
    "DifficultyLevel",
    "DocumentSection",
    "DocumentType",
    "DomainModel",
    "DomainProvenance",
    "DriveType",
    "DtcCategory",
    "Engine",
    "FastenerCondition",
    "Figure",
    "FuelType",
    "HazardType",
    "Inspection",
    "InspectionOutcome",
    "Manual",
    "PartNumber",
    "Procedure",
    "ProcedureStep",
    "ProcedureType",
    "Repair",
    "Symptom",
    "SymptomCategory",
    "System",
    "Table",
    "TableType",
    "Tool",
    "ToolCategory",
    "TorqueSpecification",
    "TorqueUnit",
    "Transmission",
    "TransmissionType",
    "Vehicle",
    "Warning",
    "WarningSeverity",
]
