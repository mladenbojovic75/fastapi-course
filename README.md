# FastAPI Course lab

Repo to keep Python code, Dockerfile(s), K8s manifests and etc. stuff piled up while going through this awesome FastAPI course.

Github: [FastAPI Course](https://github.com/Sanjeev-Thiyagarajan/fastapi-course)

Youtube: [link](https://youtu.be/0sOvCWFmrtA?si=Fwv3B3p8FH3KikS7)

## Docker image for FastAPU application

Dockerfile is a bit modified compared to original:

- using Alpine for base image instead of default Debian
- using multi stage build to reduce image size
- using non-root user to run application
- using virtual environment imported from the build stage
- added startup arguments to set host,port and root path for running behind reverse proxy (nginx)

As image has Alembic installed and all required PostgreSQL libraries, it is also used for runnign migrations job.

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

### create namespace
kubectl create ns test

### pull keycloak chart from external repo
helm dependency build 

### set enable: false for migrations and keycloak, until PostgreSQL database is up

### dry run to check for errors
helm  upgrade --install  app-test .  -f values-rancher-desktop.yaml   --dry-run   --debug --namespace test

### install (debug optional)
helm  upgrade --install  app-test .  -f values-rancher-desktop.yaml --debug --namespace test

### verify postgres and pgadmin are up
### (optinally) open pgdadmin in browser and connect to postgres
### set enable: true for migrations, and repeat deployment
helm  upgrade --install  app-test .  -f values-rancher-desktop.yaml --debug --namespace test

### check if fastapi database and required tables are created (migrations job should complete without errors)

## Keycloak

Keycloak resources are set to CPU: 512m and memory:512M, as these are minimum settings it worked on local k8s deployment.
Prior to enabling Keycloak in Helm chart, it is needed to manually create empty 'keycloak' database in PostgreSQL 
(TBD: maybe automate this?). Simplest way to do it is from PGAdmin web interface.

## Ingress

In values file ingress is enabled for the following hosts:
- nginx.localhost.com
- fastapi.localhost.com
- pgadmin.localhost.com
- keycloak.localhost.com

In order for resolving to work, it is required to create hostname entries in your /etc/hosts:
```
127.0.0.1	      pgadmin.localhost.com.
127.0.0.1       nginx.localhost.com.
127.0.0.1       keycloak.localhost.com.
```
Local ingress on Rancher Desktop is configured using annotation:

```
  ingress:
     enabled: true
     annotations:
        traefik.ingress.kubernetes.io/router.entrypoints: web
```
If you don't want to use ingress, simply set `enabled: false`




