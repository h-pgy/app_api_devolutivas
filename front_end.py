import dash_html_components as html
import dash_bootstrap_components as dbc


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("PDM 2021-2024", href="#")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Nossos Portais", header=True),
                dbc.DropdownMenuItem("Portal SEPEP", href="#"),
                dbc.DropdownMenuItem("Portal Prefeitura", href="#"),
            ],
            nav=True,
            in_navbar=True,
            label="Mais",
        ),
    ],
    brand="SEPEP",
    color="primary",
    dark=True,
)
