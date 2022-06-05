### TESTS

To run all tests, run the following command:

- python3 manage.py test --debug-mode

### CELERY

To run scheduled payment you will need to run both the Celery worker and Celery beat, which send the scheduled tasks to the worker to be processed.

Make sure you are within the project directory and the run the following to commands in separate terminals
OBS. You must have a RabbitMQ server running on localhost:5672

- docker run -d -p 5672:5672 rabbitmq
- celery -A bankbuddy worker -l INFO
- celery -A bankbuddy beat -l INFO

  -l flag for logging is optional
