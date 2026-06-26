# ============================================================
# CÉLULA 1: IMPORTS E CONFIGURAÇÃO
# ============================================================
from models.captura_tela import CapturaTela
from models.automacao_cliques import AutomacaoOCR
import pyautogui
import time


def executar_atualizacao_ncm():
    """
    Navega no i-Broker Import e executa a atualização da tabela NCM.
    """

    print("AUTOMAÇÃO ATUALIZAÇÃO NCM")
    print("="*60)

    # ============================================================
    # CÉLULA 2: NAVEGAR ATÉ A TELA DE IMPORT
    # ============================================================
    print("\n ETAPA 1: Navegando → iBROKER Import")
    print("-"*60)

    # 1. Encontra e foca janela Módulos
    captura = CapturaTela()
    if not captura.encontrar_janela('i-Broker Import'):
        print(" Janela i-Broker Import não encontrada!")
        if not captura.encontrar_janela('i-Broker Export'):
            print(" Janela i-Broker Export não encontrada!")

    captura.focar_janela()
    print("✓ Janela i-Broker Import focada")

    # ============================================================
    # CÉLULA PARA CLICAR EM NO MENU 'Tabelas'
    # ============================================================
    auto_ocr = AutomacaoOCR('i-Broker Import')
    # Lista todos os textos que o OCR consegue ver
    #textos = auto_ocr.listar_todos_textos(confianca_minima=30)
    #auto_ocr.criar_mapa_visual('debug_ibroker_ocr.png')

    sucesso = auto_ocr.clicar_em_texto('Tabelas', pausar=2)

    if sucesso:
        print("\n✓ Clique em 'Tabelas' executado com sucesso!")
    else:
        #auto_ocr.listar_todos_textos(
        #confianca_minima=10
        #)
        print("\n OCR não encontrou, tentando coordenadas fixas...")
        # Fallback: usa coordenadas fixas
        x, y = captura.obter_posicao_absoluta(131, 41)
        pyautogui.click(x, y)
        time.sleep(2)
        print("✓ Clique executado com coordenadas fixas")

    # ============================================================
    # CÉLULA PARA CLICAR EM NO SUBMENU 'Produtos'
    # ============================================================
    #textos = auto_ocr.listar_todos_textos(confianca_minima=30)
    #auto_ocr.criar_mapa_visual('debug_tabelas_ocr.png')

    sucesso = auto_ocr.clicar_em_texto('Produtos', pausar=2)

    if sucesso:
        print("\n✓ Clique em 'Produtos' executado com sucesso!")
    else:
        #auto_ocr.listar_todos_textos(
        #confianca_minima=10
        #)
        print("\n OCR não encontrou, tentando coordenadas fixas...")
        # Fallback: usa coordenadas fixas
        x, y = captura.obter_posicao_absoluta(149, 169)
        pyautogui.click(x, y)
        time.sleep(2)
        print(" Clique executado com coordenadas fixas.")

    # ============================================================
    # CÉLULA PARA CLICAR EM NO SUBMENU 'NCM'
    # ============================================================
    #textos = auto_ocr.listar_todos_textos(confianca_minima=30)
    #auto_ocr.criar_mapa_visual('debug_tabelas_ocr.png')

    sucesso = auto_ocr.clicar_em_texto('NCM', pausar=2)

    if sucesso:
        print("\n Clique em 'NCM' executado com sucesso!")
    else:
        #auto_ocr.listar_todos_textos(
        #confianca_minima=10
        #)
        print("\n OCR não encontrou, tentando coordenadas fixas...")
        # Fallback: usa coordenadas fixas
        x, y = captura.obter_posicao_absoluta(289, 251)
        pyautogui.click(x, y)
        time.sleep(2)
        print(" Clique em NCM executado com coordenadas fixas")
        
    # ============================================================
    # CÉLULA PARA CLICAR EM 'Atualizar Tabela'
    # ============================================================
    print("\n ETAPA 4: Clicando em 'Atualizar Tabela'")
    print("-"*60)

    # Definindo a região para o OCR do botão 'Atualizar Tabela'
    # (x_rel, y_rel, largura, altura) - ajustado com base na imagem completa da janela
    # Esta região cobre a barra de botões da janela NCM, relativa à janela principal i-Broker Import.
    regiao_atualizar_tabela = (10, 200, 500, 50) # Coordenadas ajustadas

    # Listar textos na região para depuração (opcional, mas útil)
    print(f" Listando textos na região: {regiao_atualizar_tabela}")
    textos_na_regiao = auto_ocr.listar_texto_regiao(confianca_minima=30, regiao=regiao_atualizar_tabela)

    sucesso = auto_ocr.clicar_em_texto(
        'Tabela',
        pausar=1,
        regiao=regiao_atualizar_tabela, # Passa a região delimitada para o OCR
        confianca_minima=30,
        similaridade_minima=0.8 # Ajuste a similaridade se o OCR tiver dificuldade
    )

    if sucesso:
        print("\n✓ Clique em 'Atualizar Tabela' executado com sucesso!")
    else:
        print("\n  OCR não encontrou 'Atualizar Tabela', tentando coordenadas fixas...")
        # Fallback: usa coordenadas fixas
        x, y = captura.obter_posicao_absoluta(355, 234)
        pyautogui.click(x, y)
        time.sleep(2)
        print("✓ Clique executado com coordenadas fixas")

    # 1. Aguardar o popup 'Informação' aparecer
    popup_apareceu = auto_ocr.aguardar_popup_informacao(timeout=240, intervalo=2) # Aumentei o timeout para 240s

    if not popup_apareceu:
        raise Exception(" O popup 'Informação' não apareceu dentro do tempo esperado. Abortando.")

    #REIGIÃO BOTÃO 'OK'(689, 506)
    regiao_botao_ok = (150, 320, 700, 210) # Coordenadas ajustadas para o botão OK no popup
    #X_GRADE     = 150
    #Y_GRADE     = 320
    #LARGURA     = 700
    #ALTURA      = 210

    # Listar textos na região para depuração (opcional, mas útil)
    print(f" Listando textos na região: {regiao_botao_ok}")
    #textos_na_regiao = auto_ocr.listar_texto_regiao(confianca_minima=30, regiao=regiao_botao_ok)

    sucesso = auto_ocr.clicar_em_texto(
        'OK',
        pausar=1,
        regiao=regiao_botao_ok, # Passa a região delimitada para o OCR
        confianca_minima=30,
        similaridade_minima=0.8 # Ajuste a similaridade se o OCR tiver dificuldade
    )

    if sucesso:
        print("\n✓ Clique em 'OK' executado com sucesso!")
    else:
        print("\n OCR não encontrou 'OK', tentando coordenadas fixas...")
        # Fallback: usa coordenadas fixas
        # (517, 507) coordenada do popup OK em 1024x768
        x, y = captura.obter_posicao_absoluta(517, 507)
        pyautogui.click(x, y)
        time.sleep(2)
        print("✓ Clique executado com coordenadas fixas")
        
    # COORDENADAS BOTÃO SAIR DO SISTEMA - 969, 80 - 1366x768 / (967, 73) - 1024x768
    x, y = captura.obter_posicao_absoluta(967, 73)
    pyautogui.click(x, y)
    print("\n✓ Botão 'Sair do Sistema' clicado, processo finalizado!")
    time.sleep(2)

    # ============================================================
    # CÉLULA: CLICAR EM 'Sim' NO POPUP 'Sair do sistema'
    # ============================================================
    # (493, 396) coordenada do popup Sim, sair do sistema em 1024x768
    sucesso = auto_ocr.clicar_botao_janela_independente(
        titulo_janela='Sair do sistema',
        titulo_botao='Sim',
        timeout=15
    )

    if sucesso:
        print("\n✓ Clique em 'Sim' executado com sucesso!")
    else:
        print("\n Não foi possível clicar em 'Sim'.")    