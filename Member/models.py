from django.db import models

from SGFriend import settings
from MainApp.models import *
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.views.generic import CreateView, DetailView
# Create your models here.

class MemberManager(BaseUserManager):
    def create_user(self,  email, name, student_number=None, loc=None, introduction=None, password=None):
        if not email:
            raise ValueError('이메일을 입력하세요')

        member = self.model(
            email=self.normalize_email(email),
            name=name,
            student_number=student_number,
            location=loc,
            introduction=introduction,
        )

        member.set_password(password)
        member.save(using=self._db)
        return member

    def create_superuser(self, email, name, password):
        member = self.create_user(email=email, name=name, password=password)
        member.is_admin = True
        member.is_active = True
        member.save(using=self._db)
        return member

#class Profile(models.Model):
#    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 현 계정의 사용자를 가져올 수 있음.
#    nickname = models.CharField(max_length=64)
 #   profile_photo = models.ImageField(blank=True)                 # 값을 채워넣지 않아도 되는 속성.


class Member(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=30, unique=True, verbose_name='name')  # blank랑 null차이? -> blank는 DB에 '' 로 저장됨, null은 열 자체에 값이 없음
    student_number = models.IntegerField(blank=True, null=True, verbose_name='student_number')  # choices(select박스) -> 폼에서 설정합니다!
    email = models.EmailField(max_length=50, unique=True, blank=False, verbose_name='email')  # 이메일 검증은 views.py 에서 저희가 로직을 만들어서 검증을 합니다
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True, verbose_name='location')
    # 알아봐야될거같은데 보안 때문에, 사용자가 패스워드로 123456 입력 -> 내부에 해쉬함수로 못알아보는 값으로 저장을 해야 돼요 -> 장고는 어떻게?
    profile_photo = models.ImageField(blank=True)

    introduction = models.TextField(blank=True, null=True, verbose_name='introduction')  # help_text(필드입력도움말기능) -> 폼에서 설정합니당!
    last_login = models.DateTimeField(blank=True, null=True)
  
    is_active = models.BooleanField(
        'active',
        default=False,  #이메일 인증 전까지는 False인 상태
        help_text="")
    is_admin = models.BooleanField(default=False)

    objects = MemberManager()

    ''' 채팅방 리스트가 있어야 함'''

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

image = models.ImageField(upload_to='Member', null=True)