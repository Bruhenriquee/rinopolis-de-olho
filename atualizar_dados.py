"""Busca nas fontes oficiais os números que mudam durante o ano e grava no index.html.

    python atualizar_dados.py

- Contas do ano (Tesouro Nacional, Siconfi): o relatório bimestral mais novo que a prefeitura entregou.
- Emendas federais mandadas direto pra prefeitura (Transferegov): valor, objeto e se o relatório de execução foi enviado.

Troca só o bloco entre DADOS-AUTOMATICOS e FIM-DADOS-AUTOMATICOS. O GitHub roda este arquivo toda segunda
(.github/workflows/atualizar-dados.yml); depois é só rodar gerar_site.py, que o próprio GitHub também faz.
O balanço anual (receitas e gastos por área de 2025) muda uma vez por ano e continua sendo conferido à mão.
"""
import datetime
import json
import pathlib
import re
import unicodedata
import urllib.request

PASTA = pathlib.Path(__file__).parent
IBGE = 3543808
CNPJ = '46478053000113'
SICONFI = 'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo'
TRANSFEREGOV = 'https://api.transferegov.gestao.gov.br/transferenciasespeciais/'
MES_FIM = {1: 'fevereiro', 2: 'abril', 3: 'junho', 4: 'agosto', 5: 'outubro', 6: 'dezembro'}

# títulos curtos para as emendas já conhecidas; uma emenda nova aparece com o começo do objeto
CURADO = {
    65651: {'titulo': 'LED nos postes', 'resumo': 'trocar 622 lâmpadas dos postes por LED', 'pergunta': 'Quais ruas receberam?'},
    81138: {'titulo': 'Quadras de padel no Jardim Boa Vista', 'resumo': 'construir duas quadras de padel no Jardim Boa Vista', 'pergunta': 'A obra começou?'},
}


def baixar(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'rinopolis-de-olho'}), timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def sem_acento(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().upper()


def contas():
    """Relatório bimestral (RREO) mais novo: tenta o ano atual do 6º bimestre para trás, depois o ano anterior."""
    hoje = datetime.date.today()
    for ano in (hoje.year, hoje.year - 1):
        for per in range(6, 0, -1):
            itens = baixar(f'{SICONFI}?an_exercicio={ano}&nr_periodo={per}&co_tipo_demonstrativo=RREO%20Simplificado&id_ente={IBGE}')['items']
            if not itens:
                continue
            def valor(anexo, conta, coluna, campo='cod_conta'):
                for x in itens:
                    if x['anexo'] == anexo and x[campo] == conta and sem_acento(x['coluna']).startswith(coluna):
                        return round(x['valor'])
                raise ValueError(f'não achei {conta} / {coluna} no relatório {ano}-{per}')
            return {
                'ano': ano, 'periodo': per, 'mesFim': MES_FIM[per],
                'recebido': valor('RREO-Anexo 01', 'TotalReceitas', 'ATE O BIMESTRE'),
                'gasto': valor('RREO-Anexo 01', 'TotalDespesas', 'DESPESAS LIQUIDADAS ATE O BIMESTRE'),
                'orcInicial': valor('RREO-Anexo 01', 'TotalDespesas', 'DOTACAO INICIAL'),
                'orcAtual': valor('RREO-Anexo 01', 'TotalDespesas', 'DOTACAO ATUALIZADA'),
                'urbanos': valor('RREO-Anexo 02', 'Serviços Urbanos', 'DESPESAS LIQUIDADAS ATE O BIMESTRE', 'conta'),
            }
    raise RuntimeError('nenhum relatório bimestral encontrado')


def emendas():
    planos = baixar(f'{TRANSFEREGOV}plano_acao_especial?cnpj_beneficiario_plano_acao=eq.{CNPJ}&order=ano_plano_acao.desc')
    ids = ','.join(str(p['id_plano_acao']) for p in planos)
    if not ids:
        return []
    executores = {e['id_plano_acao']: e for e in baixar(f'{TRANSFEREGOV}executor_especial?id_plano_acao=in.({ids})')}
    relatorios = {r['id_plano_acao'] for r in baixar(f'{TRANSFEREGOV}relatorio_gestao_especial?id_plano_acao=in.({ids})')}
    lista = []
    for p in planos:
        e = executores.get(p['id_plano_acao'], {})
        objeto = re.sub(r'\s+', ' ', (e.get('objeto_executor') or '').replace('Objeto:', '')).strip()
        cur = CURADO.get(p['id_plano_acao'], {})
        lista.append({
            'id': p['id_plano_acao'], 'ano': p['ano_plano_acao'], 'parlamentar': p['nome_parlamentar_emenda_plano_acao'],
            'valor': round((p['valor_custeio_plano_acao'] or 0) + (p['valor_investimento_plano_acao'] or 0)),
            'titulo': cur.get('titulo') or (objeto[:60].rstrip(' ,.') + ('…' if len(objeto) > 60 else '')),
            'pergunta': cur.get('pergunta', 'O dinheiro já foi usado?'),
            'resumo': cur.get('resumo', objeto), 'relatorio': p['id_plano_acao'] in relatorios,
        })
    return lista


dados = {'conferido': datetime.date.today().isoformat(), 'contas': contas(), 'emendas': emendas()}
html = PASTA / 'index.html'
texto = html.read_text(encoding='utf-8')
novo, n = re.subn(r'(/\* DADOS-AUTOMATICOS[^\n]*\n).*?(\n/\* FIM-DADOS-AUTOMATICOS \*/)',
                  lambda m: m.group(1) + 'const DADOS = ' + json.dumps(dados, ensure_ascii=False) + ';' + m.group(2),
                  texto, count=1, flags=re.S)
if n != 1:
    raise SystemExit('não achei o bloco DADOS-AUTOMATICOS no index.html')
html.write_text(novo, encoding='utf-8')
c = dados['contas']
print(f"contas {c['ano']}, {c['periodo']}º bimestre (até {c['mesFim']}): recebido {c['recebido']:,}, gasto {c['gasto']:,}")
print(f"{len(dados['emendas'])} emendas federais")
