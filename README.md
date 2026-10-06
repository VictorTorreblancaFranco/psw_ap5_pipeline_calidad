# AP5 - Pipeline de Calidad

Trabajo individual de Víctor Raúl Torreblanca Franco para integrar el proyecto base con Jenkins, SonarQube, JMeter y Slack.

## Flujo implementado

`Código -> Jenkins -> Build -> SonarQube -> JMeter -> Slack`

El pipeline contiene las etapas obligatorias `Checkout`, `Build`, `Análisis con SonarQube`, `Pruebas con JMeter` y `Notificación`. También incluye una validación controlada para obtener una evidencia segura de la notificación de error.

## Requisitos

- Java 17 o superior.
- Maven 3.9 o superior.
- Docker Desktop.
- Un repositorio GitHub para este proyecto.
- Un canal y una aplicación de Slack para las notificaciones de Jenkins.

## 1. Verificar el proyecto

```bash
mvn clean verify
mvn spring-boot:run
```

En otra terminal:

```bash
curl http://localhost:8085/actuator/health
curl http://localhost:8085/products
curl -X POST http://localhost:8085/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"123456"}'
```

## 2. Iniciar Jenkins y SonarQube

```bash
docker compose up -d --build
docker compose ps
```

- Jenkins: <http://localhost:8080>
- SonarQube: <http://localhost:9000>

Obtén la contraseña inicial de Jenkins:

```bash
docker exec psw-ap5-jenkins \
  cat /var/jenkins_home/secrets/initialAdminPassword
```

La imagen personalizada ya incluye Maven, JMeter y los plugins necesarios.

## 3. Configurar SonarQube

1. Ingresa a SonarQube con `admin` / `admin` y cambia la contraseña.
2. Crea el proyecto `victor-torreblanca-psw-ap5`.
3. Genera un token de análisis.
4. En Jenkins crea una credencial de tipo **Secret text** con ese token.
5. En **Manage Jenkins -> System -> SonarQube servers** agrega:
   - Name: `SonarQube`
   - Server URL: `http://sonarqube:9000`
   - Server authentication token: la credencial creada.

El nombre `SonarQube` debe coincidir exactamente con el usado en el `Jenkinsfile`.

## 4. Configurar Slack

1. Crea el canal `#jenkins-calidad-victor`.
2. Crea una Slack App desde un manifiesto e instálala en tu workspace.
3. Copia el **Bot User OAuth Token** y guárdalo en Jenkins como **Secret text**.
4. Instala e invita el bot al canal.
5. En **Manage Jenkins -> System -> Slack** configura el workspace, la credencial y el canal predeterminado.
6. Activa **Custom slack app bot user** y usa **Test Connection**.

Nunca guardes el token de Slack en este repositorio ni dentro del `Jenkinsfile`.

## 5. Crear el Pipeline

1. En Jenkins selecciona **New Item -> Pipeline**.
2. Nombre sugerido: `PSW-AP5-Pipeline-Calidad`.
3. En **Pipeline** selecciona **Pipeline script from SCM**.
4. SCM: `Git`.
5. Repository URL: URL de tu repositorio GitHub.
6. Branch: `*/main`.
7. Script Path: `Jenkinsfile`.
8. Guarda y ejecuta **Build Now**.

## 6. Prueba de carga

El plan `performance/pipeline-load-test.jmx` ejecuta:

- 50 usuarios concurrentes.
- Ramp-up de 10 segundos.
- 5 iteraciones por usuario.
- `GET /products` y `POST /login`.
- 500 solicitudes totales.

Registra tiempo de respuesta, P95, throughput, porcentaje de errores y cantidad de solicitudes. Los criterios automatizados son:

- Tasa de errores menor o igual a 1 %.
- P95 menor o igual a 2,000 ms.

El reporte HTML queda disponible como **Reporte JMeter** dentro del build de Jenkins.

## 7. Obtener ambas evidencias de Slack

- Ejecución exitosa: deja `SIMULAR_FALLO` desactivado.
- Ejecución fallida: ejecuta **Build with Parameters** y activa `SIMULAR_FALLO`.

El fallo ocurre después de SonarQube y JMeter, por lo que no altera el proyecto ni invalida sus resultados.

## Evidencias solicitadas

1. Proyecto ejecutándose y endpoints respondiendo.
2. Vista del pipeline con todas sus etapas.
3. Panel de SonarQube con bugs, vulnerabilidades, code smells, cobertura y duplicaciones.
4. Tres problemas de calidad, su impacto y propuesta de mejora.
5. Thread Group y peticiones de JMeter.
6. Resultado agregado y reporte HTML de JMeter.
7. Notificación exitosa de Slack.
8. Notificación fallida de Slack.

Las capturas deben proceder de la ejecución individual del estudiante.
