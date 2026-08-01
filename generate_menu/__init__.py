"""
Menu Processor — Python package that generates C code for an embedded
LCD1602 menu system from a YAML/JSON menu definition.

Pipeline:
    config → MenuConfig → MenuValidator → MenuFlattener
           → FlatNode / BaseFlatNode → MenuProcessor → MenuGenerator
"""

__version__ = "1.0.0"
