# <div align="center">📄 Round Review - Plugins</div>

<div align="center">
Round Review is a PDF platform to manage documents and reviews with collaborators.
This is a mono-repository that contains **plugins** for the platform working via REST API and WEBHOOKS.
</div>

> [!IMPORTANT]
> REPOSITORY UNDER DEVELOPMENT


### Requirements

- Docker with Docker Compose (v2+)

## Plugins

> [!IMPORTANT]
> Follow these instructions to get the plugin you need up and running properly

### PDF Notary Bot - Plugin

1. Create a folder within the docker compose file and move inside it:
    - `mkdir ./certs && cd ./certs`
1. Generate a new SSL certificate: 
    - `openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout key.pem -out cert.pem`
1. Prepare the environment variables file
    - `cd .. && cp envs/template.rr-pdf-notary-bot.env envs/rr-pdf-notary-bot.env`
1. Edit the environment file according to your needs (see [envs documentation](./docs/envs.md))
1. Start the container: 
    - `docker-compose up roundreview_pdf_notary_bot -d --build`
      - In case of port error (e.g. already in use), change the first port inside the docker-compose file to something else
      - To stop the container, use `docker-compose down roundreview_pdf_notary_bot`

## Docker stack management

1. `docker-compose up -d`: Start all containers in the stack
1. `docker-compose down`: Stop all containers in the stack

> [!TIP]
> Copy `docker-compose.yml` and paste as `docker-compose.custom.yml`. Then customize the stack according to your needs.

1. `docker-compose -f docker-compose.custom.yml up -d`
1. `docker-compose -f docker-compose.custom.yml down`

### Version update (with GIT)

1. `git pull` the last updates from the repo
1. `docker-compose up -d --build`: Start and build all containers; this will automatically update the internal database


## License and Credits

[Apache 2.0 License](./LICENSE)

Developed by [Maxelweb](https://github.com/Maxelweb) for anyone!