FOLIO bot
=====

## 2023/8 Archived due to sunsetting of theme investment.

-----

[![Build Status](https://travis-ci.org/kouki-dan/Folio-bot.svg?branch=master)](https://travis-ci.org/kouki-dan/Folio-bot)

## How to use
Please try it with this command.
```
docker run -e USERNAME="<Your mail address>" -e PASSWORD="<Your password>" -e WEBHOOK_URL="<Your slack incoming-webhook URL>" [-e TITLE="今日のFOLIO"] koukidan/folio-bot
```

After login successful, you will see like this image:   
<img width="553" alt="screen shot 2018-03-03 at 11 43 54 pm" src="https://user-images.githubusercontent.com/1401711/45990546-c7e6a900-c0bb-11e8-8f2b-51ff4c9ca39d.png">


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

## Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

1. Use above button to create heroku app
2. Setup schedule when deployed
    - Click `Manage app` button to show overview
    - Click `Heroku Scheduler` add-on to setup schedule
    - Click `Add new job` button
    - Set this command `python folio.py`
    - Set schedule like below screen shot.
    - ![setup image](https://user-images.githubusercontent.com/1401711/42095645-2a18190a-7bee-11e8-9d1e-94919289ea2e.png)
3. Finished!

