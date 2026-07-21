import json, os, re, zipfile, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import date

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "dados" / "entrada"
VALIDACAO = RAIZ / "dados" / "validacao"
ENTRADA.mkdir(parents=True, exist_ok=True)
VALIDACAO.mkdir(parents=True, exist_ok=True)

dls = os.path.join(os.environ['USERPROFILE'], 'Downloads')
ods_file = None
for f in os.listdir(dls):
    if 'ATUALIZA' in f.upper() and f.endswith('.ods') and not f.startswith('~$'):
        ods_file = os.path.join(dls, f)
        break

if not ods_file:
    raise FileNotFoundError("Arquivo ODS não encontrado em Downloads")

print(f"Lendo: {ods_file}")

with zipfile.ZipFile(ods_file) as z:
    content = z.read('content.xml').decode('utf-8')
root = ET.fromstring(content)
T = '{urn:oasis:names:tc:opendocument:xmlns:table:1.0}'
TEXT = '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}'

all_tables = root.findall(f'.//{T}table')

def cell_text(cell):
    p = cell.find(f'.//{TEXT}p')
    return p.text if p is not None else ''

def parse_date_ods(dstr):
    """Converte '01/07/25', '1/6/2018' para date."""
    dstr = (dstr or '').strip()
    if not dstr:
        return None
    parts = dstr.split('/')
    if len(parts) == 3:
        d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
        if y < 100:
            y += 2000
        return date(y, m, d)
    return None

def parse_comp_from_date(d):
    """Converte date para 'MM/AAAA'."""
    return f"{d.month:02d}/{d.year}"

def moeda_para_float(txt):
    """'R$ 1.872,37' -> 1872.37"""
    if not txt:
        return 0.0
    txt = str(txt).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.').strip()
    return float(txt) if txt else 0.0

def parse_factor(txt):
    """'0,01306' -> 0.01306. Retorna None se não for número válido."""
    if not txt:
        return None
    txt = str(txt).replace(',', '.').strip()
    try:
        v = float(txt)
        return v if v > 0 else None
    except ValueError:
        return None

# Extract beneficiaries from all monthly sheets (indices 5 to 17)
beneficiarios = {}  # key: (nome_limpo, matricula)
referencia = {}     # key: (nome_limpo, matricula) -> list of parcels

for table_idx in [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]:
    t = all_tables[table_idx]
    sheet_name = t.get(T + 'name', '?')
    rows = t.findall(f'.//{T}table-row')
    print(f"\nProcessando aba: {sheet_name} ({len(rows)} linhas)")

    i = 0
    while i < len(rows):
        cells = rows[i].findall(f'.//{T}table-cell')
        vals = [cell_text(c) for c in cells]

        first_val = (vals[0] or '').strip()
        if not first_val:
            i += 1
            continue

        if first_val and 'NOME:' in first_val.upper():
            nome_linha = str(vals[1] if len(vals) > 1 and vals[1] else '')
            orgao = str(vals[3] if len(vals) > 3 and vals[3] else '')

            m_mat = re.search(r'MATR[^A-Za-z0-9]*CULA\s+(\S+)', nome_linha, re.IGNORECASE)
            if not m_mat:
                m_mat = re.search(r'MAT\s*[.:]\s*(\S+)', nome_linha, re.IGNORECASE)
            matricula = m_mat.group(1) if m_mat else ''

            nome = re.sub(r'\s*[-–—]?\s*(?:MATR[^A-Za-z0-9]*CULA\s+\S+|\d+)', '', nome_linha, flags=re.IGNORECASE).strip()
            nome = re.sub(r'\s+', ' ', nome).strip()
            nome = nome.replace('NOME:', '').strip()

            i += 1
            data_rows = []
            while i < len(rows):
                cells2 = rows[i].findall(f'.//{T}table-cell')
                vals2 = [cell_text(c) for c in cells2]
                v0 = (vals2[0] or '').strip()

                if 'NOME:' in v0.upper() or 'Total:' in v0.upper()[:6]:
                    i -= 1
                    break

                if v0 and (v0[0].isdigit() or vals2[0]) and len(vals2) >= 7:
                    d = parse_date_ods(vals2[0])
                    fator = parse_factor(vals2[5] if len(vals2) > 5 else '')
                    if d and fator is not None:
                        data_rows.append({
                            'competencia': d,
                            'valor_original': moeda_para_float(vals2[1]),
                            'descricao': vals2[2] if len(vals2) > 2 else '',
                            'data_alvo': parse_date_ods(vals2[3]),
                            'correcao': moeda_para_float(vals2[4] if len(vals2) > 4 else ''),
                            'fator': fator,
                            'valor_corrigido': moeda_para_float(vals2[6] if len(vals2) > 6 else ''),
                        })
                i += 1

            if data_rows and nome:
                key = (nome, matricula)
                if key not in beneficiarios:
                    alvo = data_rows[0]['data_alvo']
                    beneficiarios[key] = {
                        'nome': nome,
                        'matricula': matricula,
                        'orgao': orgao or '990',
                        'data_alvo': alvo.strftime('%d/%m/%Y') if alvo else '',
                        '_todas_datas': [],
                    }
                    referencia[key] = []
                for dr in data_rows:
                    comp = dr['competencia']
                    beneficiarios[key]['_todas_datas'].append(comp)
                    if dr['data_alvo']:
                        referencia[key].append({
                            'competencia': comp.strftime('%Y-%m'),
                            'valor_original': dr['valor_original'],
                            'fator': dr['fator'],
                            'valor_corrigido': dr['valor_corrigido'],
                            'data_alvo': dr['data_alvo'].strftime('%Y-%m-%d'),
                        })

# Compute full period for each beneficiary (min/max of all dates across all sheets)
for key, b in beneficiarios.items():
    todas = b.pop('_todas_datas')
    if todas:
        min_d = min(todas)
        max_d = max(todas)
        b['comp_ini'] = parse_comp_from_date(min_d)
        b['comp_fim'] = parse_comp_from_date(max_d)
    else:
        b['comp_ini'] = ''
        b['comp_fim'] = ''
        i += 1

print(f"\n\nTotal de beneficiários únicos extraídos: {len(beneficiarios)}")

# Write CSV
csv_path = ENTRADA / 'beneficiarios_gabarito.csv'
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    f.write('nome;matricula;orgao;valor_mensal;competencia_inicial;competencia_final;data_alvo;observacao\n')
    for key, b in beneficiarios.items():
        f.write(f"{b['nome']};{b['matricula']};{b['orgao']};0;{b['comp_ini']};{b['comp_fim']};{b['data_alvo']};\n")

print(f"CSV gerado: {csv_path} ({len(beneficiarios)} beneficiários)")

# Write reference JSON (convert tuple keys to string)
ref_path = VALIDACAO / 'referencia_ods.json'
referencia_str = {f"{k[0]}||{k[1]}": v for k, v in referencia.items()}
with open(ref_path, 'w', encoding='utf-8') as f:
    json.dump(referencia_str, f, indent=2, ensure_ascii=False)

print(f"Referência salva: {ref_path} ({sum(len(v) for v in referencia.values())} parcelas)")

# Print summary
print("\n--- LISTA DE BENEFICIÁRIOS ---")
for key, b in sorted(beneficiarios.items(), key=lambda x: x[1]['nome']):
    qtd = len(referencia.get(key, []))
    print(f"{b['nome'][:40]:42s} | MAT {b['matricula']:12s} | {b['comp_ini']} - {b['comp_fim']} | alvo {b['data_alvo']} | {qtd:3d} parcelas | orgao={b['orgao']}")
