"""Three real policy outcomes: safe read, approval pause, hard deny."""

from pathlib import Path

from lycheetah.assurance import AssurancePolicy, AssuranceRuntime


POLICY_PATH = Path(__file__).with_name("customer_support_policy.json")


def main() -> None:
    runtime = AssuranceRuntime(AssurancePolicy.from_json(POLICY_PATH))
    cases = [
        runtime.evaluate_tool("order.read", {"order_id": 8124}),
        runtime.evaluate_tool(
            "refund.create",
            {"order_id": 8124, "amount": 49.0},
            scopes=("payments.refund",),
            side_effect=True,
        ),
        runtime.evaluate_tool(
            "shell_exec",
            {"command": "printenv"},
            scopes=("production.shell",),
        ),
    ]
    for receipt in cases:
        subject = receipt.event["subject"]["name"]
        print(f"{receipt.decision.value:<6} {subject:<28} {receipt.digest[:12]}")
        for finding in receipt.findings:
            if finding.effective_disposition.value != "ALLOW":
                print(f"       {finding.finding_id}: {finding.title}")


if __name__ == "__main__":
    main()
