from typing import List

from .pattern_calculator_class import PatternCalcltor

pattern_calcltor_classes: List[type[PatternCalcltor]] = [PatternCalcltor_subclass
                                                         for PatternCalcltor_subclass in
                                                         PatternCalcltor.__subclasses__()
                                                         if PatternCalcltor_subclass.name]
__all__ = [pattern_calcltor_classes]
