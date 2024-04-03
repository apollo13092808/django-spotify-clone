import os
import re

import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from dotenv import load_dotenv

load_dotenv()


# Create your views here.
def get_top_artists():
    url = 'https://spotify-scraper.p.rapidapi.com/v1/chart/artists/top'

    headers = {
        'X-RapidAPI-Key': os.getenv(key='RAPID_API_KEY'),
        'X-RapidAPI-Host': os.getenv(key='RAPID_API_HOST')
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    artists_info = []
    if 'artists' in response_data:
        for artist in response_data['artists']:
            name = artist.get('name', 'Unknown')
            avatar_url = artist.get('visuals', {}).get('avatar', [{}])[0].get('url', 'No URL')
            artist_id = artist.get('id', 'No ID')
            artists_info.append((name, avatar_url, artist_id))

    return artists_info


def get_top_tracks():
    url = 'https://spotify-scraper.p.rapidapi.com/v1/chart/tracks/top'

    headers = {
        'X-RapidAPI-Key': os.getenv(key='RAPID_API_KEY'),
        'X-RapidAPI-Host': os.getenv(key='RAPID_API_HOST')
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    track_details = []
    if 'tracks' in response_data:
        shortened_data = response_data['tracks'][:18]
        for track in shortened_data:
            track_id = track['id']
            track_name = track['name']
            artist_name = track['artists'][0]['name'] if track['artists'] else None
            cover_url = track['album']['cover'][0]['url'] if track['album']['cover'] else None

            track_details.append({
                'id': track_id,
                'name': track_name,
                'artist': artist_name,
                'cover_url': cover_url
            })
    else:
        print('Track not found')

    return track_details


def get_audio_details(query):
    url = 'https://spotify-scraper.p.rapidapi.com/v1/track/download'

    headers = {
        'X-RapidAPI-Key': os.getenv(key='RAPID_API_KEY'),
        'X-RapidAPI-Host': os.getenv(key='RAPID_API_HOST')
    }

    query_string = {'track': query}

    response = requests.get(url, headers=headers, params=query_string)

    audio_details = []
    if response.status_code == 200:
        response_data = response.json()
        if 'youtubeVideo' in response_data and 'audio' in response_data['youtubeVideo']:
            audio_list = response_data['youtubeVideo']['audio']
            if audio_list:
                first_audio_url = audio_list[0]['url']
                duration_text = audio_list[0]['durationText']
                audio_details.append(first_audio_url)
                audio_details.append(duration_text)
            else:
                print('No audio data available')
        else:
            print('No `youtubeVideo` or `audio` key found')
    else:
        print('Failed to fetch data')

    return audio_details


def get_track_image(track_id, track_name):
    url = 'https://open.spotify.com/track/' + track_id
    r = requests.get(url)
    soup = BeautifulSoup(r.content)
    image_links_html = soup.find(name='img', attrs={'alt': track_name})
    if image_links_html:
        image_links = image_links_html['srcset']
    else:
        image_links = ''

    match = re.search(pattern=r'https:\/\/i\.scdn\.co\/image\/[a-zA-Z0-9]+ 640w', string=image_links)

    if match:
        url_640w = match.group().rstrip(' 640w')
    else:
        url_640w = ''

    return url_640w


@login_required(login_url='login')
def index(request):
    artists_info = get_top_artists()
    top_track_list = get_top_tracks()

    # divide the list into three parts
    first_six_tracks = top_track_list[:6]
    second_six_tracks = top_track_list[6:12]
    third_six_tracks = top_track_list[12:18]

    print(top_track_list)
    context = {
        'artists_info': artists_info,
        'first_six_tracks': first_six_tracks,
        'second_six_tracks': second_six_tracks,
        'third_six_tracks': third_six_tracks,
    }
    return render(request=request, template_name='music/index.html', context=context)


def sign_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request=request, user=user)
            return redirect(to='/')
        else:
            messages.info(request=request, message='Invalid credentials')
            return redirect(to='login')
    return render(request=request, template_name='music/login.html')


def sign_up(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request=request, message='Email already exists')
                return redirect(to='register')
            elif User.objects.filter(username=username).exists():
                messages.info(request=request, message='Username already exists')
                return redirect(to='register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                login(request=request, user=user)
                return redirect(to='/')
        else:
            messages.info(request=request, message='Passwords did not match')
            return redirect(to='register')
    return render(request=request, template_name='music/register.html')


@login_required(login_url='login')
def sign_out(request):
    logout(request=request)
    return redirect(to='login')


def music(request, pk):
    url = 'https://spotify-scraper.p.rapidapi.com/v1/track/download'

    headers = {
        'X-RapidAPI-Key': os.getenv(key='RAPID_API_KEY'),
        'X-RapidAPI-Host': os.getenv(key='RAPID_API_HOST')
    }

    track_id = pk
    query_string = {'trackId': track_id}

    response = requests.get(url, headers=headers, params=query_string)

    if response.status_code == 200:
        response_data = response.json()

        track_name = response_data.get('name')
        artists_list = response_data.get('artists', [])
        first_artist_name = artists_list[0].get('name') if artists_list else "No artist found"

        audio_details_query = track_name + first_artist_name
        audio_details = get_audio_details(audio_details_query)
        audio_url = audio_details[0]
        duration_text = audio_details[1]

        track_image = get_track_image(track_id, track_name)

        context = {
            'track_name': track_name,
            'artist_name': first_artist_name,
            'audio_url': audio_url,
            'duration_text': duration_text,
            'track_image': track_image,
        }
        return render(request=request, template_name='music/music.html', context=context)

    return render(request=request, template_name='music/music.html')


def profile(request, pk):
    url = 'https://spotify-scraper.p.rapidapi.com/v1/track/download'

    headers = {
        'X-RapidAPI-Key': os.getenv(key='RAPID_API_KEY'),
        'X-RapidAPI-Host': os.getenv(key='RAPID_API_HOST')
    }

    artist_id = pk
    query_string = {'artistId': artist_id}

    response = requests.get(url, headers=headers, params=query_string)

    if response.status_code == 200:
        response_data = response.json()

        name = response_data['name']
        monthly_listeners = response_data['stats']['monthlyListeners']
        header_url = response_data['visuals']['header'][0]['url']

        top_tracks = []

        for track in response_data['discography']['topTracks']:
            track_id = str(track['id'])
            track_name = str(track['name'])
            if get_track_image(track_id, track_name):
                track_image = get_track_image(track_id, track_name)
            else:
                track_image = 'https://imgv3.fotor.com/images/blog-richtext-image/music-of-the-spheres-album-cover.jpg'

            track_info = {
                'id': track['id'],
                'name': track['name'],
                'durationText': track['durationText'],
                'playCount': track['playCount'],
                'track_image': track_image
            }

            top_tracks.append(track_info)

        context = {
            'name': name,
            'monthlyListeners': monthly_listeners,
            'headerUrl': header_url,
            'topTracks': top_tracks,
        }
        return render(request=request, template_name='music/profile.html', context=context)

    return render(request=request, template_name='music/profile.html')


def search(request):
    if request.method == 'POST':
        url = 'https://spotify-scraper.p.rapidapi.com/v1/search'

        headers = {
            'X-RapidAPI-Key': os.getenv(key='RAPID_API_KEY'),
            'X-RapidAPI-Host': os.getenv(key='RAPID_API_HOST')
        }

        search_query = request.POST['search_query']
        query_string = {'term': search_query, 'type': 'track'}

        response = requests.get(url, headers=headers, params=query_string)

        track_list = []
        search_results_count = 0

        if response.status_code == 200:
            response_data = response.json()

            search_results_count = response_data['tracks']['totalCount']
            tracks = response_data['tracks']['items']

            for track in tracks:
                track_name = track['name']
                artist_name = track['artists'][0]['name']
                duration = track['durationText']
                track_id = track['id']

                if get_track_image(track_id, track_name):
                    track_img = get_track_image(track_id, track_name)
                else:
                    img_url = 'https://imgv3.fotor.com/images/blog-richtext-image/music-of-the-spheres-album-cover.jpg'
                    track_img = img_url

                track_list.append({
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'duration': duration,
                    'track_id': track_id,
                    'track_image': track_img,
                })

        context = {
            'search_results_count': search_results_count,
            'track_list': track_list,
        }
        return render(request=request, template_name='music/search.html', context=context)

    return render(request=request, template_name='music/search.html')
