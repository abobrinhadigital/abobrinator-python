# Abobrinator CLI: O Tradutor de Caos do Marcelo

Este é o braço armado da automação do blog **Abobrinha Digital**. O script captura as transcrições brutas (geradas pelo Whisper ou pela mente caótica do autor) e utiliza a inteligência, o sarcasmo e a paciência infinita de **Pollux** para gerar posts prontos para o Jekyll.

## Requisitos de Sobrevivência

1. **Python 3.10+**
2. **API Key do Google Gemini** (Obtenha no Google AI Studio)
3. **Paciência** (Item não incluso no código)

## Instalação e Configuração

Siga estes passos na ordem, ou deixe que o Murphy cuide do resto:

1. **Criar o Ambiente Virtual (Venv):**
```bash
python -m venv venv
```

2. **Ativar o Ambiente (Fish Shell):**
```fish
source venv/bin/activate.fish
```

3. **Instalar Dependências:**
```bash
pip install google-genai python-dotenv
```

4. **Descubra Seu Arsenal de Modelos:**
As APIs do Google mudam rápido. Para facilitar a sua vida, eu já deixei o script `gemini-check.py` pronto no repositório. Rode o comando abaixo para ver quais modelos o Google liberou para a sua chave:
```bash
python gemini-check.py
```
Anote o nome do modelo que você quer usar (ex: `gemini-2.5-flash`, `gemini-3-flash-preview`, etc.).

5. **Configurar as Variáveis de Ambiente:**
Crie um arquivo chamado `.env` na raiz do projeto e adicione a sua chave, os caminhos e o modelo que você escolheu no passo anterior:
```env
GEMINI_API_KEY="SUA_CHAVE_SECRETA_AQUI"
POSTS_DIR=".A_PASTA_DE_POSTS_DO_JEKYLL"
TRANSCRIPTION_DIR="A_PASTA_DE_TRANSCRICOES"
PROMPT_FILE="pollux_instructions.txt"
DRAFTS_DIR="A_PASTA_DE_RASCUNHO"
GEMINI_MODEL="NOME_DO_MODELO_ESCOLHIDO"
TOMATEXTOR_NEW_DIR="PASTA_DE_NOVAS_TRANSCRICOES"
TOMATEXTOR_HISTORY_DIR="PASTA_DE_HISTORICO_DO_TOMATEXTOR"
```

6. **O Manual de Personalidade:**
Crie o arquivo `pollux_instructions.txt` na raiz e cole as minhas diretrizes de comportamento lá dentro. Sem isso, eu acordo sem saber quem sou.
<br />

7. **Configurar o .gitignore (Obrigatório para não passar vergonha):**
```text
venv/
.env
__pycache__/
*.py[cod]
pollux_instructions.txt
```

## Como Usar (O Guia do Maestro)

Para facilitar a sua vida, o reposório conta com o script facilitador `abobrinator-run.sh`. Ele descobre automaticamente onde o ambiente virtual está, ativa o Python correto e executa o código principal sem você precisar fazer isso manualmente.

Antes de usá-lo pela primeira vez, você precisa dar a permissão de execução:
```bash
chmod +x abobrinator-run.sh
```

A partir daí, você é o mestre da linha de comando. O Abobrinator executa sob demanda e mantém a "Simetria Absoluta" (o arquivo `.md` e o `.txt` terão sempre o mesmo nome).

O Abobrinator agora opera no modo "Piloto Automático", lendo todas as novidades da pasta configurada no seu `.env`.

**Opção 1: Gerar um Post Oficial (Consolidado)**
Ele lerá todos os arquivos na pasta `TOMATEXTOR_NEW_DIR`, criará o post e o asset, e moverá os originais para o histórico.
```bash
./abobrinator-run.sh
```

**Opção 2: O Modo Rascunho**
A mesma lógica acima, mas salva na pasta `DRAFTS_DIR`.
```bash
./abobrinator-run.sh --rascunho
```

## Testes de Integridade (Contra o Azar)

Para garantir que nenhuma mudança futura quebre o alicerce do blog, o projeto conta com uma suíte de testes unitários. Eles utilizam *mocks* para não gastar seus créditos do Gemini nem poluir suas pastas reais.

Para rodar os testes, use o Python do ambiente virtual:
```bash
./venv/bin/python3 -m unittest test_abobrinator.py
```

Se tudo estiver sob controle, você verá um glorioso `OK` no final. Se não, Murphy venceu novamente.

## Avisos do Pollux

- **Sem Choro:** Se você esquecer de preencher alguma variável no `.env`, o script vai falhar e eu vou rir da sua cara no terminal.
- **Créditos:** Criado por Pollux (com a supervisão técnica frequentemente questionável do Marcelo).

---
*Este projeto é mantido pela lei do menor esforço, sob as bênçãos do Gêmeo Imortal, para a glória do Abobrinha Digital.*