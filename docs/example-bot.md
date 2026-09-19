
# Example Bot - Plugin

The example bot plugin is a boilerplate to get started with Round Review integration.

## First installation (via CLI)

1. Start the container:
    - `docker-compose up roundreview_example_bot -d --build`
      - In case of port error (e.g. already in use), change the first port inside the docker-compose file to something else
      - To stop the container, use `docker-compose down roundreview_example_bot`

## Web routes

- `/`: index page with status of the bot
- `/webhook`: listen and receive webhook notification upon document update from RoundReview

## Environment Variables

| Variable name | Description | Default | Required to change |
|---|---|---|---|
| `DEBUG` | Enable debug logging and development mode for the plugin | None (unset) | No — let empty in production and `1` or `True` in development |