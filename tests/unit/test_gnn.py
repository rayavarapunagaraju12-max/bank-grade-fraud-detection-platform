import torch

from ml.gnn.model import FraudGNN


def test_fraud_gnn_returns_probability_per_node() -> None:
    model = FraudGNN(input_dim=4, hidden_dim=8)
    x = torch.rand(3, 4)
    edge_index = torch.tensor([[0, 1, 2], [1, 2, 0]], dtype=torch.long)

    probability = model(x, edge_index=edge_index)

    assert probability.shape == (3,)
    assert torch.all(probability >= 0)
    assert torch.all(probability <= 1)
