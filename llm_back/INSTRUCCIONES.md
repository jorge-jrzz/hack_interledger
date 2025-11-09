# 🔧 Instrucciones para Configurar OPENAI_API_KEY

## ⚠️ Problema Común

Si exportaste la API key pero el servidor no la detecta, es porque:
- La exportaste en una terminal diferente a donde ejecutas el servidor
- O la variable no está persistente entre sesiones

## ✅ Solución: Configurar Permanente

### Paso 1: Agregar a ~/.zshrc (macOS/Linux con zsh)

```bash
# Abre tu archivo de configuración
nano ~/.zshrc

# O usa este comando para agregarlo automáticamente:
echo 'export OPENAI_API_KEY="sk-proj-tu-api-key-completa-aqui"' >> ~/.zshrc

# Recarga la configuración
source ~/.zshrc
```

### Paso 2: Verificar que funciona

```bash
# Verificar que la variable esté configurada
echo $OPENAI_API_KEY

# Probar con el script de verificación
cd /Users/misaelalvarezcamarillo/Desktop/Back/Back_LLM
python check_api_key.py
```

### Paso 3: Iniciar el servidor

```bash
cd /Users/misaelalvarezcamarillo/Desktop/Back/Back_LLM
python main.py
```

## 🔍 Verificación Rápida

Ejecuta este comando para verificar todo:

```bash
cd /Users/misaelalvarezcamarillo/Desktop/Back/Back_LLM
python check_api_key.py
```

Si ves "✅ OPENAI_API_KEY encontrada", entonces está configurada correctamente.

## 🚀 Scripts Útiles

1. **Verificar API key:**
   ```bash
   python check_api_key.py
   ```

2. **Iniciar servidor (con verificación):**
   ```bash
   ./start_server.sh
   ```

3. **Probar el endpoint:**
   ```bash
   python test_with_example.py
   ```

## 📝 Notas Importantes

- ✅ La API key **NUNCA** está hardcodeada en el código
- ✅ Solo se lee de la variable de entorno `OPENAI_API_KEY`
- ✅ Si la agregas a `~/.zshrc`, estará disponible en todas las terminales nuevas
- ⚠️ Si cambias de terminal, recuerda ejecutar `source ~/.zshrc` o cerrar y abrir una nueva terminal

