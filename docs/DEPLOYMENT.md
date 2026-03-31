# Deployment Guide

This guide covers deploying the Ethics Engine API to production environments.

## Table of Contents

- [Quick Start with Docker Compose](#quick-start-with-docker-compose)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Providers](#cloud-providers)
- [Scaling](#scaling)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Quick Start with Docker Compose

The fastest way to deploy locally or on a single server:

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (8GB recommended)

### Deployment

```bash
# Clone repository
git clone https://github.com/RedCiprianPater/ethics-engine.git
cd ethics-engine

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f ethics-engine
```

### Services Included

| Service | Port | Description |
|---------|------|-------------|
| ethics-engine | 8000 | Main API server |
| redis | 6379 | Caching layer |
| postgres | 5432 | Audit database |
| nginx | 80/443 | Reverse proxy |

### Environment Variables

Create `.env` file:

```env
# API Configuration
ETHICS_ENGINE_ENV=production
ETHICS_API_KEY=your-secret-key
ETHICS_MODEL_PATH=/app/models/ethics-v1

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/ethics
REDIS_URL=redis://redis:6379

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

## Kubernetes Deployment

For production-scale deployments.

### Prerequisites

- Kubernetes 1.24+
- kubectl configured
- Helm 3.0+ (optional)

### Architecture

```
┌─────────────────────────────────────────┐
│           Load Balancer (Ingress)        │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         ethics-engine-service            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ Pod 1   │ │ Pod 2   │ │ Pod 3   │  │
│  │ (API)   │ │ (API)   │ │ (API)   │  │
│  └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────┘
         │              │
    ┌────▼────┐   ┌────▼────┐
    │  Redis  │   │Postgres │
    │ (Cache) │   │ (Audit) │
    └─────────┘   └─────────┘
```

### Deployment Files

Create `k8s/` directory with these files:

#### 1. Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ethics-engine
```

#### 2. ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ethics-engine-config
  namespace: ethics-engine
data:
  ETHICS_ENGINE_ENV: "production"
  DATABASE_URL: "postgresql://postgres:postgres@postgres:5432/ethics"
  REDIS_URL: "redis://redis:6379"
```

#### 3. Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ethics-engine-secrets
  namespace: ethics-engine
type: Opaque
stringData:
  ETHICS_API_KEY: "your-secret-api-key"
  DATABASE_PASSWORD: "postgres-password"
```

#### 4. Redis Deployment

```yaml
# k8s/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: ethics-engine
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: ethics-engine
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

#### 5. PostgreSQL Deployment

```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: ethics-engine
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ethics-engine-secrets
              key: DATABASE_PASSWORD
        - name: POSTGRES_DB
          value: ethics
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: ethics-engine
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: ethics-engine
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

#### 6. Ethics Engine Deployment

```yaml
# k8s/ethics-engine.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ethics-engine
  namespace: ethics-engine
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ethics-engine
  template:
    metadata:
      labels:
        app: ethics-engine
    spec:
      containers:
      - name: ethics-engine
        image: nwo-capital/ethics-engine:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: ethics-engine-config
        - secretRef:
            name: ethics-engine-secrets
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ethics-engine
  namespace: ethics-engine
spec:
  selector:
    app: ethics-engine
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

#### 7. Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ethics-engine-ingress
  namespace: ethics-engine
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - api.nworobotics.cloud
    secretName: ethics-engine-tls
  rules:
  - host: api.nworobotics.cloud
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ethics-engine
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/ethics-engine.yaml
kubectl apply -f k8s/ingress.yaml

# Check status
kubectl get pods -n ethics-engine
kubectl get svc -n ethics-engine
kubectl get ingress -n ethics-engine
```

## Cloud Providers

### AWS Deployment

#### Using EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name ethics-engine \
  --region us-west-2 \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5

# Deploy
kubectl apply -f k8s/

# Get load balancer URL
kubectl get svc -n ethics-engine
```

#### Using ECS

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name ethics-engine

# Deploy using Docker Compose
ecs-cli compose up
```

### Google Cloud Deployment

#### Using GKE

```bash
# Create GKE cluster
gcloud container clusters create ethics-engine \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2

# Deploy
kubectl apply -f k8s/
```

### Azure Deployment

#### Using AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group myResourceGroup \
  --name ethics-engine \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Deploy
kubectl apply -f k8s/
```

## Scaling

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ethics-engine-hpa
  namespace: ethics-engine
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ethics-engine
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Pod Autoscaler

```yaml
# k8s/vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: ethics-engine-vpa
  namespace: ethics-engine
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ethics-engine
  updatePolicy:
    updateMode: "Auto"
```

### Load Testing

```bash
# Install k6
brew install k6

# Run load test
cat > load-test.js << 'EOF'
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
};

export default function () {
  const res = http.post('https://api.nworobotics.cloud/ethics/v1/resolve', {
    scenario: 'Test scenario',
  }, {
    headers: {
      'Authorization': 'Bearer test-key',
      'X-Agent-ID': 'test-agent',
    },
  });
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
EOF

k6 run load-test.js
```

## Monitoring

### Prometheus & Grafana

```yaml
# k8s/monitoring.yaml
apiVersion: v1
kind: Service
metadata:
  name: ethics-engine-metrics
  namespace: ethics-engine
  labels:
    app: ethics-engine
spec:
  selector:
    app: ethics-engine
  ports:
  - name: metrics
    port: 9090
    targetPort: 9090
```

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `ethics_requests_total` | Total requests | - |
| `ethics_request_duration_seconds` | Request latency | p99 > 500ms |
| `ethics_errors_total` | Error count | > 1% of requests |
| `ethics_active_connections` | Active connections | > 1000 |

### Dashboard

Import this Grafana dashboard JSON (create `grafana-dashboard.json`):

```json
{
  "dashboard": {
    "title": "Ethics Engine",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(ethics_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, rate(ethics_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

## Security

### Best Practices

1. **Use HTTPS only**
   - TLS 1.3 minimum
   - Valid certificates (Let's Encrypt)

2. **API Key Management**
   - Rotate keys regularly
   - Use separate keys per agent
   - Monitor key usage

3. **Network Policies**
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: ethics-engine-network-policy
   spec:
     podSelector:
       matchLabels:
         app: ethics-engine
     policyTypes:
     - Ingress
     - Egress
     ingress:
     - from:
       - namespaceSelector:
           matchLabels:
             name: ingress-nginx
       ports:
       - protocol: TCP
         port: 8000
   ```

4. **Secrets Management**
   - Use Kubernetes Secrets
   - Enable encryption at rest
   - Rotate credentials

## Troubleshooting

### Common Issues

#### Pod CrashLoopBackOff

```bash
# Check logs
kubectl logs -n ethics-engine deployment/ethics-engine

# Check events
kubectl get events -n ethics-engine --sort-by='.lastTimestamp'
```

#### High Latency

```bash
# Check resource usage
kubectl top pods -n ethics-engine

# Scale up
kubectl scale deployment ethics-engine --replicas=5 -n ethics-engine
```

#### Database Connection Issues

```bash
# Check postgres pod
kubectl get pods -n ethics-engine -l app=postgres

# Check logs
kubectl logs -n ethics-engine deployment/postgres
```

### Debug Commands

```bash
# Shell into pod
kubectl exec -it -n ethics-engine deployment/ethics-engine -- /bin/bash

# Port forward for local testing
kubectl port-forward -n ethics-engine svc/ethics-engine 8000:80

# Check config
kubectl get configmap -n ethics-engine ethics-engine-config -o yaml
```

## Production Checklist

- [ ] HTTPS enabled with valid certificates
- [ ] API authentication configured
- [ ] Rate limiting enabled
- [ ] Monitoring and alerting set up
- [ ] Backups configured for PostgreSQL
- [ ] Disaster recovery plan documented
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] Runbook created for on-call

## Support

For deployment issues:
- GitHub Issues: https://github.com/RedCiprianPater/ethics-engine/issues
- Email: robotics@nwo.capital
