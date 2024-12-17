from .arbitrary_geometry.digitization.project import DigitizationProject
from .arbitrary_geometry.footprint.project import FootprintProject
from .arbitrary_geometry.footprint.tutorial import FootprintTutorial
from .media_classification.project import MediaClassificationProject
from .street.project import StreetProject
from .street.tutorial import StreetTutorial
from .tile_map_service.change_detection.project import ChangeDetectionProject
from .tile_map_service.change_detection.tutorial import ChangeDetectionTutorial
from .tile_map_service.classification.project import ClassificationProject
from .tile_map_service.classification.tutorial import ClassificationTutorial
from .tile_map_service.completeness.project import CompletenessProject
from .tile_map_service.completeness.tutorial import CompletenessTutorial

__all__ = [
    "ClassificationProject",
    "ChangeDetectionProject",
    "CompletenessProject",
    "ClassificationTutorial",
    "ChangeDetectionTutorial",
    "CompletenessTutorial",
    "MediaClassificationProject",
    "FootprintProject",
    "FootprintTutorial",
    "DigitizationProject",
    "StreetProject",
    "StreetTutorial",
]
