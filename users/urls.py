from django.urls import path
from users import views
from users import ajax


urlpatterns = [
    path("my-profile/", views.MyProfile.as_view(), name="my_profile"),
    # ajax
    path("add-email/", ajax.add_email, name="add_email"),
    path('delete-email/<int:pk>/', ajax.delete_email, name='delete_email'),
    path("toggle-translate-email/<int:pk>/", ajax.toggle_translate_email, name="toggle_translate_email")
]