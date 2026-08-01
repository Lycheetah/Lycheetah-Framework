from __future__ import annotations

from .model import CompressionDecision, CompressionMode, ProgramAST


class BreathingCompression:
    def decide(self, ast: ProgramAST) -> CompressionDecision:
        ctx = ast.context
        ops = set(ast.operation_path)
        reasons: list[str] = []

        consequential = bool(ops & {"T", "X", "Y", "V", "M"})
        unresolved_dissent = any(
            str(d.get("status", "UNRESOLVED")).upper() != "RESOLVED"
            for d in ctx.dissent
        )
        hidden_value = any(
            not bool(v.get("declared", True)) or not v.get("consent")
            for v in ctx.value_ledger
        )

        if ctx.risk_level in {"high", "critical"}:
            reasons.append("high-impact context requires semantic expansion")
        if ctx.irreversible:
            reasons.append("irreversible action cannot remain compressed")
        if ctx.decoder_confidence < 0.80:
            reasons.append("decoder confidence is below 0.80")
        if not ctx.shared_context:
            reasons.append("participants do not share a verified context")
        if consequential and ctx.unknowns:
            reasons.append("consequential unknowns remain unresolved")
        if consequential and not ctx.authority:
            reasons.append("consequential authority is not visible")
        if unresolved_dissent:
            reasons.append("protected dissent remains unresolved")
        if hidden_value:
            reasons.append("value flow contains hidden or unconsented extraction")

        if reasons:
            return CompressionDecision(
                CompressionMode.EXPAND, reasons, ctx.decoder_confidence, ctx.risk_level
            )

        compressible = (
            ctx.risk_level == "low"
            and ctx.decoder_confidence >= 0.90
            and ctx.shared_context
            and not ctx.irreversible
        )
        if compressible:
            return CompressionDecision(
                CompressionMode.COMPRESS,
                ["shared context, stable decoder, low risk, and recoverable meaning"],
                ctx.decoder_confidence,
                ctx.risk_level,
            )

        return CompressionDecision(
            CompressionMode.HOLD,
            ["conditions are neither unsafe enough to force expansion nor stable enough to compress"],
            ctx.decoder_confidence,
            ctx.risk_level,
        )
