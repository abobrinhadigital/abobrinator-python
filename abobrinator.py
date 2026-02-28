import os
import sys
import re
import shutil
import argparse
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# =======================================================================
# ABOBRINATOR v2.0 - EDIÇÃO SIMETRIA ABSOLUTA
# =======================================================================

load_dotenv()

def validar_ambiente():
    vars_obrigatorias = ["GEMINI_API_KEY", "POSTS_DIR", "TRANSCRIPTION_DIR", "PROMPT_FILE", "DRAFTS_DIR", "GEMINI_MODEL"]
    config = {var: os.getenv(var) for var in vars_obrigatorias}
    if faltando := [var for var, val in config.items() if not val]:
        print(f"\n[ABOBRINATOR] ERRO: Faltando no .env: {', '.join(faltando)}")
        sys.exit(1)
    return config

cfg = validar_ambiente()

def carregar_instrucoes():
    with open(cfg["PROMPT_FILE"], 'r', encoding='utf-8') as f:
        return f.read()

def processar_arquivo(filepath, is_rascunho):
    filename_orig = os.path.basename(filepath)
    print(f"\n[ABOBRINATOR] Operação [{'RASCUNHO' if is_rascunho else 'POST'}] para: {filename_orig}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            transcricao_bruta = f.read()

        client = genai.Client(api_key=cfg["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model=cfg["GEMINI_MODEL"], 
            config={'system_instruction': carregar_instrucoes()},
            contents=f"Transcrição original: '{filename_orig}'. Processe:\n\n{transcricao_bruta}"
        )
        
        conteudo_md = response.text
        # Limpeza de blocos do markdown da API
        conteudo_md = re.sub(r'^```markdown\s*\n|^```\s*\n|\n\s*```$', '', conteudo_md, flags=re.I | re.M)

        # 1. Extração do Título e geração do Nome Base (Data + Slug)
        match_titulo = re.search(r'^title:\s*(.+)$', conteudo_md, flags=re.M)
        titulo = match_titulo.group(1).strip().strip('"').strip("'") if match_titulo else "caos-sem-titulo"
        slug = re.sub(r'[^a-z0-9]+', '-', titulo.lower()).strip('-')
        data_str = datetime.now().strftime("%Y-%m-%d")
        nome_base = f"{data_str}-{slug[:45]}"
        
        # 2. A MÁGICA DA SIMETRIA: Força o link para o nome_base exato
        conteudo_md = re.sub(
            r'/assets/transcricoes/[^\s)\]"\']+\.txt', 
            f'/assets/transcricoes/{nome_base}.txt', 
            conteudo_md, 
            flags=re.IGNORECASE
        )

        # 3. Definição do arquivo (Sem prefixo RASCUNHO, simetria total)
        md_filename = f"{nome_base}.md"
        md_filepath = os.path.join(cfg["DRAFTS_DIR"] if is_rascunho else cfg["POSTS_DIR"], md_filename)

        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo_md)
        
        print(f"[ABOBRINATOR] SUCESSO! Post salvo em: {md_filepath}")

        # 4. Movimentação da Transcrição
        if not is_rascunho:
            dest_asset = os.path.join(cfg["TRANSCRIPTION_DIR"], f"{nome_base}.txt")
            shutil.move(filepath, dest_asset)
            print(f"[ABOBRINATOR] Transcrição renomeada para: {nome_base}.txt e movida.")
        else:
            print(f"[ABOBRINATOR] Como é rascunho, o .txt original não foi movido.")
            print(f"[ABOBRINATOR] AVISO: O link no post aponta para o futuro arquivo {nome_base}.txt")

    except Exception as e:
        print(f"[ABOBRINATOR] ERRO FATAL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    for p in [cfg["POSTS_DIR"], cfg["TRANSCRIPTION_DIR"], cfg["DRAFTS_DIR"]]: os.makedirs(p, exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("arquivo")
    parser.add_argument("--rascunho", action="store_true")
    args = parser.parse_args()
    processar_arquivo(args.arquivo, args.rascunho)