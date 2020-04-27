from crontab import CronTab


cron = CronTab(user=True)
job = cron.new(command='scrapy crawl HAS')
job.day.every(1)

cron.write()
