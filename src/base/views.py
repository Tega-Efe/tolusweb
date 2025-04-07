from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.test import Client
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
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


# class Waterflow(ListView):
#     model = Waterflow
#     context_object_name = 'waterflows'
#     template_name = 'base/waterflows.html'
from django.middleware.csrf import get_token

    
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
            # Change the API endpoint to specifically target the user flow data endpoint
            api_url = self.request.build_absolute_uri('/api/user-flow-data/')

            # Set up session authentication
            client.cookies[settings.SESSION_COOKIE_NAME] = self.request.session.session_key

            headers = {
                'X-User-ID': str(self.request.user.user_id),
                'X-CSRFToken': csrf_token,
                'Accept': 'application/json',
            }
            
            response = client.get(api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nUser: {self.request.user.username}")
                print(f"User ID: {self.request.user.user_id}")
                print("\nAPI Response Data:")
                for i in range(1, 4):
                    distribution = data.get(f'distribution{i}', {})
                    if distribution:
                        print(f"\nDistribution {i}:")
                        print(f"Flow Rate: {distribution.get('flowRate')}")
                        print(f"Volume: {distribution.get('volume')}")
                        print(f"Created: {distribution.get('created')}")

                context['api_data'] = data
                context.update(data)
            else:
                error_message = f"API Error: Failed to fetch data (Status: {response.status_code})"
                print(f"\n{error_message}")
                print(f"Response content: {response.content}")
                context['error'] = error_message
                context['api_data'] = None
                
        except Exception as e:
            print(f"\nException occurred: {str(e)}")
            context['error'] = str(e)
            context['api_data'] = None

        return context

    def post(self, request, *args, **kwargs):
        try:
            csrf_token = get_token(request)
            api_url = request.build_absolute_uri('/api/flow-data/')

            # Login the test client with the current user's session
            client.cookies[settings.SESSION_COOKIE_NAME] = request.session.session_key
            
            headers = {
                'X-User-ID': str(request.user.user_id),
                'X-CSRFToken': csrf_token,
                'Content-Type': 'application/json',
            }

            # Format data to match API expectations
            flow_data = {
                'sensor_id': 'default'
            }
            
            # Add flow data for each distribution
            for i in range(1, 4):
                flow_data[f'flowRate{i}'] = request.POST.get(f'flowRate{i}')
                flow_data[f'volume{i}'] = request.POST.get(f'volume{i}')
            
            response = client.post(
                api_url, 
                data=json.dumps(flow_data),  # Serialize to JSON
                headers=headers
            )

            if response.status_code in [200, 201]:
                return JsonResponse({'message': 'Data saved successfully'})
            else:
                return JsonResponse({
                    'error': 'Failed to save data',
                    'details': response.json()
                }, status=400)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)