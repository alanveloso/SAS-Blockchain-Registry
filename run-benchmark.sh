#!/bin/bash
set -e

echo "Subindo rede Besu local..."
docker compose -f besu-compose.yaml up -d

echo "Aguardando Besu iniciar..."
sleep 10

echo "Compilando contratos..."
npx hardhat compile

echo "Rodando benchmark Caliper..."
npx caliper launch master \
  --caliper-workspace . \
  --caliper-benchconfig benchmark/cbsdregistry-benchmark.yaml \
  --caliper-networkconfig network-config.yaml

sudo ./run-benchmark.sh 