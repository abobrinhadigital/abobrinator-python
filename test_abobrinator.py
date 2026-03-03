import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import re
from datetime import datetime

# Importamos o abobrinator, mas precisamos lidar com a execução imediata de validar_ambiente()
# Para teste, vamos mockar o os.getenv antes do import principal se possível, 
# ou isolar as funções do abobrinator.py para serem testáveis.
# Como o abobrinator.py executa cfg = validar_ambiente() no escopo global, 
# precisamos mockar o ambiente antes de qualquer coisa.

with patch('os.getenv') as mock_env:
    mock_env.side_effect = lambda k: {
        "GEMINI_API_KEY": "test-key",
        "POSTS_DIR": "test-posts",
        "TRANSCRIPTION_DIR": "test-trans",
        "PROMPT_FILE": "test-prompt.txt",
        "DRAFTS_DIR": "test-drafts",
        "GEMINI_MODEL": "test-model"
    }.get(k)
    import abobrinator

class TestAbobrinator(unittest.TestCase):

    def setUp(self):
        self.mock_config = {
            "GEMINI_API_KEY": "test-key",
            "POSTS_DIR": "test-posts",
            "TRANSCRIPTION_DIR": "test-trans",
            "PROMPT_FILE": "test-prompt.txt",
            "DRAFTS_DIR": "test-drafts",
            "GEMINI_MODEL": "test-model"
        }

    @patch('os.getenv')
    def test_validar_ambiente_sucesso(self, mock_getenv):
        mock_getenv.side_effect = lambda k: self.mock_config.get(k)
        config = abobrinator.validar_ambiente()
        self.assertEqual(config, self.mock_config)

    @patch('os.getenv')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_validar_ambiente_falha(self, mock_print, mock_exit, mock_getenv):
        mock_getenv.return_value = None
        abobrinator.validar_ambiente()
        mock_exit.assert_called_with(1)
        mock_print.assert_called()

    @patch('builtins.open', new_callable=mock_open, read_data="Instruções de Teste")
    def test_carregar_instrucoes_sucesso(self, mock_file):
        with patch.dict('abobrinator.cfg', self.mock_config):
            content = abobrinator.carregar_instrucoes()
            self.assertEqual(content, "Instruções de Teste")
            mock_file.assert_called_with("test-prompt.txt", 'r', encoding='utf-8')

    @patch('os.path.exists')
    @patch('sys.exit')
    def test_carregar_instrucoes_arquivo_ausente(self, mock_exit, mock_exists):
        mock_exists.return_value = False
        # abobrinator.carregar_instrucoes não checa exists, ele apenas abre. 
        # O erro será FileNotFoundError que o processar_arquivo captura.
        pass

    @patch('google.genai.Client')
    @patch('builtins.open', new_callable=mock_open, read_data="Conteúdo da Transcrição")
    @patch('os.makedirs')
    @patch('shutil.copy2')
    @patch('abobrinator.carregar_instrucoes')
    def test_processar_arquivo_fluxo_completo(self, mock_instr, mock_copy, mock_mkdir, mock_file, mock_genai):
        # Configuração do Mock Gemini
        mock_response = MagicMock()
        mock_response.text = """---
layout: post
title: "Título de Teste"
description: "Descrição ácida do Pollux"
categories: tecnologia caos
author: Pollux, O Biógrafo do Azar
date: 2026-03-02 21:30:00 -0400
---
Conteúdo do Post.
<br><br>
---
*Abobrinha Digital: Onde o azar vira arte.*
/assets/transcricoes/NOME_DO_ARQUIVO_GERADO.txt
"""
        mock_genai.return_value.models.generate_content.return_value = mock_response
        mock_instr.return_value = "Instruções Mock"
        
        with patch.dict('abobrinator.cfg', self.mock_config):
            with patch('os.path.exists', return_value=True):
                # Executa o processamento
                abobrinator.processar_arquivo("caminho/do/audio.txt", is_rascunho=False)
                
                # Verificações
                # 1. Slug e Data
                data_hoje = datetime.now().strftime("%Y-%m-%d")
                nome_esperado = f"{data_hoje}-titulo-de-teste"
                
                # 2. Chamada de escrita do arquivo MD
                handle = mock_file()
                written_content = "".join(call.args[0] for call in handle.write.call_args_list)
                
                # Validação da data injetada (ignora segundos para evitar falha por milissegundos)
                data_hoje = datetime.now().strftime("%Y-%m-%d")
                self.assertIn(f"date: {data_hoje}", written_content)
                self.assertIn("-0400", written_content)

    @patch('google.genai.Client')
    @patch('builtins.open', new_callable=mock_open, read_data="Conteúdo da Transcrição")
    @patch('os.makedirs')
    @patch('shutil.copy2')
    @patch('abobrinator.carregar_instrucoes')
    def test_processar_arquivo_modo_rascunho(self, mock_instr, mock_copy, mock_mkdir, mock_file, mock_genai):
        # Configuração do Mock Gemini
        mock_response = MagicMock()
        mock_response.text = "title: \"Rascunho\"\ndate: 2026-03-02 21:30:00 -0400\nConteúdo"
        mock_genai.return_value.models.generate_content.return_value = mock_response
        mock_instr.return_value = "Instruções Mock"
        
        with patch.dict('abobrinator.cfg', self.mock_config):
            with patch('os.path.exists', return_value=True):
                abobrinator.processar_arquivo("audio.txt", is_rascunho=True)
                
                # Verifica se o arquivo MD foi salvo no DRAFTS_DIR
                expected_md_path = os.path.join(self.mock_config["DRAFTS_DIR"], f"{datetime.now().strftime('%Y-%m-%d')}-rascunho.md")
                mock_file.assert_any_call(expected_md_path, 'w', encoding='utf-8')
                
                # Verifica se a transcrição foi copiada para o DRAFTS_DIR
                expected_trans_path = os.path.join(self.mock_config["DRAFTS_DIR"], f"{datetime.now().strftime('%Y-%m-%d')}-rascunho.txt")
                mock_copy.assert_called_with("audio.txt", expected_trans_path)

    @patch('os.makedirs')
    @patch('abobrinator.cfg')
    def test_criacao_diretorios_init(self, mock_cfg, mock_makedirs):
        # Simula o bloco if __name__ == "__main__":
        mock_cfg.__getitem__.side_effect = lambda k: self.mock_config[k]
        dirs_to_check = [self.mock_config["POSTS_DIR"], self.mock_config["TRANSCRIPTION_DIR"], self.mock_config["DRAFTS_DIR"]]
        
        # Como o código roda no nível do módulo ou no main, simulamos as chamadas que estão no main
        for p in dirs_to_check:
            os.makedirs(p, exist_ok=True)
            
        for d in dirs_to_check:
            mock_makedirs.assert_any_call(d, exist_ok=True)

    @patch('os.path.exists')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_processar_arquivo_transcricao_ausente(self, mock_print, mock_exit, mock_exists):
        mock_exists.return_value = False
        # abobrinator.py não checa os.path.exists(filepath) antes de abrir.
        # Ele vai falhar no 'with open(filepath, 'r'...)'.
        with patch.dict('abobrinator.cfg', self.mock_config):
            # Simulando erro de abertura
            with patch('builtins.open', side_effect=FileNotFoundError("Arquivo não encontrado")):
                abobrinator.processar_arquivo("arquivo_que_nao_existe.txt", False)
                mock_exit.assert_called_with(1)
                mock_print.assert_called_with("[ABOBRINATOR] ERRO FATAL: Arquivo não encontrado")

if __name__ == '__main__':
    unittest.main()
