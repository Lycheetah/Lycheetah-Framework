from pathlib import Path

from lamague_runtime import AbstractInterpreter, CanonicalMilestoneCompiler, TraceStore

text = (
    "Human and AI collaborators examine an unproven claim, preserve uncertainty, "
    "record contributions, and publish only what the evidence supports."
)
ast = CanonicalMilestoneCompiler().compile(text)
result = AbstractInterpreter().execute(ast)
path = TraceStore(Path(__file__).resolve().parents[1] / "traces").save(ast, result)

print(result.explanation)
print("Audit:", result.audit.outcome.value)
print("Executed:", result.executed)
print("Trace:", path)
