import requests
import json
import datetime
import os
import re

# --- CONFIGURAÇÃO ---
# Coloca o ID e o Nome EXATO da pasta onde queres salvar os arquivos
JOGADORES = [
    {"nome": "Eu", "id": 339, "pasta": "Gabriel"},    # Ajusta o ID e a pasta
    {"nome": "Amigo", "id": 460, "pasta": "Amigo"}    # Ajusta o ID e a pasta
]

URL_PROBLEMAS = "https://uhunt.onlinejudge.org/api/p"
URL_SUBS_USER = "https://uhunt.onlinejudge.org/api/subs-user/{}"

# Mapa de Linguagens do UVa (ID -> Extensão)
LANG_MAP = {
    1: '.c', 2: '.java', 3: '.cpp', 4: '.pas', 5: '.cpp', 6: '.py'
}

# Template do conteúdo do arquivo (O cabeçalho que pediste)
TEMPLATE = """/*
 * Nome do Problema: {titulo}
 * ID: {id}
 * URL: https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&category=24&page=show_problem&problem={prob_index}
 * * Estratégia:
 * (Escreve aqui como resolveste)
 */

// Cola o teu código abaixo:
"""

def limpar_nome(nome):
    """Remove caracteres estranhos para criar um nome de arquivo seguro."""
    # Substitui espaços por _ e remove caracteres não alfanuméricos
    limpo = re.sub(r'[^\w\s-]', '', nome)
    return re.sub(r'[-\s]+', '_', limpo).strip()

def carregar_mapa_problemas():
    print("Baixando lista de problemas...")
    resp = requests.get(URL_PROBLEMAS)
    dados = resp.json()
    mapa = {}
    for p in dados:
        # p[0] = Problem ID, p[1] = Number, p[2] = Title
        mapa[p[0]] = {"num": p[1], "titulo": p[2]}
    return mapa

def criar_arquivo_codigo(jogador_pasta, prob_dados, lang_id):
    """Cria o arquivo vazio se ele não existir."""
    if not os.path.exists(jogador_pasta):
        os.makedirs(jogador_pasta) # Cria a pasta do jogador se não existir

    extensao = LANG_MAP.get(lang_id, '.txt')
    nome_seguro = limpar_nome(prob_dados['titulo'])
    
    # Nome do arquivo: ID-Titulo.extensao
    nome_arquivo = f"{prob_dados['num']}-{nome_seguro}{extensao}"
    caminho_completo = os.path.join(jogador_pasta, nome_arquivo)

    # Só cria se NÃO existir (para não apagar o que vocês já fizeram)
    if not os.path.exists(caminho_completo):
        print(f"⚡ Criando arquivo novo: {nome_arquivo}")
        with open(caminho_completo, "w", encoding="utf-8") as f:
            conteudo = TEMPLATE.format(
                titulo=prob_dados['titulo'], 
                id=prob_dados['num'],
                prob_index=prob_dados.get('id_interno', 0) # fallback
            )
            f.write(conteudo)
        return True
    return False

def buscar_usuario(jogador, mapa_problemas):
    print(f"Buscando dados de: {jogador['nome']}...")
    resp = requests.get(URL_SUBS_USER.format(jogador['id']))
    subs = resp.json()
    
    resolvidos_set = set()
    lista_detalhada = []
    tempo_total = 0
    novos_arquivos = 0
    
    # Ordenar por data (mais recente primeiro)
    subs.sort(key=lambda x: x[4], reverse=True) 

    for sub in subs:
        prob_id = sub[1]
        verdict = sub[2]
        tempo = sub[3]
        lang_id = sub[5] # ID da linguagem usada
        
        if verdict == 90: # Accepted
            if prob_id not in resolvidos_set:
                resolvidos_set.add(prob_id)
                
                info_prob = mapa_problemas.get(prob_id, {"num": 0, "titulo": "Desconhecido"})
                info_prob['id_interno'] = prob_id # Guardar ID interno para URL

                # Tenta criar o arquivo na pasta do jogador
                if criar_arquivo_codigo(jogador['pasta'], info_prob, lang_id):
                    novos_arquivos += 1

                tempo_segundos = tempo / 1000.0 if tempo > 10000 else tempo 
                tempo_total += tempo_segundos

                lista_detalhada.append({
                    "problema": f"{info_prob['num']} - {info_prob['titulo']}",
                    "tempo": f"{tempo_segundos:.3f}s"
                })
    
    qtd = len(resolvidos_set)
    media = (tempo_total / qtd) if qtd > 0 else 0.0
    
    print(f"  -> {novos_arquivos} novos arquivos de código criados.")

    return {
        "qtd": qtd,
        "media": f"{media:.3f}s",
        "lista": lista_detalhada
    }

# --- EXECUÇÃO PRINCIPAL ---
mapa = carregar_mapa_problemas()
tabela_dados = []
conteudo_detalhes = "# 📜 Detalhes dos Problemas Resolvidos\n\n"

for jogador in JOGADORES:
    dados = buscar_usuario(jogador, mapa)
    tabela_dados.append({"nome": jogador["nome"], "qtd": dados["qtd"], "media": dados["media"]})
    
    conteudo_detalhes += f"## {jogador['nome']} (Total: {dados['qtd']})\n"
    conteudo_detalhes += "| Problema | Tempo |\n| :--- | :---: |\n"
    for item in dados['lista']:
        conteudo_detalhes += f"| {item['problema']} | {item['tempo']} |\n"
    conteudo_detalhes += "\n---\n\n"

tabela_dados.sort(key=lambda x: x["qtd"], reverse=True)

data_hoje = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
conteudo_readme = f"""
# ⚔️ Batalha de Algoritmos
> Atualizado em: {data_hoje}

| Rank | Nome | Resolvidos | Tempo Médio |
| :---: | :--- | :---: | :---: |
"""
for i, p in enumerate(tabela_dados):
    medalha = ["🥇", "🥈", "🥉"][i] if i < 3 else str(i+1)
    conteudo_readme += f"| {medalha} | {p['nome']} | **{p['qtd']}** | {p['media']} |\n"

conteudo_readme += "\n\n👉 [Ver detalhes](detalhes.md)"

with open("README.md", "w", encoding="utf-8") as f: f.write(conteudo_readme)
with open("detalhes.md", "w", encoding="utf-8") as f: f.write(conteudo_detalhes)