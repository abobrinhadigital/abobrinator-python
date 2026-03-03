import os
import sys
import re
import shutil
import argparse
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# =======================================================================
# ABOBRINATOR v2.2 - EDIÇÃO SIMETRIA ABSOLUTA
# =======================================================================

load_dotenv()

def validar_ambiente():
    vars_obrigatorias = ["GEMINI_API_KEY", "POSTS_DIR", "TRANSCRIPTION_DIR", "PROMPT_FILE", "DRAFTS_DIR", "GEMINI_MODEL", "TOMATEXTOR_HISTORY_DIR", "TOMATEXTOR_NEW_DIR"]
    config = {var: os.getenv(var) for var in vars_obrigatorias}
    if faltando := [var for var, val in config.items() if not val]:
        print(f"\n[ABOBRINATOR] ERRO: Faltando no .env: {', '.join(faltando)}")
        sys.exit(1)
    return config

cfg = validar_ambiente()

def carregar_instrucoes():
    with open(cfg["PROMPT_FILE"], 'r', encoding='utf-8') as f:
        return f.read()

def processar_pasta(diretorio, is_rascunho):
    if not os.path.isdir(diretorio):
        print(f"[ABOBRINATOR] ERRO: '{diretorio}' não é um diretório válido.")
        sys.exit(1)

    # Lista arquivos .txt em ordem alfabética
    arquivos = sorted([
        os.path.join(diretorio, f) 
        for f in os.listdir(diretorio) 
        if f.endswith(".txt") and os.path.isfile(os.path.join(diretorio, f))
    ])

    if not arquivos:
        print(f"[ABOBRINATOR] AVISO: Nenhum arquivo .txt encontrado em: {diretorio}")
        return

    print(f"\n[ABOBRINATOR] Operação [{'RASCUNHO' if is_rascunho else 'POST'}] para pasta: {diretorio}")
    print(f"[ABOBRINATOR] Consolidando {len(arquivos)} arquivos...")

    try:
        transcricao_consolidada = ""
        conteudo_original_bruto = ""
        
        for i, filepath in enumerate(arquivos, 1):
            filename = os.path.basename(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                conteudo = f.read()
                # Para o Gemini: Identificamos cada trecho
                transcricao_consolidada += f"\n--- PARTE {i} ({filename}) ---\n{conteudo}\n"
                # Para o Asset: Apenas o conteúdo bruto sequencial
                conteudo_original_bruto += f"\n--- ORIGEM: {filename} ---\n{conteudo}\n"

        client = genai.Client(api_key=cfg["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model=cfg["GEMINI_MODEL"], 
            config={'system_instruction': carregar_instrucoes()},
            contents=f"Múltiplas transcrições detectadas. Consolide em um único post coerente:\n\n{transcricao_consolidada}"
        )
        
        conteudo_md = response.text
        # Limpeza de blocos do markdown da API
        conteudo_md = re.sub(r'^```markdown\s*\n|^```\s*\n|\n\s*```$', '', conteudo_md, flags=re.I | re.M)

        # 1. Extração do Título e geração do Nome Base (Data + Slug)
        match_titulo = re.search(r'^title:\s*(.+)$', conteudo_md, flags=re.M)
        titulo = match_titulo.group(1).strip().strip('"').strip("'") if match_titulo else "caos-consolidado"
        
        # Normalização para remover acentos
        import unicodedata
        titulo_normalizado = unicodedata.normalize('NFKD', titulo).encode('ascii', 'ignore').decode('ascii')
        slug = re.sub(r'[^a-z0-9]+', '-', titulo_normalizado.lower()).strip('-')
        
        # Data e Fuso Horário
        timezone_offset = os.getenv("TIMEZONE_OFFSET", "-0400")
        data_atual = datetime.now()
        data_str = data_atual.strftime("%Y-%m-%d")
        data_completa_str = data_atual.strftime(f"%Y-%m-%d %H:%M:%S {timezone_offset}")
        
        nome_base = f"{data_str}-{slug[:45]}"

        # FORÇAR DATA NO FRONT MATTER
        conteudo_md = re.sub(r'^date:.*$', f'date: {data_completa_str}', conteudo_md, flags=re.M)
        
        # 2. A MÁGICA DA SIMETRIA: Força o link para o nome_base exato
        conteudo_md = re.sub(
            r'/assets/transcricoes/[^\s)\]"\']+\.txt', 
            f'/assets/transcricoes/{nome_base}.txt', 
            conteudo_md, 
            flags=re.IGNORECASE
        )

        # 3. Definição do arquivo
        md_filename = f"{nome_base}.md"
        md_filepath = os.path.join(cfg["DRAFTS_DIR"] if is_rascunho else cfg["POSTS_DIR"], md_filename)

        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo_md)
        
        print(f"[ABOBRINATOR] SUCESSO! Post consolidado salvo em: {md_filepath}")

        # 4. Cópia da Transcrição Consolidada (Simetria Absoluta)
        pasta_destino = cfg["DRAFTS_DIR"] if is_rascunho else cfg["TRANSCRIPTION_DIR"]
        os.makedirs(pasta_destino, exist_ok=True)
        
        dest_asset = os.path.join(pasta_destino, f"{nome_base}.txt")
        
        with open(dest_asset, 'w', encoding='utf-8') as f:
            f.write(conteudo_original_bruto)
        
        print(f"[ABOBRINATOR] ✅ Transcrição consolidada salva em: {dest_asset}")

        # 5. EXPURGO: Move os arquivos originais para o histórico (Tarefa do mestre)
        os.makedirs(cfg["TOMATEXTOR_HISTORY_DIR"], exist_ok=True)
        for filepath in arquivos:
            filename = os.path.basename(filepath)
            dest_history = os.path.join(cfg["TOMATEXTOR_HISTORY_DIR"], filename)
            shutil.move(filepath, dest_history)
            print(f"[ABOBRINATOR] 📁 Arquivo original arquivado: {filename}")

    except Exception as e:
        print(f"[ABOBRINATOR] ERRO FATAL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Garante estrutura de pastas
    for p in [cfg["POSTS_DIR"], cfg["TRANSCRIPTION_DIR"], cfg["DRAFTS_DIR"]]: os.makedirs(p, exist_ok=True)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--rascunho", action="store_true")
    args = parser.parse_args()
    
    processar_pasta(cfg["TOMATEXTOR_NEW_DIR"], args.rascunho)