import jwt
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import JsonResponse
from django.views.generic import FormView

from .serializers import UserSerializer, LoginSerializer, profile, profile_delete
from .models import User, CreateNotes, Labels
from django.http import HttpResponse
from django.shortcuts import render, redirect
from rest_framework.generics import CreateAPIView, \
    DestroyAPIView  # Used for a create-only endpoints, provides a post method handler
from .tokens import account_activation_token
from .forms import SignupForm
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from .custom_decorators import custom_login_required
from django.utils.decorators import method_decorator
from .services import redis_information, upload_image, delete_from_s3
from self import self
import imghdr
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser


# from tasks import create_random_user_accounts


def index(request):
    return render(request, "index.html", {})  # home page


def home(request):
    return render(request, "home.html", {})  # home page


def log_me(request):
    return render(request, 'user_login.html', {})


def signup(request):
    if request.method == 'POST':  # IF method id POST
        form = SignupForm(request.POST)  # SignUp Form
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()  # Save in a DB
            current_site = get_current_site(request)  # get the current site by comparing the domain with the host
            # name from the request.get_host() method.
            message = render_to_string('activate.html', {  # Pass the link information to the message variable
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            mail_subject = 'Activate your blog account.'
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return JsonResponse('Please confirm your email address to complete the registration', safe=False)
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


class Registerapi(CreateAPIView):
    """
        This module is Register the User
         """
    serializer_class = UserSerializer

    def post(self, request):
        res = {"message": "something bad happened",
               "data": {},
               "success": False}
        print(request.data)
        email = request.data['email']
        print(email)
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        password = request.data['password']

        if email and password is not "":
            user_already = User.object.filter(email=email)
            if user_already:
                res['message'] = "User Allready Exists"
                res['success'] = True
                return JsonResponse(res)
            else:
                user = User.object.create_user(email=email, first_name=first_name, last_name=last_name,
                                               password=password)
                user.is_active = False
                user.save()
                current_site = get_current_site(request)
                message = render_to_string('activate.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token': account_activation_token.make_token(user),
                })
                mail_subject = 'Activate your account...'
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
                res['message'] = "registered Successfully...Please activate your Account"
                res['success'] = True
                return JsonResponse(res)
        else:
            return JsonResponse(res)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))  # UserId for a decoding
        user = User.object.get(pk=uid)
        if user is not None and account_activation_token.check_token(user, token):  # if its a valid token
            user.is_active = True  # User is Active
            user.save()
            return render(request, 'user_login.html')
        else:
            return HttpResponse('Activation link is invalid!')
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None


@api_view(['POST'])
@require_POST
def logins(request):
    res = {}
    res['message'] = 'Something bad happend'
    res['success'] = False

    print('**********************************loginsssss***************************')
    try:
        email = request.POST.get('email')  # Get Email
        print("Emails", email)
        password = request.POST.get('password')  # Get Password

        if email is None:
            raise Exception("Email is required")
        if password is None:
            raise Exception("Password is required")
        user = authenticate(email=email, password=password)
        print("User Name", user)
        print("password", password)

        if user:  # If it is a User
            if user.is_active:  # If a User is active
                login(request, user)  # Login maintains a request and a user
                try:
                    payload = {
                        # 'id': User.id,
                        'email': email,
                        'password': password,
                    }
                    token_encode = jwt.encode(payload, "secret_key", algorithm='HS256').decode('utf-8')
                    res['message'] = "Login Sucessfull"
                    res['success'] = True
                    res['data'] = token_encode
                    redis_information.set_token(self, 'token', res['data'])
                    return render(request, 'profile.html')  # After Sucessfull returns to the profile page
                except Exception as e:  # Invalid
                    result = {'error1': 'please provide an valid email and a password'}
                    return JsonResponse(result)
            else:
                res['message'] = "User is Inactive"
                return JsonResponse(res)
        else:
            res['message'] = 'Username or Password is not correct'  # Invalid login details
            messages.error(request, 'Invalid login details')
            return JsonResponse(res)
    except Exception as e:
        print(e)


def exit(request):  # For a Logout
    # logout(request)
    return render(request, "home.html")


class Login(CreateAPIView):
    """
        This module is to Login
         """
    serializer_class = LoginSerializer

    def post(self, request):
        res = {}
        res['message'] = 'Something bad happend'
        res['success'] = False

        print('**********************************API Login***************************')
        try:
            email = request.data['email']  # Get Email
            password = request.data['password']  # Get Password
            if email is None:
                raise Exception("Email is required")
            if password is None:
                raise Exception("Password is required")
            user = authenticate(email=email, password=password)
            print("User Name", user)
            if user:  # If it is a User
                if user.is_active:  # If a User is active
                    try:  # The claims in a JWT are encoded as a JSON object that is digitally signed using
                        # JSON Web Signature (JWS) and/or encrypted using JSON Web Encryption (JWE)
                        payload = {
                            # 'id': User.id,
                            'email': email,
                            'password': password,
                        }
                        token_encode = jwt.encode(payload, "secret_key", algorithm='HS256').decode('utf-8')
                        res['message'] = "Login Sucessfull"
                        res['success'] = True
                        res['data'] = token_encode
                        redis_information.set_token(self, 'token', res['data'])
                        return JsonResponse(res, status=200)
                    except Exception as e:  # Invalid
                        print(e)
                        result = {'error1': 'please provide an valid email and a password'}
                        return JsonResponse(result, safe=False)
                else:
                    res['message'] = "User is Inactive"
                    return JsonResponse(res, safe=False)
            else:
                res['message'] = 'Username or Password is not correct'  # Invalid login details
                messages.error(request, 'Invalid login details')
                return JsonResponse(res)
        except Exception as e:
            print(e)


def upload_profilenew(request):
    res = {}
    token = redis_information.get_token(self, 'token')  # Redis Cache GET
    token_decode = jwt.decode(token, "secret_key", algorithms=['HS256'])
    eid = token_decode.get('email')  # Additional code of a decorator to get an email
    user = User.object.get(email=eid)
    try:
        file = request.FILES['pic']  # Uploading a Pic
        print("File", file)
        tag_file = request.POST.get('email')  # Load an id of a user
        print("tag_file", tag_file)
        valid_image = imghdr.what(file)  # Validate the image file
        if str(user) == tag_file:  # if user:
            if valid_image:  # if Valid Image
                upload_image(file, tag_file, valid_image)  # Upload the image by calling the service file
                user.image = str(file)  # save a image file in db
                user.save()  # file save
                res['message'] = "Sucessfully Uploaded the Image"  # message
                res['Success'] = True
                return JsonResponse(res, status=200)
            else:
                res['message'] = "Invalid Image"  # Invalid Image
                res['Success'] = False
                return JsonResponse(res, status=404)
        else:
            res['message'] = "Invalid"  # Invalid User
            res['Success'] = False
            return JsonResponse(res, status=404)
    except Exception as e:
        print(e)
        return HttpResponse(e)


def delete_profile(request):
    """This method is used to delete any object from s3 bucket """

    token = redis_information.get_token(self, 'token')  # Redis Cache GET
    token_decode = jwt.decode(token, "secret_key", algorithms=['HS256'])
    eid = token_decode.get('email')  # Additional code of a decorator to get an email of a user
    user = User.object.get(email=eid)  # Authorize User
    tag_file = request.POST.get('email')  # Particular user upload image
    res = {}
    try:
        if str(user) == tag_file:  # if user
            delete_from_s3(tag_file)  # delete image through S3 by calling service file method
            user.image = " "  # image Null
            user.save()  # save in db
            res['message'] = " Successfully Deleted"  # message for deletion
            res['Sucess'] = True
            return JsonResponse(res, status=200)
        else:
            res['message'] = "Not Deleted"  # False
            res['Sucess'] = False
            return JsonResponse(res, status=404)
    except Exception as e:
        return HttpResponse('Invalid')


def showarchive(request):  # Archive Show
    res = {}
    notes = Notes.objects.all().order_by('-created_time')  # Sort the Notes according to the time
    try:
        if notes:
            return render(request, 'notes/index1.html', {'notes': notes})
    except notes.DoesNotExist:
        res['message'] = "No Notes in Archive"
        # res['success']=False
    except Exception as e:
        print(e)
        return HttpResponse(res, status=404)


def trash(request):
    res = {}
    notes = Notes.objects.all().order_by('-created_time')
    try:
        if notes is not None:
            return render(request, 'notes/trash.html', {'notes': notes})
        else:
            return HttpResponse("Trash is Empty")
    except Exception as e:
        res['message'] = "No Notes in Trash"
        # res['success']=False
        print(e)
        return HttpResponse(res, status=404)


def showpinned(request):
    res = {}
    notes = Notes.objects.all().order_by('-created_time')
    try:
        if notes:
            return render(request, 'notes/pinned.html', {'notes': notes})
    except Exception as e:
        res['message'] = "No Pinned Notes"
        # res['success'] = False
        print(e)
        return HttpResponse(res, status=404)


def showlabels(request):
    res = {}
    labels = Labels.objects.all().order_by('-created_time')
    try:
        if labels:
            return render(request, 'notes/showlabels.html', {'labels': labels})
    except Exception as e:
        res['message'] = "No Labels Notes"
        print(e)
        return HttpResponse(res, status=404)


def table(request):  # Display the contents of the tables using a Jinga Template
    notes = Notes.objects.all().order_by('-created_time')  # Sort the Notes according to the time
    return render(request, 'notes/index.html', {'notes': notes})


class upload_images(CreateAPIView):
    serializer_class = profile
    parser_classes = (FormParser, MultiPartParser)

    @method_decorator(custom_login_required)
    def post(self, request, *args, **kwargs):
        """
         Create a MyModel
            Create a MyModel
            ---
            parameters:
                - name: source
                  description: file
                  required: True
                  type: file
            responseMessages:
                - code: 201
                  message: Created
        """

        res = {}
        user = request.user_id
        try:
            image = request.FILES.get('image')  # Get the image File
            print('image', type(image))
            tag_file = request.data['email']
            print(tag_file)
            valid_image = imghdr.what(image)
            print(valid_image)
            print("User", user)
            if str(user) == tag_file:  # if user:
                if valid_image:  # if Valid Image
                    upload_image(image, tag_file, valid_image)  # Upload the image by calling the service file
                    user.image = str(image)  # save a image file in db
                    user.save()  # file save
                    res['message'] = "Sucessfully Uploaded the Image"  # message
                    res['Success'] = True
                    return JsonResponse(res, status=200)
                else:
                    res['message'] = "Invalid Image"  # Invalid Image
                    res['Success'] = False
                    return JsonResponse(res, status=404)
            else:
                res['message'] = "Invalid"  # Invalid User
                res['Success'] = False
                return JsonResponse(res, status=404)
        except Exception as e:
            res['message'] = "Not Valid"  # Invalid User
            return JsonResponse(res, status=404)


class delete_image(DestroyAPIView):
    serializer_class = profile_delete
    parser_classes = (FormParser, MultiPartParser)

    @method_decorator(custom_login_required)
    def post(self, request):
        """
                Create a MyModel
                ---
                parameters:
                     - name: source
                        description: file
                        required: True
                        type: file
                responseMessages:
                    - code: 201
                      message: Created
               """
        user = request.user_id
        tag_file = request.data['email']  # Particular user upload image
        res = {}
        try:
            if str(user) == tag_file:  # if user
                delete_from_s3(tag_file)  # delete image through S3 by calling service file method
                user.image = " "  # image Null
                user.save()  # save in db
                res['message'] = " Successfully Deleted"  # message for deletion
                res['Sucess'] = True
                return JsonResponse(res, status=200)
            else:
                res['message'] = "Not Deleted"  # False
                res['Sucess'] = False
                return JsonResponse(res, status=404)
        except Exception as e:
            return JsonResponse('Invalid', status=False)


