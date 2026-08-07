"""System, Component, and PartNumber domain entities."""

from __future__ import annotations

from pydantic import Field

from mechai.domain.base import DomainModel, DomainProvenance


class PartNumber(DomainModel):
    """Automotive part number and supersession record.

    Attributes:
        part_number_id: Unique domain identifier (e.g., 'pn_toyota_04465_14080').
        part_number: Part number string format (e.g., '04465-14080', '13568-19046').
        manufacturer: OEM or aftermarket manufacturer name (e.g., 'Toyota', 'Denso').
        description: Description of the physical component or assembly.
        superseded_by: Newer part number that replaces this part.
        supersedes: Previous part numbers replaced by this part.
        interchanges: Equivalent/compatible aftermarket part numbers.
        is_oem: Whether this is an Original Equipment Manufacturer part.
        provenance: Grounding provenance.
    """

    part_number_id: str = Field(min_length=1)
    part_number: str = Field(min_length=1)
    manufacturer: str | None = None
    description: str | None = None
    superseded_by: str | None = None
    supersedes: tuple[str, ...] = Field(default_factory=tuple)
    interchanges: tuple[str, ...] = Field(default_factory=tuple)
    is_oem: bool = True
    provenance: DomainProvenance | None = None


class Component(DomainModel):
    """Physical vehicle component or assembly entity.

    Attributes:
        component_id: Unique domain identifier (e.g., 'comp_front_brake_caliper').
        name: Standard automotive component name.
        system_id: Identifier of the vehicle system this component belongs to.
        subsystem_id: Optional sub-system identifier.
        parent_component_id: Identifier of parent assembly if this is a sub-component.
        description: Detailed physical description and functional purpose.
        part_numbers: Known OEM or aftermarket part numbers.
        location: Physical location description within the vehicle.
        material: Construction material (e.g., 'Cast Iron', 'Aluminum').
        operating_parameters: Standard operating specifications (e.g., voltage, pressure).
        failure_modes: Known physical fault conditions or failure mechanisms.
        provenance: Grounding provenance.
    """

    component_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    system_id: str = Field(min_length=1)
    subsystem_id: str | None = None
    parent_component_id: str | None = None
    description: str | None = None
    part_numbers: tuple[PartNumber, ...] = Field(default_factory=tuple)
    location: str | None = None
    material: str | None = None
    operating_parameters: dict[str, str] = Field(default_factory=dict)
    failure_modes: tuple[str, ...] = Field(default_factory=tuple)
    provenance: DomainProvenance | None = None


class System(DomainModel):
    """Major functional vehicle system or subsystem.

    Attributes:
        system_id: Unique domain identifier (e.g., 'sys_braking', 'sys_engine_mechanical').
        name: Human-readable system name (e.g., 'Braking System').
        code: System abbreviation or standard code (e.g., 'BRK', 'ENG').
        description: System functional description and architecture overview.
        parent_system_id: Identifier of parent system if this is a sub-system.
        subsystems: List of subsystem identifiers.
        primary_components: Identifiers of principal components in this system.
        provenance: Grounding provenance.
    """

    system_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    code: str | None = None
    description: str | None = None
    parent_system_id: str | None = None
    subsystems: tuple[str, ...] = Field(default_factory=tuple)
    primary_components: tuple[str, ...] = Field(default_factory=tuple)
    provenance: DomainProvenance | None = None
