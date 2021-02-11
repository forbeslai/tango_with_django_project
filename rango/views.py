from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from django.shortcuts import redirect
from django.urls import reverse
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    return render(request, 'rango/index.html', context=context_dict)
    
def about(request):
    # prints out whether method is GET or POST
    print(request.method)
    # prints out user name, if no one is logged then prints 'AnonymousUser'
    print(request.user)
    return render(request, 'rango/about.html', {})

def show_category(request, category_name_slug):
    # pass this context dictionary to the template render
    context_dict = {}
    
    try:
        #find slug with given name
        #.get() returns one model instance or raises DoesNotExist exception
        category = Category.objects.get(slug=category_name_slug)
        
        #Retrieve all associated pages
        #filter() returns empty list or list of page objects
        pages = Page.objects.filter(category=category)
        
        #Adds results list to template context under name pages
        context_dict['pages'] = pages
        #Add category object from db to context dict
        #Use in template to verify category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        #didn't find specified category
        #do nothing, let template display "no category" message
        context_dict['category'] = None
        context_dict['pages'] = None
    
    #render response and return to client
    return render(request, 'rango/category.html', context=context_dict)
    
def add_category(request):
    form = CategoryForm()
    
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        
        # valid form provided?
        if form.is_valid():
            # Save new category to db
            form.save(commit=True)
            #redirect to index vied
            return redirect('/rango/')
        else:
            # form contained errors, print to terminal
            print(form.errors)
    # render form with error messages if any
    return render(request, 'rango/add_category.html', {'form': form})
    
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    # cannot add page to Category that does not exists
    if category is None:
        return redirect('/rango/')
        
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
            
        else:
            print(form.errors)
        
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    # boolean value for whether registration was successful
    # initial False, change to True when registration succeds
    registered = False
    
    # If HTTP POST, process form data
    if request.method == 'POST':
        # grab info from raw form info
        # use both UserForm and UserProfileForm
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        # if both forms valid
        if user_form.is_valid() and profile_form.is_valid():
            # save user's form data to db
            user = user_form.save()
            
            # hash pw with set_password method, then update user object
            user.set_password(user.password)
            user.save()
            
            # sort out UserProfile instance
            # set commit=False to delay saving model
            # until ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user= user
            
            # get profile pic from input form if user provided
            # put in UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
                
            # save UserProfile model instance
            profile.save()
            
            # update variable to indicate template reg successful
            registered = True
        else:
            # invalid form/forms - mistakes?
            # print problems to terminal
            print(user_form.errors, profile_form.errors)
    else:
        # Not HTTP POST, render using two ModelForm instances
        # blank forms ready for user input
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    # render template by context
    return render(request,
                  'rango/register.html',
                  context = {'user_form': user_form,
                             'profile_form': profile_form,
                             'registered': registered})