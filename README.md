### TESTS

To run all tests, run the following command `python3 manage.py test --debug-mode`

### Scheduled transactions

To facilitate scheduled transactions we have used [django-crontab](https://pypi.org/project/django-crontab/).
When setting up a new Bankbuddy instance, remember to add cronjobs with `python manage.py crontab add`
