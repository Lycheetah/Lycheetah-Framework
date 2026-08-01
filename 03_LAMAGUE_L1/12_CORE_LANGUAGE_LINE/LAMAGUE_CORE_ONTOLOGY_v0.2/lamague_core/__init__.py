from .core import parse_source, run_source
from .errors import LamagueError, LexError, ParseError, SemanticError
from .lexer import Lexer
from .parser import Parser
from .semantics import Runtime
from .normalizer import normalize, canonical, equivalent, semantic_hash
from .graph import semantic_graph
from .ontology import (
    CoreType,
    ATOM_ONTOLOGY,
    DERIVED_ONTOLOGY,
    OPERATOR_SIGNATURES,
    ontology_export,
    ontology_record,
    is_subtype,
    parse_type,
)

__version__ = "0.2.0"
