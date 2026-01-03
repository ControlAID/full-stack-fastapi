# Arquitectura de Clientes: ControlAI

Este documento define la estrategia técnica para los dos clientes principales del ecosistema ControlAI: la App de Residentes (Móvil) y el Centro de Control de Seguridad (Escritorio).

## 1. Visión General del Ecosistema

| Cliente | Tipo | Usuario | Tecnología Recomendada | Propósito Principal |
| :--- | :--- | :--- | :--- | :--- |
| **App Residentes** | Mobile (iOS/Android) | Residentes, Visitas | **React Native (Expo)** | Generar QR, Notificaciones, Pagos. |
| **Control Center** | Desktop (Win/Mac/Linux) | Guardias, Administradores | **Electron + React** | Monitoreo CCTV 24/7, Control Talanqueras, Biometría. |

---

## 2. Centro de Control (Desktop App)

Para el requerimiento de monitoreo de cámaras y control de talanqueras, una aplicación de escritorio es superior a una web o tablet por rendimiento y acceso a hardware.

### Stack Tecnológico: Electron
Recomendamos usar **Electron** envolviendo la aplicación React existente o un nuevo repositorio React.

### Ventajas para Seguridad:
1.  **Integración de Hardware Nativo (Serial/GPIO)**:
    *   Para controlar **talanqueras** y puertas automáticas, la app necesita comunicarse con placas controladoras (Arduino/PLC) vía USB/Serial.
    *   *Solución Electron*: Librería `serialport` de Node.js.
    *   ```javascript
        // Ejemplo: Abrir talanquera enviando pulso por puerto COM3
        const { SerialPort } = require('serialport');
        const port = new SerialPort({ path: 'COM3', baudRate: 9600 });
        port.write('OPEN_GATE_1');
        ```

2.  **Monitoreo CCTV de Alto Rendimiento**:
    *   Los navegadores web tienen límites para decodificar múltiples streams RTSP de alta calidad simultáneamente.
    *   *Solución Electron*: Puede integrar `ffmpeg` o librerías nativas para decodificar streams H.264/H.265 directamente en la GPU sin sobrecargar el navegador.

3.  **Modo Kiosko y Multi-Ventana**:
    *   Permite tener una ventana dedicada al "Grid de Cámaras" en un monitor secundario y el "Registro de Visitantes" en el principal.
    *   Evita que el guardia cierre la app accidentalmente (Kiosk Mode).

### Arquitectura de Conexión
La Desktop App funciona como un **Access Point** privilegiado:
*   **Auth**: Se loguea con credenciales de admin/seguridad.
*   **Registro**: Se registra en `/api/v1/access-points/` enviando su `HardwareID` único de PC.
*   **Licencia**: Consume una licencia de tipo "Monitoring Station".

---

## 3. App de Residentes (Mobile)

Para los usuarios finales, la prioridad es la portabilidad y notificaciones.

### Stack Tecnológico: React Native (Expo)
Mantiene la misma base de lenguaje (TypeScript/React) que el Desktop y Web, permitiendo compartir lógica de negocio (API Clients, Tipos).

### Funcionalidades Clave
1.  **Autenticación**: Login contra `/api/v1/login/access-token`.
2.  **Acceso Rápido**: Generación de códigos QR temporales para visitas.
3.  **Notificaciones Push**: Avisos de llegada de paquetes o visitas (vía Firebase/Expo Notifications).

### Ejemplo de Integración (Login)
```typescript
// Shared logic: Puede ser la misma función para Desktop y Mobile
export const login = async (email, password) => {
  // ... lógica de axios contra backend ...
  // Mobile usa SecureStore, Desktop usa keytar o safeStorage
};
```

---

## 4. Estrategia de Desarrollo ("Monorepo")

Recomendamos estructurar el proyecto así para maximizar la reutilización de código:

```text
/
├── backend/            (FastAPI - Núcleo Lógico)
├── shared/             (Tipos TypeScript, Lógica de Validación Cliente)
├── frontend-web/       (Admin Panel - React)
├── frontend-desktop/   (Control Center - Electron + React)
└── frontend-mobile/    (Resident App - React Native)
```

**Nota**: Al usar tecnologías basadas en JS/TS en todas las capas, cualquier cambio en el Backend (ej. nuevo campo en `User`) se refleja automáticamente en Desktop y Móvil al regenerar los clientes API.

---

## 5. Deep Dive: ¿Cómo controla Electron el Hardware?

Electron combina la belleza de React con el poder crudo de **Node.js**. Esto es lo que lo hace la mejor opción:

### A. Control de Talanqueras (Barreras) y Puertas
La mayoría de controladoras de acceso (ZKTeco, Hikvision o placas Arduino/Relay) funcionan mediante **Puerto Serial (USB/RS485)** o **Sockets TCP**.

*   **En Web (Navegador)**: Es imposible acceder libremente al puerto USB/Serial por seguridad.
*   **En Electron**: Tienes acceso total al Hardware de la PC.
    *   **Tecnología**: Librería `serialport` de Node.js.
    *   **Flujo**: El guardia hace clic en "Abrir" -> React envía evento al "Main Process" -> Node.js envía el byte `0x01` por el puerto `COM3` -> La talanquera se abre.

### B. Cámaras de Seguridad (CCTV)
Las cámaras profesionales usan protocolo **RTSP**, el cual **NO** es compatible con navegadores web estándar (Chrome/Firefox).

*   **En Web**: Necesitas un servidor intermedio costoso que convierta RTSP a HLS/WebRTC.
*   **En Electron**: Puedes integrar herramientas nativas.
    *   **Opción 1 (FFmpeg)**: Ejecutar una instancia interna de FFmpeg que tome el RTSP y lo entregue a la vista sin servidores extra.
    *   **Opción 2 (VLC)**: Integrar el plugin de VLC o usar `webchimera.js` para renderizar el video crudo directamente en la ventana.

### C. Biometría (SDKs Nativos)
Los lectores de huella suelen venir con **DLLs (Windows)** o **Libs (Linux)** en C++.

*   **En Electron**: Puedes usar `ffi-napi` (Foreign Function Interface). Esto permite que tu código JavaScript "llame" directamente a funciones escritas en C++ dentro de los DLLs del fabricante del lector, integrándolo nativamente.

### Conclusión: ¿Por qué es la mejor opción?
1.  **Reutilización**: Usas React y TypeScript, igual que en tu Web Admin y App Móvil. No necesitas contratar programadores de C# o C++.
2.  **Poder**: A diferencia de una Web App, tienes el mismo acceso al sistema que un programa hecho en C++.
3.  **Modernidad**: Creas interfaces hermosas y animadas (CSS/React) que son muy difíciles de lograr en sistemas de escritorio tradicionales.
