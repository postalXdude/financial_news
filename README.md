# financial_news
Periodical fetching of Yahoo RSS feeds

## Execution Flow
Stored symbols in `rss_feeds_symbols` are loaded on startup. 
For each symbol periodical task is triggered that will obtain the latest RSS feeds that will be saved in `rss_feeds_news`.

Executing `docker-compose` below will collect all dependencies and set the app on autopilot.
```bash
docker-compose -f docker/docker_compose.yml --env-file docker/default_config.env up -d
```

### Note: Had tremendous issues with pip resolver and celery version in general... lost most time on this.
Currently, for quick inspection, see `rss_feeds/tasks.py` ... 

### TODO
- Clean the repo
- Add unit tests
- Maybe add 1-2 paths
- Some basic auth
