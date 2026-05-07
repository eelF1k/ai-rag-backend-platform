# Kubernetes Deploy Guide

This folder provides a minimal local/dev Kubernetes setup for the platform.

## Prerequisites
- Docker image built locally: `ai-rag-backend:latest`
- A running Kubernetes cluster (kind/minikube/k3d)
- `kubectl` and optionally `kustomize`

## Apply manifests
```bash
kubectl apply -k infra/k8s
```

## Verify
```bash
kubectl get pods
kubectl get svc
kubectl logs deploy/api
kubectl logs deploy/worker
```

## Port-forward API
```bash
kubectl port-forward svc/api 8000:8000
```

Then open:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/api/v1/health`
- `http://127.0.0.1:8000/api/v1/metrics`

## Notes
- This setup is intentionally simple for portfolio/demo purposes.
- Use managed databases and persistent volumes for production.

