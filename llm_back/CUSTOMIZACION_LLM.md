# 🎨 Guía de Customización del LLM

Esta guía te explica dónde y cómo modificar el comportamiento del LLM con el JSON recibido de WhatsApp.

## 📍 Lugares donde puedes modificar el comportamiento

### 1. **System Prompt** (`apps/Interledger_LLM/api/agent/system_prompt.md`)

Este archivo define el comportamiento general del LLM. Aquí puedes definir:
- La personalidad del asistente
- Instrucciones de cómo responder
- Reglas de comportamiento
- Estilo de comunicación

**Ejemplo:**
```markdown
Eres un asistente útil y amigable que responde mensajes de WhatsApp.

Instrucciones:
- Responde de manera natural y conversacional
- Sé conciso pero informativo
- Usa el nombre del usuario cuando sea apropiado
- Mantén un tono profesional pero amigable
```

### 2. **Construcción del Mensaje** (`apps/Interledger_LLM/api/main.py` - Línea ~65)

Aquí puedes modificar cómo se construye el mensaje que se envía al LLM antes de procesarlo.

**Opción 1: Solo el mensaje del usuario (actual)**
```python
user_message = message.message
```

**Opción 2: Agregar contexto del usuario**
```python
user_message = f"Usuario: {message.name} (ID: {message.wa_id})\nMensaje: {message.message}"
```

**Opción 3: Formato personalizado**
```python
user_message = f"[WhatsApp] {message.name} dice: {message.message}"
```

**Opción 4: Incluir información completa del JSON**
```python
user_message = f"""
Información del usuario:
- Nombre: {message.name}
- WhatsApp ID: {message.wa_id}
- Mensaje: {message.message}
"""
```

### 3. **Procesamiento del Mensaje** (`apps/Interledger_LLM/api/agent/main.py`)

Aquí puedes modificar cómo se procesa el mensaje antes de enviarlo al LLM.

**Ejemplo: Preprocesar el mensaje**
```python
def process_message(message: str, system_prompt: Optional[str] = None) -> str:
    # Preprocesar el mensaje si es necesario
    message = message.strip()
    
    # Agregar contexto adicional
    enhanced_message = f"Contexto: Este es un mensaje de WhatsApp.\n{message}"
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": enhanced_message})
    
    # ... resto del código
```

## 🎯 Ejemplos de Customización

### Ejemplo 1: Asistente de Soporte Técnico

**system_prompt.md:**
```markdown
Eres un asistente de soporte técnico especializado en ayudar a usuarios con problemas técnicos.

Instrucciones:
- Responde de manera profesional y empática
- Haz preguntas claras para entender el problema
- Proporciona soluciones paso a paso
- Si no sabes la respuesta, sé honesto y ofrece buscar más información
```

**main.py (construcción del mensaje):**
```python
user_message = f"[Soporte] Usuario {message.name} ({message.wa_id}): {message.message}"
```

### Ejemplo 2: Bot de Ventas

**system_prompt.md:**
```markdown
Eres un asistente de ventas amigable y persuasivo.

Instrucciones:
- Sé entusiasta pero no agresivo
- Destaca los beneficios de los productos
- Responde preguntas sobre precios y características
- Guía al cliente hacia una decisión de compra
```

**main.py:**
```python
user_message = f"Cliente {message.name} pregunta: {message.message}"
```

### Ejemplo 3: Bot Personalizado con Memoria de Contexto

**main.py:**
```python
# Aquí podrías agregar lógica para mantener contexto de conversaciones
# Por ejemplo, usando una base de datos o caché

user_message = f"""
Usuario: {message.name}
ID: {message.wa_id}
Mensaje anterior: [Aquí iría el último mensaje del usuario]
Mensaje actual: {message.message}
"""
```

## 🔧 Modificaciones Avanzadas

### Agregar Validación de Mensajes

```python
# En main.py, antes de procesar
if not message.message or len(message.message.strip()) == 0:
    raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

if len(message.message) > 1000:
    raise HTTPException(status_code=400, detail="El mensaje es demasiado largo")
```

### Filtrar o Transformar Mensajes

```python
# Convertir a minúsculas, eliminar espacios extra, etc.
user_message = message.message.strip().lower()

# O mantener el formato original
user_message = message.message
```

### Agregar Información Adicional al System Prompt Dinámicamente

```python
# Cargar system prompt base
system_prompt = "..."
# Agregar información del usuario
system_prompt += f"\n\nUsuario actual: {message.name} (ID: {message.wa_id})"
```

## 📝 Resumen de Archivos a Modificar

1. **`apps/Interledger_LLM/api/agent/system_prompt.md`**
   - Define la personalidad y comportamiento del LLM

2. **`apps/Interledger_LLM/api/main.py`** (Línea ~65)
   - Modifica cómo se construye el mensaje del usuario
   - Agrega contexto adicional si es necesario

3. **`apps/Interledger_LLM/api/agent/main.py`** (Opcional)
   - Modifica el procesamiento del mensaje antes de enviarlo al LLM
   - Cambia el modelo de OpenAI si es necesario
   - Agrega lógica de preprocesamiento

## 🚀 Próximos Pasos

1. Modifica `system_prompt.md` según tus necesidades
2. Ajusta la construcción del mensaje en `main.py`
3. Prueba con `python test_with_example.py`
4. Ajusta según los resultados

