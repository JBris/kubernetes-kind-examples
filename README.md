# Kubernetes Kind Examples

Local testing environment for Kubernetes using Kind with Helm, the Argo ecosystem, and others installed.

# Table of contents

- [Kubernetes Kind Examples](#kubernetes-kind-examples)
- [Table of contents](#table-of-contents)
- [kubectl](#kubectl)
- [helm](#helm)
- [kind](#kind)
- [k9s](#k9s)
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
- [Tekton](#tekton)
- [Redis](#redis)
- [Knative](#knative)
  - [Quickstart](#quickstart)
  - [End to end](#end-to-end)
  - [Send Review Comment to Broker](#send-review-comment-to-broker)
- [Kubeflow](#kubeflow)
  - [Standalone Installation](#standalone-installation)
  - [KServe Installation](#kserve-installation)
    - [Secure InferenceService with ServiceMesh](#secure-inferenceservice-with-servicemesh)
    - [KServe test run](#kserve-test-run)
  
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

# k9s

Add k9s:

```
wget https://github.com/derailed/k9s/releases/download/v0.32.7/k9s_linux_amd64.deb 
sudo apt install ./k9s_linux_amd64.deb 
rm k9s_linux_amd64.deb

k9s help
k9s -n default
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

# Tekton

Add Tekton

```
kubectl apply -f https://storage.googleapis.com/tekton-releases/operator/latest/release.yaml
kubectl get pods --namespace tekton-pipelines  

# Install CLI
sudo apt update;sudo apt install -y gnupg
sudo mkdir -p /etc/apt/keyrings/
sudo gpg --no-default-keyring --keyring /etc/apt/keyrings/tektoncd.gpg --keyserver keyserver.ubuntu.com --recv-keys 3EFE0E0A2F2F60AA
echo "deb [signed-by=/etc/apt/keyrings/tektoncd.gpg] http://ppa.launchpad.net/tektoncd/cli/ubuntu eoan main"|sudo tee /etc/apt/sources.list.d/tektoncd-ubuntu-cli.list
sudo apt update && sudo apt install -y tektoncd-cli
```

Create task:

```
kubectl apply -f deployment/dev/tekton/hello-world.yaml
kubectl apply -f deployment/dev/tekton/hello-world-run.yaml

kubectl get taskrun hello-task-run --watch
kubectl logs --selector=tekton.dev/taskRun=hello-task-run
```

Create a second task, and then create a pipeline:

```
kubectl apply -f deployment/dev/tekton/goodbye-world.yaml
kubectl apply -f deployment/dev/tekton/hello-goodbye-pipeline.yaml
kubectl apply -f deployment/dev/tekton/hello-goodbye-pipeline-run.yaml

kubectl logs --selector=tekton.dev/pipelineRun=hello-goodbye-run
```

Add triggers:

```
kubectl apply -f deployment/dev/tekton/trigger-template.yaml
kubectl apply -f deployment/dev/tekton/trigger-binding.yaml 
kubectl apply -f deployment/dev/tekton/event-listener.yaml 
kubectl apply -f deployment/dev/tekton/rbac.yaml

kubectl port-forward service/el-hello-listener 8080
```

Trigger run:

```
curl -v \
   -H 'content-Type: application/json' \
   -d '{"username": "Tekton"}' \
   http://localhost:8080

kubectl get pipelineruns
```

# Redis

Add Redis

```
kubectl apply -f deployment/dev/redis/redis-deployment.yaml 
kubectl apply -f deployment/dev/redis/redis-service.yaml 
kubectl apply -f deployment/dev/redis/redis-ingress.yaml

kubectl port-forward service/redis 6379
```

# Knative

Add Knative:

```
# Serving
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-core.yaml
kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.17.0/kourier.yaml
kubectl patch configmap/config-network \
  --namespace knative-serving \
  --type merge \
  --patch '{"data":{"ingress-class":"kourier.ingress.networking.knative.dev"}}'
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-hpa.yaml

# Eventing
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.17.2/eventing-crds.yaml
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.17.2/eventing-core.yaml
# Kafka
kubectl apply -f https://github.com/knative-extensions/eventing-kafka-broker/releases/download/knative-v1.17.1/eventing-kafka-controller.yaml
kubectl apply -f https://github.com/knative-extensions/eventing-kafka-broker/releases/download/knative-v1.17.1/eventing-kafka-controller.yaml
kubectl apply -f https://github.com/knative-extensions/eventing-kafka-broker/releases/download/knative-v1.17.1/eventing-kafka-controller.yaml

# Configure magic DNS
kubectl --namespace kourier-system get service kourier
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-default-domain.yaml

kubectl get pods -n knative-serving
kubectl get pods -n knative-eventing
```

Add CLI tools:

```
# kn
wget https://github.com/knative/client/releases/download/knative-v1.17.0/kn-linux-amd64
sudo mv kn-linux-amd64 /usr/local/bin/kn
sudo chmod +x /usr/local/bin/kn

kn

# func
wget https://github.com/knative/func/releases/download/knative-v1.17.0/func_linux_amd64
sudo mv func_linux_amd64 /usr/local/bin/func
sudo chmod +x /usr/local/bin/func

func version
```

## Quickstart

Create a hello() function:

```
func create -l go hello

export FUNC_REGISTRY=ghcr.io/... # You will need to change this

cd hello
func run --build
func invoke
```

Deploy a Knative service:

```
kubectl create ns knative-operator
kubectl apply -f deployment/dev/knative/hello.yaml

kn service list

echo "Accessing URL $(kn service describe hello -o url)"
curl "$(kn service describe hello -o url)"

kubectl get pod -l serving.knative.dev/service=hello -w
```

Revise the service:

```
kn service update hello \
--env TARGET=Knative

kn revisions list

# Split traffic
kn service update hello \
--traffic hello-00001=50 \
--traffic @latest=50
kn revisions list
```

Create an event source:

```
kn service create cloudevents-player \
--image quay.io/ruben/cloudevents-player:latest

kn source binding create ce-player-binding --subject "Service:serving.knative.dev/v1:cloudevents-player" --sink broker:example-broker
```

Create trigger:

```
kn trigger create cloudevents-trigger --sink cloudevents-player  --broker example-broker
```

## End to end

[View: https://knative.dev/docs/bookstore/page-0/welcome-knative-bookstore-tutorial/](https://knative.dev/docs/bookstore/page-0/welcome-knative-bookstore-tutorial/)

Clone repo and spin up front end:

```
git clone https://github.com/knative/docs.git

cd docs/code-samples/eventing/bookstore-sample-app/start
kubectl apply -f frontend/config/100-front-end-deployment.yaml
kubectl get pods

kubectl port-forward svc/bookstore-frontend-svc 3000
```

Now the backend:

```
cd docs/code-samples/eventing/bookstore-sample-app/start
kubectl apply -f node-server/config/100-deployment.yaml
kubectl get pods

kubectl port-forward svc/node-server-svc 8080:80
```

## Send Review Comment to Broker

```
kubectl apply -f deployment/dev/knative/200-broker.yaml 

kubectl get brokers
kubectl describe broker bookstore-broker

kubectl apply -f deployment/dev/knative/300-sinkbinding.yaml
kubectl get sinkbindings

kubectl apply -f deployment/dev/knative/100-event-display.yaml
kubectl get pods

kubectl apply -f deployment/dev/knative/200-log-trigger.yaml 
kubectl get triggers

kubectl logs -l=app=event-display -f
```

Create sentiment analysis function:

```
# func create -l python sentiment-analysis-app # See tutorial code
cd sentiment-analysis-app
func build -b=s2i -v
func run -b=s2i -v

# Simulate cloud event
cd sentiment-analysis-app
func invoke -f=cloudevent --data='{"reviewText": "I love Knative so much"}' --content-type=application/json --type="new-review-comment" -v

func deploy -b=s2i -v

kubectl get kservice
func invoke -f=cloudevent --data='{"reviewText":"I love Knative so much"}' -v
```

Create a sequence:

```
kubectl apply -f deployment/dev/knative/100-create-sequence.yaml 
kubectl get sequences

kubectl apply -f deployment/dev/knative/200-create-trigger.yaml 
kubectl get triggers
```

Create a database:

```
cd docs/code-samples/eventing/bookstore-sample-app/start
kubectl apply -f db-service
kubectl get pods
```

# Kubeflow

## Standalone Installation

Add Kubeflow

```
# Pipelines
export PIPELINE_VERSION=2.3.0
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=$PIPELINE_VERSION"

kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80

# Trainer
kubectl apply --server-side -k "https://github.com/kubeflow/trainer.git/manifests/overlays/manager?ref=master"
kubectl get pods -n kubeflow-system
kubectl apply --server-side -k "https://github.com/kubeflow/trainer.git/manifests/overlays/runtimes?ref=master"

# Katib
kubectl apply -k "github.com/kubeflow/katib.git/manifests/v1beta1/installs/katib-standalone?ref=v0.17.0"
kubectl apply -k "github.com/kubeflow/katib.git/manifests/v1beta1/installs/katib-standalone?ref=master"

# Model registry
MODEL_REGISTRY_VERSION=0.2.12
kubectl apply -k "https://github.com/kubeflow/model-registry/manifests/kustomize/options/csi?ref=v${MODEL_REGISTRY_VERSION}"
# Istio 
# kubectl apply -k "https://github.com/kubeflow/model-registry/manifests/kustomize/options/istio?ref=v${MODEL_REGISTRY_VERSION}"
kubectl wait --for=condition=available -n kubeflow deployment/model-registry-deployment --timeout=1m
kubectl port-forward svc/model-registry-service -n kubeflow 8081:8080
# in another terminal:
curl -X 'GET' \
  'http://localhost:8081/api/model_registry/v1alpha3/registered_models?pageSize=100&orderBy=ID&sortOrder=DESC' \
  -H 'accept: application/json' | jq
```

## KServe Installation

Add KServe

```
# Knative (if not installed already)
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.17.0/serving-core.yaml

# Istio
kubectl apply -l knative.dev/crd-install=true -f https://github.com/knative/net-istio/releases/download/knative-v1.17.0/istio.yaml
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.17.0/istio.yaml
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.17.0/net-istio.yaml
kubectl label namespace knative-serving istio-injection=enabled
kubectl apply -f deployment/dev/knative/auth.yaml 
kubectl --namespace istio-system get service istio-ingressgateway

kubectl get pods -n knative-serving

# No DNS config (for dev environment)
kubectl patch configmap/config-domain \
      --namespace knative-serving \
      --type merge \
      --patch '{"data":{"example.com":""}}'

# Cert Manager (if not installed already)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.0/cert-manager.yaml
kubectl apply -f deployment/dev/certs/staging-issuer.yaml 
kubectl apply --server-side -f https://github.com/kserve/kserve/releases/download/v0.14.1/kserve.yaml
kubectl apply --server-side -f https://github.com/kserve/kserve/releases/download/v0.14.1/kserve-cluster-resources.yaml
```

### Secure InferenceService with ServiceMesh

```
kubectl create namespace user1
kubectl apply -f deployment/dev/kubeflow/peer-auth.yaml 

kubectl edit configmap/inferenceservice-config --namespace kserve

# ingress : |- {
#    "disableIstioVirtualHost": true # Add this flag to ingress section
# }

kubectl apply -f deployment/dev/kubeflow/gateway-patch.yaml
# Sidecar injection
kubectl label namespace user1 istio-injection=enabled --overwrite

# Add inference service
kubectl apply -f deployment/dev/kubeflow/sklearn-inference.yaml

# Make inference
kubectl apply -f deployment/dev/kubeflow/httpbin.yaml

kubectl get pod -n user1
kubectl exec -it httpbin-b56d8fdf-ss489 -c istio-proxy -n user1 -- curl -v sklearn-iris-predictor-default.user1.svc.cluster.local/v1/models/sklearn-iris # The podname will be different from httpbin-6484879498-qxqj8
kubectl exec -it httpbin-6484879498-qxqj8 -c istio-proxy -n user1 -- curl -v sklearn-iris-burst-predictor-default.user1.svc.cluster.local/v1/models/sklearn-iris-burst # The podname will be different from httpbin-6484879498-qxqj8
```

### KServe test run

Perform test run:

```
kubectl create namespace kserve-test
kubectl apply -f deployment/dev/kubeflow/sklearn-inference-test.yaml 

kubectl get inferenceservices sklearn-iris -n kserve-test
kubectl get svc istio-ingressgateway -n istio-system

# Port forwarding for testing
export INGRESS_HOST=worker-node-address # Change me based off external IP from above command
INGRESS_GATEWAY_SERVICE=$(kubectl get svc --namespace istio-system --selector="app=istio-ingressgateway" --output jsonpath='{.items[0].metadata.name}')
kubectl port-forward --namespace istio-system svc/${INGRESS_GATEWAY_SERVICE} 8080:80
```