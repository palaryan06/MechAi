"""Unit tests for safety engine components."""

from mechai.contracts.provenance import SourceRef
from mechai.contracts.safety import HazardCategory, SafetySeverity
from mechai.safety.action_extractor import ActionExtractor
from mechai.safety.condition_extractor import ConditionExtractor
from mechai.safety.config import SafetyEngineConfig
from mechai.safety.consequence_extractor import ConsequenceExtractor
from mechai.safety.hazard_extractor import HazardExtractor
from mechai.safety.severity_classifier import SeverityClassifier


class TestSafetyUnit:
    """Unit tests for safety component extraction."""

    def test_severity_classifier(self) -> None:
        classifier = SeverityClassifier()
        
        sev, label = classifier.classify_severity("WARNING: Hot surface")
        assert sev == SafetySeverity.WARNING
        assert label == "WARNING"
        
        sev, label = classifier.classify_severity("CAUTION: Battery fluid")
        assert sev == SafetySeverity.CAUTION
        assert label == "CAUTION"
        
        sev, label = classifier.classify_severity("Just a normal sentence.")
        assert sev == SafetySeverity.UNKNOWN_ADMONITION

    def test_hazard_extractor(self) -> None:
        extractor = HazardExtractor()
        
        cat, conf = extractor.extract_hazard("Risk of explosion.")
        assert cat == HazardCategory.EXPLOSION
        
        cat, conf = extractor.extract_hazard("High voltage present.")
        assert cat == HazardCategory.HIGH_VOLTAGE
        
        cat, conf = extractor.extract_hazard("Avoid contact with battery acid.")
        assert cat == HazardCategory.BATTERY

    def test_condition_extractor(self) -> None:
        extractor = ConditionExtractor()
        prov = SourceRef(page_number=1)
        
        conds = extractor.extract_conditions("When engine is hot, wait.", prov)
        assert len(conds) == 1
        assert "When engine is hot" in conds[0].text

    def test_consequence_extractor(self) -> None:
        extractor = ConsequenceExtractor()
        prov = SourceRef(page_number=1)
        
        cons = extractor.extract_consequences("This may result in severe burns.", prov)
        assert len(cons) == 1
        assert "may result in severe burns" in cons[0].text

    def test_action_extractor(self) -> None:
        extractor = ActionExtractor()
        prov = SourceRef(page_number=1)
        
        acts = extractor.extract_actions("Always wear safety glasses. Do not touch.", prov)
        assert len(acts) == 2
        assert acts[0].text == "Always wear safety glasses"
        assert not acts[0].is_restriction
        assert acts[1].text == "Do not touch"
        assert acts[1].is_restriction
        
        reqs = extractor.extract_requirements("Always wear safety glasses.", prov)
        assert len(reqs) == 1
        assert reqs[0].equipment == "Safety Glasses"
