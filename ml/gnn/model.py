from dataclasses import dataclass

import torch
from torch import nn

try:
    from torch_geometric.nn import SAGEConv
except Exception:  # pragma: no cover - keeps local demos usable without compiled PyG extras
    SAGEConv = None


@dataclass(frozen=True)
class GNNInferenceOutput:
    fraud_probability: torch.Tensor
    node_embeddings: torch.Tensor
    architecture: str


class FraudGNN(nn.Module):
    """GraphSAGE fraud-ring scorer with a dense fallback for local demos.

    In production mode the model consumes node features and an edge index from a
    k-hop entity subgraph. The fallback path keeps the API usable for unit tests
    and CPU-only local demos where PyTorch Geometric graph ops are unavailable.
    """

    def __init__(self, input_dim: int = 16, hidden_dim: int = 64, dropout: float = 0.15) -> None:
        super().__init__()
        self.uses_graph_layers = SAGEConv is not None
        self.dropout = nn.Dropout(dropout)

        if self.uses_graph_layers:
            self.conv1 = SAGEConv(input_dim, hidden_dim)
            self.conv2 = SAGEConv(hidden_dim, hidden_dim)
            self.classifier = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim // 2, 1),
            )
        else:
            self.fallback = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, 1),
            )

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor | None = None,
        target_node_index: torch.Tensor | None = None,
    ) -> torch.Tensor:
        output = self.infer_subgraph(x, edge_index=edge_index, target_node_index=target_node_index)
        return output.fraud_probability

    def infer_subgraph(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor | None = None,
        target_node_index: torch.Tensor | None = None,
    ) -> GNNInferenceOutput:
        if self.uses_graph_layers and edge_index is not None:
            embeddings = self.conv1(x, edge_index).relu()
            embeddings = self.dropout(embeddings)
            embeddings = self.conv2(embeddings, edge_index).relu()
            selected = self._select_target_nodes(embeddings, target_node_index)
            logits = self.classifier(selected).squeeze(-1)
            return GNNInferenceOutput(
                fraud_probability=torch.sigmoid(logits),
                node_embeddings=embeddings,
                architecture="graphsage",
            )

        logits = self.fallback(x).squeeze(-1)
        return GNNInferenceOutput(
            fraud_probability=torch.sigmoid(logits),
            node_embeddings=x,
            architecture="dense-fallback",
        )

    @staticmethod
    def _select_target_nodes(x: torch.Tensor, target_node_index: torch.Tensor | None) -> torch.Tensor:
        if target_node_index is None:
            return x
        return x[target_node_index]
