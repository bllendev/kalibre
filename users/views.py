# from django.urls import reverse_lazy
# from django.views import generic
# from .forms import CustomUserCreationForm
# from django.contrib.auth import get_user_model
# from django.shortcuts import redirect, render
# from django.urls import reverse, resolve


# CustomUser = get_user_model()


# class SignupPageView(generic.CreateView):
#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy('login')
#     template_name = 'signup.html'


# # def add_email(request):
# #     email = request.post.get('email')
# #     new_email = Email(email_address=email)
# #     new_email.save()
# #     return redirect(reverse("my_emails"))


# # def my_emails(request):
# #     email_addresses = []
# #     if request.user.is_authenticated:
# #         username = request.user.username
# #         email_addresses = CustomUser.objects.get(username=username).email_address.all()

# #     if request.method == "POST":
# #         pass

# #     print(CustomUser.__dict__)
# #     return render(
# #         request,
# #         'books/my_emails.html',
# #         {
# #             'email_address': email_addresses,
# #         }
# #     )