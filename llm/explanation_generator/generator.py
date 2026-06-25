from llm.ollama_client.client import OllamaClient


class NarrativeGenerator:
    def __init__(self) -> None:
        self.client = OllamaClient()

    async def generate(self, shap_output: dict, graph_findings: dict) -> str:
        top = shap_output.get("features", [])[:5]
        prompt = (
            "You are a senior bank fraud analyst. Write a concise investigation narrative. "
            f"Model explanation: {top}. Graph findings: {graph_findings}. "
            "Include why the transaction is risky and the next analyst action."
        )
        narrative = await self.client.generate(prompt)
        if narrative and "Narrative unavailable" not in narrative:
            return narrative
        return self.local_narrative(shap_output, graph_findings)

    def local_narrative(self, shap_output: dict, graph_findings: dict) -> str:
        features = shap_output.get("features", [])[:5]
        feature_names = [
            str(item.get("feature", "unknown")).replace("_", " ")
            for item in features
            if item.get("contribution", 0) > 0
        ]
        reasons = ", ".join(feature_names[:4]) or "unusual transaction behavior"
        graph_flags = []
        if graph_findings.get("shared_device_count", 0):
            graph_flags.append(f"{graph_findings['shared_device_count']} shared device link(s)")
        if graph_findings.get("shared_ip_count", 0):
            graph_flags.append(f"{graph_findings['shared_ip_count']} shared IP link(s)")
        if graph_findings.get("shortest_path_to_fraud", 99) < 4:
            graph_flags.append("close graph path to a known fraud account")
        graph_text = f" Graph signals show {', '.join(graph_flags)}." if graph_flags else ""
        return (
            f"This transaction was flagged because the strongest risk drivers are {reasons}."
            f"{graph_text} Recommended action: hold for analyst review, verify customer intent, "
            "check linked device/IP activity, and document the decision in the case record."
        )
