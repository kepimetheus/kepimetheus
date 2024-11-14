# Kepimetheus

This project use Amazon Bedrock to transform natural language into Prometheus queries.
Please visit https://kepimetheus.github.io

## Overview

The Kubernetes operator in this project is responsible for:

1. Deploying a web interface that interacts with Amazon Bedrock.
2. Managing the lifecycle of this application in the Kubernetes cluster.
3. Handling the secure configuration of AWS credentials necessary for interacting with Amazon Bedrock.

## Building from source
To build and run Kepimetheus from source code, You need:

Python version 3.12.
Rust version 1.82 or greater.
Start by cloning the repository:

```sh
git clone https://github.com/kepimetheus/kepimetheus.git
cd kepimetheus
```

## Building the Docker image

Docker version 26 or greater
Start by cloning the repository:

```sh
git clone https://github.com/kepimetheus/kepimetheus.git
cd kepimetheus

docker build -t kepimetheus .
```

## Contributing

Contributions are welcome! Please open an issue to discuss proposed changes or submit a pull request.

## License

[Insert license information here]
