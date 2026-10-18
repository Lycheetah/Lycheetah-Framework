"""Compare claims with a previously frozen external gold JSONL; no model is run."""
import argparse
import json
from hybrid_gateway.evaluation import evaluate


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--gold', required=True, help='Frozen, independently annotated JSONL')
    ap.add_argument('--predictions', required=True, help='Model predictions JSONL')
    ap.add_argument('--expected-corpus-digest', help='Reject changed gold file')
    ap.add_argument('--output', help='Aggregate, privacy-minimal JSON report')
    args = ap.parse_args()
    report = evaluate(args.gold, args.predictions,
                      expected_corpus_digest=args.expected_corpus_digest).public_dict()
    encoded = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.output:
        with open(args.output, 'w', encoding='utf8') as f:
            f.write(encoded)
    print(encoded)


if __name__ == '__main__':
    main()
