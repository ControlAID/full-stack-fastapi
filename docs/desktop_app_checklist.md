# Checklist: Aplicación de Escritorio Modular (PyQt6)

Este documento detalla el estado actual y los pasos necesarios para construir la aplicación de escritorio solicitada.

## 1. Lo que ya tienes (Backend & Conceptos)

### Backend (FastAPI)
- [x] **Autenticación**: Endpoints para login y obtención de tokens JWT (`/api/v1/login/access-token`).
- [x] **Gestión de Licencias**: Modelos de datos para Licencias y Access Points (según `CLIENTS_ARCHITECTURE.md`).
- [x] **Sistema de Plugins (Backend)**: Estructura `BaseModule` para plugins del lado del servidor.
- [x] **API Client**: Tienes un cliente generado para Frontend Web que puede servir de referencia para el cliente Python.

### Arquitectura
- [x] **Definición de Roles**: "Monitoring Station" definido como el rol de la app de escritorio.
- [x] **Requisitos de Hardware**: Identificada la necesidad de puerto Serial (Talanqueras) y RTSP (Cámaras).

## 2. Lo que nos falta (Desktop Client)

### Estructura del Proyecto
- [ ] **Repositorio/Carpeta**: Crear `frontend-desktop/` (o nombre similar).
- [ ] **Entorno Virtual**: Definir dependencias (`PyQt6`, `requests`/`httpx`, `pydantic`).

### Núcleo de la Aplicación (Core)
- [ ] **Login Window**: Interfaz para ingresar credenciales.
- [ ] **Hardware Binding**: Lógica para obtener el `MachineID` único del PC y registrarlo como "Access Point" en el backend.
- [ ] **Gestor de Sesión**: Guardado seguro del JWT (usando `keyring` o cifrado local).
- [ ] **Main Window**: Contenedor principal (MDI o pestañas) para alojar los módulos.

### Sistema Modular (El reto principal)
- [ ] **API de Módulos (Cliente)**: Definir una clase base `ClientModule` (similar a `BaseModule` del backend) que todos los módulos de UI deben heredar.
    - Métodos: `load_ui()`, `unload()`, `get_menu_action()`.
- [ ] **Module Loader**:
    1.  Consultar al Backend: Endpoint que retorne "¿Qué módulos tiene habilitados mi licencia?".
    2.  **Descarga/Sincronización**:
        -   *Opción A (Simple)*: Los módulos vienen pre-instalados en el ejecutable y se ocultan/muestran según licencia.
        -   *Opción B (Dinámica - Solicitada)*: Mecanismo para descargar paquetes `.zip` o `.py` desde el servidor, descomprimirlos en una carpeta `local_modules/` y cargarlos con `importlib`.
- [ ] **License Watchdog**: Hilo en segundo plano que verifique periódicamente si la licencia sigue activa.

## 3. Cosas a tener en cuenta (Riesgos y Decisiones)

### Seguridad
- **Ejecución de Código Remoto**: Si descargas módulos (`.py`) desde el servidor y los ejecutas, asegúrate de verificar firmas digitales o usar HTTPS estricto para evitar ataques Man-in-the-Middle.
- **Protección del Código**: Python es fácil de descompilar. Si la validación de licencia es puramente local (if `license_ok`: show_module), puede ser crackeada. *Recomendación*: Que el módulo requiera datos del backend para funcionar, de modo que sin licencia válida en el servidor, el módulo sea inútil aunque se cargue visualmente.

### UI/UX
- **Bloqueo de UI**: Las operaciones de red (descarga de módulos, login) deben ir en hilos separados (`QThread`) para no congelar la interfaz PyQt.
- **Estilos**: PyQt se ve "nativo" (a veces antiguo) por defecto. Considerar usar una hoja de estilos (QSS) moderna o librerías como `qt-material`.

### Implementación Técnica
- **Diferencia Backend vs Frontend Modules**: Los módulos del backend (`weather_connector`) son lógica pura. Los del desktop necesitan UI (`QWidget`). ¿El backend servirá también el código UI? ¿O son repositorios separados?
    - *Sugerencia*: Mantener el código UI de los módulos en el repositorio del proyecto, versionado junto con la app base, a menos que la descarga dinámica sea un requisito estricto "sine qua non".

## 4. Plan de Acción Inmediato
1.  Inicializar entorno Python para `frontend-desktop`.
2.  Crear estructura básica interna (`/core`, `/modules`, `/services`).
3.  Implementar Login contra tu backend existente.
4.  Crear "Dummy Module" y probar el sistema de carga dinámica.
