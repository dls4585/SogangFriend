from django.shortcuts import render, redirect
from .helper import send_mail
from django.views.generic import *
from .models import Member
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .forms import *
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from mainApp.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

User = get_user_model()


def mail_send(member, request, find):
    '''if find:
        send_mail(
            "~~~제목~~~~",
            #~~~누구한테 보낼지~~~~
            #~~~~~html~~~~~~
            # 아래 양식 참고
        )
    else:
        send_mail(
            "{}님의 회원가입 인증 메일입니다.".format(member.name), [member.email],
            html=render_to_string('send_mail.html', {
                "user": member,
                'uid': urlsafe_base64_encode(force_bytes(member.pk)).encode().decode(),
                'domain': request.META['HTTP_HOST'],
                # 'token': default_token_generator.make_token(self.object),
            })
        )'''
    send_mail(
        "{}님의 회원가입 인증 메일입니다.".format(member.name), [member.email],
        html=render_to_string('send_mail.html', {
            "user": member,
            'uid': urlsafe_base64_encode(force_bytes(member.pk)).encode().decode(),
            'domain': request.META['HTTP_HOST'],
            # 'token': default_token_generator.make_token(self.object),
        })
    )


class RegisterView(APIView):

    def get(self, request):
        return render(request, 'Member/register.html')

    def post(self, request):
        name = request.POST.get('name', '')
        student_number = request.POST.get('student_number', '')
        email = request.POST.get('email', '')
        location = request.POST.get('location', '')
        password = request.POST.get('password', '')
        re_password = request.POST.get('re_password', '')
        introduction = request.POST.get('introduction', '')
        res_data = {}
        if not (name and email and password and re_password and location and introduction):
            # return HttpResponse('필수문항(*)을 입력해 주세요.')
            res_data['error'] = "필수문항(*)을 입력해 주세요."
        if password != re_password:
            # return HttpResponse('비밀번호가 다릅니다.')
            res_data['error'] = '비밀번호가 다릅니다.'

        else:
            location_info = str(location).split(' ')
            # 수정 필요 이미 있는지 검사
            si = Si(name=location_info[0], isGYorTB=True)  # 수정 필요 나중에 특별시 광역시 검사 로직
            si.save()
            gu = Gu(name=location_info[1], si=si)
            gu.save()
            dong = Dong(name=location_info[2], si=si, gu=gu)
            dong.save()
            loc = Location(si=si, gu=gu, dong=dong)
            loc.save()
            member = Member(name=name, student_number=student_number, email=email, password=make_password(password),
                            location=loc, introduction=introduction)
            member.save()
            user = User.objects.create_user(email=request.data['email'], name=request.data['name'], password=request.data['password'])
            user.save()
            mail_send(member, request)
            token = Token.objects.create(user=user)
            return Response({"Token": token.key})
        return render(request, 'Member/register.html', res_data)  # register를 요청받으면 register.html 로 응답.


class LoginView(View):
    response_data = {}
    form_class = LoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'Member/login.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            login_email = form.cleaned_data['email']
            login_password = form.cleaned_data['password']
            member = authenticate(email=request.data['email'], name=request.data['name'], password=request.data['password'])
            if member is not None:
                token = Token.objects.get(member=member)
                Response({"Token": token.key})
                return redirect('/')

            else:
                self.response_data['error'] = "비밀번호를 틀렸습니다."
        else:
            self.response_data['error'] = "이메일과 비밀번호를 모두 입력해주세요."
        return render(request, 'Member/login.html', self.response_data)


def logout(request):
    request.session.pop('Member')
    return redirect('/')
