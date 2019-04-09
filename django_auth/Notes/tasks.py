import datetime
from datetime import datetime
from datetime import timedelta
from datetime import date
from celery.task import task
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from users.models import CreateNotes
from django.core import serializers
from .views import *




@task
def run():
    a=10
    b=50
    c=a+b
    print(c)
    return c

@task
def running():
    a="Shahazad Shaikh"
    print()
    return a


@task
def auto_delete_archive(a_user,email_user):
    auth_user = a_user
    try:
        notes = CreateNotes.objects.filter(user=auth_user, is_archived=True).values('id','title','created_time')
        print("Notes", notes)
        for i in notes:
            todays = datetime.datetime.today()
            print("Today Date", todays)
            # end_date = todays + datetime.timedelta(days=15)
            end_date = i['created_time'] + timedelta(days=15)
            print("END Date of Archive Notes", end_date)
            if end_date.date == todays:
                print("Days Matches")
                item = CreateNotes.objects.get(pk=i['id'])
                item.trash = True
                item.save()
                current_site = '127.0.0.8000'
                print("Current Site Domain", current_site)
                data = {'title': "Reminderrrr",  # i['title'],
                        'reminder_date': i,
                        'domain': current_site,
                        }
                print("Hello Title")
                message = "Archive Message Notification "
                mail_subject = 'Archive Notification alert !'  # mail subject
                to_email = email_user  # mail id to be sent to
                email = EmailMessage(mail_subject, message,
                                     to=[to_email])  # takes 3 args: 1. mail subject 2. message 3. mail id to send
                email.send()
                print("Email sent")

            else:
                print("No Matches of Date")

        trash_notes = CreateNotes.objects.filter(user=auth_user, trash=True).values('id', 'title','created_time')

        for j in trash_notes:
            todays = datetime.datetime.today()
            end_date = j['created_time'] + timedelta(days=7)
            print("End date of Trash Notes", end_date)

            if end_date.date == todays:
                delete_item = CreateNotes.objects.get(id=j['id'])
                delete_item.delete()
                print("Days Matches")
                item = CreateNotes.objects.get(pk=i['id'])
                item.trash = True
                item.save()
                current_site = '127.0.0.8000'
                print("Current Site Domain", current_site)
                data = {'title': "Reminderrrr",  # i['title'],
                        'reminder_date': i,
                        'domain': current_site,
                        }
                print("Hello Title")
                message = "Delete Message Notification "
                mail_subject = 'Delete Notification alert !'  # mail subject
                to_email = 'sk.shahazad@gmail.com'  # mail id to be sent to
                email = EmailMessage(mail_subject, message,
                                     to=[to_email])  # takes 3 args: 1. mail subject 2. message 3. mail id to send
                email.send()
                print("Email sent for Notification")

                print("Deleted Successfully")
            else:
                print("Days are Not Match")

        archive_delete = []
        for i in notes:
            archive_delete.append(i)

        trash_delete = []
        for j in trash_notes:
            trash_delete.append(j)

        # return JsonResponse(notes, trash_notes, status=False)
        return notes, trash_notes
    except Exception as e:
        print("Display", e)


