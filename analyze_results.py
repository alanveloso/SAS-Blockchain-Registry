#!/usr/bin/env python
# coding: utf-8
"""
Análise Estatística dos Resultados de Performance (JMeter .jtl)
Este script lê e analisa automaticamente os arquivos de resultados de testes de performance localizados em 'results/',
gerando estatísticas, gráficos e relatórios para facilitar a avaliação dos experimentos.

Uso:
    python analyze_results.py

Dependências:
    pip install pandas numpy matplotlib seaborn
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List
import matplotlib.ticker as mticker

# Configurações globais de visualização
sns.set(style='whitegrid', palette='Set2')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 13
plt.rcParams['legend.fontsize'] = 11

RESULTS_DIR = 'results'
OUTPUT_DIR = 'analysis_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Ordem fixa dos cenários para os gráficos e tabelas
SCENARIO_LABELS = {
    'sas_full_flow_low': 'Low',
    'sas_full_flow_medium': 'Medium',
    'sas_full_flow_high': 'High',
    'sas_full_flow_stress': 'Stress',
}
SCENARIO_ORDER = ['Low', 'Medium', 'High', 'Stress']

def get_scenario_label(scenario):
    return SCENARIO_LABELS.get(scenario, scenario)

def normalize_request_type(request_type):
    """Normaliza o nome do tipo de requisição para evitar duplicatas por diferenças de formatação."""
    if pd.isna(request_type):
        return 'unknown'
    
    # Converte para string, remove espaços extras e converte para minúsculas
    normalized = str(request_type).strip().lower()
    
    # Remove caracteres especiais comuns que podem causar problemas
    normalized = normalized.replace('_', '').replace('-', '').replace(' ', '')
    
    # Mapeamento específico para tipos conhecidos
    request_type_mapping = {
        'authorize': 'Authorize',
        'authorize_': 'Authorize',
        'registration': 'Registration',
        'registration_': 'Registration',
        'grant': 'Grant',
        'grant_': 'Grant',
        'revoke': 'Revoke',
        'revoke_': 'Revoke',
        'relinquishment': 'Relinquishment',
        'relinquishment_': 'Relinquishment',
        'deregistration': 'Deregistration',
        'deregistration_': 'Deregistration',
    }
    
    # Se encontrou no mapeamento, usa o valor mapeado
    if normalized in request_type_mapping:
        return request_type_mapping[normalized]
    
    # Caso contrário, capitaliza a primeira letra para manter consistência
    if normalized:
        normalized = normalized.capitalize()
    
    return normalized

def get_jtl_files(base=RESULTS_DIR) -> List[Path]:
    """Busca recursiva por arquivos .jtl no diretório base."""
    return sorted(Path(base).rglob('*.jtl'))

def parse_metadata(fp: Path):
    parts = fp.parts
    scenario = parts[1] if len(parts) > 2 else 'unknown'
    run_id = fp.stem.split('_')[1] if '_' in fp.stem else '1'
    return scenario, run_id

def load_data(jtl_files: List[Path]) -> pd.DataFrame:
    """Lê todos os arquivos .jtl e concatena em um único DataFrame, com tratamento de erros."""
    dfs = []
    for f in jtl_files:
        try:
            df = pd.read_csv(f)
            scenario, run_id = parse_metadata(f)
            df['scenario'] = scenario
            df['run'] = run_id
            df['request_type'] = df['label'] if 'label' in df.columns else 'unknown'
            # Normaliza os nomes dos tipos de requisição
            df['request_type'] = df['request_type'].apply(normalize_request_type)
            dfs.append(df)
        except Exception as e:
            print(f"[ERRO] Falha ao ler {f}: {e}")
    if dfs:
        all_data = pd.concat(dfs, ignore_index=True)
        print(f"[INFO] Total de linhas carregadas: {len(all_data)}")
        
        # Mostra os tipos de requisição encontrados após normalização
        unique_types = sorted(all_data['request_type'].unique())
        print(f"[INFO] Tipos de requisição encontrados: {unique_types}")
        
        # Cálculo do tempo relativo (em segundos desde o início de cada run)
        if 'timeStamp' in all_data.columns:
            all_data['timeStamp'] = pd.to_datetime(all_data['timeStamp'], unit='ms')
            all_data['time_rel'] = (
                all_data.groupby(['scenario','run'])['timeStamp']
                .transform(lambda ts: (ts - ts.min()).dt.total_seconds())
            )
        return all_data
    else:
        print("[ERRO] Nenhum dado carregado.")
        return pd.DataFrame()

def calc_stats(all_data: pd.DataFrame) -> pd.DataFrame:
    """Calcula estatísticas descritivas por cenário, tipo e run."""
    if 'elapsed' not in all_data.columns:
        print("[ERRO] Coluna 'elapsed' não encontrada.")
        return pd.DataFrame()
    per_run = (
        all_data
        .groupby(['scenario','request_type','run'])['elapsed']
        .agg(
          count='count',
          mean='mean',
          p50=lambda x: x.median(),
          p90=lambda x: np.percentile(x, 90),
          p99=lambda x: np.percentile(x, 99),
          std='std'
        )
        .reset_index()
    )
    per_run.to_csv(f'{OUTPUT_DIR}/stats_per_run.csv', index=False)
    print(f"[INFO] Estatísticas por run salvas em {OUTPUT_DIR}/stats_per_run.csv")
    return per_run

def plot_latency_boxplot(all_data: pd.DataFrame, request_type_order=None):
    """Generates statistical aggregation plots and individual run plots for latency."""
    if 'elapsed' not in all_data.columns:
        print("[ERROR] Column 'elapsed' not found for latency.")
        return
    all_data = all_data.copy()
    all_data['scenario_label'] = all_data['scenario'].map(get_scenario_label)
    
    # Calculate statistics per run
    stats = []
    for (scenario, req_type, run), grp in all_data.groupby(['scenario','request_type','run']):
        lat = grp['elapsed']
        stats.append({
            'scenario': get_scenario_label(scenario),
            'request_type': req_type,
            'run': run,
            'mean': float(lat.mean()),
            'median': float(lat.median()),
            'std': float(lat.std()),
            'min': float(lat.min()),
            'max': float(lat.max()),
            'p90': float(np.percentile(lat, 90)),
            'p95': float(np.percentile(lat, 95)),
            'p99': float(np.percentile(lat, 99))
        })
    df_stats = pd.DataFrame(stats)
    # Ensure scenario order in export
    df_stats['scenario'] = pd.Categorical(df_stats['scenario'], categories=SCENARIO_ORDER, ordered=True)
    df_stats = df_stats.sort_values(['scenario', 'request_type', 'run'])
    df_stats.to_csv(f'{OUTPUT_DIR}/latency_stats.csv', index=False)
    print(f"[INFO] Latency statistics saved to {OUTPUT_DIR}/latency_stats.csv")

    # --- INCONSISTÊNCIA ENTRE RUNS: LATÊNCIA ---
    inconsistency = (
        df_stats.groupby(['scenario', 'request_type'])['mean']
        .agg(['mean', 'std', 'min', 'max', 'count'])
        .reset_index()
        .sort_values('std', ascending=False)
    )
    inconsistency.to_csv(f'{OUTPUT_DIR}/latency_mean_inconsistency.csv', index=False)
    print("[INFO] Inconsistência (desvio padrão) da latência média entre runs:")
    print(inconsistency[['scenario', 'request_type', 'std']].head(10))
    
    # Generate statistical aggregation plots (distribution of statistics across runs)
    for metric in ['mean', 'median', 'p95', 'p99']:
        plt.figure(figsize=(10,6))
        sns.boxplot(data=df_stats, x='scenario', y=metric, hue='request_type', 
                    hue_order=request_type_order, order=SCENARIO_ORDER, showfliers=False)
        plt.yscale('log')
        plt.title(f'Latency {metric.capitalize()} (ms) - Distribution Across Runs')
        plt.xlabel('Scenario')
        plt.ylabel(f'Latency {metric.capitalize()} (ms)')
        plt.legend(title='Request Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/boxplot_latency_{metric}_stats.png')
        plt.close()
        print(f"[INFO] Latency {metric} statistics boxplot saved: {OUTPUT_DIR}/boxplot_latency_{metric}_stats.png")
    
    # Generate separate boxplot for each run
    for run_id in sorted(all_data['run'].unique()):
        run_data = all_data[all_data['run'] == run_id].copy()
        if run_data.empty:
            continue
            
        plt.figure(figsize=(10,6))
        sns.boxplot(data=run_data, x='scenario_label', y='elapsed', hue='request_type', 
                    hue_order=request_type_order, order=SCENARIO_ORDER, showfliers=False)
        plt.yscale('log')
        plt.title(f'Latency Boxplot (ms) - Run {run_id}')
        plt.xlabel('Scenario')
        plt.ylabel('Latency (ms)')
        plt.legend(title='Request Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/boxplot_latency_Run{run_id}.png')
        plt.close()
        print(f"[INFO] Latency boxplot for Run {run_id} saved: {OUTPUT_DIR}/boxplot_latency_Run{run_id}.png")

def plot_throughput_boxplot(all_data: pd.DataFrame, request_type_order=None):
    """Generates statistical aggregation plots and individual run plots for throughput."""
    if 'time_rel' not in all_data.columns:
        print("[ERROR] Column 'time_rel' not found for throughput.")
        return
    all_data = all_data.copy()
    all_data['time_rel_rounded'] = all_data['time_rel'].round().astype(int)
    all_data['scenario_label'] = all_data['scenario'].map(get_scenario_label)
    
    # Calculate statistics per run
    stats = []
    for (scenario, req_type, run), grp in all_data.groupby(['scenario','request_type','run']):
        ts = grp.groupby('time_rel_rounded').size()
        stats.append({
            'scenario': get_scenario_label(scenario),
            'request_type': req_type,
            'run': run,
            'mean': float(ts.mean()),
            'median': float(ts.median()),
            'std': float(ts.std()),
            'min': float(ts.min()),
            'max': float(ts.max()),
            'p90': float(np.percentile(ts, 90)),
            'p95': float(np.percentile(ts, 95)),
            'p99': float(np.percentile(ts, 99))
        })
    df_stats = pd.DataFrame(stats)
    # Ensure scenario order in export
    df_stats['scenario'] = pd.Categorical(df_stats['scenario'], categories=SCENARIO_ORDER, ordered=True)
    df_stats = df_stats.sort_values(['scenario', 'request_type', 'run'])
    df_stats.to_csv(f'{OUTPUT_DIR}/throughput_stats.csv', index=False)
    print(f"[INFO] Throughput statistics saved to {OUTPUT_DIR}/throughput_stats.csv")

    # --- INCONSISTÊNCIA ENTRE RUNS: THROUGHPUT ---
    inconsistency = (
        df_stats.groupby(['scenario', 'request_type'])['mean']
        .agg(['mean', 'std', 'min', 'max', 'count'])
        .reset_index()
        .sort_values('std', ascending=False)
    )
    inconsistency.to_csv(f'{OUTPUT_DIR}/throughput_mean_inconsistency.csv', index=False)
    print("[INFO] Inconsistência (desvio padrão) do throughput médio entre runs:")
    print(inconsistency[['scenario', 'request_type', 'std']].head(10))
    
    # Generate statistical aggregation plots (distribution of statistics across runs)
    for metric in ['mean', 'median', 'p95', 'p99']:
        plt.figure(figsize=(10,6))
        sns.boxplot(data=df_stats, x='scenario', y=metric, hue='request_type', 
                    hue_order=request_type_order, order=SCENARIO_ORDER, showfliers=False)
        plt.title(f'Throughput {metric.capitalize()} (req/s) - Distribution Across Runs')
        plt.xlabel('Scenario')
        plt.ylabel(f'Throughput {metric.capitalize()} (req/s)')
        plt.legend(title='Request Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/boxplot_throughput_{metric}_stats.png')
        plt.close()
        print(f"[INFO] Throughput {metric} statistics boxplot saved: {OUTPUT_DIR}/boxplot_throughput_{metric}_stats.png")
    
    # Generate separate boxplot for each run (using raw throughput data)
    throughput_data = []
    for (scenario, req_type, run), grp in all_data.groupby(['scenario','request_type','run']):
        ts = grp.groupby('time_rel_rounded').size()
        for v in ts:
            throughput_data.append({
                'scenario': get_scenario_label(scenario), 
                'request_type': req_type, 
                'run': run,
                'throughput': v
            })
    df_throughput = pd.DataFrame(throughput_data)
    
    if not df_throughput.empty:
        for run_id in sorted(df_throughput['run'].unique()):
            run_throughput = df_throughput[df_throughput['run'] == run_id].copy()
            if run_throughput.empty:
                continue
                
            plt.figure(figsize=(10,6))
            sns.boxplot(data=run_throughput, x='scenario', y='throughput', hue='request_type', 
                        hue_order=request_type_order, order=SCENARIO_ORDER, showfliers=False)
            plt.title(f'Throughput Boxplot (req/s) - Run {run_id}')
            plt.xlabel('Scenario')
            plt.ylabel('Requests per second')
            plt.legend(title='Request Type', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig(f'{OUTPUT_DIR}/boxplot_throughput_Run{run_id}.png')
            plt.close()
            print(f"[INFO] Throughput boxplot for Run {run_id} saved: {OUTPUT_DIR}/boxplot_throughput_Run{run_id}.png")

def plot_error_rate_barplot(all_data: pd.DataFrame, request_type_order=None):
    """Generates statistical aggregation plots and individual run plots for error rate."""
    if 'success' not in all_data.columns:
        print("[ERROR] Column 'success' not found for error rate.")
        return
    all_data = all_data.copy()
    all_data['is_error'] = ~all_data['success'].astype(bool)
    all_data['scenario_label'] = all_data['scenario'].map(get_scenario_label)
    
    # Calculate statistics per run
    stats = (
        all_data.groupby(['scenario','request_type','run'])['is_error']
        .agg(['mean','std','min','max'])
        .reset_index()
        .rename(columns={'mean':'error_rate_mean','std':'error_rate_std','min':'error_rate_min','max':'error_rate_max'})
    )
    # Replace scenario names in export and ensure order
    stats['scenario'] = stats['scenario'].map(get_scenario_label)
    stats['scenario'] = pd.Categorical(stats['scenario'], categories=SCENARIO_ORDER, ordered=True)
    stats = stats.sort_values(['scenario', 'request_type', 'run'])
    stats.to_csv(f'{OUTPUT_DIR}/error_rate_stats.csv', index=False)
    print(f"[INFO] Error rate statistics saved to {OUTPUT_DIR}/error_rate_stats.csv")

    # --- INCONSISTÊNCIA ENTRE RUNS: TAXA DE ERRO ---
    inconsistency = (
        stats.groupby(['scenario', 'request_type'])['error_rate_mean']
        .agg(['mean', 'std', 'min', 'max', 'count'])
        .reset_index()
        .sort_values('std', ascending=False)
    )
    inconsistency.to_csv(f'{OUTPUT_DIR}/error_rate_mean_inconsistency.csv', index=False)
    print("[INFO] Inconsistência (desvio padrão) da taxa de erro média entre runs:")
    print(inconsistency[['scenario', 'request_type', 'std']].head(10))
    
    # Generate statistical aggregation plots (distribution of statistics across runs)
    for metric in ['error_rate_mean', 'error_rate_std']:
        plt.figure(figsize=(10,6))
        sns.boxplot(data=stats, x='scenario', y=metric, hue='request_type', 
                    hue_order=request_type_order, order=SCENARIO_ORDER, showfliers=False)
        metric_name = metric.replace('error_rate_', '').capitalize()
        plt.title(f'Error Rate {metric_name} - Distribution Across Runs')
        plt.xlabel('Scenario')
        plt.ylabel(f'Error Rate {metric_name}')
        plt.legend(title='Request Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/boxplot_error_rate_{metric.replace("error_rate_", "")}_stats.png')
        plt.close()
        print(f"[INFO] Error rate {metric_name} statistics boxplot saved: {OUTPUT_DIR}/boxplot_error_rate_{metric.replace('error_rate_', '')}_stats.png")
    
    # Generate separate barplot for each run
    for run_id in sorted(all_data['run'].unique()):
        run_data = all_data[all_data['run'] == run_id].copy()
        if run_data.empty:
            continue
            
        plt.figure(figsize=(10,6))
        sns.barplot(data=run_data, x='scenario_label', y='is_error', hue='request_type', 
                    hue_order=request_type_order, order=SCENARIO_ORDER, estimator=np.mean)
        plt.title(f'Mean Error Rate - Run {run_id}')
        plt.xlabel('Scenario')
        plt.ylabel('Mean error rate')
        plt.legend(title='Request Type', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'{OUTPUT_DIR}/barplot_error_rate_Run{run_id}.png')
        plt.close()
        print(f"[INFO] Error rate barplot for Run {run_id} saved: {OUTPUT_DIR}/barplot_error_rate_Run{run_id}.png")

def export_reports(all_data: pd.DataFrame):
    """Exporta tabelas de códigos de resposta e erros para CSV."""
    if 'responseCode' in all_data.columns:
        resp = (
            all_data
            .groupby(['scenario','request_type','responseCode'])
            .size()
            .reset_index(name='count')
            .sort_values(['scenario','request_type','count'], ascending=[True,True,False])
        )
        resp.to_csv(f'{OUTPUT_DIR}/response_codes.csv', index=False)
        print(f"[INFO] Tabela de responseCode salva em {OUTPUT_DIR}/response_codes.csv")
    if 'success' in all_data.columns and 'failureMessage' in all_data.columns:
        erros = all_data[all_data['success'] == False]
        if not erros.empty:
            # Garantir que as colunas existem antes de exportar
            cols = [c for c in ['timeStamp','label','responseCode','responseMessage','failureMessage','scenario','request_type','run'] if c in erros.columns]
            erros[cols].to_csv(f'{OUTPUT_DIR}/erros.csv', index=False)
            print(f"[INFO] Tabela de erros salva em {OUTPUT_DIR}/erros.csv")

def tail_latency_stats(all_data: pd.DataFrame):
    """Calculates and exports advanced percentiles (p95, p99, p99.9) for latency by scenario, request type and run."""
    stats = []
    for (scenario, req_type, run), grp in all_data.groupby(['scenario','request_type','run']):
        lat = grp['elapsed']
        stats.append({
            'scenario': get_scenario_label(scenario),
            'request_type': req_type,
            'run': run,
            'p95': float(np.percentile(lat, 95)),
            'p99': float(np.percentile(lat, 99)),
            'p999': float(np.percentile(lat, 99.9)),
            'max': float(lat.max()),
            'count': int(len(lat))
        })
    df_stats = pd.DataFrame(stats)
    df_stats['scenario'] = pd.Categorical(df_stats['scenario'], categories=SCENARIO_ORDER, ordered=True)
    df_stats = df_stats.sort_values(['scenario', 'request_type', 'run'])
    df_stats.to_csv(f'{OUTPUT_DIR}/tail_latency_stats.csv', index=False)
    print(f"[INFO] Tail latency percentiles saved to {OUTPUT_DIR}/tail_latency_stats.csv")
    print(df_stats)

def tail_throughput_stats(all_data: pd.DataFrame):
    """Calculates and exports advanced percentiles (p95, p99, p99.9) for throughput by scenario, request type and run."""
    if 'time_rel' not in all_data.columns:
        print("[ERROR] Column 'time_rel' not found for tail throughput stats.")
        return
    all_data = all_data.copy()
    all_data['time_rel_rounded'] = all_data['time_rel'].round().astype(int)
    throughput_data = []
    for (scenario, req_type, run), grp in all_data.groupby(['scenario','request_type','run']):
        ts = grp.groupby('time_rel_rounded').size()
        throughput_data.append({
            'scenario': get_scenario_label(scenario),
            'request_type': req_type,
            'run': run,
            'p95': float(np.percentile(ts, 95)) if len(ts) > 0 else np.nan,
            'p99': float(np.percentile(ts, 99)) if len(ts) > 0 else np.nan,
            'p999': float(np.percentile(ts, 99.9)) if len(ts) > 0 else np.nan,
            'max': float(ts.max()) if len(ts) > 0 else np.nan,
            'count': int(len(ts))
        })
    df_stats = pd.DataFrame(throughput_data)
    df_stats['scenario'] = pd.Categorical(df_stats['scenario'], categories=SCENARIO_ORDER, ordered=True)
    df_stats = df_stats.sort_values(['scenario', 'request_type', 'run'])
    df_stats.to_csv(f'{OUTPUT_DIR}/tail_throughput_stats.csv', index=False)
    print(f"[INFO] Tail throughput percentiles saved to {OUTPUT_DIR}/tail_throughput_stats.csv")
    print(df_stats)

def plot_latency_by_type(all_data: pd.DataFrame):
    """Gera boxplots de latência por tipo de requisição, comparando cenários."""
    yticks = [10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
    for req_type in all_data['request_type'].unique():
        subset = all_data[all_data['request_type'] == req_type].copy()
        if subset.empty:
            continue
        subset['scenario_label'] = subset['scenario'].map(get_scenario_label)
        plt.figure(figsize=(8,5))
        sns.boxplot(
            data=subset,
            x='scenario_label',
            y='elapsed',
            order=SCENARIO_ORDER,
            showfliers=False
        )
        plt.yscale('log')
        plt.ylim(10, 10000)
        plt.yticks(yticks, [str(y) for y in yticks])
        plt.grid(which='major', axis='y', linestyle='-', linewidth=1, alpha=0.8)
        plt.title(f'Latency (ms) — {req_type}')
        plt.xlabel('Scenario')
        plt.ylabel('Latency (ms)')
        plt.tight_layout()
        fname = f'{OUTPUT_DIR}/boxplot_latency_{req_type}.png'.replace(' ', '_')
        plt.savefig(fname)
        plt.close()
        print(f"[INFO] Latency boxplot by type saved: {fname}")

def plot_throughput_by_type(all_data: pd.DataFrame):
    """Gera boxplots de throughput por tipo de requisição, comparando cenários, todos alinhados com o mesmo limite de eixo y."""
    if 'time_rel' not in all_data.columns:
        print("[ERROR] Column 'time_rel' not found for throughput by type.")
        return
    all_data = all_data.copy()
    all_data['time_rel_rounded'] = all_data['time_rel'].round().astype(int)
    all_data['scenario_label'] = all_data['scenario'].map(get_scenario_label)
    throughput_data = []
    for (scenario, req_type), grp in all_data.groupby(['scenario','request_type']):
        ts = grp.groupby('time_rel_rounded').size()
        for v in ts:
            throughput_data.append({'scenario': get_scenario_label(scenario), 'request_type': req_type, 'throughput': v})
    df_throughput = pd.DataFrame(throughput_data)
    # Calcular o maior throughput global
    if not df_throughput.empty:
        max_throughput_global = df_throughput['throughput'].max()
    else:
        max_throughput_global = 10
    y_max = max(10, max_throughput_global * 1.1)
    # Definir yticks globais
    if y_max <= 20:
        yticks = np.arange(0, y_max+1, 2)
    elif y_max <= 50:
        yticks = np.arange(0, y_max+1, 5)
    else:
        yticks = np.arange(0, y_max+1, 10)
    for req_type in df_throughput['request_type'].unique():
        subset = df_throughput[df_throughput['request_type'] == req_type].copy()
        if subset.empty:
            continue
        subset['scenario_label'] = subset['scenario'].map(get_scenario_label)
        subset['scenario_label'] = pd.Categorical(subset['scenario_label'], categories=SCENARIO_ORDER, ordered=True)
        plt.figure(figsize=(8,5))
        sns.boxplot(
            data=subset,
            x='scenario_label',
            y='throughput',
            order=SCENARIO_ORDER,
            showfliers=False
        )
        plt.ylim(0, y_max)
        plt.yticks(yticks)
        plt.grid(which='major', axis='y', linestyle='-', linewidth=1, alpha=0.8)
        plt.title(f'Throughput (req/s) — {req_type}')
        plt.xlabel('Scenario')
        plt.ylabel('Requests per second')
        plt.tight_layout()
        fname = f'{OUTPUT_DIR}/boxplot_throughput_{req_type}.png'.replace(' ', '_')
        plt.savefig(fname)
        plt.close()
        print(f"[INFO] Throughput boxplot by type saved: {fname}")

def plot_error_rate_by_type(all_data: pd.DataFrame):
    """Gera gráficos de barra da taxa de erro por tipo de requisição, comparando cenários."""
    all_data = all_data.copy()
    all_data['is_error'] = ~all_data['success'].astype(bool)
    for req_type in all_data['request_type'].unique():
        subset = all_data[all_data['request_type'] == req_type].copy()
        if subset.empty:
            continue
        subset['scenario_label'] = subset['scenario'].map(get_scenario_label)
        plt.figure(figsize=(8,5))
        sns.barplot(
            data=subset,
            x='scenario_label',
            y='is_error',
            order=SCENARIO_ORDER,
            estimator=np.mean
        )
        plt.ylim(0, 1)
        plt.yticks(np.arange(0, 1.05, 0.1))
        plt.title(f'Mean Error Rate — {req_type}')
        plt.xlabel('Scenario')
        plt.ylabel('Mean error rate')
        plt.tight_layout()
        fname = f'{OUTPUT_DIR}/barplot_error_rate_{req_type}.png'.replace(' ', '_')
        plt.savefig(fname)
        plt.close()
        print(f"[INFO] Error rate barplot by type saved: {fname}")

def main():
    print("[INFO] Searching for .jtl files...")
    jtl_files = get_jtl_files()
    print(f"[INFO] {len(jtl_files)} files found.")
    all_data = load_data(jtl_files)
    if all_data.empty:
        print("[ERROR] No data to analyze.")
        return
    calc_stats(all_data)
    request_type_order = sorted(all_data['request_type'].unique())
    plot_latency_boxplot(all_data, request_type_order=request_type_order)
    plot_throughput_boxplot(all_data, request_type_order=request_type_order)
    plot_error_rate_barplot(all_data, request_type_order=request_type_order)
    tail_latency_stats(all_data)
    tail_throughput_stats(all_data)
    plot_latency_by_type(all_data)
    plot_throughput_by_type(all_data)
    plot_error_rate_by_type(all_data)
    export_reports(all_data)
    print(f"[INFO] Analysis completed. Results in: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()


