FOLIO bot
=====

[![Build Status](https://travis-ci.org/kouki-dan/Folio-bot.svg?branch=master)](https://travis-ci.org/kouki-dan/Folio-bot)

## How to use
Please try it with this command.
```
docker run -e USERNAME="<Your mail address>" -e PASSWORD="<Your password>" -e WEBHOOK_URL="<Your slack incoming-webhook URL>" [-e TITLE="今日のFOLIO"] koukidan/folio-bot
```

After login successful, you will see like this image:
<img width="553" alt="screen shot 2018-03-03 at 11 43 54 pm" src="https://user-images.githubusercontent.com/1401711/36935689-1b5c807a-1f3e-11e8-96f3-eefb6bf3ea1b.png">


## How to develop
1. Copy env file from `env.sample` to `env` and replace them for development info
2. Run this command for development `docker-compose up --build`


## Deploy to kubernetes
This uses alpha version feature of Kubernetes.
To use it on GKE, you must [make alpha feature on](https://cloud.google.com/container-engine/docs/alpha-clusters)

1. Create Secret
```
kubectl create secret generic folio-bot-credentials --from-literal=username=[your username] --from-literal=password=[your password] --from-literal=webhook-url=[your slack incoming-webhook url]
```

2. Create CronJob
```
kubectl create -f folio-cron.yml
```

That's all. You will show your data on slack if configuration succeeded.

test
