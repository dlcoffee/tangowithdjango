from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime


# import forms
from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

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
    category_list = Category.objects.order_by('views')[:5 ]
    context_dict = {'categories': category_list}

    # loop through each category and make a category attribute
    # and replace spaces with underscores
    for category in category_list:
        category.url = encode_url(category.name)

    page_list = Page.objects.order_by('views')[:5]
    context_dict['pages'] = page_list

    if request.session.get('last_visit'):
        # The session has a value for the last visit
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).seconds > 5:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        # The get returns None, and the session does not have a value for the last visit.
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

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


def register(request):
    '''
    '''
    
    context = RequestContext(request)

    # boolean value for telling the template whether the registration was
    # succesful or not
    registered = False

    # if it's an HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        # grab information using both UserForm and UserProfileForm
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # if the two forms are valid,
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # hash the password with set_password
            user.set_password(user.password)
            user.save()

            # sort out the UserProfile instance
            # since we need to set the attribtues ourselves, set commit=False
            profile = profile_form.save(commit=False)
            profile.user = user # establish a link between the two models

            if 'picture' in request.FILES['picture']:
                profile.picture = request.FILES['picture']

            profile.save()

            # registration successful
            registered = True

        # invalid forms
        else:
            print user_form.errors, profile_form.errors

    # not an HTTP POST, so render the blank forms
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()


    context_dict = {'user_form': user_form}
    context_dict['profile_form'] = profile_form
    context_dict['registered'] = registered 

    return render_to_response('rango/register.html', context_dict, context)



def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # use django machinery to attempt to see if combo is valid
        user = authenticate(username=username, password=password)

        # if we have a User object and detials are correct
        if user:
            # is the account active?
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/') # status code 302 (redirect)
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            # bad credentials
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        # most likely an HTTP GET
        return render_to_response('rango/login.html', {}, context)


@login_required
def user_logout(request):
    # since we require login already, just log out
    logout(request)

    return HttpResponseRedirect('/rango/')


def about(request):
    context = RequestContext(request)
   
    # check if there is a 'visits' serverside cookie or not
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    return render_to_response('rango/about.html', {'visits': count}, context)


@login_required
def restricted(request):
    # if we're not logged in, we are redirected to a login page
    context = RequestContext(request)

    
    return render_to_response('rango/restricted.html', {}, context)
    #return HttpResponse("Since you're logged in, you can see this text!")
