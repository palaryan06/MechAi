"""Unit tests for automotive domain entities and value objects."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mechai.domain import (
    AspirationType,
    Component,
    DiagnosticCode,
    DiagramType,
    DifficultyLevel,
    DocumentSection,
    DocumentType,
    DomainProvenance,
    DriveType,
    DtcCategory,
    Engine,
    FastenerCondition,
    Figure,
    FuelType,
    HazardType,
    Inspection,
    InspectionOutcome,
    Manual,
    PartNumber,
    Procedure,
    ProcedureStep,
    ProcedureType,
    Repair,
    Symptom,
    SymptomCategory,
    System,
    Table,
    TableType,
    Tool,
    ToolCategory,
    TorqueSpecification,
    TorqueUnit,
    Transmission,
    TransmissionType,
    Vehicle,
    Warning,
    WarningSeverity,
)

# ---------------------------------------------------------------------------
# Vehicle, Engine, Transmission Tests
# ---------------------------------------------------------------------------


def test_engine_creation_and_immutability() -> None:
    """Verify Engine instantiation and immutability."""
    provenance = DomainProvenance(
        manual_id="man_2jz", section_id="sec_specs", page_number=12, confidence=1.0
    )
    engine = Engine(
        engine_id="eng_toyota_2jz_gte",
        code="2JZ-GTE",
        name="Toyota 3.0L Inline-6 Twin-Turbo",
        displacement_liters=3.0,
        displacement_cc=2997,
        cylinder_count=6,
        configuration="Inline-6",
        fuel_type=FuelType.GASOLINE,
        aspiration=AspirationType.TWIN_TURBOCHARGED,
        valvetrain="DOHC 24V VVT-i",
        horsepower=320.0,
        torque_nm=440.0,
        oil_capacity_liters=5.4,
        oil_viscosity="5W-30",
        provenance=provenance,
    )
    assert engine.code == "2JZ-GTE"
    assert engine.displacement_liters == 3.0
    assert engine.aspiration == AspirationType.TWIN_TURBOCHARGED

    with pytest.raises(ValidationError):
        # Immutable check
        setattr(engine, "horsepower", 400.0)


def test_transmission_creation() -> None:
    """Verify Transmission instantiation and serialization."""
    trans = Transmission(
        transmission_id="trans_v160",
        code="V160",
        name="Getrag 6-Speed Manual",
        transmission_type=TransmissionType.MANUAL,
        gear_count=6,
        drive_type=DriveType.RWD,
        fluid_type="Toyota Type T-IV",
        fluid_capacity_liters=1.8,
    )
    assert trans.gear_count == 6
    assert trans.transmission_type == TransmissionType.MANUAL

    json_str = trans.model_dump_json()
    loaded = Transmission.model_validate_json(json_str)
    assert loaded == trans


def test_vehicle_creation_and_validation() -> None:
    """Verify Vehicle creation and year range validation."""
    engine = Engine(engine_id="eng_2jz", code="2JZ-GTE")
    trans = Transmission(transmission_id="trans_v160", code="V160")

    vehicle = Vehicle(
        vehicle_id="veh_toyota_supra_a80",
        make="Toyota",
        model="Supra",
        year_start=1993,
        year_end=2002,
        generation="A80",
        trim="Twin Turbo",
        drive_type=DriveType.RWD,
        engines=(engine,),
        transmissions=(trans,),
        body_styles=("Coupe", "Targa"),
    )
    assert vehicle.make == "Toyota"
    assert vehicle.year_end == 2002
    assert len(vehicle.engines) == 1

    # Valid single year (year_end is None)
    v1 = Vehicle(vehicle_id="veh_1", make="Toyota", model="Supra", year_start=1993)
    assert v1.year_end is None

    # Invalid year range (year_end < year_start)
    with pytest.raises(ValidationError) as exc_info:
        Vehicle(
            vehicle_id="veh_invalid",
            make="Toyota",
            model="Supra",
            year_start=2000,
            year_end=1995,
        )
    assert "year_end (1995) cannot be earlier than year_start (2000)" in str(exc_info.value)


# ---------------------------------------------------------------------------
# System, Component, PartNumber Tests
# ---------------------------------------------------------------------------


def test_part_number_and_supersessions() -> None:
    """Verify PartNumber model attributes and serialization."""
    part = PartNumber(
        part_number_id="pn_04465_14080",
        part_number="04465-14080",
        manufacturer="Toyota",
        description="Front Brake Pad Set",
        superseded_by="04465-14081",
        supersedes=("04465-14030",),
        interchanges=("D707-7578", "EBC-DP31044C"),
        is_oem=True,
    )
    assert part.part_number == "04465-14080"
    assert part.superseded_by == "04465-14081"
    assert len(part.interchanges) == 2


def test_component_and_system_hierarchy() -> None:
    """Verify Component and System creation with relationships."""
    part = PartNumber(part_number_id="pn_caliper", part_number="47730-14260")
    component = Component(
        component_id="comp_front_brake_caliper",
        name="Front Right Brake Caliper Assembly",
        system_id="sys_braking",
        subsystem_id="sys_disc_brakes",
        part_numbers=(part,),
        location="Front right wheel knuckle assembly",
        material="Cast Iron / Aluminum",
        operating_parameters={"operating_pressure_psi": "1500"},
        failure_modes=("Piston seizure", "Fluid seal deterioration"),
    )
    assert component.name == "Front Right Brake Caliper Assembly"
    assert len(component.part_numbers) == 1
    assert "Piston seizure" in component.failure_modes

    system = System(
        system_id="sys_braking",
        name="Braking System",
        code="BRK",
        subsystems=("sys_disc_brakes", "sys_abs"),
        primary_components=("comp_front_brake_caliper", "comp_brake_master_cylinder"),
    )
    assert system.code == "BRK"
    assert len(system.subsystems) == 2


# ---------------------------------------------------------------------------
# Procedure, Step, Tool, Torque, Warning Tests
# ---------------------------------------------------------------------------


def test_torque_specification_validation() -> None:
    """Verify TorqueSpecification validation and limit checks."""
    spec = TorqueSpecification(
        torque_id="tq_caliper_bolt",
        fastener="Front Brake Caliper Mounting Bolt",
        nominal_value=108.0,
        min_value=100.0,
        max_value=115.0,
        unit=TorqueUnit.NM,
        angle_degrees=None,
        is_yield_fastener=False,
        condition=FastenerCondition.DRY,
    )
    assert spec.nominal_value == 108.0
    assert spec.unit == TorqueUnit.NM

    # Valid partial limit bounds
    s1 = TorqueSpecification(torque_id="tq_1", fastener="Bolt", min_value=10.0)
    assert s1.max_value is None
    s2 = TorqueSpecification(torque_id="tq_2", fastener="Bolt", max_value=20.0)
    assert s2.min_value is None

    # Invalid limits: max_value < min_value
    with pytest.raises(ValidationError) as exc_info:
        TorqueSpecification(
            torque_id="tq_invalid",
            fastener="Bolt",
            min_value=120.0,
            max_value=90.0,
        )
    assert "max_value (90.0) cannot be less than min_value (120.0)" in str(exc_info.value)


def test_warning_entity() -> None:
    """Verify Warning safety entity."""
    warning = Warning(
        warning_id="warn_high_voltage",
        severity=WarningSeverity.DANGER,
        message="High voltage components present. Disconnect service plug before servicing.",
        hazard_type=HazardType.HIGH_VOLTAGE,
        required_ppe=("Class 0 1000V Insulated Gloves", "Face Shield"),
        safety_precautions=("Wait 10 minutes for capacitor discharge",),
    )
    assert warning.severity == WarningSeverity.DANGER
    assert warning.hazard_type == HazardType.HIGH_VOLTAGE
    assert len(warning.required_ppe) == 2


def test_tool_entity() -> None:
    """Verify Tool entity."""
    tool = Tool(
        tool_id="tool_sst_crank_holder",
        name="Crankshaft Pulley Holding Tool",
        category=ToolCategory.SPECIAL_SERVICE_TOOL_SST,
        sst_number="09213-70011",
        specification="Universal sprocket holder",
    )
    assert tool.category == ToolCategory.SPECIAL_SERVICE_TOOL_SST
    assert tool.sst_number == "09213-70011"


def test_procedure_and_step_assembly() -> None:
    """Verify complete Procedure with steps, tools, and warnings."""
    tool = Tool(tool_id="tool_14mm", name="14mm Socket", size=14.0, size_unit="mm")
    torque = TorqueSpecification(
        torque_id="tq_14mm",
        fastener="Slide Pin Bolt",
        nominal_value=34.0,
        unit=TorqueUnit.NM,
    )
    warning = Warning(
        warning_id="warn_brake_dust",
        severity=WarningSeverity.CAUTION,
        message="Do not use compressed air to clean brake assemblies.",
        hazard_type=HazardType.CHEMICAL,
    )

    step1 = ProcedureStep(
        step_number=1,
        instruction="Remove the caliper lower slide pin bolt using a 14mm socket.",
        tools=(tool,),
        torques=(torque,),
        warnings=(warning,),
    )

    procedure = Procedure(
        procedure_id="proc_brake_pad_replace",
        title="Front Brake Pad Replacement",
        procedure_type=ProcedureType.REPLACEMENT,
        system_id="sys_braking",
        component_ids=("comp_front_brake_caliper",),
        steps=(step1,),
        required_tools=(tool,),
        safety_warnings=(warning,),
        estimated_minutes=45,
    )

    assert procedure.procedure_type == ProcedureType.REPLACEMENT
    assert len(procedure.steps) == 1
    assert procedure.steps[0].tools[0].name == "14mm Socket"


# ---------------------------------------------------------------------------
# Diagnostics: DTC, Symptom, Inspection, Repair Tests
# ---------------------------------------------------------------------------


def test_diagnostic_code_normalization() -> None:
    """Verify DiagnosticCode normalizes code to uppercase."""
    dtc = DiagnosticCode(
        code_id="dtc_p0301",
        code="p0301",
        category=DtcCategory.POWERTRAIN_P,
        description="Cylinder 1 Misfire Detected",
        technical_meaning="ECM detected deceleration during firing stroke.",
        mil_illuminated=True,
        affected_component_ids=("comp_spark_plug_1", "comp_ignition_coil_1"),
        possible_causes=("Faulty spark plug", "Defective coil", "Low compression"),
        associated_symptoms=("Engine stumble under load", "Flashing check engine light"),
    )
    assert dtc.code == "P0301"
    assert dtc.category == DtcCategory.POWERTRAIN_P
    assert len(dtc.possible_causes) == 3

    # Already uppercase
    dtc_upper = DiagnosticCode(code_id="dtc_2", code="P0420", description="Catalyst")
    assert dtc_upper.code == "P0420"


def test_symptom_model() -> None:
    """Verify Symptom domain model."""
    symptom = Symptom(
        symptom_id="sym_brake_squeal",
        description="High pitched metallic squealing noise when applying brakes at low speed",
        category=SymptomCategory.NOISE,
        system_id="sys_braking",
        trigger_conditions=("Light brake pedal application", "Vehicle moving forward < 20 mph"),
        probable_causes=("Worn brake pads contacting wear indicator", "Glazed rotor"),
        suspected_components=("comp_brake_pad", "comp_brake_rotor"),
    )
    assert symptom.category == SymptomCategory.NOISE
    assert len(symptom.trigger_conditions) == 2


def test_inspection_limits_validation() -> None:
    """Verify Inspection validation rules."""
    insp = Inspection(
        inspection_id="insp_rotor_thickness",
        point_name="Front Brake Disc Thickness",
        description="Measure disc thickness at 8 points using a micrometer.",
        nominal_spec="32.0 mm",
        min_tolerance=30.0,
        max_tolerance=32.5,
        tolerance_unit="mm",
        outcome=InspectionOutcome.PASS,
        observed_value=31.2,
    )
    assert insp.outcome == InspectionOutcome.PASS
    assert insp.observed_value == 31.2

    # Valid partial tolerances
    i1 = Inspection(inspection_id="i1", point_name="Rotor", description="d", min_tolerance=10.0)
    assert i1.max_tolerance is None
    i2 = Inspection(inspection_id="i2", point_name="Rotor", description="d", max_tolerance=20.0)
    assert i2.min_tolerance is None

    # Invalid tolerance range (max < min)
    with pytest.raises(ValidationError) as exc_info:
        Inspection(
            inspection_id="insp_invalid",
            point_name="Rotor",
            description="Measure",
            min_tolerance=30.0,
            max_tolerance=28.0,
        )
    assert "max_tolerance (28.0) cannot be less than min_tolerance (30.0)" in str(exc_info.value)


def test_repair_model() -> None:
    """Verify Repair entity."""
    repair = Repair(
        repair_id="rep_front_brake_service",
        title="Replace Front Brake Pads and Resurface Rotors",
        description="Replace worn friction materials and machine or replace brake discs.",
        target_dtcs=(),
        target_symptoms=("sym_brake_squeal",),
        component_ids=("comp_brake_pad", "comp_brake_rotor"),
        procedure_ids=("proc_pad_replace", "proc_rotor_resurface"),
        estimated_labor_hours=1.5,
        difficulty=DifficultyLevel.INTERMEDIATE,
    )
    assert repair.difficulty == DifficultyLevel.INTERMEDIATE
    assert repair.estimated_labor_hours == 1.5


# ---------------------------------------------------------------------------
# Technical Documentation: Manual, Section, Figure, Table Tests
# ---------------------------------------------------------------------------


def test_document_section_page_validation() -> None:
    """Verify DocumentSection hierarchy and page range validation."""
    section = DocumentSection(
        section_id="sec_br_pad",
        section_number="BR-14",
        title="Front Disc Brake Pad Replacement",
        level=2,
        page_start=45,
        page_end=48,
    )
    assert section.level == 2
    assert section.page_end == 48

    # Valid partial page ranges
    s1 = DocumentSection(section_id="s1", title="Title", page_start=10)
    assert s1.page_end is None
    s2 = DocumentSection(section_id="s2", title="Title", page_end=20)
    assert s2.page_start is None

    # Invalid page range: page_end < page_start
    with pytest.raises(ValidationError) as exc_info:
        DocumentSection(
            section_id="sec_invalid",
            title="Invalid Range",
            page_start=50,
            page_end=40,
        )
    assert "page_end (40) cannot be less than page_start (50)" in str(exc_info.value)


def test_figure_and_table_entities() -> None:
    """Verify Figure and Table entity structure."""
    fig = Figure(
        figure_id="fig_caliper_exploded",
        label="Fig. 14-2",
        caption="Exploded view of front brake caliper components",
        diagram_type=DiagramType.EXPLODED_VIEW,
        referenced_components=("comp_caliper_body", "comp_piston_seal", "comp_dust_boot"),
        page_number=46,
    )
    assert fig.diagram_type == DiagramType.EXPLODED_VIEW
    assert len(fig.referenced_components) == 3

    tbl = Table(
        table_id="tbl_torque_matrix",
        label="Table BR-1",
        title="Brake System Tightening Specifications",
        table_type=TableType.TORQUE_MATRIX,
        headers=("Fastener", "Torque (N.m)", "Torque (ft-lb)"),
        rows=(
            ("Caliper Mounting Bolt", "108", "80"),
            ("Slide Pin Bolt", "34", "25"),
        ),
        page_number=48,
    )
    assert tbl.table_type == TableType.TORQUE_MATRIX
    assert len(tbl.rows) == 2


def test_manual_aggregate() -> None:
    """Verify Manual aggregate entity."""
    section = DocumentSection(section_id="sec_1", title="Brakes", page_start=1, page_end=50)
    fig = Figure(figure_id="fig_1", label="Fig 1", page_number=10)
    tbl = Table(table_id="tbl_1", label="Table 1", page_number=12)

    manual = Manual(
        manual_id="man_supra_1994_rm390u",
        title="1994 Toyota Supra Repair Manual Volume 1",
        document_type=DocumentType.WORKSHOP_MANUAL,
        publisher="Toyota Motor Corporation",
        publication_year=1994,
        document_code="RM390U",
        target_vehicles=("veh_toyota_supra_a80",),
        target_engines=("eng_toyota_2jz_gte", "eng_toyota_2jz_ge"),
        sections=(section,),
        figures=(fig,),
        tables=(tbl,),
        total_pages=980,
    )
    assert manual.publication_year == 1994
    assert manual.total_pages == 980
    assert len(manual.target_engines) == 2

    # Roundtrip serialization
    json_data = manual.model_dump_json()
    loaded_manual = Manual.model_validate_json(json_data)
    assert loaded_manual == manual
