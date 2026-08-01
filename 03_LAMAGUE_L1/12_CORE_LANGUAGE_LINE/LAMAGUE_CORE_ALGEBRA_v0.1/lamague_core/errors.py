class LamagueError(Exception):
    """Base LAMAGUE core error."""


class LexError(LamagueError):
    pass


class ParseError(LamagueError):
    pass


class SemanticError(LamagueError):
    pass
