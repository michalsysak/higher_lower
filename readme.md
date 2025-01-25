
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

## Uruchomienie:
* Trzeba posiadać docker
docker build -t higher_lower_movie . 

potrzeba dockera żeby uruchomić 

stawiasz sobie baze redisa :
docker run -p 6379:6379 -it redis/redis-stack:latest

instalujesz pozycje z requirements.txt


użyj sobie keygen i stwórz FLASK_SECRET_KEY
wklejasz FLASK_SECRET_KEY do .env 

pliki dockerowe które są w projekcie to work in progress jak coś

docker-compose build

docker-compose up