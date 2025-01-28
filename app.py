import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import json
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Inicialización de la app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Necesario para Render

# Configuración de autenticación
server.config.update(
    SECRET_KEY='tu_clave_secreta'
)

# Login manager
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# Clase Usuario
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

# Cargar usuarios desde CSV
def load_users():
    try:
        df = pd.read_csv('data/usuarios.csv')
        return {row['username']: row['password'] for _, row in df.iterrows()}
    except:
        return {'admin': generate_password_hash('admin')}  # Usuario por defecto

USERS_DB = load_users()

@login_manager.user_loader
def load_user(username):
    if username not in USERS_DB:
        return None
    return User(username)

# Layout principal
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='notification-store', data=[]),
    html.Div(id='page-content'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # en milisegundos
        n_intervals=0
    )
])

# Página de login
login_layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Iniciar Sesión", className="text-center mb-4"),
            dbc.Card([
                dbc.CardBody([
                    dbc.Input(id="username", placeholder="Usuario", type="text", className="mb-3"),
                    dbc.Input(id="password", placeholder="Contraseña", type="password", className="mb-3"),
                    dbc.Button("Entrar", id="login-button", color="primary", className="w-100"),
                    html.Div(id="login-error")
                ])
            ])
        ], width=6)
    ], justify="center", className="vh-100 align-items-center")
])

# Página principal
def serve_layout():
    # Cargar datos de turnos
    try:
        turnos_df = pd.read_csv('data/turnos.csv')
        turnos = turnos_df.to_dict('records')
    except:
        turnos = []
    
    return dbc.Container([
        dbc.Navbar([
            dbc.NavbarBrand("Calendario de Cocina"),
            dbc.Nav([
                dbc.NavItem(
                    dbc.Button(
                        html.I(className="fas fa-bell"),
                        id="notification-button",
                        color="link"
                    )
                ),
                dbc.NavItem(
                    dbc.Button("Salir", id="logout-button", color="link")
                )
            ])
        ], color="light", className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dcc.Calendar(
                    id='calendar',
                    className='calendar',
                    month_format='MMMM Y',
                    display_mode='month',
                    day_size=50,
                    first_day_of_week=1,
                    with_full_screen_portal=True
                )
            ], width=8),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Items Faltantes"),
                    dbc.CardBody([
                        dbc.Input(id="new-item", placeholder="Agregar item...", type="text"),
                        dbc.Button("Agregar", id="add-item-button", color="primary", className="mt-2"),
                        html.Div(id="items-list", className="mt-3")
                    ])
                ])
            ], width=4)
        ]),
        
        dbc.Modal([
            dbc.ModalHeader("Notificaciones"),
            dbc.ModalBody(id="notifications-content"),
            dbc.ModalFooter(
                dbc.Button("Cerrar", id="close-notifications", className="ml-auto")
            )
        ], id="notifications-modal"),
        
    ], fluid=True)

# Callbacks
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/login' or not current_user.is_authenticated:
        return login_layout
    return serve_layout()

@app.callback(
    [Output("login-error", "children"), Output("url", "pathname")],
    Input("login-button", "n_clicks"),
    [State("username", "value"), State("password", "value")],
    prevent_initial_call=True
)
def login_callback(n_clicks, username, password):
    if username in USERS_DB and check_password_hash(USERS_DB[username], password):
        login_user(User(username))
        return "", "/"
    return dbc.Alert("Usuario o contraseña incorrectos", color="danger"), "/login"

@app.callback(
    Output("url", "pathname", allow_duplicate=True),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def logout_callback(n_clicks):
    if n_clicks:
        logout_user()
        return "/login"

@app.callback(
    Output("notifications-modal", "is_open"),
    [Input("notification-button", "n_clicks"),
     Input("close-notifications", "n_clicks")],
    [State("notifications-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(debug=True)