# TODO: Import all other project type classes
from .media_classification.project import MediaClassificationProject
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
]
