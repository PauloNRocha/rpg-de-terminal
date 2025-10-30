# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2025-10-30

### Adicionado

-   **Sistema de Experiência e Níveis:**
    -   O jogador agora tem `nível`, `XP atual` e `XP para o próximo nível`.
    -   Ao derrotar inimigos, o jogador ganha pontos de experiência.
    -   Implementada a função `verificar_level_up` que aumenta o nível do jogador e melhora seus atributos (`HP Máximo`, `Ataque`, `Defesa`).
    -   A interface agora exibe as informações de nível e XP do jogador.
-   **Geração Dinâmica de Inimigos:**
    -   Criado o módulo `src/inimigos.py` com templates de inimigos (estatísticas de nível 1).
    -   Criado o módulo `src/gerador_inimigos.py` que gera inimigos com atributos escalados para um nível específico.
    -   O mapa (`src/mapa.py`) foi atualizado para definir um `nivel_area` para cada sala, determinando o nível dos inimigos que aparecem.
    -   Inimigos agora são gerados dinamicamente ao entrar em uma sala, garantindo que o desafio cresça com o jogador.

## [0.5.1] - 2025-10-30

### Modificado

-   Atualizado o `README.md` para refletir todas as funcionalidades implementadas até a versão `0.5.0`, incluindo:
    -   Criação de Personagem e Exploração de Mapa.
    -   Sistema de Combate e Itens/Inventário (com geração procedural).
    -   Tela de Game Over e Estrutura Modular.
    -   Testes Automatizados e CI/CD com GitHub Actions.

## [0.5.0] - 2025-10-30

### Adicionado

-   Implementado o sistema de **Geração Processual de Itens** (loot dinâmico).
-   Criado o módulo `src/gerador_itens.py` com a lógica para criar itens aleatórios.
-   O sistema de itens foi refatorado em `src/itens.py` para usar `ITEM_TEMPLATES`, `PREFIXOS` e `SUFIXOS`.
-   Inimigos agora dropam itens gerados aleatoriamente com base em sua `drop_raridade` (comum, incomum, raro).
-   Itens estáticos foram removidos das salas para focar o loot nos drops de monstros.

## [0.4.3] - 2025-10-30

### Corrigido

-   Ajustada a lógica da função `calcular_dano` em `src/combate.py` para garantir que o dano seja 0 quando o ataque é menor ou igual à defesa.
-   Corrigido o erro de importação de módulos nos testes, adicionando o arquivo `pytest.ini` com `pythonpath = .` na raiz do projeto.

## [0.4.2] - 2025-10-29

### Adicionado

-   Criado `requirements.txt` com as dependências do projeto (pytest).
-   Criado o diretório `tests/` para organizar os testes.
-   Implementado o primeiro teste unitário em `tests/test_combate.py` para a função de cálculo de dano.
-   Configurado o pipeline de CI/CD com GitHub Actions (`.github/workflows/python-ci.yml`).
    -   O workflow executa os testes automaticamente em cada `push` e `pull request` para `main`.

### Modificado

-   Refatorada a lógica de cálculo de dano em `src/combate.py` para uma função pura (`calcular_dano`), melhorando a testabilidade.

## [0.4.1] - 2025-10-28

### Corrigido

-   Corrigido `TypeError` em `iniciar_combate()`: O argumento `usar_pocao_callback` agora é passado corretamente, resolvendo o bug que impedia o início do combate.

## [0.4.0] - 2025-10-28

### Adicionado

-   Implementado o sistema de itens e inventário.
-   Criado o módulo `src/itens.py` para definir os itens (Poção de Cura, Espada Longa, Escudo de Aço).
-   O jogador agora possui um `inventario` e um dicionário `equipamento` (arma, escudo).
-   Itens podem ser encontrados em salas específicas do mapa.
-   Monstros agora podem dropar itens ao serem derrotados.
-   Adicionadas opções no menu de aventura para `Ver Inventário`, `Usar Item` e `Equipar Item`.
-   Implementada a lógica para coletar itens automaticamente ao entrar em uma sala.
-   A função `aplicar_bonus_equipamento` foi criada para recalcular os atributos do jogador com base nos itens equipados.
-   Integrada a opção de `Usar Poção` durante o combate, permitindo ao jogador curar-se em batalha.

## [0.3.2] - 2025-10-28

### Adicionado

-   Criada uma tela de "Game Over" mais elaborada em `src/utils.py`, com arte ASCII e uma mensagem final.
-   A nova tela aguarda a entrada do jogador (pressionar Enter) antes de retornar ao menu, melhorando o fluxo.
-   A lógica de fim de jogo foi centralizada em `jogo.py`, que agora chama a função `tela_game_over`.

## [0.3.1] - 2025-10-28

### Modificado

-   O sistema de comandos por texto (`ir norte`) foi substituído por um menu de ações numérico, melhorando a usabilidade.
-   O menu de ações agora é gerado dinamicamente, mostrando apenas os movimentos possíveis para a sala atual.
-   Adicionada a ação "Voltar por onde veio", permitindo ao jogador retornar à sua posição anterior.
-   A lógica de fuga do combate agora retorna o jogador para a sala anterior.

## [0.3.0] - 2025-10-28

### Adicionado

-   Implementado o sistema de combate por turnos.
-   Criado o módulo `src/combate.py` para gerenciar a lógica das batalhas.
-   Adicionados três tipos de inimigos (Goblin, Orc, Chefe) com atributos distintos em `src/mapa.py`.
-   Salas do mapa agora podem conter inimigos.
-   O combate é iniciado automaticamente ao entrar em uma sala com um inimigo.
-   Implementadas as ações de `atacar` e `fugir` no combate.
-   Adicionado um pequeno fator de aleatoriedade no cálculo de dano.
-   Inimigos derrotados são removidos permanentemente do mapa.
-   O jogo agora termina se o HP do jogador chegar a zero.

## [0.2.1] - 2025-10-28

### Modificado

-   Refatorada a estrutura do projeto para uma arquitetura modular.
-   Criado o diretório `src` para abrigar o código-fonte principal.
-   Lógica de criação de personagem movida para `src/personagem.py`.
-   Definição do mapa movida para `src/mapa.py`.
-   Funções utilitárias (como `limpar_tela`) movidas para `src/utils.py`.
-   O arquivo `jogo.py` foi simplificado para atuar como o orquestrador principal do jogo.

## [0.2.0] - 2025-10-28

### Adicionado

-   Implementado o sistema de mapa como uma grade 3x3.
-   Cada sala no mapa agora tem um nome e uma descrição únicos.
-   Adicionado rastreamento da posição do jogador (coordenadas x, y).
-   Criada a função `iniciar_aventura` que contém o loop de exploração.
-   Implementada a lógica de movimentação com os comandos `ir norte`, `ir sul`, `ir leste`, `ir oeste`.
-   Adicionada verificação de limites para impedir que o jogador saia do mapa.

## [0.1.0] - 2025-10-28

### Adicionado

-   Estrutura inicial do projeto com o loop principal do jogo (`jogo.py`).
-   Função para limpar a tela do terminal, melhorando a legibilidade.
-   Funcionalidade de criação de personagem com escolha de nome e classe.
-   Três classes iniciais com atributos distintos: Guerreiro, Mago e Arqueiro.
-   Configuração do repositório Git e envio inicial para o GitHub.
