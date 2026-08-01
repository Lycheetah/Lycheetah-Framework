from __future__ import annotations

from .model import ProgramAST


_EXPLANATIONS = {
    "A": "return the state toward its declared baseline",
    "B": "build a mapping without erasing source identity",
    "C": "repeat a bounded operation until its stop condition",
    "D": "measure drift from the protected invariant",
    "E": "attach traceable evidence and preserve contradiction",
    "F": "fold relevant history into the present state",
    "G": "guard the action through declared invariants and fallback",
    "H": "declare the consequence horizon",
    "I": "declare the properties that must survive transformation",
    "J": "branch according to an explicit condition",
    "K": "extract the minimal load-bearing kernel",
    "L": "apply a typed limit",
    "M": "merge states under a visible conflict policy",
    "N": "measure novelty against a declared comparison space",
    "O": "observe the target with time, scope, and observer context",
    "P": "test the claim against evidence without deleting uncertainty",
    "Q": "state the unresolved question",
    "R": "attempt resolution while preserving unknown if unresolved",
    "S": "form a bounded state record",
    "T": "record a typed transition from one state to another",
    "U": "preserve unresolved content as a typed unknown",
    "V": "construct an alternative path while preserving legitimate intent",
    "W": "weave participants without merging identity or dissent",
    "X": "make an exchange with visible consent and value flow",
    "Y": "yield only the result permitted by proof and scope",
    "Z": "compress only while protected meaning remains recoverable",
}


class Explainer:
    def explain(self, ast: ProgramAST) -> str:
        lines: list[str] = []
        if ast.expanded_from:
            lines.append(
                "Expanded programme seal(s): " + ", ".join(ast.expanded_from) + "."
            )
        lines.append("Runtime v0.2 operation path: " + " → ".join(ast.operation_path) + ".")
        for index, node in enumerate(ast.nodes, 1):
            extra = ""
            if node.operation == "U" and node.arguments.get("type"):
                extra = f" The unresolved type is {node.arguments['type']}."
            lines.append(f"{index}. {node.operation} — {_EXPLANATIONS[node.operation]}.{extra}")
        if ast.context.unknowns:
            lines.append("Preserved unknowns: " + "; ".join(ast.context.unknowns) + ".")
        if ast.context.invariants:
            lines.append("Protected invariants: " + "; ".join(ast.context.invariants) + ".")
        if ast.context.authority:
            lines.append("Visible authority: " + "; ".join(ast.context.authority) + ".")
        return "\n".join(lines)
