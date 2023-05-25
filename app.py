import pandas as pd 
import streamlit as st
import re

# calisma klasorundeki verileri alalım
df_movies = pd.read_csv(filepath_or_buffer='movies.csv')
df_ratings = pd.read_csv(filepath_or_buffer='ratings.csv')


# streamlit sayfa basligini ayarlayalim
st.set_page_config(page_title='Popular Movies', page_icon='🎬', layout='wide')
#st.title('Popular Movies')
st.markdown("""  # Study of Popular Movies by Year and Genre

Let's see the poular movies in the selected range of years. 

'Movie Lens Latest Small Dataset' is used for this study. 

""")

st.write("This app is developed and published by **Latmos Apps**. [Web](https://latmosapps.com) | [Instagram](https://instagram.com/latmos.apps)")

# veri setimiz uzerinde gerekli islemleri yapalım

df_movies_ratings = df_movies.merge(df_ratings,on='movieId', how ='left')

df_movies_ratings['total_ratings'] = df_movies_ratings.groupby('movieId')['rating'].transform('count')
df_movies_ratings['mean_ratings'] = df_movies_ratings.groupby('movieId')['rating'].transform('mean')

df_movies_ratings.drop_duplicates('movieId', keep='first', inplace=True)


# title içinden yıl bilgisini alacak fonksiyon
# title içinden yıl bilgisini alacak fonksiyon
def scrape_year(title):
    res = re.findall(r'\(.*?\)', title)
    howManyParanthesis = len(res)
    if howManyParanthesis == 0:
        result = 0
    else:
        result = res[howManyParanthesis-1][1:-1]
        if result == '2006–2007':
            result = '2007'
        result = int(result)
    return result

# yıl verisini olusturalım
df_movies_ratings['year'] = df_movies_ratings['title'].apply(scrape_year)



# ayrılmış veri turlerini satırlarda dağıtacak fonksiyon.
def row_genre_seperator(txt):
    row_genres = []
    x = txt.split('|')
    row_genres.append(x)
    # for gnr in txt:
    #     x = gnr.split('|')
    #     row_genres.append(x)
    return row_genres

#  -*-
df_movies_ratings['genres_list']=df_movies_ratings['genres'].apply(row_genre_seperator)


# filtreleme işlemlerini yapacağımız bir sidebar oluşturalım
st.sidebar.header('Filters')
years_range = st.sidebar.slider(label='Years',min_value=1960,max_value=2018,value=(1994,2008))

filtered_movies = df_movies_ratings[(df_movies_ratings['year'] >= years_range[0]) & (df_movies_ratings['year'] <= years_range[1])]
filtered_movies = filtered_movies.sort_values(by=['year'],ascending=False)


# film türlerini title içinden alıp filtrelemede kullanılabilir hale getirelim. 
# - film türlerini bulalım - birleşik - 
genres_list = df_movies['genres'].unique().tolist()

# birleşik film türlerini ayıralım
genres_seperated = []
for genre in genres_list:
    x = genre.split('|')
    genres_seperated.append(x) 


# kümeleştirme (set) yaparak listedeki tekrarlayanları kaldıralım
genres = []
for genre in genres_seperated:
    if type(genre)==list:
        for gnr in genre:
            genres.append(gnr)
    else:
        genres.append(genre)
        
genres_set = set(genres)

# üzerinde çalışabilmek için tekrar listeye çevirelim
genres = list(genres_set)

# alfabeetik olarak sıralayalım
sorted_genres = sorted(genres)


# filtreyi oluşturalım
genres_selected = st.sidebar.multiselect(label='Choose Genres',options=sorted_genres,default=sorted_genres)

def is_selected_filter_in_genres(gnrs):
    selected_genres_set = set(genres_selected)
    gnrs_set = set(gnrs[0])
    if len(selected_genres_set.intersection(gnrs_set)):
        return True
    else:
        return False

filtered_movies_genres = filtered_movies[filtered_movies['genres_list'].apply(is_selected_filter_in_genres)]

filtered_movies_genres_sorted = filtered_movies_genres.sort_values(by=['total_ratings','mean_ratings'],ascending=False)

movies_list = filtered_movies_genres_sorted[['movieId','title','genres','total_ratings','mean_ratings']]

# gosterilecek liste
st.dataframe(data=movies_list)