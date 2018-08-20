import os, sys, getopt
from celery import Celery
from celery.schedules import crontab
import sqlite3

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_backend.settings')

app = Celery('chat_msg_cleaner')
app.config_from_object('django.conf:settings', namespace='CELERY')
days = 1


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Clean data every 60 * 60 seconds == 1 hour.
    sender.add_periodic_task(3600.0, clean.s(days), name='add every 1 hour')

    # Executes every Monday morning at 0:30 a.m.
    sender.add_periodic_task(
        crontab(hour=0, minute=30, day_of_week=1),
        clean.s(days),
    )


@app.task
def clean(arg):
    print(arg)
    app_path = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(app_path,"db.sqlite3")
    print(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create table
    c.execute("DELETE FROM chat_chatsessionmessage WHERE create_date < date('now','-"+str(arg)+" days')")

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()


def main(argv):
    days = 1
    try:
        opts, args = getopt.getopt(argv, "hd:", ["days="])
    except getopt.GetoptError:
        print('test.py -d <days>')
        # sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -d <days> ')
            sys.exit()
        elif opt in ("-d", "--days"):
            print('days : '+arg)
            days = int(arg)

    clean(days)


if __name__ == '__main__':
    main(sys.argv[1:])