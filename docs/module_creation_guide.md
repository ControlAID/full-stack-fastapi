# Guía de Creación de Módulos / Plugins (ControlAI)

Esta guía detalla cómo extender la funcionalidad del sistema mediante la creación de módulos (**también referidos como plugins**) internos (locales) y externos (conectores).

## Arquitectura del Sistema de Módulos

El sistema utiliza tres componentes principales:
1. **BaseModule**: Clase abstracta que define la interfaz obligatoria.
2. **ModuleLoader**: Escanea directorios y carga clases que heredan de `BaseModule`.
3. **ModuleRegistry**: Almacena y gestiona las instancias de los módulos cargados.

---

## Tipos de Módulos

### 1. Módulos Internos (Locales)
- **Ubicación**: `backend/app/plugins/local/`
- **Propósito**: Funcionalidades integradas que requieren acceso directo a la base de datos o lógica interna del sistema.
- **Configuración**: `is_external=False` en los metadatos.

### 2. Módulos Externos (Conectores)
- **Ubicación**: `backend/app/plugins/external/`
- **Propósito**: Integraciones con servicios de terceros (APIs, Webhooks, etc.).
- **Configuración**: `is_external=True` en los metadatos.

---

## Pasos para Crear un Módulo

### 1. Estructura de Directorios
Crea una carpeta para tu módulo dentro de `plugins/local` o `plugins/external`.
```text
my_module/
├── __init__.py
└── module.py
```

### 2. Implementar la Clase del Módulo
Tu clase debe heredar de `BaseModule` e implementar los métodos abstractos:

```python
from app.modules.base import BaseModule, ModuleMetadata

class MyModule(BaseModule):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            name="my_module",
            version="1.0.0",
            description="Descripción de mi módulo",
            author="Tu Nombre",
            license_required=True,
            is_external=False # o True
        )
    
    async def initialize(self) -> bool:
        # Lógica de inicio
        return True
    
    async def shutdown(self) -> bool:
        # Limpieza
        return True
    
    async def health_check(self):
        return {"status": "ok"}
    
    def register_routes(self):
        @self.router.get("/hello")
        async def hello():
            return {"message": "Hello from MyModule"}
```

### 3. Registro Automático
El sistema cargará automáticamente cualquier clase que herede de `BaseModule` dentro de los paquetes configurados en `app/main.py`.

---

## Mejores Prácticas
- **Aislamiento**: Mantén la lógica del módulo dentro de su propia carpeta.
- **Rutas**: Usa `self.router` para definir endpoints. El sistema los montará automáticamente bajo `/api/v1/modules/{module_name}/`.
- **Manejo de Errores**: Asegúrate de que `initialize` retorne `False` si algo falla críticamente.
