# Aventura no Terminal

Bem-vindo a "Aventura no Terminal", um RPG solo em modo texto que roda direto no seu terminal, com uma interface moderna construída com `rich`.

## Panorama do Projeto

- **Gênero:** Roguelike leve por turnos.
- **Versão atual:** `v1.4.2`.
- **Plataforma:** Python 3.12+.
- **UI:** Painéis, barras e entradas estilizadas com `rich` (nada de `print` cru!).

## Pré-requisitos

1. **Python 3.12 ou superior** instalado e disponível no seu `PATH`.
2. Opcional, mas recomendado: criar um ambiente virtual (`venv`, `conda`, `pipenv`, etc.).

## Instalação Rápida (Jogador)

Execute os comandos abaixo exatamente nessa ordem:

```bash
# 1. Clonar o repositório
git clone https://github.com/PauloNRocha/rpg-de-terminal.git

# 2. Entrar na pasta do projeto
cd rpg-de-terminal

# 3. (Opcional) Criar e ativar um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 4. Instalar dependências de execução
pip install -r requirements.txt

# 5. Iniciar a aventura 😎
python3 jogo.py
```

## Ambiente de Desenvolvimento

Se for contribuir ou rodar os testes automatizados:

```bash
# Partindo da raíz do projeto e com o venv ativo (se estiver usando)
pip install -r requirements-dev.txt

# (Opcional) Configurar o pre-commit para o lint automático
pre-commit install

# Rodar o suite de testes
pytest
```

## Funcionalidades Principais (v1.4.0)

- **Progressão de Masmorra Dinâmica:** mapas 10x10 gerados proceduralmente com caminho garantido, salas especiais (entrada, chefe, escada) e becos extras (`src/gerador_mapa.py`).
- **Combate por Turnos Estilizado:** interface completa com barras de HP/XP, log de combate e opções de ação (`src/combate.py`, `src/ui.py`).
- **Sistema de XP e Level Up:** múltiplos níveis por loop, atributos restaurados e bônus aplicados automaticamente (`jogo.py:29`).
- **Salvar e Continuar:** grave o progresso com um clique no menu de exploração e retome pelo menu principal quando quiser.
- **Arquitetura com Dataclasses:** personagens, itens e inimigos usam `dataclasses`, garantindo serialização confiável, menos bugs e APIs mais claras para novas features.
- **Inventário Inteligente:** telas dedicadas para visualizar, equipar e usar itens, com comparação lado a lado dos bônus (`jogo.py`, `src/ui.py`).
- **Loot Procedural:** inimigos droparam itens gerados a partir de templates por raridade (`src/gerador_itens.py`, `src/data/itens.json`).
- **Inimigos Escaláveis:** atributos escalam 15% por nível e tipos são carregados de JSON (`src/gerador_inimigos.py`, `src/data/inimigos.json`).

## Créditos e IA

- Este projeto é desenvolvido por Paulo N. Rocha, com apoio de IA (assistente de código e revisão técnica).
- Desenvolvedores: Paulo N. Rocha e IA.
- Notas: partes do design e refatorações foram planejadas e validadas com auxílio de ferramentas de IA, mantendo revisão humana e testes automatizados.
- **Fluxo Polido de UI:** menus, prompts, eventos e game over cinematográfico via `rich.Panel`, `rich.Table` e `rich.Bar` (`src/ui.py`).
- **Tratamento Seguro de Ctrl+C:** saída elegante com mensagem final (`jogo.py:348`).

## Como Jogar (Passo a Passo)

1. Inicie o jogo (`python3 jogo.py`).
2. **Criação do Personagem:** informe o nome e escolha uma classe (Guerreiro, Mago ou Arqueiro) visualizando a descrição completa.
3. **Exploração:** use o menu numérico para se mover, abrir o inventário ou sair da masmorra.
4. **Salvar Progresso:** escolha a opção "Salvar jogo" a qualquer momento da exploração para gravar o estado atual. O menu principal exibirá "Continuar Aventura" quando houver um save.
5. **Combate:** enfrente inimigos por turnos; use itens, ataque ou tente fugir. Vitória concede XP e loot.
6. **Level Up:** ao acumular XP suficiente, suba de nível, restaure o HP e receba melhorias automáticas.
7. **Chefe e Escada:** derrote o Chefe Orc para liberar a escada e avançar para níveis mais profundos (com cura parcial ao descer).
8. **Fim de Jogo:** morrendo, fugindo ou saindo voluntariamente, receba uma despedida estilizada.

## Estrutura do Código

- `jogo.py` – loop principal, gerenciamento de estados e progressão de masmorra.
- `src/ui.py` – todos os componentes de interface baseados em `rich`.
- `src/gerador_mapa.py` – geração procedural do mapa.
- `src/gerador_inimigos.py` / `src/data/inimigos.json` – templates e escala de inimigos.
- `src/gerador_itens.py` / `src/data/itens.json` – catálogo de itens e raridades.
- `src/personagem.py` / `src/data/classes.json` – classes jogáveis e criação de personagem.
- `tests/` – suíte de testes unitários com `pytest`.

## Roadmap Sugerido

- Sistema de salvamento e carregamento rápido.
- Novos slots de equipamento (armadura, acessórios) e efeitos especiais de itens.
- Balanceamento fino da curva de XP e raridade de drops via tabelas JSON.
- Empacotamento com `console_scripts` para rodar via `aventura-terminal` após instalação.

## Contribuindo

1. Crie um fork e uma branch descritiva.
2. Garanta que `pre-commit` e `pytest` passem antes do commit.
3. Atualize `CHANGELOG.md` (Keep a Changelog) e o número da versão em `src/version.py` quando entregar novas features.
4. Abra um PR descrevendo claramente as mudanças e incluindo demonstrações se possível.

Divirta-se explorando a masmorra pelo terminal! 🐉
