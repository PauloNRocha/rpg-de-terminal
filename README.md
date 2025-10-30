# Aventura no Terminal

Bem-vindo ao "Aventura no Terminal", um RPG de texto clássico inspirado em D&D, construído com Python.

## Sobre o Jogo

Este é um jogo de RPG para um jogador onde você assume o papel de um herói explorando masmorras perigosas, enfrentando monstros e buscando tesouros. Toda a interação acontece através de comandos de texto simples no seu terminal.

## Como Jogar

Para executar o jogo, siga os passos:

1.  **Clone o repositório (se ainda não o fez):**
    ```bash
    git clone https://github.com/PauloNRocha/rpg-de-terminal.git
    ```

2.  **Navegue até o diretório do projeto:**
    ```bash
    cd rpg-de-terminal
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute o script principal:**
    ```bash
    python3 jogo.py
    ```

## Funcionalidades Atuais (v0.5.0)

*   **Criação de Personagem:** Escolha nome e classe (Guerreiro, Mago, Arqueiro) com atributos iniciais.
*   **Exploração de Mapa:** Navegue por um mapa de masmorra com um menu de ações numérico e dinâmico.
*   **Sistema de Combate:** Enfrente monstros em batalhas por turnos, com opções de atacar e fugir.
*   **Sistema de Itens e Inventário:**
    *   Colete itens gerados proceduralmente (armas, escudos, poções) com bônus aleatórios.
    *   Gerencie seu inventário, equipe armas e escudos, e use poções de cura (inclusive em combate).
*   **Tela de Game Over:** Uma tela de fim de jogo mais elaborada para quando seu herói for derrotado.
*   **Estrutura Modular:** O código é organizado em módulos (`personagem`, `mapa`, `combate`, `itens`, `gerador_itens`, `utils`) para facilitar a manutenção e expansão.
*   **Testes Automatizados:** Testes unitários com `pytest` garantem a qualidade do código.
*   **CI/CD com GitHub Actions:** O projeto é automaticamente testado em cada `push` e `pull request`.

## Próximos Passos

*   Sistema de Experiência e Níveis.
*   Geração Procedural de Mapas (Masmorras Infinitas).