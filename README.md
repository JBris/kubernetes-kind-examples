# Kubernetes Kind Local Environment 

Local testing environment for Kubernetes using Kind with Helm, the Argo ecosystem, and others installed.

# Table of contents

- [Kubernetes Kind Local Environment](#kubernetes-kind-local-environment)
- [Table of contents](#table-of-contents)
- [kubectl](#kubectl)
- [helm](#helm)
- [kind](#kind)
- [Add storage classes](#add-storage-classes)
- [Sealed Secrets](#sealed-secrets)
- [ArgoCD](#argocd)
- [Argo Workflows](#argo-workflows)
- [Argo Events](#argo-events)
- [Argo Rollouts](#argo-rollouts)
- [NGINX Ingress Operator](#nginx-ingress-operator)
- [Cert Manager](#cert-manager)
- [Argo Rollouts with NGINX](#argo-rollouts-with-nginx)
- [Test ML stack](#test-ml-stack)
- [Volcano](#volcano)
- [KubeRay](#kuberay)
  
# kubectl 

```
sudo apt-get update
# apt-transport-https may be a dummy package; if so, you can skip that package
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg

# If the folder `/etc/apt/keyrings` does not exist, it should be created before the curl command, read the note below.
# sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg # allow unprivileged APT programs to read this keyring

# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list   # helps tools such as command-not-found to work correctly

sudo apt-get update
sudo apt-get install -y kubectl
```

# helm

```
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

# kind

Install Docker first. Then...

```
# For AMD64 / x86_64
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.26.0/kind-linux-amd64
# For ARM64
[ $(uname -m) = aarch64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.26.0/kind-linux-arm64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

To create a cluster:

```
kind create cluster --name kind
```

To delete a cluster:

```
kind delete cluster --name kind
```

List clusters:

```
kind get clusters
```

# Add storage classes

Add local storage class:

```
kubectl apply -f deployment/dev/storage/local-storage-class.yaml 
kubectl apply -f deployment/dev/storage/local-storage-pv.yaml 

kubectl get sc
kubectl get pv
```

# Sealed Secrets

Install Sealed Secrets:

```
helm repo add sealed-secrets https://bitnami-labs.github.io/sealed-secrets
helm install sealed-secrets -n kube-system --set-string fullnameOverride=sealed-secrets-controller sealed-secrets/sealed-secrets

KUBESEAL_VERSION='0.23.0'
curl -OL "https://github.com/bitnami-labs/sealed-secrets/releases/download/v${KUBESEAL_VERSION:?}/kubeseal-${KUBESEAL_VERSION:?}-linux-amd64.tar.gz"
tar -xvzf kubeseal-${KUBESEAL_VERSION:?}-linux-amd64.tar.gz kubeseal
sudo install -m 755 kubeseal /usr/local/bin/kubeseal
```


Usage example:

```
echo -n bar | kubectl create secret generic mysecret --dry-run=client --from-file=foo=/dev/stdin -o json >mysecret.json

kubeseal -f mysecret.json -w mysealedsecret.json
kubectl create -f mysealedsecret.json
kubectl get secret mysecret
```

# ArgoCD

```
kubectl create namespace argocd

kubectl get ns

kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

kubectl get svc -n argocd

# Port forwarding
kubectl port-forward -n argocd service/argocd-server 8443:443
```

Get admin password

```
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

Default username for ArgoCD is admin.

Visit localhost:8443 on your web browser.

```
xdg-open localhost:8443
```

# Argo Workflows

Install Argo Workflows:

```
ARGO_WORKFLOWS_VERSION="v3.6.4"
kubectl create namespace argo
kubectl apply -n argo -f "https://github.com/argoproj/argo-workflows/releases/download/${ARGO_WORKFLOWS_VERSION}/quick-start-minimal.yaml"

# Add CLI
ARGO_OS="linux"

curl -sLO "https://github.com/argoproj/argo-workflows/releases/download/v3.6.4/argo-$ARGO_OS-amd64.gz"
gunzip "argo-$ARGO_OS-amd64.gz"
chmod +x "argo-$ARGO_OS-amd64"
sudo mv "./argo-$ARGO_OS-amd64" /usr/local/bin/argo
argo version
```

Submit an example workflow:

```
argo submit -n argo --watch https://raw.githubusercontent.com/argoproj/argo-workflows/main/examples/hello-world.yaml

argo list -n argo
argo get -n argo @latest
argo logs -n argo @latest
```

View the GUI:

```
kubectl -n argo port-forward service/argo-server 2746:2746
```

Navigate your browser to https://localhost:2746. Click + Submit New Workflow and then Edit using full workflow options. You can find an example workflow already in the text field. Press + Create to start the workflow

# Argo Events

Install Argo Events:

```
kubectl create namespace argo-events
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-events/stable/manifests/install.yaml
# Install with a validating admission controller
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-events/stable/manifests/install-validating-webhook.yaml

kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/stable/examples/eventbus/native.yaml

kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/stable/examples/event-sources/webhook.yaml

 # sensor rbac
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/master/examples/rbac/sensor-rbac.yaml
 # workflow rbac
kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/master/examples/rbac/workflow-rbac.yaml

kubectl apply -n argo-events -f https://raw.githubusercontent.com/argoproj/argo-events/stable/examples/sensors/webhook.yaml
```

Setup a sensor:

```
kubectl -n argo-events port-forward $(kubectl -n argo-events get pod -l eventsource-name=webhook -o name) 12000:12000 &

sleep 5

curl -d '{"message":"this is my first webhook"}' -H "Content-Type: application/json" -X POST http://localhost:12000/example
kubectl -n argo-events get workflows | grep "webhook"
```

# Argo Rollouts

Add Argo Rollouts

```
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

kubectl apply -k https://github.com/argoproj/argo-rollouts/manifests/crds\?ref\=stable

# Plugin install
curl -LO https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-amd64
chmod +x ./kubectl-argo-rollouts-linux-amd64
sudo mv ./kubectl-argo-rollouts-linux-amd64 /usr/local/bin/kubectl-argo-rollouts
kubectl argo rollouts version
```

Run the demo:

```
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-rollouts/master/docs/getting-started/basic/rollout.yaml
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-rollouts/master/docs/getting-started/basic/service.yaml

kubectl argo rollouts get rollout rollouts-demo --watch
```

Update rollout:

```
kubectl argo rollouts set image rollouts-demo \
  rollouts-demo=argoproj/rollouts-demo:yellow

kubectl argo rollouts get rollout rollouts-demo --watch
```

Promote rollout:

```
kubectl argo rollouts promote rollouts-demo
kubectl argo rollouts get rollout rollouts-demo --watch
```

Abort rollout

```
kubectl argo rollouts set image rollouts-demo \
  rollouts-demo=argoproj/rollouts-demo:red

kubectl argo rollouts abort rollouts-demo
```

Set rollout as healthy:

```
kubectl argo rollouts set image rollouts-demo \
  rollouts-demo=argoproj/rollouts-demo:yellow
```

View the dashboard:

```
kubectl argo rollouts dashboard
```

# NGINX Ingress Operator

Install NGINX using helm

```
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

If you want a full list of values that you can set, while installing with Helm, then run:

```
helm show values ingress-nginx --repo https://kubernetes.github.io/ingress-nginx
```

To check which ports are used by your installation of ingress-nginx, look at the output of:

```
kubectl -n ingress-nginx get pod -o yaml
```

Get pods in ingress-inginx namespace:

```
kubectl get pods --namespace=ingress-nginx
```

Let's create a simple web server and the associated service:

```
kubectl create deployment demo --image=httpd --port=80
kubectl expose deployment demo
```

Then create an ingress resource. The following example uses a host that maps to localhost:

```
kubectl create ingress demo-localhost --class=nginx \
  --rule="demo.localdev.me/*=demo:80"
```

Now, forward a local port to the ingress controller:

```
kubectl port-forward --namespace=ingress-nginx service/ingress-nginx-controller 8080:80
```

Access localhost:8080

```
curl --resolve demo.localdev.me:8080:127.0.0.1 http://demo.localdev.me:8080
```

# Cert Manager

Add Cert Manager:

```
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.0/cert-manager.yaml
```

Add LetsEncrypt staging:

```
kubectl apply -f deployment/dev/certs/staging-issuer.yaml 
kubectl get issuer
```

Add kuard test service, deployment, and ingress:

```
kubectl delete deployment kuard
kubectl delete service kuard
kubectl delete ingress kuard

kubectl apply -f deployment/dev/kuard/kuard-deployment.yaml 
kubectl apply -f deployment/dev/kuard/kuard-service.yaml
kubectl apply -f deployment/dev/kuard/kuard-ingress.yaml

kubectl port-forward -n default service/kuard 9500:80
```

Ping the endpoint:

```
curl --resolve kuard.localdev.me:9500:127.0.0.1 http://kuard.localdev.me:9500
```

# Argo Rollouts with NGINX

Run the following commands to deploy:

* A Rollout
* Two Services (stable and canary)
* An Ingress

```
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-rollouts/master/docs/getting-started/nginx/rollout.yaml
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-rollouts/master/docs/getting-started/nginx/services.yaml
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-rollouts/master/docs/getting-started/nginx/ingress.yaml

kubectl get ro
kubectl get svc
kubectl get ing
kubectl argo rollouts get rollout rollouts-demo
```

Update the rollout:

```
kubectl argo rollouts set image rollouts-demo rollouts-demo=argoproj/rollouts-demo:yellow
kubectl argo rollouts get rollout rollouts-demo
```

# Test ML stack

```
kubectl delete deployment ml-dev
kubectl delete service ml-dev
kubectl delete ingress ml-dev
kubectl delete pvc vol-ml-prefect

kubectl apply -f deployment/dev/ml/ml-deployment.yaml 
kubectl apply -f deployment/dev/ml/ml-service.yaml
kubectl apply -f deployment/dev/ml/ml-ingress.yaml
kubectl apply -f deployment/dev/ml/vol-ml-prefect.yaml

kubectl port-forward -n default service/ml-dev 8025:8025 9001:9001 9000:9000 8978:8978 4200:4200 5432:5432
```

# Volcano

Add Volcano:

```
kubectl apply -f https://raw.githubusercontent.com/volcano-sh/volcano/master/installer/volcano-development.yaml
```

Add a Volcano job and view results:

```
kubectl create -f deployment/dev/volcano/queue.yaml
kubectl create -f deployment/dev/volcano/vcjob.yaml

kubectl get vcjob job-1 -oyaml
kubectl get podgroup
kubectl get queue test -oyaml
```

# KubeRay

Add KubeRay:

```
helm repo update
helm install kuberay-operator kuberay/kuberay-operator --version 1.3.0 --set batchScheduler.enabled=true

# Add RayCluster
kubectl apply -f https://raw.githubusercontent.com/ray-project/kuberay/v1.3.0/ray-operator/config/samples/ray-cluster.volcano-scheduler.yaml
kubectl get pod -l ray.io/cluster=test-cluster-0

kubectl delete raycluster --all
```

With gang scheduling:

```
kubectl create -f - <<EOF
apiVersion: scheduling.volcano.sh/v1beta1
kind: Queue
metadata:
  name: kuberay-test-queue
spec:
  weight: 1
  capability:
    cpu: 4
    memory: 6Gi
EOF

kubectl apply -f https://raw.githubusercontent.com/ray-project/kuberay/v1.3.0/ray-operator/config/samples/ray-cluster.volcano-scheduler-queue.yaml

kubectl get podgroup ray-test-cluster-0-pg -o yaml
kubectl get queue kuberay-test-queue -o yaml

kubectl delete raycluster test-cluster-0
kubectl delete queue kuberay-test-queue
```

Use KubeRay with Modin:

```
kubectl apply -f https://raw.githubusercontent.com/ray-project/kuberay/master/ray-operator/config/samples/ray-job.modin.yaml

kubectl logs -l=job-name=rayjob-sample
```