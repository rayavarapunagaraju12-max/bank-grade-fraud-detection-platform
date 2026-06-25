# Kubernetes Deployment

Local manifests live in `infra/kubernetes`.

```bash
kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/secrets.example.yaml
kubectl apply -f infra/kubernetes/
```

Helm chart:

```bash
helm upgrade --install fraud infra/helm/fraud-detection
```
