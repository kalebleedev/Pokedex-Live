from django.shortcuts import render
from django.http import Http404
from . import services

# Create your views here.
def home(request):
    try:
        page = max(1, int(request.GET.get("page", 1)))
    except ValueError:
        page = 1


    try:
        data = services.get_pokemon_page(page)
    except services.PokeAPIError:
        return render(request, "pokedex/error.html", status=502)

    return render(request, "pokedex/home.html", {
        "pokemon": data["results"],
        "page": page,
        "has_next": data["has_next"],
        "has_previous": data["has_previous"],
    })

def details(request, name):
    try:
        pokemon = services.get_pokemon(name)

    except services.PokemonNotFound:
        raise Http404("Pokemon not found.")
    
    except services.PokeAPIError:
        return render(request, "pokedex/error.html", status=503)

    return render(request, "pokedex/details.html", {"pokemon": pokemon})