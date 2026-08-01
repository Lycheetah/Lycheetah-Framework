from .core import parse_source, run_source
from .errors import LamagueError, LexError, ParseError, SemanticError
from .lexer import Lexer
from .parser import Parser
from .semantics import Runtime
from .normalizer import normalize, canonical, equivalent, semantic_hash
from .graph import semantic_graph

__version__ = "0.1.0"
