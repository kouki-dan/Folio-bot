FOLIO bot
=====

## How to use
Please try it with this command.
```
docker run -e USERNAME="<Your mail address>" -e PASSWORD="<Your password>" -e WEBHOOK_URL="<Your slack incoming-webhook URL>" koukidan/folio-bot
```

## How to develop
1. Copy env file from `env.sample` to `env` and replace them for development info
2. Run this command for development `docker-compose up --build`

