# OpenMetadata Helm ArgoCD

GitOps test deployment of OpenMetadata via Helm and ArgoCD

# Table of contents

- [OpenMetadata Helm ArgoCD](#openmetadata-helm-argocd)
- [Table of contents](#table-of-contents)
- [Installation](#installation)
  - [Install kubectl](#install-kubectl)
  - [Install helm](#install-helm)
  - [Install kind](#install-kind)
  - [Install ArgoCD](#install-argocd)
  - [Install NGINX Ingress Operator](#install-nginx-ingress-operator)
  - [Test MinIO](#test-minio)
  
# Installation

## Install kubectl 

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

## Install helm

```
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

## Install kind

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

## Install ArgoCD

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

## Install NGINX Ingress Operator

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

````
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

## Test MinIO

