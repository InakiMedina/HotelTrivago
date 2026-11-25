# HotelTrivago: comandos de validación local y CI

Guía para la rama `feat/CI-CD`. Estos comandos son una propuesta para ejecutar; este documento no acredita que el pipeline ya haya pasado.

## 1. Entrar al repositorio y verificar la rama

```bash
cd HotelTrivago
git status
git switch feat/CI-CD
git pull --ff-only origin feat/CI-CD
```

Si hay cambios locales, revísalos antes de cambiar de rama o actualizarla.

## 2. Preparar las variables locales

Ejecutar solo si todavía no existe `.env`, para no sobrescribir sus valores:

```bash
# Bash / Git Bash
cp -n .env.example .env
```

En PowerShell, como alternativa:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Editar `.env` y configurar una contraseña local. No subir ese archivo al repositorio.

## 3. Revisar las tres correcciones de Compose

En `docker-compose.yml`, verificar:

```yaml
# Dentro de services.mongodb.environment
MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD:?Define MONGO_ROOT_PASSWORD en .env}
```

```yaml
# Comando del healthcheck del backend
- "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=3)"
```

```yaml
# Sección superior, al final del archivo
volumes:
  mongodb_data:
```

Son fragmentos separados: no pegarlos juntos como un archivo Compose completo.

## 4. Validar y arrancar

```bash
docker --version
docker compose version
docker compose config --quiet
docker compose up --build -d --wait --wait-timeout 120
docker compose ps
```

Si algún comando falla, resolver el error antes de continuar.

## 5. Consultar el backend

```bash
curl --fail http://localhost:8000/health
```

En PowerShell puede utilizarse `curl.exe`:

```powershell
curl.exe --fail http://localhost:8000/health
```

Respuesta esperada:

```json
{"status":"ok"}
```

Esto comprueba la respuesta del servidor, no la conexión autenticada del backend con MongoDB.

## 6. Diagnóstico

```bash
docker compose ps --all
docker compose logs --tail=200 backend mongodb
docker compose logs -f backend mongodb
```

`Ctrl+C` termina el seguimiento de logs sin detener los contenedores iniciados con `-d`.

## 7. Detener o reiniciar

```bash
# Detener y retirar contenedores conservando el volumen de datos
docker compose down

# Volver a levantar
docker compose up --build -d --wait --wait-timeout 120
```

### Reinicializar datos locales desechables

ADVERTENCIA: el siguiente comando elimina los volúmenes del proyecto y sus datos. No ejecutarlo si debes conservar información. Cambiar variables de inicialización no actualiza por sí solo las credenciales de una base ya inicializada.

```bash
docker compose down --volumes
docker compose up --build -d --wait --wait-timeout 120
```

## 8. Revisar y subir correcciones

```bash
git status
git diff --check
git diff -- docker-compose.yml .github/workflows/ci.yml .env.example .gitignore
git add docker-compose.yml
git commit -m "fix: correct MongoDB credentials and Compose healthcheck"
git push origin feat/CI-CD
```

El `git add` de este ejemplo solo incluye Compose. Si modificaste otros archivos, revisarlos y agregarlos explícitamente. No crear un commit si no existen cambios pendientes.

## 9. Abrir el pull request y comprobar CI

En GitHub:

1. Abrir un pull request con base `beta` y compare `feat/CI-CD`.
2. Revisar la pestaña Checks.
3. Comprobar que `Docker Compose smoke test` termina correctamente.
4. Si falla, consultar el paso fallido y el diagnóstico antes de corregir y volver a subir cambios.

El workflow revisado escucha pushes a `beta` y `main`, no a `feat/CI-CD`. Un push a la rama de trabajo actualizará el check si ya existe un PR abierto hacia una de esas ramas objetivo.

## 10. Siguientes entregables

- Obtener una ejecución exitosa del smoke test.
- Añadir pruebas Pytest y definir el alcance de cobertura mínima del 80%.
- Añadir el linter del backend y después las validaciones del frontend cuando esté implementado.
- Configurar checks obligatorios y revisión de PR en las ramas compartidas.
- Añadir una prueba de conexión autenticada a MongoDB.
- Diseñar publicación de imágenes y despliegue a AWS en una etapa separada.

## Referencias

- Docker Compose CLI: https://docs.docker.com/reference/cli/docker/compose/
- Volúmenes de Compose: https://docs.docker.com/reference/compose-file/volumes/
- Pruebas Python en GitHub Actions: https://docs.github.com/actions/guides/building-and-testing-python
