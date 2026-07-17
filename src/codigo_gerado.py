import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.sigrh.df.gov.br/login/Log.aspx")
    page.locator("#TxtCd_Empresa").fill("990")
    page.locator("#TxtNu_Matricula").click()
    page.locator("#TxtNu_Matricula").fill("2874946")
    page.locator("#TxtTe_Senha").click()
    page.locator("#TxtTe_Senha").fill("070790")
    page.get_by_role("button", name="Submit").click()
    page.locator("frame[name=\"cabecalho\"]").content_frame.locator("#PAG").click()
    page.locator("#menu").content_frame.get_by_text("Relatórios de Pagamento (RPG)").click()
    page.locator("#menu").content_frame.locator("div").filter(has_text=re.compile(r"^Ficha Financeira Individual$")).click()
    page.locator("#corpoprincipal").content_frame.locator("#Matricula").click()
    page.locator("#corpoprincipal").content_frame.locator("#Matricula").fill("17151538")
    page.locator("#corpoprincipal").content_frame.get_by_role("button", name="Pesquisar").click()
    page.locator("#corpoprincipal").content_frame.locator("#chkSelecaoCabecalho").check()
    page.locator("#corpoprincipal").content_frame.get_by_role("button", name="Enviar").click()
    page.locator("#corpoprincipal").content_frame.locator("#CompetenciaInicial").select_option("2023")
    page.locator("#corpoprincipal").content_frame.locator("#CompetenciaFinal").select_option("2026")
    with page.expect_popup() as page1_info:
        page.locator("#corpoprincipal").content_frame.get_by_role("button", name="EXCEL").click()
    page1 = page1_info.value
    page1.close()
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
