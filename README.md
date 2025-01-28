# Calendario de Cocina - Aplicación Dash

Aplicación web para gestionar turnos de cocina y recursos compartidos.

## Características

- Calendario interactivo
- Sistema de autenticación de usuarios
- Gestión de turnos de cocina
- Lista de items faltantes
- Sistema de notificaciones

## Instalación Local

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/calendario-cocina.git
cd calendario-cocina
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Preparar archivos de datos:

Crear archivo `data/usuarios.csv`:
```csv
username,password
usuario1,contraseña1
usuario2,contraseña2
```

Crear archivo `data/turnos.csv`:
```csv
fecha,usuario_id
2024-01-01,1
2024-01-02,2
```

5. Ejecutar la aplicación:
```bash
python app.py
```

## Despliegue en Render

1. Crear cuenta en Render.com
2. Conectar con repositorio de GitHub
3. Crear nuevo Web Service
4. Configurar:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:server`
   - Python Version: 3.9
   - Environment Variables:
     - SECRET_KEY: tu_clave_secreta

## Estructura de Archivos

- `app.py`: Aplicación principal Dash
- `requirements.txt`: Dependencias del proyecto
- `data/`: Directorio para archivos CSV
- `assets/`: Archivos estáticos (CSS, JS)

## Uso

1. Acceder a la aplicación con las credenciales de usuario
2. El calendario muestra los turnos de cocina
3. Se pueden agregar items faltantes en el panel lateral
4. Las notificaciones aparecen en el icono de campana

## Desarrollo

Para contribuir al proyecto:

1. Crear un fork del repositorio
2. Crear una rama para tu feature:
```bash
git checkout -b feature/nueva-caracteristica
```
3. Hacer commit de los cambios:
```bash
git commit -am 'Agregar nueva caracteristica'
```
4. Hacer push a la rama:
```bash
git push origin feature/nueva-caracteristica
```
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.