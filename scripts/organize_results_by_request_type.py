import os
import csv
from collections import defaultdict

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')

# Função para processar um arquivo .jtl
def process_jtl_file(jtl_path, output_dir):
    with open(jtl_path, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        header = reader.fieldnames
        if header is None:
            print(f"Arquivo {jtl_path} sem cabeçalho, pulando.")
            return
        rows_by_label = defaultdict(list)
        for row in reader:
            label = row['label']
            rows_by_label[label].append(row)

    for label, rows in rows_by_label.items():
        label_dir = os.path.join(output_dir, label)
        os.makedirs(label_dir, exist_ok=True)
        out_path = os.path.join(label_dir, os.path.basename(jtl_path))
        with open(out_path, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows)


def main():
    for root, dirs, files in os.walk(RESULTS_DIR):
        # Só processa diretórios de nível 1 (ex: sas_full_flow_high)
        if root == RESULTS_DIR:
            for d in dirs:
                bench_dir = os.path.join(root, d)
                for fname in os.listdir(bench_dir):
                    if fname.endswith('.jtl'):
                        jtl_path = os.path.join(bench_dir, fname)
                        process_jtl_file(jtl_path, bench_dir)

if __name__ == '__main__':
    main() 