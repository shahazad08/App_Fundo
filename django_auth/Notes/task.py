from datetime import datetime as dt, datetime
import datetime
import string
from email.message import EmailMessage

from celery.task import task

import jwt
# from django.contrib.auth.models import User
from django.db.models import Q
# from .models import User
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from rest_framework.views import APIView
from users.models import User, CreateNotes
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from users.custom_decorators import custom_login_required
from celery import shared_task
from django.utils.decorators import method_decorator

from self import self
# from users.models import CreateNotes
# from users.services import redis_information
from users.services import redis_information



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
def auto_delete_archive(a_user):

    auth_user=a_user
    print("User", auth_user)
    try:
        notes = CreateNotes.objects.filter(user=auth_user, is_archived=True).values('id','trash_time','created_time').order_by(
'-created_time')
        print("Notes", notes)
        for i in notes:
            todays=datetime.date.today()
            print("Today Date",todays)
            # end_date = todays + datetime.timedelta(days=15)
            end_date = i['created_time'] + datetime.timedelta(days=15)
            print("END Date of Archive Notes", end_date)
            if end_date.date == todays:
                print("Days Matches")
                item = CreateNotes.objects.get(pk=i['id'])
                item.trash = True
                item.save()
            else:
                print("No Matches of Date")

        trash_notes = CreateNotes.objects.filter(user=auth_user, trash=True).values('id','trash_time','created_time').order_by(
'-created_time')

        for j in trash_notes:
            todays = datetime.date.today()
            end_date = j['created_time'] + datetime.timedelta(days=7)
            print("End date of Trash Notes",end_date)


            if end_date.date == todays:
                delete_item = CreateNotes.objects.get(id=j['id'])
                delete_item.delete()
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
        print("Display",e)



