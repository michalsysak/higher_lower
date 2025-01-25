
# Higher Lower - movies: README
## Opis aplikacji:
Celem projektu było stworzenie gry na bazie popularnej gry przeglądarkowej "The Higher Lower Game" 
która polega na tym że użytkownik odgaduje który z dwóch filmów jest bardziej popularny aktualnie. 

## Funkcje aplikacji:
* Użytkownik zgaduje czy jeden film jest bardziej popularny od drugiego
* Uzytkownicy rywalizują w ilości odgadniętych tytułów w tablicy wyników (**leaderboard**)
* Aplikacja posiada **obsługę sesji** (wielu użytkowników może grać jednocześnie swoje gry)
* Aplikacja pobiera swoje dane z **TMDB** - dane są aktualne

## Technologie:
* **Backend**: Flask(Python)
* **Redis**: Obsługa sesji i przetrzymywanie danych
* **API**: Pobieranie danych o filmach z TMDB
* **Frontend**: HTML z osadzonym Pythonem
* **Docker**: Uruchamianie projektu w kontenerze

## Uruchomienie używając docker:
Kopiujemy repozytorium</br></br>
W katalogu głównym projektu tworzymy plik "**.env**" w którym mamy: <br /><br />

FLASK_PORT=5000<br />
REDIS_PORT=6379<br />
REDIS_HOST=redis<br />
TMDB_API_TOKEN=**[Twój API token z TMDB]**<br /><br />

(Porty **FLASK_PORT** i **REDIS_PORT** można zmieniać według potrzeb)</br></br>
W miejscu **[Twój API token z TMDB]** wklejamy API key ze strony TMDB</br>
https://developer.themoviedb.org/reference/intro/getting-started</br>
Na stronie wybieramy "**Get API Key**" i postępujemy dalej z instrukcjami </br></br>


W katalogu głównym projektu używamy poleceń:</br></br>

docker-compose build</br>
docker-compose up</br></br>

Uruchomioną aplikacje zobaczymy domyślnie na **localhost:5000**</br>