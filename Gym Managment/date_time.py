from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

def my_job(text):
    print()

# The job will be executed on November 6th, 2009
sched.add_job(my_job, 'date', run_date=datetime(2021, 9, 19, 19, 2, 5), args=['Heloo'])

sched.start()