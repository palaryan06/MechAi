"""Integration tests for the Automotive Safety Intelligence Engine."""

from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutCIR, OrderedLayoutRegion, OrderedPageCIR
from mechai.contracts.provenance import BoundingBox, SourceRef
from mechai.contracts.safety import HazardCategory, SafetySeverity
from mechai.safety.factory import SafetyEngineFactory


class TestSafetyIntegration:
    """Integration tests for the full safety pipeline."""

    def test_pipeline(self) -> None:
        """Test full safety extraction on mock layout CIR."""
        
        # Mock layout regions
        bbox = BoundingBox(left=0, top=0, right=100, bottom=50)
        prov = SourceRef(page_number=1)
        
        region = OrderedLayoutRegion(
            id="r1",
            region_type=RegionType.WARNING_BOX,
            text="WARNING: High voltage. Do not touch. May result in shock.",
            page_number=1,
            bbox=bbox,
            reading_order_index=1,
            confidence=1.0,
            provenance=prov,
        )
        
        from mechai.contracts.ordering import ReadingOrderGraph, ReadingFlowType
        from mechai.contracts.layout import PageMargins
        
        page = OrderedPageCIR(
            page_number=1,
            ordered_regions=(region,),
            width=800,
            height=1000,
            margins=PageMargins(top=0, right=0, bottom=0, left=0),
            reading_order_graph=ReadingOrderGraph(),
            sequence_confidence=1.0,
            reading_flow_type=ReadingFlowType.SINGLE_COLUMN,
        )
        
        cir = OrderedLayoutCIR(
            document_id="test_doc",
            total_pages=1,
            pages=(page,),
            global_graph=ReadingOrderGraph(),
            provenance=SourceRef(page_number=1),
        )
        
        # Run engine
        engine = SafetyEngineFactory.create_engine()
        safety_set = engine.reconstruct_safety(cir)
        
        assert safety_set.total_admonitions == 1
        adm = safety_set.admonitions[0]
        
        assert adm.severity == SafetySeverity.WARNING
        assert adm.hazard_category == HazardCategory.HIGH_VOLTAGE
        assert len(adm.actions) == 1
        assert adm.actions[0].is_restriction
        assert "Do not touch" in adm.actions[0].text
        assert len(adm.consequences) == 1
