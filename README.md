# FastAPI Course lab

Repo to keep Python code, Dockerfile(s), K8s manifests and etc. stuff piled up while going through this awesome FastAPI course.

Github: [FastAPI Course](https://github.com/Sanjeev-Thiyagarajan/fastapi-course)

Youtube: [link](https://youtu.be/0sOvCWFmrtA?si=Fwv3B3p8FH3KikS7)

## Docker image for FastAPI application

Dockerfile is a bit modified compared to the original:

- using Alpine for base image instead of default Debian
- using multi stage build to reduce image size
- using non-root user to run application
- using virtual environment imported from the build stage
- added startup arguments to set host,port and root path for running behind reverse proxy (nginx)

As image has Alembic installed and all required PostgreSQL libraries, it is also used for runnign migrations job.

Also, there was some minor code refactoring in order for it to work with Alpine image, Python 3.12. and updated libraries.

Image referenced in helm charts `fastapi-course:alpine` was built localy with:
```
docker build  -t fastapi-course:alpine .
```

# Requirements:

Local OS: Ubuntu 22.04 

Rancher Desktop: 1.17.0 running Docker and Kubernetes 1.31

Helm : v3.16.4

# Helm chart

## Local directories

pgadmin, postgres and migrations volumes need to be persistent, 
so you need to create three directories and set path for them in values file, e.g.:

```
pgadmin:
...
  persistentVolume:
      name: pgadmin-pv-volume
      ....
      hostPath:
        basePath: "/home/some_user/local_k8s/pgadmin"
```

TBD: Make storage part more agnostic (.e.g. cloud friendly)

### How to use

- create namespace

```
kubectl create ns test
```
- pull keycloak chart from external repo

From `helm_chart` directory run:
```
helm dependency build 
```
- set `enable: false` for migrations and keycloak, until PostgreSQL database is up

- dry run to check for errors

From `helm_chart` directory run:
```
helm  upgrade --install  app-test .  -f values-rancher-desktop.yaml   --dry-run   --debug --namespace test
```
- install (debug optional) ,if there are no errors

From `helm_chart` directory run:
```
helm  upgrade --install  app-test .  -f values-rancher-desktop.yaml --debug --namespace test
```
- verify postgres and pgadmin are up
- (optinally) open pgdadmin in browser and connect to postgres
- set `enable: true` for migrations, and repeat deployment

```
helm  upgrade --install  app-test .  -f values-rancher-desktop.yaml --debug --namespace test
```
Job `fastapi-migrations` should be created and run the job pod that will perform migrations.

- check if fastapi database and required tables are created (migrations job should complete without errors)

- endpoints for fastapi applications should be available at: `http://nginx.localhost.com/fastapi`

- you should be able to see Swagger/OpenAPI specification at:  `http://nginx.localhost.com/fastapi/docs`

## Migrations

Migrations are automated with [migrations.sh](helm_chart/charts/fastapi/files/migrations.sh) script that is using Alembic commands presented in the course.

Additional modification is added to check if `fastapi` database exists and to create it if not.

As information about migration needs to be persistent, data is kept on a volume (mapped to local directory for local k8s deployment)
and on each run, alembic will perform `alembic check` to detect if any changes are required.
If there are some changes, new revision will be auto-generated and applied.

**NOTE:**  Changes to the database schema outside alembic can produce undesirable effects.

## Keycloak

**NOTE:** Keycloak is not used yet anywhere in the code. so you do not need to enable it. 
I plan to implement it as an IAM solution refactoring current code.

Keycloak resources are set to CPU: 512m and memory:512M, as these are minimum settings that worked with local k8s deployment.

Prior to enabling Keycloak in the Helm chart, it is needed to manually create empty 'keycloak' database in PostgreSQL 
(TBD: maybe automate this?). Simplest way to do it is from PGAdmin web interface.

## Ingress

In values file ingress is enabled for the following hosts:
- nginx.localhost.com
- pgadmin.localhost.com
- keycloak.localhost.com

In order for resolving to work, it is required to create hostname entries in your /etc/hosts:
```
127.0.0.1 pgadmin.localhost.com.
127.0.0.1 nginx.localhost.com.
127.0.0.1 keycloak.localhost.com.
```
Local ingress on Rancher Desktop is configured using annotation:

```
  ingress:
     enabled: true
     annotations:
        traefik.ingress.kubernetes.io/router.entrypoints: web
```
If you don't want to use ingress, simply set `enabled: false`




