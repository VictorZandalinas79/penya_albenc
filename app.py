import dash
from dash import dcc, html, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import pandas as pd
from datetime import datetime
import json
from flask import Flask

# Inicializar la aplicación Flask
server = Flask(__name__)
server.config.update(SECRET_KEY='tu_clave_secreta_aqui')

# Inicializar la aplicación Dash
app = dash.Dash(
    __name__, 
    server=server, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# Clase de Usuario
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return User(username)

def load_data():
    try:
        users_df = pd.read_csv('data/usuarios.csv')
        events_df = pd.read_csv('data/eventos.csv')
        maintenance_df = pd.read_csv('data/mantenimiento.csv')
        inventory_df = pd.read_csv('data/inventario.csv')
        return users_df, events_df, maintenance_df, inventory_df
    except Exception as e:
        print(f"Error cargando datos: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def create_event_card(event, index):
    return dbc.Card([
        dbc.CardHeader(
            html.H5(f"{event['nombre']} - {event['fecha']}", className="mb-0")
        ),
        dbc.CardBody([
            html.Div([
                html.Strong("Turno actual: "),
                html.Span(event['turno'], className="me-2"),
                dbc.Button(
                    "Cambiar turno",
                    id={'type': 'event-button', 'index': index},
                    color="primary",
                    size="sm"
                )
            ])
        ])
    ], className="mb-3")

def create_inventory_item(item, index):
    return dbc.ListGroupItem([
        html.Div([
            html.Span(item['item']),
            html.Small(
                f" (Añadido: {item['fecha']})",
                className="text-muted ms-2"
            ),
            dbc.Button(
                "×",
                id={'type': 'delete-item', 'index': index},
                color="danger",
                size="sm",
                className="float-end"
            )
        ])
    ])

# Layout de login
login_layout = html.Div([
    dbc.Container([
        html.H1("Penya L'Albenc - Login", className="text-center mt-4"),
        dbc.Row([
            dbc.Col([
                dbc.Input(id="username-input", placeholder="Usuario", type="text", className="mb-2"),
                dbc.Input(id="password-input", placeholder="Contraseña", type="password", className="mb-2"),
                dbc.Button("Iniciar Sesión", id="login-button", color="primary", className="mt-2 w-100"),
                html.Div(id="login-error", className="text-danger mt-2")
            ], width={"size": 6, "offset": 3})
        ])
    ])
])

# Layout principal
def create_main_layout():
    try:
        events_df = pd.read_csv('data/eventos.csv')
        users_df = pd.read_csv('data/usuarios.csv')
        inventory_df = pd.read_csv('data/inventario.csv')
        user_options = [{'label': user, 'value': user} for user in users_df['username']]
    except Exception as e:
        print(f"Error cargando datos: {str(e)}")
        events_df = pd.DataFrame()
        inventory_df = pd.DataFrame()
        user_options = []
    
    layout = html.Div([
        # Navbar
        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Calendario", href="#")),
                dbc.NavItem(dbc.NavLink("Tablón", href="#")),
                dbc.NavItem(dbc.NavLink("Cerrar Sesión", id="logout-button", href="#")),
            ],
            brand="Penya L'Albenc",
            color="primary",
            dark=True,
        ),
        
        # Contenido principal
        dbc.Container([
            dbc.Row([
                # Columna de Eventos
                dbc.Col([
                    html.H2("Calendario de Eventos", className="mt-4"),
                    html.Div([
                        create_event_card(row, idx) 
                        for idx, row in events_df.iterrows()
                    ])
                ], md=6),
                
                # Columna del Tablón
                dbc.Col([
                    html.H2("Tablón de Anuncios", className="mt-4"),
                    dbc.InputGroup([
                        dbc.Input(
                            id="new-item-input",
                            placeholder="Añadir nuevo item...",
                            type="text"
                        ),
                        dbc.Button(
                            "Añadir",
                            id="add-item-button",
                            color="success"
                        )
                    ], className="mb-3"),
                    dbc.ListGroup([
                        create_inventory_item(row, idx)
                        for idx, row in inventory_df.iterrows()
                    ])
                ], md=6)
            ]),
            
            # Modal para cambios de turno
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Cambiar turno")),
                dbc.ModalBody([
                    dbc.Select(
                        id='user-select',
                        options=user_options,
                        placeholder="Selecciona usuario para intercambiar"
                    )
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancelar", id="cancel-button", className="me-2"),
                    dbc.Button("Confirmar", id="confirm-button", color="primary")
                ])
            ], id="change-modal", is_open=False),
            
            # Toast para notificaciones
            dbc.Toast(
                id="notification-toast",
                header="Notificación",
                is_open=False,
                dismissable=True,
                duration=4000,
                style={"position": "fixed", "top": 66, "right": 10, "width": 350},
            )
        ])
    ])
    
    return layout

# Layout principal de la aplicación
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    dcc.Store(id='authentication-status', storage_type='session'),
    dcc.Store(id='app-state', storage_type='memory', data={'inventory': [], 'last_action': None}),
    dcc.Store(id='modal-state', storage_type='memory', data={'open': False, 'selected_event': None}),
    html.Div(id='page-content'),
    dbc.Toast(
        id="notification-toast",
        header="Notificación",
        is_open=False,
        dismissable=True,
        duration=4000,
        style={"position": "fixed", "top": 66, "right": 10, "width": 350},
    )
])

# Callback para actualizar el estado visible del modal
@app.callback(
    Output("change-modal", "is_open"),
    Input("modal-state", "data")
)
def update_modal_state(modal_state):
    if modal_state:
        return modal_state.get('open', False)
    return False

# Callback para actualizar usuario seleccionado en el modal
@app.callback(
    Output("user-select", "value"),
    [Input("change-modal", "is_open")],
    prevent_initial_call=True
)
def reset_dropdown(is_open):
    if not is_open:
        return None
    raise PreventUpdate

# Callback para mostrar la página
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'),
     Input('authentication-status', 'data'),
     Input('app-state', 'data')]
)
def display_page(pathname, auth_status, app_state):
    if pathname == '/logout':
        logout_user()
        return login_layout
    
    if auth_status and auth_status.get('authenticated'):
        return create_main_layout()
        
    return login_layout

# Callback para autenticación
@app.callback(
    [Output('authentication-status', 'data'),
     Output('url', 'pathname')],
    [Input('login-button', 'n_clicks')],
    [State('username-input', 'value'),
     State('password-input', 'value')]
)
def authenticate(n_clicks, username, password):
    if n_clicks is None:
        raise PreventUpdate
    
    if not username or not password:
        return None, '/login'
    
    users_df = pd.read_csv('data/usuarios.csv')
    user = users_df[users_df['username'] == username]
    
    if user.empty or user.iloc[0]['password'] != password:
        return None, '/login'
    
    login_user(User(username))
    return {'authenticated': True, 'username': username}, '/dashboard'

# Callback para el logout
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('logout-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks:
        return '/logout'
    raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)