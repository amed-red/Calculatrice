# Application Microservices

Ce dossier contient le code des trois microservices de la calculatrice.

## Construction des images

Exécutez ces commandes depuis la racine du dossier `application` :

```bash
# Backend
docker build -t registry-binome1-binome2/backend:latest ./backend

# Consumer
docker build -t registry-binome1-binome2/consumer:latest ./consumer

# Frontend
docker build -t registry-binome1-binome2/frontend:latest ./frontend
```

## Push vers le registre de conteneurs

```bash
# Exemple pour Scaleway (adapter l'URL selon le résultat de Terraform)
docker tag registry-binome1-binome2/backend:latest rg.fr-par.scw.cloud/registry-binome1-binome2/backend:latest
docker push rg.fr-par.scw.cloud/registry-binome1-binome2/backend:latest
```
