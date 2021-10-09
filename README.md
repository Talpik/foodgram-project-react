# Author of `Foodgram` project is Vladimir.Talpa - it's final work in Yandex.Praktikum for Python Backend Course.
The Foodgram project allows users to post recipes, add recipes to favorites
and shopping lists, follow other users, and download a grocery list.
Please, test the service at:
```
http://62.84.117.174/
```
```
login: admin@admin.com
pass: 0228
```
### Launching a local project
- Clone the repository with the command:
```
git clone https://github.com/Talpik/foodgram-project-react.git
```
- Change to the directory with the command:
```
cd foodgram-project-react/backend/
``` 
- Run the command to start the container:
```
sudo docker-compose up -d
``` 
- Perform migrations:
```
sudo docker-compose exec web python manage.py migrate --noinput
```
- Perform ingredients upload fixtures data:
```
sudo docker-compose exec web python manage.py load_ingredients

```
- Command for collecting statics:
```
sudo docker-compose exec web python manage.py collectstatic --no-input
```
- Create superuser:
```
sudo docker-compose exec web python manage.py createsuperuser
```
- Go to the project page in browser:
```
https://127.0.0.1:80 or https://127.0.0.1:80/admin
```
### Stack technology
- Python 3
- Django
- Docker, docker-compose
- Postgresql
- Nginx
