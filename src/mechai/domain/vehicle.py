"""Vehicle, Engine, and Transmission domain entities."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field, field_validator

from mechai.domain.base import DomainModel, DomainProvenance
from mechai.domain.enums import AspirationType, DriveType, FuelType, TransmissionType


class Engine(DomainModel):
    """Internal combustion engine or electric powertrain specification.

    Attributes:
        engine_id: Unique domain identifier (e.g., 'eng_toyota_2jz_gte').
        code: Manufacturer engine code (e.g., '2JZ-GTE', 'B58B30O1').
        name: Common name or descriptive title.
        displacement_liters: Displacement in liters (e.g., 3.0).
        displacement_cc: Displacement in cubic centimeters (e.g., 2997).
        cylinder_count: Total number of combustion cylinders.
        configuration: Cylinder arrangement (e.g., 'Inline-6', 'V8', 'Boxer-4').
        fuel_type: Primary fuel source.
        aspiration: Air intake aspiration mechanism.
        valvetrain: Valvetrain configuration (e.g., 'DOHC 24V VVT-i').
        bore_mm: Cylinder bore diameter in millimeters.
        stroke_mm: Piston stroke length in millimeters.
        compression_ratio: Compression ratio string (e.g., '10.5:1').
        horsepower: Rated peak engine power (HP/bhp).
        torque_nm: Rated peak torque in Newton-meters.
        oil_capacity_liters: Total engine oil capacity including filter.
        oil_viscosity: Recommended oil viscosity grade (e.g., '5W-30', '0W-20').
        provenance: Grounding provenance.
    """

    engine_id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    name: str | None = None
    displacement_liters: Annotated[float, Field(gt=0.0)] | None = None
    displacement_cc: Annotated[int, Field(gt=0)] | None = None
    cylinder_count: Annotated[int, Field(gt=0)] | None = None
    configuration: str | None = None
    fuel_type: FuelType = FuelType.GASOLINE
    aspiration: AspirationType = AspirationType.NATURALLY_ASPIRATED
    valvetrain: str | None = None
    bore_mm: Annotated[float, Field(gt=0.0)] | None = None
    stroke_mm: Annotated[float, Field(gt=0.0)] | None = None
    compression_ratio: str | None = None
    horsepower: Annotated[float, Field(gt=0.0)] | None = None
    torque_nm: Annotated[float, Field(gt=0.0)] | None = None
    oil_capacity_liters: Annotated[float, Field(gt=0.0)] | None = None
    oil_viscosity: str | None = None
    provenance: DomainProvenance | None = None


class Transmission(DomainModel):
    """Vehicle transmission/gearbox entity.

    Attributes:
        transmission_id: Unique domain identifier (e.g., 'trans_getrag_v160').
        code: Manufacturer transmission code (e.g., 'V160', 'ZF 8HP70').
        name: Descriptive transmission name.
        transmission_type: Transmission architecture type.
        gear_count: Number of forward gear ratios.
        drive_type: Drive configuration layout.
        fluid_type: Recommended transmission fluid specification.
        fluid_capacity_liters: Transmission fluid capacity in liters.
        provenance: Grounding provenance.
    """

    transmission_id: str = Field(min_length=1)
    code: str = Field(min_length=1)
    name: str | None = None
    transmission_type: TransmissionType = TransmissionType.MANUAL
    gear_count: Annotated[int, Field(ge=1, le=14)] | None = None
    drive_type: DriveType | None = None
    fluid_type: str | None = None
    fluid_capacity_liters: Annotated[float, Field(gt=0.0)] | None = None
    provenance: DomainProvenance | None = None


class Vehicle(DomainModel):
    """Automotive vehicle model and configuration.

    Attributes:
        vehicle_id: Unique domain identifier (e.g., 'veh_toyota_supra_a80').
        make: Vehicle manufacturer brand (e.g., 'Toyota').
        model: Vehicle model name (e.g., 'Supra').
        year_start: First model year of production/application.
        year_end: Final model year of production (None if ongoing or single year).
        generation: Generation or chassis designation (e.g., 'A80', 'MK4').
        trim: Trim or sub-model designation (e.g., 'Turbo', 'RZ').
        vin_pattern: VIN pattern or regular expression for identification.
        drive_type: Default or primary drivetrain configuration.
        engines: Available engine options for this vehicle.
        transmissions: Available transmission options.
        body_styles: Available body style variants (e.g., ('Coupe', 'Targa')).
        provenance: Grounding provenance.
    """

    vehicle_id: str = Field(min_length=1)
    make: str = Field(min_length=1)
    model: str = Field(min_length=1)
    year_start: Annotated[int, Field(ge=1886, le=2100)]
    year_end: Annotated[int, Field(ge=1886, le=2100)] | None = None
    generation: str | None = None
    trim: str | None = None
    vin_pattern: str | None = None
    drive_type: DriveType = DriveType.FWD
    engines: tuple[Engine, ...] = Field(default_factory=tuple)
    transmissions: tuple[Transmission, ...] = Field(default_factory=tuple)
    body_styles: tuple[str, ...] = Field(default_factory=tuple)
    provenance: DomainProvenance | None = None

    @field_validator("year_end")
    @classmethod
    def validate_year_range(cls, v: int | None, info: object) -> int | None:
        """Ensure year_end is greater than or equal to year_start."""
        if v is not None and hasattr(info, "data") and "year_start" in info.data:
            year_start = info.data["year_start"]
            if year_start is not None and v < year_start:
                raise ValueError(f"year_end ({v}) cannot be earlier than year_start ({year_start})")
        return v
