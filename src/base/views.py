from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.test import Client
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.middleware.csrf import get_token
import json
from api.models import FlowData
from django.conf import settings
# Initialize the test client
client = Client()

class CustomLoginView(FormView):
    template_name = 'base/login.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()

        if user is not None:
            login(self.request, user)

            # Debug: Check session ID generation
            session_id = self.request.session.session_key
            # print(f"Session ID after login: {session_id}")

            return redirect('waterflow')
        else:
            print("User authentication failed in form_valid()")

        return super().form_invalid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('waterflow')
def about(request):
    return render(request, 'base/about.html')

class RegisterPage(FormView):
    template_name = 'base/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('waterflow')

    def form_valid(self, form):
        user = form.save()
        user.save()  # Ensure the user is saved

        login(self.request, user)

        return redirect(self.success_url)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('waterflow')
        return super(RegisterPage, self).get(*args, **kwargs)


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')  

    # GET requests also redirect to the login page
    elif request.method == 'GET':
        logout(request)
        return redirect('login')  

    # If the request method is neither GET nor POST, return an error response
    return JsonResponse({'status': 'failed'}, status=400)

class Waterflow(LoginRequiredMixin, ListView):
    model = FlowData
    context_object_name = 'waterflows'
    template_name = 'base/waterflows.html'

    def get_queryset(self):
        return FlowData.objects.filter(user=self.request.user).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        csrf_token = get_token(self.request)
        
        try:
            # Get flow data
            api_url = self.request.build_absolute_uri('/api/flow-data/user/')

            # Set up session authentication
            client = Client()
            client.cookies[settings.SESSION_COOKIE_NAME] = self.request.session.session_key

            headers = {
                'X-User-ID': str(self.request.user.user_id),
                'X-CSRFToken': csrf_token,
                'Accept': 'application/json',
            }
            
            # Get flow data with token info
            response = client.get(api_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                for i in range(1, 4):
                    sensor = data.get(f'sensor{i}', {})
                    if sensor:
                        print(f"\nSensor {i}:")

                context['api_data'] = data

        except Exception as e:
            print(f"\nException occurred: {str(e)}")
            context['error'] = str(e)
            context['api_data'] = None

        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        
        if action == 'recharge':
            return self.handle_recharge(request)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

    def handle_recharge(self, request):
        try:
            csrf_token = get_token(request)
            api_url = request.build_absolute_uri('/api/token/recharge/')

            # Get token amount from form
            token_amount = request.POST.get('token_amount')

            if not token_amount:
                return JsonResponse({
                    'error': 'Token amount is required'
                }, status=400)

            # Set up client
            client = Client()
            client.cookies[settings.SESSION_COOKIE_NAME] = request.session.session_key

            headers = {
                'X-User-ID': str(self.request.user.user_id),
                'X-CSRFToken': csrf_token,
                'Content-Type': 'application/json',
            }

            # Send recharge request
            response = client.post(
                api_url,
                data=json.dumps({
                    'token_amount': token_amount
                }),
                content_type='application/json',
                headers=headers
            )

            if response.status_code == 201:
                return JsonResponse({
                    'message': 'Token recharged successfully',
                    'data': response.json()
                })
            else:
                return JsonResponse({
                    'error': 'Recharge failed',
                    'details': response.json()
                }, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def get_auth_headers(self):
        return {
            'X-User-ID': str(self.request.user.user_id),
            'X-CSRFToken': get_token(self.request),
            'Accept': 'application/json',
        }

class TokenHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'base/token_history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        csrf_token = get_token(self.request)
        
        try:
            token_history_url = self.request.build_absolute_uri('/api/token/history/')
            client = Client()
            client.cookies[settings.SESSION_COOKIE_NAME] = self.request.session.session_key

            headers = {
                'X-User-ID': str(self.request.user.user_id),
                'X-CSRFToken': csrf_token,
                'Accept': 'application/json',
            }
            
            response = client.get(token_history_url, headers=headers)
            if response.status_code == 200:
                context['token_history'] = response.json()
            else:
                context['error'] = 'Failed to fetch token history'
                
        except Exception as e:
            context['error'] = str(e)
            context['token_history'] = []

        return context