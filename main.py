import psycopg2
from ofxparse import OfxParser

# -------------------------------------------------------------
# 1. LEITURA E PROCESSAMENTO DO ARQUIVO OFX
# -------------------------------------------------------------
with open("extrato.ofx", "rb") as arquivo:
    ofx = OfxParser.parse(arquivo)

transacoes = ofx.account.statement.transactions

print("=" * 45)
print("             EXTRATO BANCÁRIO              ")
print("=" * 45)

entradas = 0.0
saidas = 0.0
total_movimentacoes = len(transacoes)

# Percorrendo as movimentações financeiras
for t in transacoes:
    valor = float(t.amount)
    data_formatada = t.date.strftime("%d/%m/%Y")
    
    if valor > 0:
        entradas += valor
    else:
        saidas += valor

    print(f"Data      : {data_formatada}")
    print(f"Valor     : R$ {valor:.2f}")
    print(f"Descrição : {t.memo}")
    print("-" * 45)

saldo = entradas + saidas

# -------------------------------------------------------------
# 2. EXIBIÇÃO DOS TOTAIS E RESUMO
# -------------------------------------------------------------
print("\n" + "=" * 45)
print("            RESUMO DA ATIVIDADE            ")
print("=" * 45)
print(f"Total de Movimentações : {total_movimentacoes}")
print(f"Total de Entradas      : R$ {entradas:.2f}")
print(f"Total de Saídas        : R$ {saidas:.2f}")
print(f"Saldo Calculado        : R$ {saldo:.2f}")
print("=" * 45)

# -------------------------------------------------------------
# 3. DESAFIO EXTRA: GRAVAÇÃO NO POSTGRESQL (COM PREVENÇÃO DE DUPLICATAS)
# -------------------------------------------------------------
DB_HOST = "localhost"
DB_NAME = "projetoofx"
DB_USER = "postgres"
DB_PASS = "123456"  # A senha que você definiu no Passo 3
DB_PORT = "5432"

try:
    conexao = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    cursor = conexao.cursor()

    # Query SQL com ON CONFLICT para ignorar registros já existentes
    query_insert = """
    INSERT INTO movimentacoes (data_movimentacao, valor, descricao)
    VALUES (%s, %s, %s)
    ON CONFLICT (data_movimentacao, valor, descricao) DO NOTHING;
    """

    novos_registros = 0
    for t in transacoes:
        cursor.execute(query_insert, (t.date.date(), t.amount, t.memo))
        # rowcount indica se a linha foi realmente inserida (1) ou ignorada (0)
        if cursor.rowcount > 0:
            novos_registros += 1

    conexao.commit()
    print(f"\n[PostgreSQL] Sucesso: {novos_registros} nova(s) transação(ões) gravada(s).")

except Exception as erro:
    print(f"\n[PostgreSQL] Erro ao conectar ou inserir dados: {erro}")

finally:
    if 'conexao' in locals() and conexao:
        cursor.close()
        conexao.close()
