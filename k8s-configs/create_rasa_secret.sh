#!/bin/sh

certificate=$(kubectl get secret rasa-webservice-ingress-tls -n rasax -o jsonpath="{.data['tls\\.crt']}" | base64 --decode)
private_key=$(kubectl get secret rasa-webservice-ingress-tls -n rasax -o jsonpath="{.data['tls\\.key']}" | base64 --decode)

echo "$private_key" | base64 > certificates/privkey.pem.b64
echo "$certificate" | base64 > certificates/fullchain.pem.b64

cat > rasa-tls-secret.yaml << EOF
apiVersion: "v1"
kind: "Secret"
metadata:
  name: rasa-tls-secret
  namespace: rasax
type: "Opaque"
stringData:
  privkey.pem: "$(cat certificates/privkey.pem.b64)"
  fullchain.pem: "$(cat certificates/fullchain.pem.b64)"
EOF

kubectl apply -f rasa-tls-secret.yaml