# Django ASGI

### Docker deployment

```
docker swarm init
docker build -t ops-api:latest .
docker stack deploy -c docker-compose.yaml ops
docker service scale ops_api=5
```
