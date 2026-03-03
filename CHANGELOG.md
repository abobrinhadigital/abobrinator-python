# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-03-03

### Added
- **Suporte a Múltiplas Transcrições**: Agora o script processa todos os arquivos `.txt` de uma pasta e os consolida em um único post.
- **Arquivamento Automático (Expurgo)**: Move os arquivos originais para o diretório de histórico após o processamento bem-sucedido.
- **Configuração via `.env`**: Introdução de `TOMATEXTOR_NEW_DIR` e `TOMATEXTOR_HISTORY_DIR` para automação total.

### Changed
- **CLI Simplificado**: Remoção da necessidade de passar o caminho do arquivo via argumento; o script agora lê diretamente da pasta configurada.
- **Asset Consolidado**: Múltiplas transcrições são unificadas em um único asset `.txt` para manter a simetria absoluta.
- **Script Shell**: Atualização do `abobrinator-run.sh` para o novo fluxo minimalista.

## [2.0.0] - 2026-03-02

### Added
- **O Big Bang da Simetria**: Versão inicial documentada com suporte a um único arquivo e geração de assets simétricos.

## [Antiguidade] - Infinito até 2026-03-01

### Added
- **O Caos Original**: Versões que existiram apenas no HD do mestre.
- **Memória Seletiva**: Códigos que funcionavam por milagre ou por intervenção direta de Murphy, mas que agora foram perdidos no éter porque o mestre esqueceu de me dar um diário.

> [!NOTE]
> Rumores dizem que existiram versões antes da 2.0.0, mas como elas não foram registradas em cartório (ou no Git), elas tecnicamente nunca aconteceram.
