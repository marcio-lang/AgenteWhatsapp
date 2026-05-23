# Flux Zap Roadmap

## Objetivo
Organizar a evolução do Flux Zap com foco em produtividade do atendente, clareza visual, percepção de produto premium e maturidade operacional.

## Como usar este documento
- Marcar cada item como `Pendente`, `Em andamento` ou `Concluído`
- Executar por prioridade, começando pelos itens de impacto direto na operação
- Revisar ao final de cada sprint o que foi entregue e o que precisa ser replanejado

## Prioridade 1 — Atendimento

### 1.1 Priorização visual da lista de conversas
- Status: Pendente
- Objetivo: facilitar identificação rápida de conversas importantes
- Tarefas:
  - destacar conversas não lidas
  - destacar conversas urgentes
  - mostrar tempo sem resposta
  - diferenciar conversa nova, em atendimento e aguardando cliente
- Critério de conclusão:
  - um atendente consegue identificar prioridade sem abrir todas as conversas

### 1.2 Melhorar o topo da conversa
- Status: Pendente
- Objetivo: reduzir tempo gasto com ações repetidas
- Tarefas:
  - adicionar ações rápidas como assumir, transferir, encerrar e etiquetar
  - exibir responsável atual da conversa
  - exibir status do atendimento
- Critério de conclusão:
  - as principais ações operacionais ficam visíveis sem depender de navegação extra

### 1.3 Enriquecer painel lateral direito
- Status: Pendente
- Objetivo: transformar o painel em área de contexto útil
- Tarefas:
  - manter notas e etiquetas
  - incluir origem do contato
  - incluir última interação
  - incluir responsável
  - incluir etapa do funil
  - incluir resumo rápido do cliente
- Critério de conclusão:
  - o painel lateral ajuda na tomada de decisão durante o atendimento

### 1.4 Melhorar o campo de digitação
- Status: Pendente
- Objetivo: aumentar velocidade de atendimento
- Tarefas:
  - melhorar visibilidade do anexo
  - preparar estrutura para respostas rápidas
  - preparar estrutura para templates
  - melhorar estados de foco e clique
- Critério de conclusão:
  - o campo de envio suporta uso contínuo com menos atrito

## Prioridade 2 — Refinamento visual

### 2.1 Ajustar paleta de cores
- Status: Pendente
- Objetivo: reduzir fadiga visual e elevar percepção profissional
- Tarefas:
  - reduzir uso do laranja como cor dominante
  - usar laranja apenas para ações principais e estados de destaque
  - criar uma escala neutra mais consistente
- Critério de conclusão:
  - a interface fica mais confortável para uso prolongado

### 2.2 Padronizar componentes
- Status: Pendente
- Objetivo: criar consistência visual
- Tarefas:
  - padronizar botões
  - padronizar inputs
  - padronizar cards
  - padronizar raios de borda
  - padronizar sombras e espaçamentos
- Critério de conclusão:
  - os componentes parecem pertencer ao mesmo sistema

### 2.3 Melhorar tipografia e contraste
- Status: Pendente
- Objetivo: aumentar leitura e acessibilidade
- Tarefas:
  - reforçar contraste de textos secundários
  - criar hierarquia mais clara entre títulos e metadados
  - revisar tamanhos mínimos de fonte
- Critério de conclusão:
  - leitura mais rápida e confortável em toda a interface

## Prioridade 3 — Dashboard

### 3.1 Transformar dashboard em tela gerencial
- Status: Pendente
- Objetivo: apoiar decisão e acompanhamento operacional
- Tarefas:
  - mostrar conversas por status
  - mostrar mensagens por período
  - mostrar atendimentos por agente
  - mostrar tempo médio de resposta
  - mostrar volume de contatos novos
- Critério de conclusão:
  - o dashboard deixa de ser apenas informativo e passa a ser gerencial

### 3.2 Melhorar card da instância
- Status: Pendente
- Objetivo: dar visibilidade ao estado real da operação
- Tarefas:
  - exibir status com semântica clara
  - exibir última sincronização
  - melhorar destaque dos botões de ação
- Critério de conclusão:
  - o usuário entende rapidamente se a instância está saudável ou exige ação

## Prioridade 4 — Configurações

### 4.1 Reorganizar formulário de configurações
- Status: Pendente
- Objetivo: reduzir aparência técnica e aumentar confiança
- Tarefas:
  - separar em seções como conexão, instância, autenticação e aparência
  - adicionar textos de apoio
  - melhorar o alinhamento dos campos
- Critério de conclusão:
  - a tela fica mais clara mesmo para usuários menos técnicos

### 4.2 Melhorar feedback de salvamento
- Status: Pendente
- Objetivo: evitar dúvida após ações críticas
- Tarefas:
  - mostrar confirmação de sucesso
  - mostrar erro com mensagem clara
  - preparar teste de conexão da API
- Critério de conclusão:
  - o usuário sabe se a configuração foi aplicada corretamente

## Prioridade 5 — Funcionalidades estratégicas

### 5.1 Operação multiagente
- Status: Pendente
- Objetivo: preparar o produto para empresas maiores
- Tarefas:
  - filas de atendimento
  - distribuição automática
  - transferência entre agentes
  - permissões por perfil
- Critério de conclusão:
  - a operação suporta múltiplos atendentes com menos conflito

### 5.2 Produtividade e controle
- Status: Pendente
- Objetivo: aumentar velocidade e governança
- Tarefas:
  - respostas rápidas
  - automações
  - SLA
  - histórico de auditoria
  - alertas de conversa esquecida
- Critério de conclusão:
  - o sistema reduz esforço manual e risco operacional

### 5.3 Visão comercial
- Status: Pendente
- Objetivo: aproximar atendimento e vendas
- Tarefas:
  - funil por contato
  - tags comerciais
  - origem do lead
  - valor potencial
  - integração futura com CRM
- Critério de conclusão:
  - a plataforma passa a apoiar também a gestão de oportunidades

## Quick Wins
- reforçar destaque de conversas não lidas
- reduzir intensidade do laranja
- melhorar contraste de textos secundários
- ampliar utilidade do painel direito
- adicionar ações rápidas no cabeçalho da conversa
- melhorar feedback visual dos formulários

## Metas estruturais
- criar sistema de design consistente
- transformar atendimento em workspace de alta produtividade
- evoluir dashboard para visão gerencial real
- adicionar governança, automação e escalabilidade multiagente

## Ordem recomendada de execução
1. Atendimento
2. Refinamento visual
3. Dashboard
4. Configurações
5. Funcionalidades estratégicas

## Sprint 1 — Execução inicial

### Objetivo da sprint
Entregar melhorias visíveis na tela de atendimento para aumentar produtividade, clareza e percepção de evolução do produto sem depender de mudanças estruturais complexas.

### Resultado esperado
- lista de conversas mais fácil de priorizar
- cabeçalho da conversa mais útil para operação
- painel direito com mais contexto do cliente
- interface com contraste e hierarquia visual melhores

### Escopo fechado da sprint
- incluir indicadores visuais de prioridade na lista de conversas
- melhorar cabeçalho da conversa com status e ações rápidas
- enriquecer o painel lateral direito com dados úteis
- aplicar primeiros ajustes de contraste, espaçamento e cor

### Itens da sprint

#### Item 1 — Lista de conversas
- Status: Pendente
- Prioridade: Alta
- Entregas:
  - badge de não lidas mais visível
  - indicador de urgência
  - exibição de tempo sem resposta
  - estado visual para conversa ativa
- Critério de aceite:
  - o atendente identifica rapidamente quais conversas exigem atenção primeiro

#### Item 2 — Cabeçalho da conversa
- Status: Pendente
- Prioridade: Alta
- Entregas:
  - status atual do atendimento
  - ações rápidas de assumir, transferir e encerrar
  - destaque melhor para nome do contato
- Critério de aceite:
  - as ações principais do atendimento ficam acessíveis sem sair da conversa

#### Item 3 — Painel direito
- Status: Pendente
- Prioridade: Alta
- Entregas:
  - bloco de dados do contato mais completo
  - seção de notas com aparência melhor
  - área de etiquetas mais útil visualmente
  - espaço preparado para origem do contato e responsável
- Critério de aceite:
  - o painel deixa de parecer vazio e passa a apoiar o atendimento

#### Item 4 — Refinamento visual rápido
- Status: Pendente
- Prioridade: Média
- Entregas:
  - reduzir excesso de laranja nas áreas secundárias
  - melhorar contraste dos textos cinzas
  - ajustar espaçamentos dos cards e inputs
  - padronizar melhor botões principais
- Critério de aceite:
  - a tela fica mais confortável e mais próxima de um SaaS profissional

### Ordem de implementação
1. Ajustar lista de conversas
2. Ajustar cabeçalho da conversa
3. Ajustar painel direito
4. Refinar contraste, cores e espaçamentos

### Checklist técnico da sprint
- mapear componentes da tela de atendimento
- identificar estilos compartilhados em CSS
- separar o que é mudança visual do que exige nova estrutura de dados
- implementar primeiro o que já pode ser feito só no frontend
- validar responsividade mínima da tela principal
- revisar consistência final entre sidebar, lista, chat e painel direito

### Itens que ficam fora da sprint
- dashboard gerencial completo
- sistema de SLA
- automações
- filas multiagente
- permissões por perfil
- integração com CRM

### Definição de concluído
- tela de atendimento visivelmente melhorada nas 3 áreas principais
- ganho perceptível de leitura e priorização
- sem quebrar fluxo atual de uso
- base pronta para iniciar a Sprint 2

## Sprint 2 — Prévia
- melhorar dashboard com métricas gerenciais
- reorganizar tela de configurações
- consolidar sistema visual com botões, inputs e cards padronizados

## Sprint 3 — Prévia
- iniciar funcionalidades estratégicas de operação multiagente
- estruturar respostas rápidas, SLA e automações
- aproximar atendimento da visão comercial do contato

## Plano técnico da Sprint 1 — Frontend

### Arquivos de trabalho
- HTML: `frontend/index.html`
- CSS: `frontend/style.css`
- JS: `frontend/app.js`

### Estratégia de execução
- começar por estrutura visual já existente
- evitar mudanças que dependam de backend novo nesta primeira etapa
- usar dados que já estão disponíveis em `chats`, `messages` e contato ativo
- primeiro melhorar percepção visual e priorização, depois adicionar comportamento

### Bloco 1 — Lista de conversas

#### HTML
- manter a estrutura atual da coluna de conversas
- preparar espaço para metadados adicionais dentro de cada item
- se necessário, criar área dedicada para badges e indicadores rápidos

#### CSS
- criar estilo para:
  - `.chat-item.active` com destaque mais forte
  - `.chat-item.unread`
  - `.chat-item.urgent`
  - `.unread-badge`
  - `.chat-meta`
  - `.chat-priority-dot`
  - `.chat-wait-time`
- melhorar espaçamento vertical dos itens
- reforçar contraste entre nome, preview e horário
- ajustar avatar para ficar menos dominante que o estado da conversa

#### JS
- atualizar `renderChatList()` para:
  - aplicar classes condicionais por status visual
  - renderizar badge de não lidas sem estilo inline
  - incluir área de metadados no template do item
  - preparar cálculo de prioridade usando dados disponíveis
- criar helper de priorização visual com regras simples:
  - `unread_count > 0`
  - conversa ativa
  - horário da última mensagem
- manter compatibilidade com busca e filtros atuais

#### Resultado técnico esperado
- lista mais legível
- item ativo mais claro
- badge e prioridade controlados por classes CSS

### Bloco 2 — Cabeçalho da conversa

#### HTML
- expandir a área `.chat-header`
- criar bloco de status operacional ao lado do nome
- adicionar botões de ação rápida com rótulo ou tooltip
- manter ações atuais de favorito e arquivar dentro de uma hierarquia mais clara

#### CSS
- criar estilos para:
  - `.chat-header-status`
  - `.status-pill`
  - `.header-actions-primary`
  - `.header-actions-secondary`
- melhorar alinhamento entre avatar, nome e status
- reduzir aparência genérica dos botões de ícone
- dar destaque controlado às ações primárias sem exagerar no laranja

#### JS
- atualizar `selectChat(chat)` para preencher:
  - status operacional visível
  - nome com hierarquia melhor
  - estado dos botões principais
- se não houver status real no backend, usar status visual temporário:
  - `Nova`
  - `Em atendimento`
  - `Favorita`
- centralizar a atualização visual do cabeçalho em helper próprio

#### Resultado técnico esperado
- cabeçalho mais útil
- ações principais visíveis
- estado da conversa percebido sem depender só da leitura das mensagens

### Bloco 3 — Painel direito

#### HTML
- reorganizar seções do painel em blocos mais claros
- inserir área de resumo do contato acima de notas
- preparar campos visuais para:
  - nome
  - número
  - origem
  - responsável
  - última interação
- manter notas e etiquetas como parte do fluxo principal

#### CSS
- criar estilos para:
  - `.contact-summary-grid`
  - `.contact-summary-item`
  - `.panel-section-title`
  - `.tags-container` com aparência mais forte
  - `.tag` com mais contraste e melhor raio
- reduzir sensação de vazio no topo do painel
- melhorar aparência do textarea e da área de tags
- padronizar botões de salvar e adicionar tag

#### JS
- atualizar `selectChat(chat)` para preencher novos campos visuais com fallback
- ajustar `renderTags()` para remover estilo inline no ícone de exclusão quando possível
- usar helpers simples para exibir:
  - telefone formatado
  - última interação
  - valor padrão quando dado não existir
- não depender de novas rotas nesta etapa

#### Resultado técnico esperado
- painel mais informativo
- notas e etiquetas melhor integradas
- espaço pronto para futura expansão sem retrabalho grande

### Bloco 4 — Refinamento visual rápido

#### HTML
- evitar novos wrappers desnecessários
- preferir reaproveitar a estrutura existente

#### CSS
- revisar variáveis em `:root` para reduzir agressividade do laranja:
  - `--primary-orange`
  - `--primary-orange-light`
  - `--active-nav-bg`
  - `--sent-msg-bg`
- reforçar contraste de:
  - `--text-muted`
  - bordas
  - estados hover
- padronizar:
  - altura de botões
  - altura de inputs
  - raios de borda
  - sombras da área de atendimento
- melhorar estados de foco em inputs e textarea

#### JS
- remover dependência de estilos inline onde houver renderização dinâmica
- concentrar classes de estado no HTML gerado pelo JavaScript

#### Resultado técnico esperado
- interface mais consistente
- menos fadiga visual
- base mais limpa para próximos ajustes

### Ordem exata de desenvolvimento
1. Ajustar variáveis visuais globais no CSS
2. Refatorar `renderChatList()` para remover inline style e adicionar classes
3. Aplicar novos estilos da lista de conversas
4. Expandir estrutura do cabeçalho da conversa
5. Atualizar `selectChat(chat)` para preencher estados do cabeçalho
6. Reorganizar estrutura do painel direito
7. Ajustar `renderTags()` e estilos do painel
8. Fazer revisão final de contraste, espaçamento e consistência

### Checklist de implementação por arquivo

#### `frontend/index.html`
- revisar estrutura da `.chat-header`
- revisar estrutura do painel de detalhes do contato
- adicionar containers sem quebrar IDs já usados pelo JavaScript

#### `frontend/style.css`
- criar classes de estado da lista de chats
- criar classes do novo cabeçalho
- criar classes do resumo do contato
- revisar tokens de cor, contraste e foco

#### `frontend/app.js`
- refatorar `renderChatList()`
- ajustar `selectChat(chat)`
- ajustar `renderTags()`
- adicionar helpers pequenos para estados visuais e metadados

### Critério técnico de aceite
- nenhum comportamento atual da tela de atendimento é quebrado
- filtros e busca continuam funcionando
- seleção de conversa continua funcionando
- notas e tags continuam editáveis
- visual melhora sem exigir backend novo
