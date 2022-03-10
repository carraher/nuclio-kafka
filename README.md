# nuclio-kafka

Trigger nuclio.io functions over kafka as event message bus
Create a simple serverless flow using Kafka as messaging hub between Nuclio (Iguazio) functions.

# Overview

Flow between the Nuclio functions (in boxes).

[!](./function-flow.png)

# deploy

## minikube

Start minikube on supported version for Nuclio. Add some convenient aliases.
```sh
minikube start --kubernetes-version=v1.21.5 --driver=none
alias ka="kubectl get pods --all-namespaces"
alias kn="kubectl --namespace"
alias ks="kn kube-system"
alias knuc="kn nuclio"
```

Install docker-registry into k8s
```sh
REGISTRY_PORT=31500
helm repo add twuni https://helm.twun.io
helm install registry twuni/docker-registry \
  --version 1.10.0 \
  --namespace kube-system \
  --set service.type=NodePort \
  --set service.nodePort=$REGISTRY_PORT

REGISTRY=127.0.0.1:$REGISTRY_PORT
curl $REGISTRY/v2/_catalog | jq -c
```


Create `nuclio` namespace and deploy Kafka along with some topic queues
```sh
kubectl create namespace nuclio
knuc get deployments,pods,services,crds

helm repo add bitnami https://charts.bitnami.com/bitnami
KAFKA_NAME="kafka-hub"
helm install $KAFKA_NAME bitnami/kafka --namespace nuclio \
  --set persistence.enabled=false \
  --set zookeeper.persistence.enabled=false

KAFKA_POD_NAME="$KAFKA_NAME-0"
KAFKA_TOPIC_0="ingested"
KAFKA_TOPIC_1="mutated"
knuc exec -it $KAFKA_POD_NAME -- kafka-topics.sh --bootstrap-server kafka-hub.nuclio.svc.cluster.local:9092 --create --replication-factor 1 --partitions 1 --topic $KAFKA_TOPIC_0
knuc exec -it $KAFKA_POD_NAME -- kafka-topics.sh --bootstrap-server kafka-hub.nuclio.svc.cluster.local:9092 --create --replication-factor 1 --partitions 1 --topic $KAFKA_TOPIC_1
knuc exec -it $KAFKA_POD_NAME -- kafka-topics.sh --bootstrap-server kafka-hub.nuclio.svc.cluster.local:9092 --list
```

Deploy Nuclio

```sh
export NUCLIO_VERSION=1.4.14

knuc get deployments,pods,services,crds

helm repo add nuclio https://nuclio.github.io/nuclio/charts

NUCLIO_DASH_PORT=31000
helm install nuclio nuclio/nuclio \
  --version=0.6.14 \
  --namespace=nuclio \
  --set controller.image.tag=$NUCLIO_VERSION-amd64 \
  --set dashboard.nodePort=$NUCLIO_DASH_PORT

knuc get deployments,pods,services,crds


curl -L https://github.com/nuclio/nuclio/releases/download/$NUCLIO_VERSION/nuctl-$NUCLIO_VERSION-linux-amd64 -o /usr/local/bin/nuctl && chmod +x /usr/local/bin/nuctl
nuctl --help && nuctl version
```

Import Nuclio Kafka functions
```sh
nuctl import functions -n nuclio ./ingest/function.yaml
nuctl import functions -n nuclio ./mutate/function.yaml
nuctl import functions -n nuclio ./sink/function.yaml

nuctl -n nuclio get functions
```


Tail all 3 containers' k8s logs and send some test json to the first service
```sh
knuc logs -f $(knuc get pod -l nuclio.io/function-name=ingest -o jsonpath='{.items[0].metadata.name}') &
knuc logs -f $(knuc get pod -l nuclio.io/function-name=mutate -o jsonpath='{.items[0].metadata.name}') &
knuc logs -f $(knuc get pod -l nuclio.io/function-name=sink -o jsonpath='{.items[0].metadata.name}') &

INGEST_FUNC_PORT=$(nuctl -n nuclio get functions | grep ingest | awk '{print $9}')
curl -X POST -H "Content-Type: application/json" -d '{ "messagedata": "original"}' "http://127.0.0.1:$INGEST_FUNC_PORT/"
```

### katacoda

katacoda webproxies behind TLS for you

```sh
HOST_SUBDOMAIN="your assigned 10 digit subdomain"
KATACODA_HOST="elsy04.environments.katacoda.com"

export REGISTRY="$HOST_SUBDOMAIN-$REGISTRY_PORT-$KATACODA_HOST"
curl $REGISTRY/v2/_catalog | jq -c

echo "https://$HOST_SUBDOMAIN-$NUCLIO_DASH_PORT-$KATACODA_HOST"



echo'alias ka="kubectl get pods --all-namespaces"
alias kn="kubectl --namespace"
alias ks="kn kube-system"
alias knuc="kn nuclio"' >>~/.bashrc
source ~/.bashrc

tmux
```