#!/bin/bash

set -e

PLANS_DIR="plans"
RESULTS_DIR="results"
CONTROL_FILE="$RESULTS_DIR/finished_runs.txt"
RUNS=2

mkdir -p "$RESULTS_DIR"
touch "$CONTROL_FILE"

for plan in "$PLANS_DIR"/*.jmx; do
    plan_name=$(basename "$plan" .jmx)
    plan_result_dir="$RESULTS_DIR/$plan_name"
    mkdir -p "$plan_result_dir"
    for i in $(seq 1 $RUNS); do
        run_id="${plan_name}/run_${i}.jtl"
        # Verifica se já foi executado
        if grep -Fxq "$run_id" "$CONTROL_FILE"; then
            echo "[SKIP] $run_id já executado."
            continue
        fi
        echo "[RUN] Executando $plan_name (run $i/$RUNS)"
        jmeter -n -t "$plan" -l "$plan_result_dir/run_${i}.jtl"
        echo "$run_id" >> "$CONTROL_FILE"
    done
done

echo "\nTodas as execuções planejadas foram concluídas!" 