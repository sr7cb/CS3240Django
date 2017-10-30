from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

from .forms import RenewBookForm

import re
'''
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
# Avoid shadowing the login() view below.
from django.contrib.auth import login as auth_login
from django.contrib.sites.models import get_current_site, Site
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from remember_me.forms import AuthenticationRememberMeForm
'''

def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.
    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits}, ) # num_visits appended
# Create your views here.

class BookListView(generic.ListView):
    model = Book
    paginate_by = 1

class BookDetailView(generic.DetailView):
    model = Book

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

'''
@csrf_protect
@never_cache
def remember_me_login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationRememberMeForm):
          
    """
    Based on login view cribbed from
    https://github.com/django/django/blob/1.2.7/django/contrib/auth/views.py#L25
    
    Displays the login form with a remember me checkbox and handles the
    login action.
    
    The authentication_form parameter has been changed from
    ``django.contrib.auth.forms.AuthenticationForm`` to
    ``remember_me.forms.AuthenticationRememberMeForm``.  To change this, pass a
    different form class as the ``authentication_form`` parameter.
    
    """
    
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    
    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            # Light security check -- make sure redirect_to isn't garbage.
            if not redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
                
            # Heavier security check -- redirects to http://example.com should
            # not be allowed, but things like /view/?param=http://example.com
            # should be allowed. This regex checks if there is a '//' *before* a
            # question mark.
            elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL
                    
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
                
            # Okay, security checks complete. Log the user in.
            auth_login(request, form.get_user())
            
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
                
            return HttpResponseRedirect(redirect_to)
            
    else:
        form = authentication_form(request)
        
    request.session.set_test_cookie()
    
    current_site = get_current_site(request)
    
    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }, context_instance=RequestContext(request))
'''
