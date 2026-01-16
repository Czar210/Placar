import requests
import json
import datetime
import os
import re

# --- CONFIGURAÇÃO ---
JOGADORES = [
    {"nome": "Zaras", "id": 1613893, "pasta": "Czar210"},    
    {"nome": "Amigo", "id": 88123, "pasta": "Amigo"}    
]

URL_PROBLEMAS = "https://uhunt.onlinejudge.org/api/p"
URL_SUBS_USER = "https://uhunt.onlinejudge.org/api/subs-user/{}"

# Mapa de Linguagens do UVa (ID -> Extensão)
LANG_MAP = {
    1: '.c', 2: '.java', 3: '.cpp', 4: '.pas', 5: '.cpp', 6: '.py'
}

# Template dinâmico (os símbolos de comentário mudam conforme a língua)
TEMPLATE = """{c_start}
 * Nome do Problema: {titulo}
 * ID: {id}
 * URL: https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&category=24&page=show_problem&problem={prob_index}
 * * Estratégia:
 * (Escreve aqui como resolveste)
 {c_end}

{c_line} Cola o teu código abaixo:
"""

def limpar_nome(nome):
    """Remove caracteres estranhos para criar um nome de arquivo seguro."""
    limpo = re.sub(r'[^\w\s-]', '', nome)
    return re.sub(r'[-\s]+', '_', limpo).strip()

def carregar_mapa_problemas():
    print("Baixando lista de problemas...")
    resp = requests.get(URL_PROBLEMAS)
    dados = resp.json()
    mapa = {}
    for p in dados:
        mapa[p[0]] = {"num": p[1], "titulo": p[2]}
    return mapa

def obter_estilo_comentario(extensao):
    """Define os símbolos de comentário baseados na linguagem."""
    if extensao == '.py':
        return {'start': '"""', 'end': '"""', 'line': '#'}
    elif extensao == '.pas':
        return {'start': '{', 'end': '}', 'line': '//'}
    else:
        # Padrão para C, C++, Java
        return {'start': '/*', 'end': '*/', 'line': '//'}

def criar_arquivo_codigo(jogador_pasta, prob_dados, lang_id):
    """Cria o arquivo vazio com o cabeçalho correto se ele não existir."""
    if not os.path.exists(jogador_pasta):
        try:
            os.makedirs(jogador_pasta)
        except FileExistsError:
            pass

    extensao = LANG_MAP.get(lang_id, '.txt')
    style = obter_estilo_comentario(extensao)
    
    nome_seguro = limpar_nome(prob_dados['titulo'])
    nome_arquivo = f"{prob_dados['num']}-{nome_seguro}{extensao}"
    caminho_completo = os.path.join(jogador_pasta, nome_arquivo)

    # Só cria se NÃO existir
    if not os.path.exists(caminho_completo):
        print(f"⚡ Criando arquivo novo: {nome_arquivo}")
        with open(caminho_completo, "w", encoding="utf-8") as f:
            conteudo = TEMPLATE.format(
                c_start=style['start'],
                c_end=style['end'],
                c_line=style['line'],
                titulo=prob_dados['titulo'], 
                id=prob_dados['num'],
                prob_index=prob_dados.get('id_interno', 0)
            )
            f.write(conteudo)
        return True
    return False

def buscar_usuario(jogador, mapa_problemas):
    print(f"Buscando dados de: {jogador['nome']} (ID: {jogador['id']})...")
    
    try:
        resp = requests.get(URL_SUBS_USER.format(jogador['id']))
        dados_api = resp.json()
    except Exception as e:
        print(f"Erro ao acessar API para {jogador['nome']}: {e}")
        return {"qtd": 0, "media": "0.000s", "lista": []}

    subs = dados_api.get("subs", [])
    
    resolvidos_set = set()
    lista_detalhada = []
    tempo_total = 0
    novos_arquivos = 0
    
    subs.sort(key=lambda x: x[4], reverse=True) 

    for sub in subs:
        prob_id = sub[1]
        verdict = sub[2]
        tempo = sub[3]
        lang_id = sub[5] 
        timestamp = sub[4]
        
        # --- FILTRO DE DATA (OPCIONAL) ---
        # Descomenta as linhas abaixo para ativar o filtro de 2026
        # if timestamp < 1768521600:
        #    continue
        # ---------------------------------
        
        if verdict == 90: # Accepted
            if prob_id not in resolvidos_set:
                resolvidos_set.add(prob_id)
                
                info_prob = mapa_problemas.get(prob_id, {"num": 0, "titulo": "Desconhecido"})
                info_prob['id_interno'] = prob_id 

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
    
    print(f"  -> {novos_arquivos} novos arquivos criados.")

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
# # Bruxo dos Dados vs Gênio da Lampada qual a verdadeira besta sagrada mecanica enjaulada da programação?
> Atualizado em: {data_hoje}

| Rank | Nome | Resolvidos | Tempo Médio |
| :---: | :--- | :---: | :---: |
"""
for i, p in enumerate(tabela_dados):
    medalha = ["🥇", "🥈", "🥉"][i] if i < 3 else str(i+1)
    conteudo_readme += f"| {medalha} | {p['nome']} | **{p['qtd']}** | {p['media']} |\n"

conteudo_readme += "\n\n👉 [Ver detalhes](detalhes.md)"
# Adiciona o Guia no final do Readme automaticamente se quiseres
# conteudo_readme += "\n\n---\n## 📘 Guia rápido...\n" 

with open("README.md", "w", encoding="utf-8") as f: f.write(conteudo_readme)
with open("detalhes.md", "w", encoding="utf-8") as f: f.write(conteudo_detalhes)
