# Guía Completa de Desarrollo de Módulos Full-Stack (ControlAI)

Esta guía explica cómo crear un módulo completo que incluye:
1.  **Backend**: Base de datos (Tablas), Migraciones, Lógica y API.
2.  **Frontend Desktop**: Interfaz de usuario que consume dicha API.

---

## 🏗️ 1. Backend: Estructura y Datos

Los módulos backend residen en `backend/app/plugins/local/`.
Cada módulo es un "slice" vertical que contiene sus propios modelos y rutas.

### 1.1 Estructura de Directorios
```text
backend/app/plugins/local/mi_modulo/
├── __init__.py
├── module.py           # Clase principal (hereda de BaseModule)
├── models.py           # Definición de Tablas (SQLModel)
└── api.py              # Rutas (FastAPI)
```

### 1.2 Modelado de Datos (models.py)
Para que los datos pertenezcan a una Organización (Cliente), **SIEMPRE** debes incluir `organization_id`.

```python
import uuid
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

# Modelo de Base de Datos
class MiData(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
    # Vinculación Multi-Tenant (CRÍTICO)
    organization_id: uuid.UUID = Field(foreign_key="organization.id", index=True)
    
    # Datos del módulo
    nombre: str
    valor: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Modelo para API (Request)
class MiDataCreate(SQLModel):
    nombre: str
    valor: float

# Modelo para API (Response)
class MiDataPublic(MiDataCreate):
    id: uuid.UUID
    created_at: datetime
```

### 1.3 Migraciones de Base de Datos (Alembic)
Cuando creas una nueva tabla en un módulo, necesitas generar una migración para que Alembic actualice la base de datos.

1.  **Importar el modelo**: Asegúrate de que tu modelo sea importado en `backend/app/models.py` (o en el `env.py` de alembic si se configura dinámicamente) para que Alembic lo detecte.
    *   *Nota: En la arquitectura actual, lo ideal es importar tus modelos en `backend/app/models.py` temporalmente o configurar Alembic para escanear plugins.*
2.  **Generar Migración**:
    ```bash
    docker compose exec backend alembic revision --autogenerate -m "Add tables for mi_modulo"
    ```
3.  **Aplicar Migración**:
    ```bash
    docker compose exec backend alembic upgrade head
    ```

### 1.4 API y Seguridad (api.py)
Usa `CurrentUser` para filtrar datos automáticamente por organización.

```python
from fastapi import APIRouter, Depends
from app.api.deps import CurrentUser, SessionDep
from sqlmodel import select
from .models import MiData, MiDataCreate, MiDataPublic

router = APIRouter()

@router.post("/", response_model=MiDataPublic)
def create_item(item_in: MiDataCreate, session: SessionDep, current_user: CurrentUser):
    # Crear objeto vinculado a la organización del usuario
    item = MiData.model_validate(item_in, update={"organization_id": current_user.organization_id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.get("/", response_model=list[MiDataPublic])
def list_items(session: SessionDep, current_user: CurrentUser): # Solo ve los de SU organización
    statement = select(MiData).where(MiData.organization_id == current_user.organization_id)
    return session.exec(statement).all()
```

---

## 🖥️ 2. Frontend Desktop: Interfaz de Usuario

El cliente de escritorio carga módulos dinámicamente que consumen la API del backend.

### 2.1 Estructura
```text
frontend-desktop/app/modules/
├── mi_modulo.py    # Lógica de UI
```

### 2.2 Implementación (mi_modulo.py)

```python
from app.modules.base import ClientModule
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
import requests
from app.core.config import settings

class MiModuloUI(ClientModule):
    def get_name(self) -> str:
        return "mi_modulo"
        
    def get_display_name(self) -> str:
        return "Mi Funcionalidad"
    
    def init_ui(self) -> QWidget:
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        
        self.label = QLabel("Datos: Cargando...")
        layout.addWidget(self.label)
        
        btn = QPushButton("Recargar")
        btn.clicked.connect(self.load_data)
        layout.addWidget(btn)
        
        return self.widget

    def on_load(self):
        self.load_data()

    def load_data(self):
        # El contexto (self.context) tiene access_token y API URL si se inyecta correctamente
        # O usas AuthService globalmente
        from app.services.auth import AuthService
        auth = AuthService()
        
        url = f"{settings.API_URL}/modules/mi_modulo/"
        headers = auth.get_headers()
        
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                self.label.setText(f"Items encontrados: {len(data)}")
        except Exception as e:
            self.label.setText(f"Error: {e}")
```

---

## 🔄 Ciclo de Vida Completo

1.  **Instalación**: El sysAdmin instala el módulo backend (`pip install` o copia carpetas) y corre migraciones.
2.  **Licencia**: Se activa el módulo en la licencia de la Organización (Backend: `License.addon_modules`).
3.  **Cliente**: 
    - Al iniciar, la App Desktop consulta `/api/v1/access-points/` y valida licencia.
    - Si la licencia incluye `mi_modulo`, el `ModuleLoader` descarga/activa la UI correspondiente.
4.  **Uso**: El usuario interactúa con la UI -> llama a API Backend -> Guarda en DB aislada por `organization_id`.
