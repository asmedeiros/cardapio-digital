import flet as ft
import json
import os
import urllib.parse

from app.components import product_card, cart_item_row

WHATSAPP_NUMERO = "5511957695751"


def carregar_produtos():
    caminho = os.path.join(os.path.dirname(__file__), "produtos.json")
    with open(caminho, "r", encoding="utf-8") as f:
        return [p for p in json.load(f) if p.get("ativo", True)]


def main(page: ft.Page):
    page.title = "Cardápio Digital"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 20

    produtos = carregar_produtos()
    carrinho = {}

    categorias = [
        ("Lanches", "lanches"),
        ("Pastéis", "pasteis"),
        ("Bebidas", "bebidas"),
        ("Sobremesas", "sobremesas"),
    ]

    grid = ft.ResponsiveRow(spacing=20, run_spacing=20)

    # =========================
    # CARRINHO
    # =========================
    def get_quantidade(pid):
        return carrinho.get(pid, {}).get("quantidade", 0)

    def total_itens():
        return sum(i["quantidade"] for i in carrinho.values())

    def total_valor():
        return sum(i["preco"] * i["quantidade"] for i in carrinho.values())

    # =========================
    # FUNÇÕES DE ATUALIZAÇÃO
    # =========================
    def atualizar_barra():
        resumo_text.value = f"🛒 {total_itens()} itens • R$ {total_valor():.2f}"
        page.update()

    def adicionar(produto):
        pid = produto["id"]
        if pid in carrinho:
            carrinho[pid]["quantidade"] += 1
        else:
            carrinho[pid] = {
                "id": pid,
                "nome": produto["nome"],
                "preco": produto["preco"],
                "quantidade": 1,
            }
        atualizar_barra()
        renderizar_categoria(categoria_atual[0])
        atualizar_sheet()

    def remover(produto):
        pid = produto["id"]
        if pid in carrinho:
            carrinho[pid]["quantidade"] -= 1
            if carrinho[pid]["quantidade"] <= 0:
                del carrinho[pid]
        atualizar_barra()
        renderizar_categoria(categoria_atual[0])
        atualizar_sheet()

    # =========================
    # WHATSAPP (VERSÃO WEB SAFE)
    # =========================
    def gerar_link_whatsapp():
        linhas = ["🛒 *Pedido:*", ""]

        for item in carrinho.values():
            linhas.append(
                f'- {item["quantidade"]}x {item["nome"]} – R$ {item["preco"] * item["quantidade"]:.2f}'
            )

        linhas.append("")
        linhas.append(f"*Total:* R$ {total_valor():.2f}")

        texto = urllib.parse.quote("\n".join(linhas))
        return f"https://wa.me/{WHATSAPP_NUMERO}?text={texto}"

    # =========================
    # BOTTOMSHEET
    # =========================
    sheet_content = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10)

    sheet = ft.BottomSheet(
        content=ft.Container(
            padding=20,
            content=sheet_content,
            height=page.height * 0.5
        ),
        open=False
    )

    page.overlay.append(sheet)

    def atualizar_sheet():
        sheet_content.controls.clear()

        sheet_content.controls.append(
            ft.Text("🧾 Revisar pedido", size=18, weight=ft.FontWeight.BOLD)
        )

        for item in carrinho.values():
            sheet_content.controls.append(
                cart_item_row(item, adicionar, remover, atualizar_sheet)
            )

        sheet_content.controls.append(ft.Divider())

        sheet_content.controls.append(
            ft.Text(f"Total: R$ {total_valor():.2f}", weight=ft.FontWeight.BOLD)
        )

        # 🔥 BOTÃO COM LINK DIRETO (SEM ASYNC)
        sheet_content.controls.append(
            ft.TextButton(
                "Finalizar no WhatsApp",
                url=gerar_link_whatsapp()
            )
        )

        page.update()

    def abrir_revisao(e):
        atualizar_sheet()
        sheet.open = True
        page.update()

    # =========================
    # RENDERIZAÇÃO DE PRODUTOS
    # =========================
    categoria_atual = ["lanches"]

    def renderizar_categoria(cat):
        categoria_atual[0] = cat
        grid.controls.clear()

        for produto in produtos:
            if produto["categoria"] == cat:
                grid.controls.append(
                    ft.Container(
                        col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                        content=product_card(
                            produto, adicionar, remover, get_quantidade
                        ),
                    )
                )

        page.update()

    # =========================
    # UI
    # =========================
    botoes = ft.Row(
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.OutlinedButton(
                texto, on_click=lambda e, c=cat: renderizar_categoria(c)
            )
            for texto, cat in categorias
        ]
    )

    resumo_text = ft.Text(weight=ft.FontWeight.BOLD)

    bottom_bar = ft.BottomAppBar(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                resumo_text,
                ft.TextButton("Revisar pedido", on_click=abrir_revisao)
            ],
        ),
    )

    page.bottom_appbar = bottom_bar

    page.add(
        ft.Text("🍔 Cardápio Digital", size=28, weight=ft.FontWeight.BOLD),
        botoes,
        ft.Divider(),
        grid,
        ft.Container(height=60)
    )

    atualizar_barra()
    renderizar_categoria("lanches")


# =========================
# START
# =========================
ft.run(
    main,
    assets_dir="assets"
)
