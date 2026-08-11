"""Validation tests against real workshop manuals (Suzuki F8D and Maruti Suzuki K10B)."""

from mechai.contracts.layout import RegionType, PageMargins
from mechai.contracts.ordering import OrderedLayoutCIR, OrderedLayoutRegion, OrderedPageCIR, ReadingOrderGraph, ReadingFlowType
from mechai.contracts.provenance import BoundingBox, SourceRef
from mechai.contracts.safety import HazardCategory, SafetySeverity
from mechai.safety.factory import SafetyEngineFactory


class TestSafetyRealManuals:
    """Validation against real manual examples."""

    def test_suzuki_f8d_radiator_warning(self) -> None:
        """Test against F8D manual radiator warning."""
        bbox = BoundingBox(left=0, top=0, right=100, bottom=50)
        
        region = OrderedLayoutRegion(
            id="r1",
            region_type=RegionType.WARNING_BOX,
            text="WARNING: Allow engine to cool before removing the radiator cap. Hot coolant may result in severe burns.",
            page_number=12,
            bbox=bbox,
            reading_order_index=1,
            confidence=1.0,
            provenance=SourceRef(page_number=12),
        )
        
        
        page = OrderedPageCIR(
            page_number=12,
            ordered_regions=(region,),
            width=800,
            height=1000,
            margins=PageMargins(top=0, right=0, bottom=0, left=0),
            reading_order_graph=ReadingOrderGraph(),
            sequence_confidence=1.0,
            reading_flow_type=ReadingFlowType.SINGLE_COLUMN,
        )
        cir = OrderedLayoutCIR(
            document_id="f8d",
            total_pages=1,
            pages=(page,),
            global_graph=ReadingOrderGraph(),
            provenance=SourceRef(page_number=12),
        )
        
        engine = SafetyEngineFactory.create_engine()
        safety_set = engine.reconstruct_safety(cir)
        
        assert safety_set.total_admonitions == 1
        adm = safety_set.admonitions[0]
        
        assert adm.severity == SafetySeverity.WARNING
        assert adm.hazard_category == HazardCategory.COOLANT
        assert len(adm.actions) == 1
        assert "Allow engine to cool" in adm.actions[0].text
        assert len(adm.conditions) == 1
        assert "before removing the radiator cap" in adm.conditions[0].text
        assert len(adm.consequences) == 1
        assert "may result in severe burns" in adm.consequences[0].text

    def test_k10b_battery_caution(self) -> None:
        """Test against K10B manual battery caution."""
        bbox = BoundingBox(left=0, top=0, right=100, bottom=50)
        
        region = OrderedLayoutRegion(
            id="r1",
            region_type=RegionType.NOTE_BOX,
            text="CAUTION: Do not disconnect battery while engine is running. This will lead to electrical system damage.",
            page_number=56,
            bbox=bbox,
            reading_order_index=1,
            confidence=1.0,
            provenance=SourceRef(page_number=56),
        )
        
        page = OrderedPageCIR(
            page_number=56,
            ordered_regions=(region,),
            width=800,
            height=1000,
            margins=PageMargins(top=0, right=0, bottom=0, left=0),
            reading_order_graph=ReadingOrderGraph(),
            sequence_confidence=1.0,
            reading_flow_type=ReadingFlowType.SINGLE_COLUMN,
        )
        cir = OrderedLayoutCIR(
            document_id="k10b",
            total_pages=1,
            pages=(page,),
            global_graph=ReadingOrderGraph(),
            provenance=SourceRef(page_number=56),
        )
        
        engine = SafetyEngineFactory.create_engine()
        safety_set = engine.reconstruct_safety(cir)
        
        assert safety_set.total_admonitions == 1
        adm = safety_set.admonitions[0]
        
        assert adm.severity == SafetySeverity.CAUTION
        assert adm.hazard_category == HazardCategory.ELECTRICAL
        assert len(adm.actions) == 1
        assert adm.actions[0].is_restriction
        assert "Do not disconnect battery" in adm.actions[0].text
        assert len(adm.conditions) == 1
        assert "while engine is running" in adm.conditions[0].text
