# Web Interface Kubernetes Operator

This project implements a Kubernetes operator that manages the deployment of a web interface using Amazon Bedrock to transform natural language into Prometheus queries.

## Overview

The Kubernetes operator in this project is responsible for:

1. Deploying a web interface that interacts with Amazon Bedrock.
2. Managing the lifecycle of this application in the Kubernetes cluster.
3. Handling the secure configuration of AWS credentials necessary for interacting with Amazon Bedrock.

## Prerequisites

- Kubernetes cluster (version 1.16+)
- kubectl configured to communicate with your cluster
- AWS credentials with appropriate permissions to access Amazon Bedrock
- Docker (for building the operator image, if necessary)

## Project Structure

```
.
├── README.md
├── operator-deployment.yaml
└── aws-credentials-secret.yaml
```

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/web-interface-operator.git
   cd web-interface-operator
   ```

2. Edit the `aws-credentials-secret.yaml` file and replace the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` values with your actual AWS credentials:
   ```yaml
   stringData:
     AWS_ACCESS_KEY_ID: your_access_key_here
     AWS_SECRET_ACCESS_KEY: your_secret_key_here
   ```

3. Apply the secret to the cluster:
   ```
   kubectl apply -f aws-credentials-secret.yaml
   ```

4. Edit the `operator-deployment.yaml` file and replace `your-registry/web-interface-operator:v1` with the actual location of your operator image.

5. Apply the operator deployment:
   ```
   kubectl apply -f operator-deployment.yaml
   ```

## Usage

After installation, the operator will be running in the `web-interface-operator-system` namespace. It will monitor the cluster for custom resources that represent instances of the web interface.

To create a new instance of the web interface, you'll need to create a custom resource (the exact definition will depend on how you've implemented the operator).

## Development

If you need to make changes to the operator:

1. Modify the operator's source code as needed.
2. Build a new Docker image:
   ```
   docker build -t your-registry/web-interface-operator:new-tag .
   ```
3. Push the new image to the registry:
   ```
   docker push your-registry/web-interface-operator:new-tag
   ```
4. Update the `operator-deployment.yaml` file with the new image tag.
5. Apply the changes:
   ```
   kubectl apply -f operator-deployment.yaml
   ```

## Troubleshooting

If you encounter issues, check the operator logs:
```
kubectl logs -f deployment/web-interface-operator -n web-interface-operator-system
```

## Security

- Never commit the `aws-credentials-secret.yaml` file to a code repository.
- Consider using more robust secret management solutions in production environments.
- Implement regular credential rotation.

## Contributing

Contributions are welcome! Please open an issue to discuss proposed changes or submit a pull request.

## License

[Insert license information here]
