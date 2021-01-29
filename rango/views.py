from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    return render(request, 'rango/index.html', context=context_dict)
    
def about(request):
    context_dict = {'boldmessage': 'This tutorial has been put together by Forbes.'}
    return render(request, 'rango/about.html', context=context_dict)

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