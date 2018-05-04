# JustDoist
**ToDoist add-on for ones, who just do it.**  

justdoist.com 

**To run JustDoist locally**
```bash
python manage.py makemigrations main
python manage.py migrate
python runserver localhost:8181
```

**Production mode**  
1. Install Docker and Docker-compose (apt users probably want to install Docker-compose directly from github)
2. Run Docker-compose in the porject directory
```bash 
cd JustDoist
sudo docker-compose up
```
3. Server will be listening on localhost:8181.
3.1 Note: by default, only `justdoist.com` domain is allowed in the production mode. 
So you won't be able to access any page without adding `*` 
(that may cause an [XSS-attack](https://en.wikipedia.org/wiki/Cross-site_scripting))
 to `ALLOWED_HOSTS` in `settings.py`. 
 