# How to install

### Make docker image
```sh
git clone https://github.com/silentesc/DatBot-Backend.git
```
```sh
cd DatBot-Backend
```
```sh
docker build -t datbot-backend .
```

### Docker Compose
```yaml
services:
  datbot-backend:
    image: datbot-backend
    container_name: datbot-backend
    ports:
      - "8001:8001"
      - "9000:9000"
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
    volumes:
      - ./data/database.db:database.db
    restart: unless-stopped
```
