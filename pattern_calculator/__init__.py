from typing import List

from .pattern_calculator_class import PatternCalcltor as _PatternCalcltor

pattern_calcltor_calsses: List[type[_PatternCalcltor]] = _PatternCalcltor.__subclasses__()
__all__ = [pattern_calcltor_calsses]
