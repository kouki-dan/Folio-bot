FOLIO bot
=====

## How to use
Please try it with this command.
```
docker run -e USERNAME="<Your mail address>" -e PASSWORD="<Your password>" -e WEBHOOK_URL="<Your slack incoming-webhook URL>" koukidan/folio-bot
```

After login successful, you will see like this image:   
<img width="486" alt="screen shot 2017-10-11 at 1 06 05 am" src="https://user-images.githubusercontent.com/1401711/31397230-6f70784a-ae20-11e7-8a61-5d0284c19c3d.png">

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

