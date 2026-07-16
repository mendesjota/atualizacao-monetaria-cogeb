"""
Automação SIGRH — download da Ficha Financeira Individual em Excel via Playwright.
Fallback: baixa PDF se EXCEL falhar.
"""
from __future__ import annotations

import re
import time
from pathlib import Path

from playwright.sync_api import Error as PwError, sync_playwright

RAIZ = Path(__file__).resolve().parent.parent
PADRAO_DESTINO = RAIZ / "fichas financeiras"


def run(
    matricula_login: str,
    senha_login: str,
    matricula_empregado: str,
    competencia_inicial: str,
    competencia_final: str,
    codigo_empresa: str = "990",
    pasta_destino: str | Path = None,
    headless: bool = True,
) -> tuple[str | None, str | None]:
    if pasta_destino is None:
        pasta_destino = PADRAO_DESTINO
    pasta_destino = Path(pasta_destino)
    pasta_destino.mkdir(parents=True, exist_ok=True)

    error_message: str | None = None
    browser = context = page = None

    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=headless)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            # ── 1. Login ──
            print("[SIGRH] Acessando página de login...")
            page.goto("https://www.sigrh.df.gov.br/login/Log.aspx", timeout=120000)
            page.locator("#TxtCd_Empresa").fill(codigo_empresa)
            page.locator("#TxtNu_Matricula").fill(matricula_login)
            page.locator("#TxtTe_Senha").fill(senha_login)
            page.get_by_role("button", name="Submit").click()
            page.wait_for_url("**/principalSigrh.aspx**", timeout=120000)
            page.wait_for_load_state("networkidle")
            print("[SIGRH] Login OK.")

            # ── 2. Cookies para subdomínio MVC ──
            cookies_mvc = []
            for c in context.cookies():
                if c["domain"] == "www.sigrh.df.gov.br" and c["name"] in ("PaginadeLogin", "UqZBpD3n"):
                    mvc = dict(c)
                    mvc["domain"] = "www.sigrhmvc.df.gov.br"
                    cookies_mvc.append(mvc)
            if cookies_mvc:
                context.add_cookies(cookies_mvc)

            # ── 3. Navegar até Ficha Financeira ──
            cabecalho = page.frame_locator("frame[name='cabecalho']")
            cabecalho.locator("#PAG").click()

            menu = page.frame_locator("#menu")
            menu.get_by_text("Relatórios de Pagamento (RPG)").click()
            menu.locator("div").filter(has_text=re.compile(r"^Ficha Financeira Individual$")).click()

            page.wait_for_selector("frame[name='corpoprincipal']", timeout=30000)
            corpo = page.frame_locator("#corpoprincipal")
            print("[SIGRH] Página da Ficha Financeira carregada.")

            # ── 4. Pesquisar matrícula ──
            corpo.locator("#Matricula").fill(matricula_empregado)
            corpo.get_by_role("button", name="Pesquisar").click()
            print(f"[SIGRH] Matrícula {matricula_empregado} pesquisada.")

            # ── 5. Selecionar todos e Enviar ──
            corpo.locator("#chkSelecaoCabecalho").wait_for(state="visible", timeout=30000)
            corpo.locator("#chkSelecaoCabecalho").check()
            corpo.get_by_role("button", name="Enviar").click()
            print("[SIGRH] Checkbox marcado e Enviar clicado.")

            # ── 6. Aguardar campos do relatório ──
            corpo.locator("#CompetenciaInicial").wait_for(state="visible", timeout=60000)
            corpo.locator("#CompetenciaFinal").wait_for(state="visible", timeout=60000)
            print("[SIGRH] Campos de competência carregados.")

            # ── 7. Selecionar competência ──
            corpo.locator("#CompetenciaInicial").select_option(competencia_inicial)
            corpo.locator("#CompetenciaFinal").select_option(competencia_final)
            print(f"[SIGRH] Competência {competencia_inicial} a {competencia_final}.")

            # ── 8. Tentativa 1: EXCEL com expect_download ──
            try:
                with context.expect_event("download", timeout=360000) as di:
                    with page.expect_popup(timeout=60000) as pi:
                        corpo.get_by_role("button", name="EXCEL").click()
                    popup = pi.value
                    print("[SIGRH] Popup EXCEL aberta, aguardando...")
                    popup.wait_for_selector("#fimdoprocesso", state="visible", timeout=300000)
                    print("[SIGRH] Processo finalizado, capturando download...")

                download = di.value
                nome = download.suggested_filename or f"ficha_{matricula_empregado}_{int(time.time())}.xls"
                file_path = str(pasta_destino / nome)
                download.save_as(file_path)
                tam = Path(file_path).stat().st_size
                if tam > 500:
                    print(f"[SIGRH] EXCEL salvo: {file_path} ({tam} bytes)")
                    if not popup.is_closed():
                        popup.close()
                    return file_path, None
            except PwError:
                print("[SIGRH] EXCEL falhou, tentando PDF...")

            # ── 9. Tentativa 2: PDF (funciona sempre) ──
            try:
                popup.close()
            except Exception:
                pass

            with context.expect_page(timeout=60000) as page_info:
                corpo.locator("#btnPDF").click()
            nova_pagina = page_info.value
            print("[SIGRH] Popup PDF aberta, aguardando download...")

            with nova_pagina.expect_download(timeout=360000) as di:
                pass
            download = di.value
            nome = download.suggested_filename or f"ficha_{matricula_empregado}_{int(time.time())}.pdf"
            file_path = str(pasta_destino / nome)
            download.save_as(file_path)
            print(f"[SIGRH] PDF salvo: {file_path}")

            if not nova_pagina.is_closed():
                nova_pagina.close()
            return file_path, None

    except PwError as e:
        error_message = f"Erro do Playwright: {e}"
        print(f"[SIGRH ERRO] {error_message}")
        return None, error_message
    except Exception as e:
        error_message = f"Erro inesperado: {e}"
        print(f"[SIGRH ERRO] {error_message}")
        return None, error_message
    finally:
        if page and not page.is_closed():
            try:
                page.close()
            except Exception:
                pass
        if context:
            try:
                context.close()
            except Exception:
                pass
        if browser:
            try:
                browser.close()
                print("[SIGRH] Navegador fechado.")
            except Exception:
                pass


if __name__ == "__main__":
    print("=== Ficha Financeira SIGRH ===\n")
    ml = input("Matrícula de Login: ")
    sl = input("Senha de Login: ")
    me = input("Matrícula do Empregado: ")
    ce = input("Código da Empresa (990/992/037/556/652) [990]: ") or "990"
    ci = input("Competência Inicial (ex: 2023): ")
    cf = input("Competência Final (ex: 2026): ")

    if not all([ml, sl, me, ci, cf]):
        print("Operação cancelada — todos os campos são obrigatórios.")
    else:
        caminho, erro = run(ml, sl, me, ci, cf, codigo_empresa=ce, headless=False)
        if caminho:
            print(f"\nOK — Arquivo salvo em: {caminho}")
        else:
            print(f"\nFalha: {erro}")
