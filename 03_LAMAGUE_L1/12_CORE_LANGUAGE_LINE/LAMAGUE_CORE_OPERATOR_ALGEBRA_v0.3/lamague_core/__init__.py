from .core import parse_source, run_source
from .errors import LamagueError, LexError, ParseError, SemanticError
from .lexer import Lexer
from .parser import Parser
from .semantics import Runtime
from .normalizer import (
    normalize, normalize_with_trace, canonical, equivalent, semantic_hash
)
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

__version__ = "0.3.0"
from .contracts import (
    LawStatus, OPERATOR_CONTRACTS, contract_record, contract_hash,
    law_result, structurally_composable, composition_matrix,
    contracts_export,
)
