# Arquitetura e Decisões de Projeto

## Visão Geral

Este projeto implementa um middleware para integração de múltiplos SASs (Spectrum Access Systems) usando uma blockchain como camada central de dados compartilhados. O objetivo é garantir consistência, auditabilidade e segurança na troca de informações entre SASs, indo além do modelo tradicional ponto-a-ponto do padrão WINNF.

---

## Blockchain como Camada Central

- **Todos os SASs conectam-se à mesma blockchain** para registrar, consultar e atualizar informações sobre CBSDs, grants, etc.
- **A blockchain garante integridade, imutabilidade e sincronização dos dados** entre todos os SASs participantes.
- **Os endpoints REST do middleware** servem como interface para leitura/escrita na blockchain, mas a fonte de verdade é sempre a blockchain.

### Vantagens
- Consistência automática entre SASs
- Auditabilidade e transparência
- Desacoplamento entre SASs (confiança apenas na blockchain)
- Facilidade de integração de novos SASs
- Resiliência e tolerância a falhas

---

## Interface REST e WINNF

- O middleware expõe endpoints REST compatíveis com fluxos CBSD-SAS e SAS-SAS (ex: `/v1.2/fullActivityDump`).
- A interface REST SAS-SAS tradicional do WINNF é **opcional** neste projeto, pois a sincronização principal ocorre via blockchain.
- Endpoints adicionais do WINNF (ex: `peerSasRegistration`, `eventNotification`) podem ser implementados conforme demanda.

### Decisão sobre testes WINNF
- **Não é obrigatório passar nos testes SAS-SAS do WINNF** se todos os SASs do ecossistema usam a blockchain como camada de sincronização.
- A interface REST SAS-SAS pode ser expandida facilmente se houver necessidade de interoperar com SASs legados ou buscar certificação.

---

## Integração e Certificados

- O middleware utiliza mTLS (mutual TLS) via Nginx para autenticação e segurança.
- Certificados e CAs podem ser compartilhados com outros projetos (ex: Spectrum-Access-System) para facilitar testes e integração.
- Scripts e exemplos de uso (curl, Python) estão disponíveis para automação e validação dos fluxos.

---

## Expansão Futura

- A arquitetura permite fácil expansão para suportar novos endpoints, fluxos WINNF ou integrações com outros sistemas.
- Para máxima compatibilidade, basta implementar os endpoints REST SAS-SAS adicionais conforme o padrão WINNF.
- O histórico de decisões e a base de código facilitam a evolução do projeto conforme novas demandas.

---

## Histórico de Decisões

- **Foco na blockchain como camada de sincronização:** Priorizado para garantir consistência e auditabilidade.
- **Interface REST SAS-SAS tradicional é opcional:** Implementada apenas conforme necessidade de interoperabilidade externa.
- **Manutenção do trabalho realizado:** Toda a infraestrutura de mTLS, automação, scripts e integração foi mantida para facilitar futuras expansões.

---

## Como contribuir ou expandir

- Consulte os exemplos de uso e scripts para integração.
- Para adicionar novos endpoints ou fluxos, siga o padrão já estabelecido no código.
- Documente novas decisões e integrações neste arquivo para manter o histórico claro. 