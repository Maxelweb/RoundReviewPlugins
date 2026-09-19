
# PDF Notary Bot - Plugin

The PDF Notary Bot is a Round Review plugin to sign PDF with a custom certificate whenever a document gets approved. This will generated a signed version of the PDF that can be downloaded from the document review page of the application.

![pdf-notary-bot-plugin](docs/images/pdf-notary-bot.jpg)

## First installation (via CLI)

1. Create a folder within the `./envs` folder and move inside it:
    - `mkdir ./envs/certs && cd ./envs/certs`
1. Generate a new SSL certificate: 
    - `openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout key.pem -out cert.pem`
1. Prepare the environment variables file
    - `cd .. && cp envs/template.rr-pdf-notary-bot.env envs/rr-pdf-notary-bot.env`
1. Edit the environment file according to your needs (see below)
1. Start the container:
    - `docker-compose up roundreview_pdf_notary_bot -d --build`
      - In case of port error (e.g. already in use), change the first port inside the docker-compose file to something else
      - To stop the container, use `docker-compose down roundreview_pdf_notary_bot`


## Web routes

- `/webhook`: listen and receive webhook notification upon document update from RoundReview
- `/download/<file>`: URL to download signed documents

## Environment Variables

> [!NOTE]
> Copy the environment file inside `envs/template.rr-pdf-notary-bot.env` and create `envs/rr-pdf-notary-bot.env`

| Variable name | Description | Default | Required to change |
|---|---|---|---|
| `API_KEY` | API key of a RoundReview user (used to authenticate plugin calls to the app) | None | Yes — required for operation; keep it secret |
| `API_BASE_URL` | RoundReview application API endpoint the plugin calls | "http://roundreview_app:8080/api" | Yes — set to your app's reachable API URL (internally via Docker or externally) |
| `PLUGIN_BASE_URL` | Public/base URL where the plugin is served; it is used to create the URL in the reviews. | "http://localhost:8081" | Yes - change this to the reachable base url + port (no forward slash) |
| `PLUGIN_KEY_PASSPHRASE` | Passphrase for the plugin private key (if any) | None | No - if your key certificate is NOT encrypted; keep it secret |
| `PLUGIN_KEY_PATH` | Filesystem path to private key used for signing | /certs/key.pem | No — ensure path matches your container/host path |
| `PLUGIN_CERT_PATH` | Filesystem path to certificate used for signing | /certs/cert.pem | No — ensure path matches your container/host path |
| `PLUGIN_SIGN_IMAGE_PATH` | Optional image used to stamp signed PDFs | None | No — set if you want a visible signature image and change it according to your container/host path (e.g. `/certs/sign.png`) |
| `PLUGIN_SIGNED_PDFS_FOLDER` | Folder where signed PDFs are stored | /signed_pdfs | No — change it according to your container/host path |
| `PLUGIN_IS_BEHIND_PROXY` | Plugin is hosted behind proxy (passing `x-forwarded-*`) | False | No — change it according to your configuration |
| `PLUGIN_BASE_URL_PREFIX` | Plugin base URL prefix for APIs (must start with `/`) | `/` | No — change it according to your configuration (useful if put under a path (e.g. `mywebsite.ltd/notary-bot`)) |
| `DEBUG` | Enable debug logging and development mode for the plugin | None (unset) | No — let empty in production and `1` or `True` in development |