from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse

# import forms
from rango.forms import CategoryForm, PageForm

# import models (haha)
from rango.models import Category
from rango.models import Page

# some helper functions
def encode_url(url):
    return url.replace(' ', '_')


def decode_url(url):
    return url.replace('_', ' ')


# each function is a view
def index(request):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    # Query for categories - add the list to our context dictionary.
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}

    # loop through each category and make a category attribute
    # and replace spaces with underscores
    for category in category_list:
        category.url = encode_url(category.name)

    # Render the response and return to the client.
    return render_to_response('rango/index.html', context_dict, context)


def category(request, category_name_url):
    # Obtain the context from the HTTP request.
    context = RequestContext(request)

    # replace underscores with spaces
    category_name = category_name_url.replace('_', ' ')

    context_dict = {'category_name': category_name}
    context_dict['category_name_url'] = category_name_url

    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(name=category_name)

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render_to_response('rango/category.html', context_dict, context)




def add_category(request):
    '''
    handles three different scenarios:
        - showing a new, blank form for adding a category
        - saving form data provided by the user to the associated model, and
          rendering the homepage
        - if there are errors, redisplay redisplay the form with error messages
    '''
    # get the context from request
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            # save the category in the database
            form.save(commit=True)

            # now call the index() view
            return index(request)
        else:
            # the supplied form contains errors
            print form.errors

    else:
        # display the form to enter details
        form = CategoryForm()


    # bad form or form details, or no form supplied
    return render_to_response('rango/add_category.html', {'form': form}, context)


def add_page(request, category_name_url):
    '''
    '''

    context = RequestContext(request)
    category_name = decode_url(category_name_url)
    
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            # not all fields are automatically populated!
            page = form.save(commit=False)

            # retrieve the associated category
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # go back and render the add category form as a way of 
                # saying the category DNE
                return render_to_response('rango/add_category.html', {}, context)

            page.views = 0
            page.save()

            # display teh category 
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response( 'rango/add_page.html', 
            {'category_name_url': category_name_url,
             'category_name': category_name, 'form': form}, context)




def about(request):
    context = RequestContext(request)
    return render_to_response('rango/about.html', context)



