from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect

from markdown import markdown
from . import util

import random

# View to display encyclopedia entries
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# View to display specified encyclopedia entry
def entry(request, name):
    # Check if specified encyclopedia entry exist
    content = util.get_entry(name)

    if content is None:
        return render(request, "encyclopedia/error.html", {
        "error": content,
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "name": name,
            "entry": markdown(content)
        })
    
# View to search entry
def search(request):
    search_value = request.GET.get("q")
    search_results = list()

    # If query matches the name of an encyclopedia entry
    if util.get_entry(search_value):
        return entry(request, search_value)
    else:
        # Search results page that displays a list of all encyclopedia entries
        # that have the query as a substring
        for x in util.list_entries():
            if search_value.lower() in x.lower():
                search_results.append(x)

        # If contain search results
        if search_results:
            return render(request, "encyclopedia/search.html", {
                "search_results": search_results,
                "name": search_value
            })
        
    return render(request, "encyclopedia/error.html", {
        "error": None,
    })  

# View to create new page
def add(request):
    # Check if method is POST
    if request.method == "POST":
        
        # Take in the data the user submitted and save it as form
        form = NewPageForm(request.POST)

        # Check if title and content data is valid
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            # Check if entry is in the list
            if util.get_entry(title) is None:
                # Add the new entry to our list of entries
                util.save_entry(title, content)

                # Redirect user to the new added entry page
                return HttpResponseRedirect(f"wiki/{title}")
            else:
                return render(request, "encyclopedia/error.html", {
                    "error": "exist"
                })

    return render(request, "encyclopedia/add.html", {
        "form": NewPageForm()
    })

# Class which has new entry form content
class NewPageForm(forms.Form):
    title = forms.CharField(label="New Page Title",
        min_length=1,
        max_length=60)
    content = forms.CharField(label="Markdown Content",
        min_length=1,
        max_length=5000, 
        widget=forms.Textarea)
            
# View to edit entry
def edit(request, name):
    # Check if method is POST
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = EditPageForm(request.POST)

        # Check if content data is valid
        if form.is_valid():
            content = form.cleaned_data["content"]

            # Edit entry if it already exists
            if util.get_entry(name) is not None:
                try:
                    # Update the entry to our list of entries
                    util.save_entry(name, content)
                except:
                    return render(request, "encyclopedia/error.html", {
                        "error": "error"
                    })
                # Redirect user to the updated entry page
                return render(request, "encyclopedia/entry.html", {
                    "name": name,
                    "entry": markdown(content)
                })
            else:
                return render(request, "encyclopedia/error.html", {
                    "error": None
                })
        else:
            return render(request, "encyclopedia/error.html", {
                "error": "error"
            })

    # GET request
    if util.get_entry(name) is not None:
        content = util.get_entry(name)
        return render(request, "encyclopedia/edit.html", {
            "form": EditPageForm(initial={"content":content}),
            "name": name
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error": None
        })

# Class which has edit entry form content
class EditPageForm(forms.Form):
    content = forms.CharField(label="Markdown Content", 
        min_length=1,
        max_length=5000,
        widget=forms.Textarea)
    
# Class that take display a random entry
def random_entry(request):
    return entry(request, random.choice(util.list_entries()))