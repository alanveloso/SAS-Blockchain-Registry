#!/bin/bash

set -e

PLANS_DIR="plans"
RESULTS_DIR="results"
CONTROL_FILE="$RESULTS_DIR/finished_runs.txt"
RUNS=2

# Backup dos resultados anteriores, se existirem
echo "[INFO] Verificando resultados anteriores..."
if [ -d "$RESULTS_DIR" ]; then
  TS=$(date +%Y%m%d_%H%M%S)
  mv "$RESULTS_DIR" "${RESULTS_DIR}_bkp_$TS"
  echo "[BACKUP] Resultados anteriores movidos para ${RESULTS_DIR}_bkp_$TS"
fi

mkdir -p "$RESULTS_DIR"
touch "$CONTROL_FILE"

for plan in "$PLANS_DIR"/sas_full_flow_*.jmx; do
    plan_name=$(basename "$plan" .jmx)
    plan_result_dir="$RESULTS_DIR/$plan_name"
    mkdir -p "$plan_result_dir"
    for i in $(seq 1 $RUNS); do
        ts=$(date +%Y%m%d_%H%M%S)
        result_file="$plan_result_dir/run_${i}_$ts.jtl"
        run_id="${plan_name}/run_${i}_$ts.jtl"
        # Verifica se já foi executado
        if grep -Fxq "$run_id" "$CONTROL_FILE"; then
            echo "[SKIP] $run_id já executado."
            continue
        fi
        echo "[RUN] Executando $plan_name (run $i/$RUNS) -> $result_file"
        jmeter -n -t "$plan" -l "$result_file"
        echo "$run_id" >> "$CONTROL_FILE"
    done
    echo "[OK] $plan_name finalizado. Resultados em $plan_result_dir/"
done

echo -e "\n🎉 Todas as execuções dos planos full flow foram concluídas!" 