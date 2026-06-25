import math


def population_stability_index(expected: list[float], actual: list[float]) -> float:
    if not expected or not actual:
        return 0.0
    exp_avg = sum(expected) / len(expected)
    act_avg = sum(actual) / len(actual)
    exp = max(exp_avg, 1e-6)
    act = max(act_avg, 1e-6)
    return (act - exp) * math.log(act / exp)


def detect_drift(reference_scores: list[float], current_scores: list[float], threshold: float = 0.2) -> dict:
    psi = abs(population_stability_index(reference_scores, current_scores))
    return {
        "psi": round(psi, 4),
        "drift_detected": psi >= threshold,
        "recommended_action": "trigger_retraining" if psi >= threshold else "monitor",
    }
