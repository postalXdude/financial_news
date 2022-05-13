# financial_news
Periodical fetching of Yahoo RSS feeds

## Short Summary of Execution Flow
For each symbol in `rss_feeds_symbols`, periodical task is triggered that will obtain the latest RSS feeds that will be saved in `rss_feeds_news`.
Task will be triggered only for enabled symbol.

Executing `./autopilot.sh` will collect all dependencies and set the app on autopilot.
When executed, following containers are up and running:
- financial_news_container
- celery_beat_container
- celery_worker_container
- redis_container
- postgres_container

To remove all traces of app, run `./autopilot --down -v`. To leave db data intact, run it without `-v` argument.

---
#### financial_news.postman_collection.json
Now when everything is prepared, some symbols can be added with periodical tasks:
- Initialize symbols:
  - POST with request body
  - http://127.0.0.1:8000/rss_feeds/symbols
  - ```json
    [
        {
            "name": "AAPL",
            "enabled": true
        },
        {
            "name": "TWTR",
            "enabled": true
        },
        {
            "name": "GOLD",
            "enabled": false
        },
        {
            "name": "INTC",
            "enabled": false
        }
    ]
- Create periodic tasks for enabled symbols:
  - POST with request body and sample response
  - http://127.0.0.1:8000/rss_feeds/sync
  - ```json
    {
        "period": "seconds",
        "every": 5
    }
  - ```json
    {
        "enabled": [
            "AAPL_periodic_sync",
            "TWTR_periodic_sync"
        ],
        "disabled": [
            "GOLD_periodic_sync",
            "INTC_periodic_sync"
        ]
    }

### TODO:
- Some basic auth (jwt)
