# Guía de Integración Móvil (Residentes y Usuarios)

Este documento detalla cómo integrar una aplicación móvil (Flutter o React Native/Expo) con el backend de ControlAI para la autenticación y consumo de servicios por parte de residentes y empleados no administradores.

## 1. Endpoints de Autenticación

El backend utiliza el estándar **OAuth2 con Password Flow**. Los usuarios obtienen un token JWT (access token) intercambiando sus credenciales (email y contraseña).

### Login (Obtener Token)
*   **URL**: `https://api.tu-dominio.com/api/v1/login/access-token`
*   **Método**: `POST`
*   **Content-Type**: `application/x-www-form-urlencoded`

#### Cuerpo de la Petición (Form Data)
| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `username` | String | Sí | El correo electrónico del usuario. |
| `password` | String | Sí | La contraseña del usuario. |

#### Respuesta Exitosa (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Respuesta de Error (400 Bad Request / 401 Unauthorized)
```json
{
  "detail": "Incorrect email or password"
}
```

---

## 2. Implementación en Flutter

### Dependencias Sugeridas
*   `http` o `dio` (para peticiones HTTP)
*   `flutter_secure_storage` (para guardar el token de forma segura)

### Ejemplo de Código (Dart)

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class AuthService {
  final String _baseUrl = 'https://api.tu-dominio.com/api/v1';
  final _storage = const FlutterSecureStorage();

  Future<bool> login(String email, String password) async {
    final url = Uri.parse('$_baseUrl/login/access-token');

    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: {
          'username': email,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token = data['access_token'];

        // Guardar token de forma segura
        await _storage.write(key: 'jwt_token', value: token);
        return true;
      } else {
        print('Error de login: ${response.body}');
        return false;
      }
    } catch (e) {
      print('Error de conexión: $e');
      return false;
    }
  }

  // Ejemplo de petición autenticada
  Future<void> getUserProfile() async {
    final token = await _storage.read(key: 'jwt_token');
    if (token == null) return;

    final url = Uri.parse('$_baseUrl/users/me');
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token',
      },
    );

    print(response.body);
  }
}
```

---

## 3. Implementación en React Native (Expo)

### Dependencias Sugeridas
*   `axios` (o `fetch` nativo)
*   `expo-secure-store` (para guardar el token de forma segura)

### Ejemplo de Código (TypeScript)

```typescript
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_URL = 'https://api.tu-dominio.com/api/v1';

export const login = async (email, password) => {
  try {
    // Nota: axios serializa x-www-form-urlencoded automáticamente si usas URLSearchParams
    // O puedes pasar un string formateado.
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);

    const response = await axios.post(`${API_URL}/login/access-token`, params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const { access_token } = response.data;

    // Guardar token de forma segura
    await SecureStore.setItemAsync('user_token', access_token);
    return true;

  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('Login error:', error.response?.data);
    } else {
      console.error('Unexpected error:', error);
    }
    return false;
  }
};

// Ejemplo de petición autenticada (usando interceptors es mejor práctica)
export const getUserProfile = async () => {
  const token = await SecureStore.getItemAsync('user_token');
  
  if (!token) return null;

  try {
    const response = await axios.get(`${API_URL}/users/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error(error);
    return null;
  }
};
```

## 4. Obtención de Datos del Usuario

Una vez logueado, la app debe llamar inmediatamente a:
*   **URL**: `/api/v1/users/me`
*   **Método**: `GET`
*   **Header**: `Authorization: Bearer <token>`

Esto devolverá la información del usuario, incluyendo su `id`, `email`, `full_name` y `organization_id`. Esta información es crucial para personalizar la interfaz de la app móvil.
