# accounts.passwords.urls.py 
from django.urls import path, re_path
# from django.contrib.auth import views as auth_views

from accounts.views import (
                         password_change,
                         password_change_done,
                         password_reset,
                         password_reset_done,
                         password_reset_confirm,
                         password_reset_complete,



                         )

app_name = "passwords"


urlpatterns  = [
                re_path(r'^password/change/$', 
                        password_change, 
                        name='password_change'),
                re_path(r'^password/change/done/$',
                        password_change_done, 
                        name='password_change_done'),

                re_path(r'^password/reset/$', 
                        password_reset, 
                        name='password_reset'),
                re_path(r'^password/reset/done/$', 
                        password_reset_done, 
                        name='password_reset_done'),
                re_path(r'^password/reset/\
                        (?P<uidb64>[0-9A-Za-z_\-]+)/\
                        (?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 
                        password_reset_confirm, 
                        name='password_reset_confirm'),

                re_path(r'^password/reset/complete/$', 
                        password_reset_complete, 
                        name='password_reset_complete'),
        ]