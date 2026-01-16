import datetime

# 1. Configuração dos Usuários
# Aqui vamos colocar os nomes de usuário do site que vocês usam
jogadores = [
    {"nome": "Tu", "user_id": "teu_usuario"},
    {"nome": "Teu Amigo", "user_id": "usuario_amigo"}
]

# 2. Função para buscar dados (Simulação)
# Nota: Quando me disseres o site, vamos mudar isto para conectar de verdade.
def buscar_dados_do_usuario(user_id):
    # Imagine que aqui o código vai à internet buscar os dados reais
    # Por enquanto, vou inventar números para testar
    import random
    return {
        "resolvidos": random.randint(10, 50),
        "tempo_medio": f"{random.randint(10, 100)}ms",
        "linguagem_fav": "Python"
    }

# 3. Gerar o Conteúdo da Tabela
conteudo_markdown = """
# 🏆 Placar de Programação 🏆
*Atualizado automaticamente em: {}*

| Rank | Nome | Problemas Resolvidos | Tempo Médio | Linguagem |
| :--- | :--- | :---: | :---: | :---: |
""".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

# Lista para guardar os resultados e ordenar
classificacao = []

for jogador in jogadores:
    dados = buscar_dados_do_usuario(jogador["user_id"])
    classificacao.append({
        "nome": jogador["nome"],
        "resolvidos": dados["resolvidos"],
        "tempo": dados["tempo_medio"],
        "lang": dados["linguagem_fav"]
    })

# Ordenar: Quem resolveu mais aparece primeiro (ordem decrescente)
classificacao.sort(key=lambda x: x["resolvidos"], reverse=True)

# Adicionar linhas à tabela
for i, p in enumerate(classificacao):
    medalha = "🥇" if i == 0 else "🥈"
    linha = f"| {medalha} | {p['nome']} | {p['resolvidos']} | {p['tempo']} | {p['lang']} |\n"
    conteudo_markdown += linha

# 4. Salvar no arquivo README.md
with open("README.md", "w", encoding="utf-8") as arquivo:
    arquivo.write(conteudo_markdown)

print("Placar atualizado com sucesso!")