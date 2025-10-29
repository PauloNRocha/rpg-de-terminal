# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

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
