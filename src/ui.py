import os
from colorama import init, Fore, Style

# Inicializa o colorama
init(autoreset=True)

# Paleta de Cores
COR_HP = Fore.GREEN
COR_XP = Fore.YELLOW
COR_NOME_SALA = Fore.CYAN
COR_TITULO = Fore.MAGENTA
COR_TEXTO = Fore.WHITE
COR_ACAO = Fore.LIGHTWHITE_EX
COR_ICONE = Fore.YELLOW

# Ícones (Unicode)
ICONE_JOGADOR = "👤"
ICONE_NIVEL = "🌟"
ICONE_HP = "❤️"
ICONE_XP = "⭐"
ICONE_ATAQUE = "⚔️"
ICONE_DEFESA = "🛡️"
ICONE_MAPA = "🗺️"
ICONE_ACOES = "🧭"
ICONE_INVENTARIO = "🎒"
ICONE_USAR_ITEM = "🧪"
ICONE_EQUIPAR_ITEM = "🧥"
ICONE_SAIR = "🚪"

def criar_barra_de_status(valor_atual, valor_max, tamanho=25, cor=Fore.GREEN):
    """Cria uma barra de status visual com base nos valores."""
    if valor_max == 0:
        percentual = 0
    else:
        percentual = valor_atual / valor_max
    
    cheio = int(tamanho * percentual)
    vazio = tamanho - cheio
    
    barra = f"[{cor}{'█' * cheio}{Style.RESET_ALL}{' ' * vazio}]"
    return f"{barra} {valor_atual}/{valor_max}"

def desenhar_tela_evento(titulo, mensagem):
    """Desenha uma tela de evento genérica para mensagens como Level Up ou Game Over."""
    os.system('cls' if os.name == 'nt' else 'clear')
    largura = 81

    print("╔" + "═" * (largura - 2) + "╗")
    print(f"║ {COR_TITULO}{titulo.upper()}{Style.RESET_ALL}" + " " * (largura - 4 - len(titulo)) + "║")
    print("╠" + "═" * (largura - 2) + "╣")
    print("║" + " " * (largura - 2) + "║")

    # Centraliza a mensagem
    for linha in mensagem.split('\n'):
        print("║" + linha.center(largura - 2) + "║")

    print("║" + " " * (largura - 2) + "║")
    print("╚" + "═" * (largura - 2) + "╝")
    input("\nPressione Enter para continuar...")


def desenhar_tela_combate(jogador, inimigo, log_combate):
    """Desenha a interface de combate, mostrando jogador e inimigo lado a lado."""
    os.system('cls' if os.name == 'nt' else 'clear')
    largura = 81

    print("╔" + "═" * (largura - 2) + "╗")
    print(f"║ {COR_TITULO}🐲 COMBATE!{Style.RESET_ALL}" + " " * (largura - 14) + "║")
    print("╠" + "═" * (largura - 2) + "╣")

    # Nomes
    nome_jogador = f"{ICONE_JOGADOR} {jogador['nome']}"
    nome_inimigo = f"👹 {inimigo['nome']}"
    print(f"║ {nome_jogador.ljust(38)} VS. {nome_inimigo.ljust(37)} ║")

    # Barras de HP
    barra_hp_jogador = criar_barra_de_status(jogador['hp'], jogador['hp_max'], tamanho=25, cor=COR_HP)
    barra_hp_inimigo = criar_barra_de_status(inimigo['hp'], inimigo.get('hp_max', inimigo['hp']), tamanho=25, cor=COR_HP)
    print(f"║ {ICONE_HP} {barra_hp_jogador.ljust(35)} | {ICONE_HP} {barra_hp_inimigo.ljust(35)} ║")

    # Atributos
    stats_jogador = f"{ICONE_ATAQUE} Atq: {jogador['ataque']} | {ICONE_DEFESA} Def: {jogador['defesa']}"
    stats_inimigo = f"{ICONE_ATAQUE} Atq: {inimigo['ataque']} | {ICONE_DEFESA} Def: {inimigo['defesa']}"
    print(f"║ {stats_jogador.ljust(38)} | {stats_inimigo.ljust(38)} ║")
    print("╠" + "═" * (largura - 2) + "╣")

    # Log de Batalha
    print(f"║ 📜 LOG DE BATALHA" + " " * (largura - 20) + "║")
    print("║" + " " * (largura - 2) + "║")
    # Exibe as últimas 4 mensagens do log
    for mensagem in log_combate[-4:]:
        print("║   " + mensagem.ljust(largura - 6) + "║")
    # Preenche com linhas vazias se o log for menor
    for _ in range(4 - len(log_combate)):
        print("║" + " " * (largura - 2) + "║")
    print("╠" + "═" * (largura - 2) + "╣")

    # Ações (Apenas o título, as opções serão mostradas em combate.py)
    print(f"║ {COR_ICONE}{ICONE_ACOES}{Style.RESET_ALL} Ações de Combate" + " " * (largura - 22) + "║")
    print("╚" + "═" * (largura - 2) + "╝")


def desenhar_tela_inventario(jogador):
    """Desenha a interface do inventário do jogador."""
    os.system('cls' if os.name == 'nt' else 'clear')
    largura = 81

    print("╔" + "═" * (largura - 2) + "╗")
    print(f"║ {COR_ICONE}{ICONE_INVENTARIO}{Style.RESET_ALL} {COR_TITULO}INVENTÁRIO{Style.RESET_ALL}" + " " * (largura - 16) + "║")
    print("╠" + "═" * (largura - 2) + "╣")

    # Status do Jogador (resumido)
    nome_classe = f"{jogador['nome']}, o {jogador['classe']}"
    nivel_str = f"{ICONE_NIVEL} Nível: {jogador['nivel']}"
    print(f"║ {COR_ICONE}{ICONE_JOGADOR}{Style.RESET_ALL} {nome_classe.ljust(35)} {COR_ICONE}{nivel_str.ljust(30)}{Style.RESET_ALL} ║")
    print("╠" + "═" * (largura - 2) + "╣")

    # Equipamento
    print(f"║ {COR_ICONE}🧥{Style.RESET_ALL} Equipamento Atual" + " " * (largura - 22) + "║")
    arma = jogador['equipamento']['arma']
    escudo = jogador['equipamento']['escudo']
    arma_str = f"   {ICONE_ATAQUE} Arma: {arma['nome'] if arma else 'Nenhuma'}"
    escudo_str = f"   {ICONE_DEFESA} Escudo: {escudo['nome'] if escudo else 'Nenhum'}"
    print("║" + arma_str.ljust(largura - 2) + "║")
    print("║" + escudo_str.ljust(largura - 2) + "║")
    print("╠" + "═" * (largura - 2) + "╣")

    # Itens no Inventário
    print(f"║ {COR_ICONE}🎒{Style.RESET_ALL} Itens na Mochila" + " " * (largura - 21) + "║")
    if not jogador['inventario']:
        print("║   Sua mochila está vazia." + " " * (largura - 28) + "║")
    else:
        for i, item in enumerate(jogador['inventario'], 1):
            item_str = f"   {i}. {item['nome']} ({item['descricao']})"
            print("║" + item_str.ljust(largura - 2) + "║")
    
    print("╚" + "═" * (largura - 2) + "╝")
    input("\nPressione Enter para voltar...")


def desenhar_hud_exploracao(jogador, sala_atual, opcoes):
    """Desenha a interface principal de exploração do jogo."""
    os.system('cls' if os.name == 'nt' else 'clear')

    # Largura total da UI
    largura = 81

    # Cabeçalho
    print("╔" + "═" * (largura - 2) + "╗")
    print(f"║ {COR_TITULO}🐲 AVENTURA NO TERMINAL{Style.RESET_ALL}" + " " * (largura - 28) + "║")
    print("╠" + "═" * 25 + "╦" + "═" * (largura - 28) + "╣")

    # Status do Jogador
    nome_classe = f"{jogador['nome']}, o {jogador['classe']}"
    nivel_str = f"{ICONE_NIVEL} Nível: {jogador['nivel']}"
    print(f"║ {COR_ICONE}{ICONE_JOGADOR}{Style.RESET_ALL} {nome_classe.ljust(20)} ║ {COR_ICONE}{nivel_str.ljust(20)}{Style.RESET_ALL}" + " " * (largura - 53) + "║")
    print("╠" + "═" * (largura - 2) + "╣")

    # Barras de HP e XP
    barra_hp = criar_barra_de_status(jogador['hp'], jogador['hp_max'], tamanho=30, cor=COR_HP)
    barra_xp = criar_barra_de_status(jogador['xp_atual'], jogador['xp_para_proximo_nivel'], tamanho=30, cor=COR_XP)
    print(f"║ {COR_ICONE}{ICONE_HP}{Style.RESET_ALL}  HP: {barra_hp}" + " " * (largura - 46) + "║")
    print(f"║ {COR_ICONE}{ICONE_XP}{Style.RESET_ALL}  XP: {barra_xp}" + " " * (largura - 46) + "║")

    # Atributos
    ataque_str = f"{ICONE_ATAQUE}  Ataque: {jogador['ataque']}"
    defesa_str = f"{ICONE_DEFESA}  Defesa: {jogador['defesa']}"
    print(f"║ {COR_ICONE}{ataque_str.ljust(15)}{Style.RESET_ALL} | {COR_ICONE}{defesa_str.ljust(15)}{Style.RESET_ALL}" + " " * (largura - 41) + "║")
    print("╠" + "═" * (largura - 2) + "╣")

    # Descrição da Sala
    print(f"║ {COR_ICONE}{ICONE_MAPA}{Style.RESET_ALL}  Local: {COR_NOME_SALA}{sala_atual['nome'].upper()}{Style.RESET_ALL}" + " " * (largura - 16 - len(sala_atual['nome'])) + "║")
    print("║" + " " * (largura - 2) + "║")
    # Quebra de linha automática para descrição
    palavras = sala_atual['descricao'].split()
    linha_atual = "   "
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 < largura - 4:
            linha_atual += palavra + " "
        else:
            print("║" + linha_atual.ljust(largura - 2) + "║")
            linha_atual = "   " + palavra + " "
    print("║" + linha_atual.ljust(largura - 2) + "║")
    print("║" + " " * (largura - 2) + "║")
    print("╠" + "═" * (largura - 2) + "╣")

    # Ações
    print(f"║ {COR_ICONE}{ICONE_ACOES}{Style.RESET_ALL} Ações Disponíveis" + " " * (largura - 23) + "║")
    # Formata as opções em duas colunas
    metade = (len(opcoes) + 1) // 2
    for i in range(metade):
        opcao_esq = f"{i+1}. {opcoes[i]}"
        linha = f"   {COR_ACAO}{opcao_esq.ljust(35)}{Style.RESET_ALL}"
        if i + metade < len(opcoes):
            opcao_dir = f"{i+1+metade}. {opcoes[i+metade]}"
            linha += f"{COR_ACAO}{opcao_dir.ljust(35)}{Style.RESET_ALL}"
        print("║" + linha.ljust(largura - 3) + " ║")

    print("╚" + "═" * (largura - 2) + "╝")
    
    # Prompt de entrada
    return input("> ")
