# JustDoist
**ToDoist add-on for ones, who just do it.**  

justdoist.com 

**To run JustDoist locally**
1. Create virtualenv with python 3.6 (I'll use virtualenvwrapper)
```bash
mkvirtualenv justdoist --python=python3.6
```
2. Activate the environment
```bash
workon justdoist
```
3. Install requirements
```bash
pip install -r requirements.txt
```
4. Run dev server
```bash
python manage.py makemigrations main
python manage.py migrate
python runserver localhost:8181
```
5. Congrats! Now you can access the site on http://localhost:8181.


**Production mode**  
1. Install Docker and Docker-compose (apt users probably want to install Docker-compose directly from github)
2. Run Docker-compose in the porject directory
```bash 
cd JustDoist
sudo docker-compose up
```
3. Server will be listening on localhost:8181.

Note: by default, only `justdoist.com` domain is allowed in the production mode. 
So you won't be able to access any page without adding `*` 
 to `ALLOWED_HOSTS` (that may cause an [XSS-attack](https://en.wikipedia.org/wiki/Cross-site_scripting))
 in `settings.py`. 
 
