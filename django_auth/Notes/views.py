import datetime
from datetime import datetime
import datetime
# from email.message import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from users.models import User, CreateNotes

from rest_framework.filters import OrderingFilter
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, DestroyAPIView, \
    UpdateAPIView,RetrieveAPIView # Used for a create-only endpoints, provides a post method handler
from rest_framework.views import APIView  # Taking the views of REST framework Request & Response
from .serializers import PageNoteSerializer, NoteSerializer, CollaborateSerializer, ColorSerializer, UpdateSerializer, \
    RemainderSerializer,SearchSerializer
from rest_framework import generics  # For a List API use a generics
from .paginate import PostPageNumberPagination  # Creating our own no. of records in a Pages
from rest_framework.filters import SearchFilter  # it allows users to filter down a queryset based on a model's
from users.custom_decorators import custom_login_required
from django.utils.decorators import method_decorator
from users.services import redis_information
from .tasks import auto_delete_archive, run, running

import jwt


class create(CreateAPIView):
    """
      This module is to create a note of a specific user
      """
    serializer_class = NoteSerializer

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request):
        res = {}
        if request.method == 'POST':
            auth_user = request.user_id.id  # get the id of a specific user through token
            try:
                title = request.data['title']  # get the title
                description = request.data['description']  # get the description
                color = request.data['color']  # get the color
                notes = CreateNotes(title=title, description=description, color=color,
                                    user_id=auth_user)  # assigned in the notes
                if title != "" and description != "":  # if not null
                    notes.save()  # add in a db
                    res['message'] = 'Notes are added in a database'
                    res['success'] = True
                    res['data'] = notes.id
                    return JsonResponse(res, status=200)
                else:
                    res['message'] = 'Unssucesss'
                    res['success'] = False
                    return JsonResponse(res, status=404)
            except Exception as e:
                res['message'] = 'Something bad happend'
                print(e)
                return JsonResponse(res, status=404)
        else:
            res['success'] = False
            res['message'] = 'Request unhandled'
            return JsonResponse(res, status=404)


class deletenote(DestroyAPIView):
    """
    This module is to delete a note of a specific user
    """

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def delete(self, request, pk):
        auth_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is None:  # If id is None
                raise Exception('Id is required')  # Raise the Exception
            else:
                note = CreateNotes.objects.get(pk=pk,
                                               user=auth_user)  # get requested id from a Note, and a particular user
                if note.trash:  # If note.trash is True
                    res['data'] = note.id
                    res['message'] = 'Notes is in Trash'  # Means Note is in a Trash
                    res['success'] = True
                    return JsonResponse(res, status=200)  # Display the data
                else:  # if trash is false, change to true
                    note.trash = True
                    note.save()  # save in a db
                    res['data'] = note.id
                    res['message'] = 'Note has been moved to trash'
                    res['success'] = True
                    return JsonResponse(res, status=200)  # Display the data
        except Exception as e:
            print('Note doent exists')
            print(e)
            res['message'] = 'Note doesnt exists'  # Exception is handled
            res['success'] = False
            return JsonResponse(res, status=404)


class get(RetrieveAPIView):
    '''
            This Moudule is to Read a notes of a specific user
        '''

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def get(self, request):
        res = {}
        a_user = request.user_id.id  # get the id though a token
        email_user=request.user_id.email
        print("Email",email_user)
        auto_delete_archive.delay(a_user,email_user)
        try:
            read_notes = CreateNotes.objects.filter(user=a_user).values()  # display the notes of a particular user
            print("****", read_notes)
            values = CreateNotes.collaborate.through.objects.filter(
                user_id=a_user).values()  # display the users which are collaborated with the users
            print("Values", values)
            collab = []  # blank collaborator array
            for i in values:  # assigned the values in i which are collaborated with the  particular user
                collab.append(i['createnotes_id'])  # append with respect to the note id
            collab_notes = CreateNotes.objects.filter(id__in=collab).values().order_by(
                '-created_time')  # id__in indicates to take all the values
            # print("collab Notes -------------", collab_notes)
            merged = read_notes | collab_notes  # as to merging the 2 query sets into one
            l = []  # Converting the query sets to a json format
            for i in merged:
                l.append(i)

            token = redis_information.get_token(self, 'token')  # Redis Cache GET
            print('Token from a redis cache------------------', token)
            return JsonResponse(l, safe=False)
        except Exception as e:  # Excaption is Handled
            res['message'] = "User Not Exist"
            res['sucess'] = False
            return JsonResponse(res, status=404)


class delete(DestroyAPIView):
    '''
       This module is to delete a note of a specific user
       '''

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def delete(self, request, pk):
        auth_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is None:  # if id is None
                raise Exception('Id is required')  # Raise the
            else:
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # get requested id from a Note
                if note.trash:  # if is_deleted is true
                    note.delete()  # delete it
                    res['message'] = 'Note has been deleted from trash'
                    res['success'] = True
                    return JsonResponse(res, status=200)
                else:
                    raise Exception()
        except Exception as e:
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            res['success'] = False
            return JsonResponse(res, status=404)


class restore(APIView):
    """
          This module is to restore a note of a specific user
          """

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request, pk):
        auth_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is None:  # If Id is None
                raise Exception('Id is required')
            else:
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # Get a requested Note
                if note.trash:  # If note.trash is true, change it to false
                    note.trash = False
                    note.save()  # save in a db
                    res['message'] = "Selected Note has been Restored"
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)
                else:
                    raise Exception()
        except Exception as e:  # Handle the Excaption
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class update(UpdateAPIView):
    '''
        This module is to Update a note of a specific user
          '''
    serializer_class = UpdateSerializer

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def put(self, request, pk):
        auth_user = request.user_id.id  # Get a user
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is None:  # If id is None
                raise Exception('Id is required')  # Raise the exception
            else:
                notes = CreateNotes.objects.get(pk=pk, user=auth_user)  # Update the particular note from a user
                title = request.data['title']  # Updates the tile or any user fields
                description = request.data['description']
                color = request.data['color']
                remainder = request.data['remainder']
                notes.title = title  # Assign the updated fields to a requsted note
                notes.description = description
                notes.color = color
                notes.remainder = remainder
                notes.save()  # save in a db
                res['message'] = "Update Successfully"
                res['success'] = True
                res['data'] = notes.id
                return JsonResponse(res, status=200)
        except Exception as e:  # Handle the exception
            print(e)
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class archive(APIView):  # Delete a Note
    """
    This module is to archive a note of a specific user
    """

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request, pk):
        auth_user = request.user_id.id  # Request for a specific user
        res = {}
        # If any fault Exception, shows the message
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is None:
                raise Exception('id is required')
            else:
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # get particular note from a id
                if note.is_archived == False:  # if archived is false, change it to true, as to move in a archived
                    note.is_archived = True
                    note.save()  # save in a db
                    res['message'] = "Selected Note has been moved to Archive"
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)  # return result
                else:
                    raise Exception()

        except Exception as e:  # catch the exception as if the note exists
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class isarchive(APIView):  # Delete a Note
    """
    This module is to archive a note of a specific user
    """

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request, pk):
        auth_user = request.user_id.id  # Request for a specific user
        res = {}  # If any fault Exception, shows the message
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is None:
                raise Exception('id is required')
            else:
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # get particular note from a id
                if note.is_archived:  # if archived is false, change it to true, as to move in a archived
                    note.is_archived = False
                    note.save()  # save in a db
                    res['message'] = "Selected Note has been moved to Dashboard"
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)  # return result
                else:
                    raise Exception()

        except Exception as e:  # catch the exception as if the note exists
            print('Note doent exists')
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class color(UpdateAPIView):  # Delete a Note
    """
       This module is set a color to a note of a specific user
      """
    serializer_class = ColorSerializer

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def put(self, request, pk):
        auth_user = request.user_id.id  # Get a specific user
        res = {}
        res['message'] = 'Something bad happened'  # If any fault Exception, shows the message
        res['success'] = False
        try:
            if pk is None:  # if id is None
                raise Exception('Id is required')  # raise a exception
            else:
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # get a selected note from a user
                note.color = request.data['color']  # request the color from notes model, for change
                lenth = len(note.color)
                if lenth <= 6:
                    note.save()  # save to db
                    res['message'] = "Color has been Changed."  # message for change color
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)  # return result
                else:
                    res['message'] = "Color should not be more than 5 letters."  # message for change color
                    res['success'] = False
                    res['data'] = note.id
                    return JsonResponse(res, status=404)  # return result

        except Exception as e:
            res['message'] = 'Note doesnt exists'  # Handles Exception message if note doesnot exists
            return JsonResponse(res, status=404)


class pinned(APIView):
    """
     This module is set a pinned to a note of a specific user
    """

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request, pk):
        auth_user = request.user_id.id  # get a specific user
        res = {}
        res['message'] = 'Something bad happened'  # If any fault Exception, shows the message
        res['success'] = False
        try:
            if pk is None:  # If id is None
                raise Exception('Id is required')  # Raise a Exception
            else:
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # get a requested pk
                if note.is_pinned == False:  # if not pinned
                    note.is_pinned = True  # change it to pin
                    note.save()  # save in a db
                    res['message'] = "Notes has been Pinned to Top."  # message in a SMD format
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)
                else:
                    raise Exception()
        except Exception as e:  # catch exception if note doesnt exists
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)

class ispinned(APIView):
    """
     This module is set a pinned to a note of a specific user
    """

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request, pk):
        auth_user = request.user_id.id  # get a specific user
        res = {}
        res['message'] = 'Something bad happened'  # If any fault Exception, shows the message
        res['success'] = False
        try:
            if pk is None:  # If id is None
                raise Exception('Id is required')  # Raise a Exception
            else:
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # get a requested pk
                if note.is_pinned:  # if not pinned
                    note.is_pinned = False  # change it to pin
                    note.save()  # save in a db
                    res['message'] = "Notes has been Move to Unpinned"  # message in a SMD format
                    res['success'] = True
                    res['data'] = note.id
                    return JsonResponse(res, status=200)
                else:
                    raise Exception()
        except Exception as e:  # catch exception if note doesnt exists
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)

class copy(APIView):
    """
        This module is set a copy of a note of a specific user
    """

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request, pk):
        auth_user = request.user_id.id  # get note with given id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is None:  # If id is None
                raise Exception('Id is required')  # Raise a exception if id not present
            else:
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # Accept a note pk
                note.id = None  # create pk as a none
                note.save()  # save in a db
                res['message'] = "Note is Coped "  # Note is copied
                res['success'] = True
                res['data'] = note.id
                return JsonResponse(res, status=200)
        except Exception as e:
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class remainder(APIView):  # get the remainder
    '''
          This module is to get a remainder note of a specific user
          '''

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def get(self, request):
        auth_user = request.user_id.id
        res = {}
        remainder_fields = CreateNotes.objects.filter(remainder__isnull=False,
                                                user=auth_user).values()  # check the remainder field
        # is not null
        try:
            if remainder_fields:  # if remainder
                remainder = []
                for i in remainder_fields:  # convert the  query set to a Json format
                    remainder.append(i)
                return JsonResponse(remainder, safe=False)
            else:  # No remainder
                res['message'] = "No remainder set"
                res['success'] = 'False'
                return JsonResponse(res, safe=False)
        except Exception as e:
            res['message'] = " Note Doesnt Exists"
            res['success'] = 'False'
            return JsonResponse(res, safe=False)


class collaborator(CreateAPIView):
    """
        This module is to create a collaborator to a particular note of a specific user
      """
    serializer_class = CollaborateSerializer

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def post(self, request, pk):  # get the require pk
        a_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happend'
        res['success'] = False
        try:
            # id = request.POST.get('id', None) # get the id of a specific note
            if pk is None:  # if id is None
                raise Exception('id required')  # raise the exception
            else:  # if not same delete it
                note = CreateNotes.objects.get(pk=pk, user=a_user)  # get the required id of a note
                note_user = note.user.id  # Get the Note User ID
                note_id = note.id
                collaborate = request.data['collaborate']  # Accept a id of a new user
                user = User.object.get(id=int(collaborate))  # get the details of a user through id
                values = CreateNotes.collaborate.through.objects.filter(
                    user_id=a_user).values()  # display the users which are collaborated with the users
            if note_user == user.id:  # If note user_id and collaborate user is same
                res['message'] = 'Cannot Collaborate to the same User'
                res['success'] = False
                return JsonResponse(res, status=404)
            elif CreateNotes.collaborate.through.objects.filter(user_id=user.id,
                                                          createnotes_id=note.id):  # Checking of a same user id and create note id for as if its exist user or not
                res['message'] = 'User Allready Exists'
                res['success'] = False
                return JsonResponse(res, status=404)
            else:
                print("user", user.id)
                note.collaborate.add(user)  # adds the user to the note
                note.save()  # save the note
                res['message'] = 'Success'
                res['success'] = True
                res['data'] = note.id
                return JsonResponse(res, status=200)
        except Exception as e:
            res['message'] = 'Note doesnt exists'
            print(e)
            return JsonResponse(res, status=404)


class deletecollaborator(DestroyAPIView):
    """
           This module is to delete a collaborator to a particular note of a specific user
        """
    serializer_class = CollaborateSerializer

    @method_decorator(custom_login_required)  # Decorator is called with respective to token user
    def delete(self, request, note_id, user_id):
        auth_user = request.user_id.id  # get the requested id
        res = {}
        res['message'] = 'Something bad happend'  # raise the exception if bad happens
        res['success'] = False
        try:
            if note_id is None:  # if id is none
                raise Exception('id is required')
            else:
                note = CreateNotes.objects.get(pk=note_id, user=auth_user)  # note id with a specific user
                auth_user = note.user.id  # Use vairable b as a Note User
                user = User.object.get(id=user_id)  # get the details of a users from a User table
                if auth_user == user.id:  # check for a collaborator when id is same
                    res['message'] = 'Cannot Collaborate to the same User'
                    res['success'] = False
                    return JsonResponse(res, status=404)  # return status
                else:  # if not same delete it
                    res['message'] = 'Deleted'  # message in a SMD format
                    res['success'] = True
                    res['data'] = note.id
                    note.collaborate.remove(user)  # remove the user
                    note.save()  # save in db
                    return JsonResponse(res, status=200)
        except Exception as e:  # if user not exists
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)


class create_remainder(CreateAPIView):
    """
        This module is to set a remainder to a note of a specific user
        """
    serializer_class = RemainderSerializer  # Get the remainder Serializer

    @method_decorator(custom_login_required)  # Get the User
    def post(self, request, pk):  # Passs the Id
        auth_user = request.user_id.id
        res = {}
        try:
            if pk is None:  # If id is None
                raise Exception("Id is required")  # raise Exception
            else:
                note = CreateNotes.objects.get(pk=pk, user=auth_user)  # Assign according to the User
                remainder = request.data['remainder']  # Get the remainder field
                note.remainder = remainder  # Set the Remainder
                note.save()  # save db
                res['message'] = 'Remainder Set Successfully '  # message in a SMD format
                res['success'] = True
                res['data'] = note.id
                return JsonResponse(res, status=200)
        except Exception as e:  # return False
            print(e)
            res['message'] = "Note Doesnot Exists"
            res['success'] = False
            return JsonResponse(res, status=404)


class PostListAPIView(generics.ListAPIView):  # Viweing the ListAPI Views that
    """
        This module is to Paginate a Pages of a Notes
         """
    serializer_class = PageNoteSerializer  # Assigning a Notes serializers fields in a Serializer class
    filter_backends = [SearchFilter, OrderingFilter]
    # search_fields=['title','description']
    pagination_class = PostPageNumberPagination  # Create our own limit of records in a pages

    def get_queryset(self, *args, **kwargs):  # Method for a itrerating of pages
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            query_list = CreateNotes.objects.filter().order_by(
                '-created_time')  # Filter down a queryset based on a model's
            # fields, displaying the form to let them do this.
            return query_list
        except Exception as e:
            res['message'] = 'Empty'
            res['success'] = False
            return JsonResponse(res, status=404)



class reminder_notification(APIView):
    """ This API is used to send email notifications to users as reminder
        RetriveAPIView: Used for read-only operations  ,provides get  method handlers"""

    @method_decorator(custom_login_required)
    def get(self, request):
        reminder_notification=False
        global j
        res = {}
        auth_user = request.user_id.id
        try:
            dates = CreateNotes.objects.filter(remainder__isnull=False,
                                         user=auth_user).values('id', 'title', 'remainder')
            todays_date = datetime.datetime.today()
            remind_dates = []
            for j in dates:
                remind_dates.append(j['remainder'])
            today = todays_date.strftime("%Y-%m-%d")
            if dates:
                for i in remind_dates:
                    print("Remainder Dates", i)
                    notify_date = i.strftime("%Y-%m-%d")

                    if notify_date == today:
                        current_site = get_current_site(request)
                        data = {'title': "Reminderrrr",  # i['title'],
                                'reminder_date': i,
                                'domain': current_site.domain,
                                }

                        print("Hello Title")
                        message = "Reminder messsage "
                        mail_subject = 'Reminder alert !'  # mail subject
                        to_email = str(request.user_id)  # mail id to be sent to
                        email = EmailMessage(mail_subject, message,
                                             to=[
                                                 to_email])  # takes 3 args: 1. mail subject 2. message 3. mail id to send
                        email.send()
                        return JsonResponse({"success": "Email sent "})
                    else:
                       reminder_notification=False
            if reminder_notification==False:
                res['message'] = "No Matches "
                res['success'] = False
                return JsonResponse(res, status=404)

        except Exception as e:
            res['message'] = "Unsuccess "
            res['success'] = False
            print(e)
            return JsonResponse(res, status=404)


class search_note(RetrieveAPIView):
    serializer_class = SearchSerializer
    @method_decorator(custom_login_required)
    def post(self,request):
        res = {}
        auth_user=request.user_id.id
        try:
            title = request.data['title']
            if title:
                note = CreateNotes.objects.filter(title=title, user=auth_user).values('id', 'title', 'description','color')
                print('Search Notes', note)
                search_notes = []
                for i in note:
                    search_notes.append(i)
                return JsonResponse(search_notes, safe=False)
            else:
                res['message'] = "Not Present"
                res['success'] = False
                return JsonResponse(res, status=404)
        except Exception as e:
            res['message'] = ""
            res['success'] = False
            return JsonResponse(res, status=404)





