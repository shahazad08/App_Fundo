from users.models import User, CreateNotes, Labels, MapLabel
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView  # Used for a create-only endpoints, provides a post method handler
from rest_framework.views import APIView  # Taking the views of REST framework Request & Response
from .serializers import ReadLabel,LabelSerializer
from rest_framework import generics, status  # For a List API use a generics
from users.custom_decorators import custom_login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse


class create(CreateAPIView):
    """
            This module is create a Label of a specific user
           """
    serializer_class=ReadLabel
    @method_decorator(custom_login_required)  # Get a decorator
    def post(self,request):
        res={}
        """
                 This module is create a Label of a specific user
        """
        a_user = request.user_id.id
        try:
            label_name = request.data['label_name']
            labels = Labels(label_name=label_name, user_id=a_user)
            if label_name != "":
                labels.save()
                res['data'] = labels.id
                res['message'] = 'Labels are added in a database'
                res['success'] = True
                return JsonResponse(res, status=200)
            else:
                print("Savvvvvv")
                res['message'] = 'Unssucess'
                res['success'] = False  # in response return data in json format
                return JsonResponse(res, status=400)
        except Exception as e:
            res['message'] = 'Unssucess'
            res['success'] = False  # in response return data in json format
            return JsonResponse(res, status=404)

class delete(DestroyAPIView):
    @method_decorator(custom_login_required)  # Get a decorator
    def delete(self,request,pk):  # Delete a Note
        """
                  This module is delete a Label of a specific user
          """
        a_user = request.user_id.id
        print('User', a_user)
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is None:  # if label pk
                raise Exception('Id is required')
            else:
                label = Labels.objects.get(pk=pk, user=a_user)  # get requested id from a Labels
                res['data'] = label.id  # Display the id that is to be delete
                label.delete()  # delete the label
                res['message'] = "Label has been deleted"
                res['success'] = True
                return JsonResponse(res, status=200)  # Display the data
        except Exception as e:
            res['message'] = 'Label doesnt exists'  # Handle the exception when label not exists
            return JsonResponse(res, status=404)

class update(UpdateAPIView):
    """
            This module is delete a Label of a specific user
           """
    serializer_class=ReadLabel
    """
        This module is update a Label of a specific user
       """

    @method_decorator(custom_login_required)  # Get a decorator
    def put(self, request,pk):
        auth_user = request.user_id.id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            if pk is None:
                raise Exception('Id is required')
            else:
                labels = Labels.objects.get(pk=pk, user_id=auth_user)
                label_name = request.data['label_name']
                labels.label_name = label_name
                print('Titles', labels.label_name)
                res['message'] = "Update Successfully"
                res['success'] = True
                labels.save()
                return JsonResponse(res, status=200)
        except Exception as e:
            print(e)
            res['message'] = 'Label doesnt exists'
            return JsonResponse(res, status=404)


class add(APIView):
    """
        This module is to add a label to a particular note of a specific user
     """

    @method_decorator(custom_login_required)  # Get a decorator
    def post(self, request,note_id,label_id):    # request a particular note of a specific user
        auth_user = request.user_id.id # get a requested if from a token
        res = {}
        res['message'] = 'Something bad happened' # raise a exception when some unhandled exception occurs
        res['success'] = False
        try:
            if note_id and label_id is None: # if note pk
                raise Exception('Id is required')
            else:
                note = CreateNotes.objects.get(pk=note_id, user=auth_user)  # reterieve the pk of a particular note
                # according to a specific user
                label = Labels.objects.get(id=label_id, user_id=auth_user) # get a label of a particular user id
                maplabel = MapLabel.objects.filter(note_id=note, label_id=label)  # filter the note and label
                if len(maplabel) == 0:  # if maplabel field is empty
                    obj = MapLabel(note_id=note, label_id=label)  # assigned the notes and a label using model by
                    # creating the oject
                    obj.save()  # save the object
                    res['data'] = note.id  # message of passing data in a SMD format
                    res['message'] = 'Labels are added to a particular note'
                    res['success'] = True
                    return JsonResponse(res, status=200)
                else:
                    res['message'] = ' Labels Allready added'  # Something wrong
                    res['success'] = False
                    return JsonResponse(res, status=200)
        except CreateNotes.DoesNotExist: # Handles Exception when notes are not present
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)
        except Exception as e:
            print(e)
            return JsonResponse(res, status=404)

class deletelabel(APIView):
    """
        This module is to add a label to a particular note of a specific user
    """
    @method_decorator(custom_login_required)  # Get a decorator
    def delete(self, request,note_id,label_id):  # request a particular note of a specific user
        auth_user = request.user_id.id # get a id of from a header token
        res = {}
        res['message'] = 'Something bad happened'  # raise a exception when unhandled occurs
        res['success'] = False
        try:
            if note_id is None: # if  requested pk
                raise Exception('Id is required')
            else:
                note = CreateNotes.objects.get(pk=note_id, user=auth_user)  # retrieve the pk of a particular note
                label = Labels.objects.get(id=label_id, user_id=auth_user) # retrieve the label of a particular user
                maplabel = MapLabel.objects.filter(note_id=note, label_id=label)  # filter the note and label
                maplabel.delete() # delete a requested note
                res['message'] = 'Labels are remove to a requested note'
                res['success'] = True
                return JsonResponse(res, status=status.HTTP_201_CREATED)
        except CreateNotes.DoesNotExist: # Handled the exception
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)
        except Exception as e:
            print(e)
            return JsonResponse(res, status=404)

class getLabelOnNotes(CreateAPIView):
    """
            This module is to add a label to a particular note of a specific user
         """
    serializer_class=LabelSerializer

    @method_decorator(custom_login_required) # Get a decorator
    def post(self, request):
        auth_user = request.user_id.id # Get a requested Id
        res = {}
        res['message'] = 'Something bad happened'
        res['success'] = False
        try:
            label_id = request.data['label_id'] # Get a requested Id
            if label_id is None:
                raise Exception("Id is required")
            else:
                label = MapLabel.objects.filter(
                    label_id=label_id).values()  # Filter down a queryset based on a model's=
                data = []  # Created a Empty List
                for i in label:  # Gets a Note id from a label data and store it in a list
                    data.append(i['note_id_id'])
                items =CreateNotes.objects.filter(id__in=data, user=auth_user).values() # Gets the Notes of a specific User
                if items:   # if notes
                    print (items)
                    notes_data = [] # Store the Notes in a list
                    for i in items:
                        notes_data.append(i) # Convert the Query Set to a Json Serializer
                    return JsonResponse(notes_data, safe=False) # Return Json Response
                else:
                    res['message'] = 'Note doesnt exists'
                    res['success'] = 'False'
                    return JsonResponse(res, status=404)

        except Exception as e:
            print(e)
            res['message'] = 'Note doesnt exists'
            return JsonResponse(res, status=404)
