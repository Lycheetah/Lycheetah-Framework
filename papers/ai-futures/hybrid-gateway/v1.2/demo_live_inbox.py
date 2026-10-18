"""Opt-in local model extraction DEMO. Does not approve or commit any claim.

Example (after installing/starting a local Ollama model):
    python demo_live_inbox.py --model YOUR_INSTALLED_MODEL

To send a fictional sample to an explicitly approved HTTPS provider, pass
--base-url https://.../v1 --remote-https --api-key-env ENV_KEY_NAME.
No remote connection is enabled by default. Never use sensitive source data.
"""
import argparse
import json
import os

from hybrid_gateway import (
    SourceDocument, HybridGateway, ProviderConfig, ExtractionTarget,
    OpenAICompatibleAdapter, HybridPipeline, ExtractionError, refund_window_quote_validator,
)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True)
    p.add_argument("--base-url", default="http://127.0.0.1:11434/v1")
    p.add_argument("--remote-https", action="store_true")
    p.add_argument("--api-key-env", default="LYCHEETAH_PROVIDER_API_KEY")
    args = p.parse_args()
    cfg = ProviderConfig(args.model, base_url=args.base_url,
                         allow_remote_https=args.remote_https, api_key=os.getenv(args.api_key_env))
    source = SourceDocument("fictional-2026-policy", "fictional-shop", "urn:fictional:demo",
                            "Refunds allowed within 14 days.")
    target = ExtractionTarget("refunds", "window_days", "online", "2026-10-01T00:00:00Z")
    g = HybridGateway(semantic_validator=refund_window_quote_validator)
    g.register_source(source)
    pipeline = HybridPipeline(g, OpenAICompatibleAdapter(cfg, target))
    try:
        staged = pipeline.stage(source)
    except ExtractionError as e:
        print(json.dumps({"status": "EXTRACTION_REJECTED", "reason": str(e), "ledger_events": 0}, indent=2))
        raise SystemExit(1)
    print(json.dumps({"status": "REQUIRES_HUMAN_REVIEW", "ledger_events": len(g.events),
                      "proposed_claims": [{"id": x.candidate.claim_id, "value": x.candidate.value,
                                           "quote": x.candidate.evidence_quote,
                                           "trusted_source_digest": x.registered_source_digest}
                                          for x in staged]}, indent=2))
    assert len(g.events) == 0 and not g.claims


if __name__ == "__main__":
    main()
