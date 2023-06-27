from typing import List
from utilities import find_leaf_subclasses
from .pattern_calculator_class import PatternCalcltor

pattern_calcltor_classes: List[type[PatternCalcltor]] = find_leaf_subclasses(PatternCalcltor)
