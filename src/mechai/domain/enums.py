"""Automotive domain enumerations.

These enums categorize domain concepts across vehicles, powertrains,
procedures, diagnostics, warnings, and technical documentation.
"""

from __future__ import annotations

from enum import StrEnum


class WarningSeverity(StrEnum):
    """Severity classification for safety warnings."""

    DANGER = "danger"
    WARNING = "warning"
    CAUTION = "caution"
    NOTE = "note"
    NOTICE = "notice"


class HazardType(StrEnum):
    """Physical hazard types encountered in automotive service."""

    HIGH_VOLTAGE = "high_voltage"
    CHEMICAL = "chemical"
    MECHANICAL = "mechanical"
    PINCH_POINT = "pinch_point"
    THERMAL = "thermal"
    EYE_HAZARD = "eye_hazard"
    FIRE = "fire"
    EXPLOSION = "explosion"
    PRESSURIZED_FLUID = "pressurized_fluid"
    GENERAL = "general"


class DriveType(StrEnum):
    """Vehicle drivetrain layout."""

    FWD = "fwd"
    RWD = "rwd"
    AWD = "awd"
    FOUR_WD = "4wd"


class FuelType(StrEnum):
    """Engine fuel and propulsion energy source."""

    GASOLINE = "gasoline"
    DIESEL = "diesel"
    HYBRID_HEV = "hybrid_hev"
    PLUG_IN_HYBRID_PHEV = "plug_in_hybrid_phev"
    BEV_ELECTRIC = "bev_electric"
    HYDROGEN_FCEV = "hydrogen_fcev"
    FLEX_FUEL = "flex_fuel"
    CNG = "cng"


class AspirationType(StrEnum):
    """Internal combustion engine air intake aspiration."""

    NATURALLY_ASPIRATED = "naturally_aspirated"
    TURBOCHARGED = "turbocharged"
    TWIN_TURBOCHARGED = "twin_turbocharged"
    SUPERCHARGED = "supercharged"
    TWINCHARGED = "twincharged"


class TransmissionType(StrEnum):
    """Transmission architecture."""

    MANUAL = "manual"
    AUTOMATIC = "automatic"
    DUAL_CLUTCH = "dual_clutch"
    CVT = "cvt"
    AUTOMATED_MANUAL = "automated_manual"
    SINGLE_SPEED_DIRECT = "single_speed_direct"


class TorqueUnit(StrEnum):
    """Measurement units for torque specifications."""

    NM = "N.m"
    FT_LB = "ft-lb"
    IN_LB = "in-lb"
    KGF_M = "kgf.m"
    KGF_CM = "kgf.cm"


class FastenerCondition(StrEnum):
    """Required condition and thread preparation for fastener torque tightening."""

    DRY = "dry"
    OIL_LUBRICATED = "oil_lubricated"
    THREADLOCKER_BLUE = "threadlocker_blue"
    THREADLOCKER_RED = "threadlocker_red"
    ANTI_SEIZE = "anti_seize"
    SEALANT = "sealant"


class ProcedureType(StrEnum):
    """Category of service or repair procedure."""

    REMOVAL = "removal"
    INSTALLATION = "installation"
    REPLACEMENT = "replacement"
    DISASSEMBLY = "disassembly"
    ASSEMBLY = "assembly"
    INSPECTION = "inspection"
    ADJUSTMENT = "adjustment"
    BLEEDING = "bleeding"
    CALIBRATION = "calibration"
    DIAGNOSTIC = "diagnostic"
    GENERAL = "general"


class ToolCategory(StrEnum):
    """Classification of automotive service tools."""

    HAND_TOOL = "hand_tool"
    POWER_TOOL = "power_tool"
    SPECIAL_SERVICE_TOOL_SST = "special_service_tool_sst"
    MEASURING_INSTRUMENT = "measuring_instrument"
    DIAGNOSTIC_SCANNER = "diagnostic_scanner"
    SAFETY_EQUIPMENT = "safety_equipment"
    LIFTING_RIGGING = "lifting_rigging"
    CHEMICAL_SUPPLY = "chemical_supply"
    GENERAL = "general"


class DtcCategory(StrEnum):
    """Standard OBD-II diagnostic trouble code categories."""

    POWERTRAIN_P = "powertrain_p"
    CHASSIS_C = "chassis_c"
    BODY_B = "body_b"
    NETWORK_U = "network_u"


class SymptomCategory(StrEnum):
    """Categories of observable vehicle symptoms."""

    NOISE = "noise"
    VIBRATION = "vibration"
    FLUID_LEAK = "fluid_leak"
    ODOR = "odor"
    DRIVEABILITY = "driveability"
    ELECTRICAL_MALFUNCTION = "electrical_malfunction"
    WARNING_LIGHT_MIL = "warning_light_mil"
    VISUAL_FAULT = "visual_fault"
    OVERHEATING = "overheating"
    STARTING_CHARGING = "starting_charging"


class DocumentType(StrEnum):
    """Type of automotive technical documentation."""

    WORKSHOP_MANUAL = "workshop_manual"
    SERVICE_MANUAL = "service_manual"
    TSB = "tsb"
    WIRING_DIAGRAM = "wiring_diagram"
    SPECIFICATION_MANUAL = "specification_manual"
    PARTS_CATALOG = "parts_catalog"
    OWNERS_MANUAL = "owners_manual"
    OTHER = "other"


class InspectionOutcome(StrEnum):
    """Result of an inspection or diagnostic test step."""

    PASS = "pass"  # noqa: S105
    FAIL = "fail"
    MARGINAL = "marginal"
    NOT_TESTED = "not_tested"


class DifficultyLevel(StrEnum):
    """Skill level required for a repair or procedure."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER_TECHNICIAN = "master_technician"


class DiagramType(StrEnum):
    """Classification of technical figures and diagrams."""

    EXPLODED_VIEW = "exploded_view"
    WIRING_DIAGRAM = "wiring_diagram"
    HYDRAULIC_SCHEMATIC = "hydraulic_schematic"
    COMPONENT_LOCATION = "component_location"
    TOOL_SETUP = "tool_setup"
    GRAPH_OR_CHART = "graph_or_chart"
    PHOTO = "photo"
    OTHER = "other"


class TableType(StrEnum):
    """Classification of technical tables."""

    SPECIFICATIONS = "specifications"
    TROUBLESHOOTING = "troubleshooting"
    DIAGNOSTIC_TREE = "diagnostic_tree"
    TORQUE_MATRIX = "torque_matrix"
    FLUID_CAPACITIES = "fluid_capacities"
    PINOUT = "pinout"
    GENERAL = "general"
