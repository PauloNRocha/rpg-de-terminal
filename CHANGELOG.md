# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2025-11-07

### Adicionado

-   **Refatoração Completa para Dataclasses:** Concluída a migração de todas as entidades do jogo (Personagem, Inimigo, Item) de dicionários para `dataclasses`.
    -   Melhora significativa na segurança de tipos, legibilidade e manutenibilidade do código.
    -   Atualização de todos os módulos (`jogo.py`, `src/combate.py`, `src/ui.py`, `src/armazenamento.py`, `src/gerador_inimigos.py`, `src/gerador_itens.py`, `src/personagem.py`) para interagir com as novas estruturas de dados.
    -   Ajustes nos testes (`tests/test_jogo.py`) para criar e manipular instâncias de `dataclasses` corretamente.

### Corrigido

-   **Erros de Linting e Formatação:** Resolvidos todos os erros de linting (`F821`, `E501`, `D401`, `D205`) e formatação (`invalid-syntax`) identificados pelo `ruff` e `pre-commit`.
    -   Garantida a conformidade com os padrões de código Python e docstrings.
-   **Erros de Teste (`AttributeError`, `TypeError`):** Corrigidos os erros nos testes que surgiram devido à transição de dicionários para `dataclasses`.
    -   Atualizadas as fixtures e a lógica dos testes para criar e manipular corretamente as instâncias de `Personagem` e `Item`.

## [1.4.0] - 2025-11-06

### Alterado

-   **Refatoração Arquitetural para Dataclasses:** Realizada uma refatoração completa da estrutura de dados do jogo, substituindo o uso de dicionários (`dict`) por `dataclasses` para representar as entidades principais (Jogador, Inimigo, Item).
    -   Criado o novo módulo `src/entidades.py` para centralizar as definições das `dataclasses`.
    -   Todos os módulos, incluindo `jogo.py`, `src/combate.py`, `src/ui.py`, e os geradores, foram atualizados para usar as novas estruturas de dados, resultando em um código mais seguro, legível e fácil de manter.
    -   O sistema de salvamento e carregamento foi ajustado para serializar e desserializar as `dataclasses` de forma transparente.

## [1.3.1] - 2025-11-06

### Corrigido

-   **Falha Crítica - Verificação de Versão no Carregamento de Saves:** Implementada a validação da versão do jogo salvo ao carregar um save. Agora, se a versão do save for incompatível com a versão atual do jogo, o carregamento será impedido e uma mensagem de erro clara será exibida ao jogador, prevenindo crashes e corrupção de dados em futuras atualizações.

## [1.3.0] - 2025-11-06

### Adicionado

-   Sistema de salvamento e carregamento em JSON, incluindo opção de salvar durante a aventura e continuar pelo menu principal.
-   Menu principal dinâmico exibindo "Continuar Aventura" quando há um save disponível.

### Corrigido

-   Exibição do campo "Efeito" no inventário agora mostra bônus de armas e escudos.

### Removido

-   Arquivos PostScript gerados acidentalmente (`copy`, `json`, `random`) foram excluídos do repositório e adicionados ao `.gitignore`.
-   Arquivo legado `src/mapa.py` removido após a migração completa para geração procedural (`src/gerador_mapa.py`).

## [1.2.9] - 2025-11-06

### Alterado

-   README atualizado com instruções para v1.2.8, diferenciando ambientes de jogador e desenvolvimento.
-   Dependências separadas entre `requirements.txt` (execução) e `requirements-dev.txt` (ferramentas de desenvolvimento).

## [1.2.8] - 2025-11-06

### Corrigido

-   **`KeyboardInterrupt` Duplo:** Corrigido o comportamento ao sair do jogo com `Ctrl+C`. A mensagem de despedida agora é exibida sem esperar por um novo `input`, evitando um segundo `KeyboardInterrupt` e a exibição de um traceback.

## [1.2.7] - 2025-11-06

### Corrigido

-   **`KeyError` no Inventário:** Corrigido um erro de digitação (`inventário` em vez de `inventario`) que causava um `KeyError` e quebrava o jogo ao tentar equipar um item.
-   **Inconsistências Lógicas em `jogo.py`:**
    -   **`KeyError` Potencial:** Garantido que `ataque_base` e `defesa_base` sejam inicializados na criação do personagem para evitar erros durante o `level up`.
    -   **`NameError`:** Corrigida a chamada da função de criação de personagem.
    -   **Feedback de UI:** Adicionada uma mensagem de evento para informar ao jogador quando um item é dropado por um inimigo.

## [1.2.6] - 2025-11-05

### Corrigido

-   **`RuntimeError` no Carregamento de Inimigos:** Corrigido o caminho para o arquivo `inimigos.json` em `src/gerador_inimigos.py`. O script agora localiza corretamente o diretório `data` dentro de `src`, resolvendo o erro que impedia o jogo de iniciar ou continuar.
-   **Inconsistência de Versionamento:** Padronizado o controle de versão do projeto.
    -   Criado o arquivo `src/version.py` como um "único ponto de verdade" para a versão.
    -   O `CHANGELOG.md` foi atualizado e alinhado com a nova versão.

## [1.2.5] - 2025-11-05

### Corrigido

-   **Padronização de Código (DevEx):** Aplicadas correções abrangentes de linting e formatação em todos os arquivos do projeto, incluindo:
    -   **Anotações de Tipo (Type Hints):** Adicionadas anotações de tipo a funções e argumentos para melhorar a clareza e a detecção de erros. Corrigida a tipagem de `monkeypatch` em `tests/test_jogo.py` para `pytest.MonkeyPatch`.
    -   **Linhas Longas (`E501`):** Quebradas linhas que excediam o limite de 100 caracteres. Corrigido `SyntaxError` de f-string não terminada em `src/ui.py`.
    -   **Múltiplas Instruções por Linha (`E701`):** Separadas instruções em linhas distintas para maior legibilidade.
    -   **Docstrings (`D103`, `D205`):** Adicionadas docstrings ausentes e ajustado o formato das existentes, incluindo a correção em `src/gerador_itens.py`.
    -   **Otimização (`SIM118`):** Corrigido o uso de `key in dict.keys()` para `key in dict`.
-   **Remoção de Arquivo Obsoleto:** Removido `src/utils.py`, pois suas funções foram migradas para `src/ui.py`.

## [1.2.4] - 2025-11-05

### Adicionado

-   **Ferramentas de Developer Experience (DevEx):** Integradas as ferramentas `ruff` (linting e formatação) e `pre-commit` (ganchos do Git) para garantir a qualidade e consistência do código.
    -   Atualizadas as dependências no `requirements.txt` para as versões mais recentes.
    -   Criado o arquivo `pyproject.toml` para configurar as regras do `ruff`.
    -   Criado o arquivo `.pre-commit-config.yaml` para automatizar a execução do `ruff` antes de cada commit.
    -   Realizada uma limpeza inicial em todo o projeto com `ruff check . --fix` e `ruff format .`.

### Alterado

-   **Configuração do Ruff:** Atualizado o `pyproject.toml` para usar a nova estrutura de configuração `[tool.ruff.lint]` e removidas as regras `ANN101` e `ANN102` depreciadas.

## [1.2.3] - 2025-11-05

### Alterado

-   **Dados de Inimigos Externalizados:** Os templates de inimigos foram movidos do código Python (`src/inimigos.py`) para o arquivo `src/data/inimigos.json`, completando a migração para uma arquitetura orientada a dados e facilitando o balanceamento e a adição de novos inimigos.

## [1.2.2] - 2025-11-05

### Adicionado

-   **Licença GNU GPLv3:** Adicionada a licença GNU General Public License v3.0 ao projeto, garantindo que o software e suas derivações permaneçam de código aberto.

## [1.2.1] - 2025-11-03

### Corrigido

-   **`SyntaxError` em `iniciar_aventura`:** Corrigido o `SyntaxError` na função `iniciar_aventura` em `jogo.py`, onde um bloco `try` não tinha um `except` correspondente.
-   **`SyntaxError` em `equipar_item`:** Corrigido o `SyntaxError` na função `equipar_item` em `jogo.py`, onde o bloco `except` estava vazio. Adicionada uma chamada a `desenhar_tela_evento` para fornecer feedback ao usuário em caso de entrada inválida.

## [1.2.0] - 2025-11-03

### Adicionado

-   **Sistema de Progressão de Masmorra:** Implementado um sistema que permite ao jogador avançar para níveis de masmorra progressivamente mais difíceis.
-   **Gerador de Mapa Aprimorado:** O gerador de mapa foi completamente refatorado para criar níveis com um caminho principal garantido, uma sala de chefe estratégica e uma escadaria para o próximo nível, eliminando a sensação de exploração sem rumo.

### Alterado

-   **Fluxo de Jogo Principal:** A lógica principal do jogo foi movida para a função `main` para gerenciar os níveis da masmorra e a geração de novos mapas.
-   **Dados de Classes Externalizados:** As definições de classes de personagens foram movidas do código Python para o arquivo `src/data/classes.json`, facilitando o balanceamento e a adição de novas classes.
-   **Dados de Itens Externalizados:** A geração procedural de itens foi substituída por um sistema que carrega itens pré-definidos do arquivo `src/data/itens.json`, simplificando a lógica e o gerenciamento de itens.

## [1.1.4] - 2025-11-03

### Corrigido

-   **Loop de Combate:** Corrigido o bug onde as opções de combate continuavam a ser exibidas após a vitória ou derrota do jogador. O loop agora termina imediatamente.
-   **Lógica do Inventário:** Corrigido o bug onde todas as opções do inventário levavam de volta ao mapa. As opções "Usar Item" e "Equipar Item" agora funcionam corretamente.
-   **Exibição de HP Negativo:** O HP exibido na UI (HUD e tela de combate) agora é fixado em um mínimo de 0, evitando a exibição de valores negativos.

### Adicionado

-   **Tela de Game Over Aprimorada:** A tela de "Game Over" foi reformulada para exibir mensagens mais temáticas e aleatórias, melhorando a imersão.

## [1.1.3] - 2025-11-03

### Corrigido

-   **Renderização da UI (Barras de HP/XP):** Corrigido o `TypeError` na renderização das barras de HP e XP em `desenhar_hud_exploracao` e `desenhar_tela_combate`. As funções foram refatoradas para usar `Table.grid` com múltiplas colunas, que é a maneira correta de compor texto e objetos `Bar`, garantindo a renderização correta.
-   **Inconsistências de UI em `src/combate.py`:** Removidas chamadas diretas a `print` e `input` no loop de combate, centralizando a interação com o usuário na função `desenhar_tela_combate`.
-   **Inconsistências de UI em `equipar_item`:** A função `desenhar_tela_equipar` em `src/ui.py` foi modificada para usar `console.input` e a função `equipar_item` em `jogo.py` foi ajustada para usar o retorno de `desenhar_tela_equipar`.
-   **Inconsistências de UI em `jogo.py`:**
    -   Substituídas chamadas diretas a `print` por `desenhar_tela_evento` na função `iniciar_aventura`.
    -   Criada e importada a função `tela_game_over` em `src/ui.py` para exibir a tela de fim de jogo.
    -   Substituídos `pass` e `time.sleep` por `desenhar_tela_evento` nos blocos `except` e `else` das funções `processo_criacao_personagem` e `main`, respectivamente, para fornecer feedback consistente ao usuário.

## [1.1.2] - 2025-11-03

### Corrigido

-   **Renderização da UI:** Corrigido o bug visual onde as barras de HP e XP eram exibidas como texto (`Bar(...)`) em vez de uma barra gráfica. A função `desenhar_hud_exploracao` agora usa `Text.assemble` para garantir a renderização correta.
-   **`AttributeError` na Tela de Combate:** Corrigida a função `desenhar_tela_combate` para lidar corretamente com o log de combate (uma lista de strings), resolvendo o erro que impedia a renderização da tela.

## [1.1.1] - 2025-11-03

### Corrigido

-   **`ImportError` da Classe `Bar`:** Corrigido o erro de importação da classe `Bar` da biblioteca `rich`, alterando a importação para o caminho correto (`rich.bar`).
-   **`ImportError` da Função `desenhar_tela_combate`:** Adicionada a função `desenhar_tela_combate` ao arquivo `src/ui.py`, que estava faltando após as refatorações da UI.
-   **`ImportError` da Função `desenhar_tela_inventario`:** Adicionada a função `desenhar_tela_inventario` ao arquivo `src/ui.py`, que estava faltando após as refatorações da UI.
-   **`KeyError` na Descrição da Classe:** Adicionada a chave `descricao` a cada classe no dicionário `CLASSES` em `src/personagem.py`, resolvendo o `KeyError` que ocorria ao tentar exibir a descrição da classe na tela de escolha.
-   **Consistência da UI:** A função `desenhar_tela_escolha_classe` em `src/ui.py` foi modificada para usar `console.input` em vez de `input` direto, garantindo consistência com a biblioteca `rich` e melhorando a interação.
-   **`NameError` na Chamada de `mostrar_inventario`:** Corrigido o erro de digitação na chamada da função `mostrar_inventario` em `jogo.py` (removido o acento).
-   **`NameError` na Variável `escudo_equipado`:** Corrigido o `NameError` na função `desenhar_tela_equipar` em `src/ui.py`. A variável `escudo_equipada` foi alterada para `escudo_equipado`, resolvendo o erro que impedia a renderização correta da tela de equipamento.

## [1.1.0] - 2025-11-02

### Adicionado

-   **Dependência `rich`:** Adicionada a biblioteca `rich` ao `requirements.txt` para uma interface de usuário aprimorada no terminal.

### Melhorado

-   **Interface de Usuário (UI) Completa:** Todas as funções de UI no módulo `src/ui.py` foram refatoradas para utilizar a biblioteca `rich`, substituindo a implementação anterior baseada em `colorama` e `print()`/`input()` diretos.
    -   **`desenhar_caixa`:** Agora utiliza `rich.panel.Panel` para caixas de texto com títulos e conteúdo formatados.
    -   **`desenhar_hud_exploracao`:** Implementa `rich.panel.Panel` para as seções de jogador, sala e opções, e `rich.progress.Bar` para as barras de HP e XP, oferecendo um HUD mais visual e informativo.
    -   **`desenhar_tela_evento`:** Utiliza `rich.panel.Panel` para exibir mensagens de evento de forma padronizada.
    -   **`desenhar_tela_equipar`:** Apresenta a comparação de itens equipados e disponíveis usando `rich.table.Table` para maior clareza.
    -   **`desenhar_menu_principal`:** Refatorado com `rich.panel.Panel` e `rich.text.Text` para um menu principal mais atraente.
    -   **`desenhar_tela_input`:** Utiliza `rich.panel.Panel` e `console.input` para prompts de entrada de texto consistentes.
    -   **`desenhar_tela_escolha_classe`:** Exibe as opções de classe usando `rich.panel.Panel` e `rich.table.Table`.
    -   **`desenhar_tela_resumo_personagem`:** Apresenta o resumo do personagem com `rich.panel.Panel` e `rich.text.Text` formatado.

## [1.0.3] - 2025-11-02

### Corrigido

-   **`ImportError` da Função `limpar_tela`:** Resolvido o erro de importação da função `limpar_tela` ao criá-la explicitamente no módulo `src/ui.py`, permitindo que `jogo.py` a importe e utilize corretamente.

## [1.0.2] - 2025-11-02

### Corrigido

-   **`NameError` na Função `usar_item`:** Corrigido o erro que impedia a função `usar_item` de limpar a tela, importando corretamente a função `limpar_tela` de `src/ui.py`.

### Melhorado

-   **Refatoração da UI de `usar_item`:** A função `usar_item` foi refatorada para utilizar o novo padrão de interface do usuário, substituindo `print()` e `input()` diretos por chamadas a funções de UI como `desenhar_tela_input` e `desenhar_tela_evento`, garantindo consistência visual e melhorando a experiência do jogador.

## [1.0.1] - 2025-11-02

### Corrigido

-   **`NameError` no Menu de Ações:** Corrigido um erro de digitação (`aco_escolhida` em vez de `acao_escolhida`) que causava um `NameError` e quebrava o jogo ao tentar selecionar uma ação como "Ver Inventário".
-   **Posição Inicial do Jogador:** O jogador agora começa consistentemente na sala "Entrada da Masmorra", em vez de em uma posição fixa (0,0) que poderia ser uma parede ou uma sala aleatória.
-   **Balanceamento de Dificuldade Inicial:** O gerador de mapas foi ajustado para garantir que as salas imediatamente adjacentes à entrada sejam sempre de nível 1, evitando encontros com inimigos de nível muito alto no início do jogo.

### Melhorado

-   **Nomes das Salas:** As salas geradas proceduralmente agora recebem nomes descritivos e variados (ex: "Câmara Empoeirada", "Corredor Estreito") em vez de nomes genéricos como "Sala 63", melhorando a imersão.

## [1.0.0] - 2025-11-02

### Adicionado

-   **Geração Procedural de Mapas:** O jogo agora gera masmorras aleatoriamente a cada nova aventura, proporcionando rejogabilidade infinita.
    -   Criado o novo módulo `src/gerador_mapa.py` para encapsular a lógica de geração de mapas.
    -   O algoritmo de geração cria salas conectadas e define níveis de área dinamicamente.

### Modificado

-   **Módulo Principal do Jogo (`jogo.py`):**
    -   Removida a importação do mapa estático (`src/mapa.py`).
    -   Integrada a chamada ao `gerar_mapa()` para criar um novo mapa a cada início de aventura.

## [0.9.1] - 2025-11-02

### Adicionado

-   **Cobertura de Testes (`jogo.py`):**
    -   Adicionado o novo arquivo de teste `tests/test_jogo.py`.
    -   Implementados testes unitários para a função `verificar_level_up`, cobrindo cenários de level up único, múltiplo e nenhum.
    -   Implementados testes unitários para a função `aplicar_bonus_equipamento`, cobrindo a aplicação de bônus de arma, escudo, ambos e a remoção de equipamento.

### Corrigido

-   **Testes de Level Up:** Corrigidos os testes de `level_up` que falhavam devido à espera por input do usuário. A função de UI `desenhar_tela_evento` foi substituída por uma função vazia durante os testes usando `monkeypatch` do `pytest`.

## [0.9.0] - 2025-11-02

### Adicionado

-   **Tratamento de Interrupção (Ctrl+C):** O jogo agora lida graciosamente com interrupções por teclado (Ctrl+C), exibindo uma mensagem de despedida amigável e encerrando o programa de forma limpa, sem exibir tracebacks.

### Modificado

-   **Módulo Principal do Jogo (`jogo.py`):** O loop principal da função `main` foi envolvido em um bloco `try...except KeyboardInterrupt` e o módulo `sys` foi importado para permitir um encerramento controlado.

## [0.8.0] - 2025-11-02

### Adicionado

-   **Persistência de Inimigos:** Inimigos agora mantêm seu HP e estado (derrotado ou não) nas salas do mapa, mesmo após o jogador fugir do combate. Isso permite que o jogador retorne para finalizar inimigos enfraquecidos.

### Modificado

-   **Módulo de Mapa (`src/mapa.py`):** Todas as salas agora incluem a chave `"inimigo_atual": None` para armazenar a instância de um inimigo persistente.
-   **Módulo de Combate (`src/combate.py`):** A função `iniciar_combate` agora retorna uma tupla `(resultado_combate, inimigo_atualizado)`, permitindo que o estado do inimigo seja salvo após o combate.
-   **Módulo Principal do Jogo (`jogo.py`):** A função `iniciar_aventura` foi atualizada para gerenciar a persistência de inimigos, verificando inimigos existentes, gerando novos quando necessário e atualizando o estado do inimigo na sala após cada combate.

## [0.7.4] - 2025-11-02

### Corrigido

-   **Bug Crítico (`NameError`):** Corrigido um `NameError` que impedia o jogo de iniciar após a criação do personagem. A variável `MAPA` não estava sendo importada em `jogo.py` após a refatoração da UI.

## [0.7.3] - 2025-11-02

### Melhorado

-   **Padronização Estética (UI/UX):**
    -   O menu principal, a tela de criação de personagem (nome e seleção de classe) e o resumo do personagem agora utilizam o novo sistema de UI com caixas e ícones Unicode, garantindo uma experiência visual coesa desde o início do jogo.
    -   As mensagens de boas-vindas e despedida também foram integradas ao novo sistema de UI.

### Refatorado

-   **Módulo de Personagem (`src/personagem.py`):** A função `criar_personagem` foi refatorada para separar a lógica de criação de personagem da apresentação da UI, tornando-a mais modular e reutilizável.
-   **Fluxo Principal do Jogo (`jogo.py`):** A função `main` e o processo de criação de personagem foram reescritos para orquestrar as chamadas às novas funções de UI, garantindo um fluxo de entrada coeso e visualmente padronizado.

## [0.7.2] - 2025-10-31

### Corrigido

-   **Loop de Múltiplos Level Ups:** A lógica de subida de nível agora usa um loop `while`, permitindo que o jogador ganhe vários níveis de uma vez se acumular XP suficiente.
-   **Lógica do Chefe:** A sala final da masmorra agora gera o "Chefe Orc" de forma consistente, como pretendido.

### Melhorado

-   **Comparação de Itens (UX):**
    -   A tela de inventário agora exibe os bônus de cada item.
    -   Uma nova tela de "Equipar Item" foi criada, mostrando o equipamento atual e os itens da mochila lado a lado para facilitar a comparação.

## [0.7.1] - 2025-10-31

### Corrigido

-   Corrigidas as asserções no teste `tests/test_combate.py` para refletir a variação de dano correta (+/- 20%), garantindo que os testes passem.

## [0.7.0] - 2025-10-30

### Adicionado

-   **Revitalização da UI/UX:**
    -   Implementado um sistema de design visual consistente para todas as telas do jogo, utilizando caixas, ícones Unicode e cores para uma experiência mais imersiva.
    -   Criado o módulo `src/ui.py` para centralizar toda a lógica de renderização da interface.
    -   Adicionada a dependência `colorama` para garantir a compatibilidade de cores em diferentes terminais.
-   **Novas Telas da UI:**
    -   `desenhar_hud_exploracao`: Uma nova interface principal com barras de status visuais para HP e XP.
    -   `desenhar_tela_combate`: Uma nova tela de batalha que mostra jogador e inimigo lado a lado e um log de combate.
    -   `desenhar_tela_inventario`: Uma nova tela de inventário com layout profissional.
    -   `desenhar_tela_evento`: Uma tela genérica para mensagens importantes como "Level Up" e "Game Over".

### Modificado

-   Os módulos `jogo.py`, `combate.py` e `utils.py` foram refatorados para usar o novo sistema de UI, separando a lógica do jogo da sua apresentação.

### Corrigido

-   Corrigido um `NameError` em `jogo.py` causado pela falta da importação de `limpar_tela` no menu principal.

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
