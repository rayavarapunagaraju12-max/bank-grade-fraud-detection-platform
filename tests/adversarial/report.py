from pathlib import Path

from tests.adversarial.fraud_ring_simulation import (
    generate_device_sharing_attack,
    generate_fraud_ring,
    generate_money_laundering_chain,
)


def build_report(output: str = "docs/adversarial_report.md") -> str:
    scenarios = {
        "fraud_ring": generate_fraud_ring(100),
        "money_laundering_chain": generate_money_laundering_chain(25),
        "device_sharing_attack": generate_device_sharing_attack(50),
    }
    lines = ["# Adversarial Evaluation Report", ""]
    for name, events in scenarios.items():
        unique_accounts = len({event["account_id"] for event in events})
        unique_devices = len({event["device_id"] for event in events})
        lines.extend(
            [
                f"## {name}",
                f"- Events: {len(events)}",
                f"- Unique accounts: {unique_accounts}",
                f"- Unique devices: {unique_devices}",
                "",
            ]
        )
    Path(output).write_text("\n".join(lines), encoding="utf-8")
    return output


if __name__ == "__main__":
    print(build_report())
