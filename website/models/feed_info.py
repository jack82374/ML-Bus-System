from django.db import models

class FeedInfo(models.Model):
    feed_publisher_name = models.CharField(max_length=255, primary_key=True)
    feed_publisher_url = models.CharField(max_length=255)
    feed_lang = models.CharField(max_length=10)
    feed_start_date = models.IntegerField()
    feed_end_date = models.IntegerField()
    feed_version = models.CharField(max_length=255)


    def __str__(self):
        return self.feed_publisher_name