from backend.schemas.transactions import FeatureVector, FraudScore
from llm.explanation_generator.generator import NarrativeGenerator
from ml.ensemble.service import EnsembleScorer
from ml.shap.explainer import explain_features


class FraudScoringService:
    def __init__(self) -> None:
        self.ensemble = EnsembleScorer()
        self.narratives = NarrativeGenerator()

    async def score(
        self,
        features: FeatureVector,
        graph_findings: dict | None = None,
        include_narrative: bool = False,
    ) -> FraudScore:
        result = self.ensemble.score(features.model_dump())
        explanation = explain_features(features.model_dump(), result["fraud_score"])
        narrative = (
            await self.narratives.generate(explanation, graph_findings or {})
            if include_narrative
            else self.narratives.local_narrative(explanation, graph_findings or {})
        )
        band = (
            "critical"
            if result["fraud_score"] >= 0.85
            else "high"
            if result["fraud_score"] >= 0.65
            else "medium"
            if result["fraud_score"] >= 0.4
            else "low"
        )
        return FraudScore(
            transaction_id=features.transaction_id,
            fraud_score=result["fraud_score"],
            risk_band=band,
            tabular_score=result["tabular_score"],
            anomaly_score=result["anomaly_score"],
            graph_score=result["graph_score"],
            explanation=explanation,
            narrative=narrative,
        )

    async def generate_narrative(self, explanation: dict, graph_findings: dict | None = None) -> str:
        return await self.narratives.generate(explanation, graph_findings or {})

    def model_status(self) -> dict:
        return {
            "mode": self.ensemble.model_mode,
            "artifacts": [
                {
                    "name": status.name,
                    "path": str(status.path),
                    "loaded": status.loaded,
                    "reason": status.reason,
                }
                for status in self.ensemble.artifact_status
            ],
            "gnn": {
                "status": "scaffold_available",
                "production_note": (
                    "Train and validate a graph model before using GNN output "
                    "for live blocking decisions."
                ),
            },
            "drift_detection": {
                "status": "psi_demo_available",
                "production_note": (
                    "Add feedback labels, champion/challenger approval, "
                    "and retraining workflow for production."
                ),
            },
        }
