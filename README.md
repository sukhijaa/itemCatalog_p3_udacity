# ItemCatalog

This application simply focuses on creating a Supermarket Dictionary which will list the items present in the supermarket into categories while having various features of Adding/Removing/Modifying the details about any item or category. 
User can add desciption to the item or category so user can understand the item better.

## Live Demo

http://ec2-18-219-184-137.us-east-2.compute.amazonaws.com/

## Connect to EC2 Instance

Public IP : 18.219.184.137 <br/>
Public DNS : ec2-18-219-184-137.us-east-2.compute.amazonaws.com
<br/>SSH Port: Default Port i.e. 22

## About the Project

UI for the project is written using ReactJS with Redux with Webpack used for bundling of JS and CSS code
ItemCatalog is a single-page web-app which performs all tasks based on CRUD operations implemented in Python server.
This app lets you Login using Google or manually using Email and Password.
For both cases, if user is not already present in system, a new entry is created.


On Server side, we have various CRUD operations in s RESTful manner.  

### Allowed URIs:
All the GET requests are listed down here.
Since UI is a Reach Single Page App, there will be no server calls while you are moving around in the website.
But these below are the paths which will load the website for you if entered manually.

```
GET /item/new
GET /category/new
GET /category/:categoryID/edit
GET /item/:itemID/edit
GET /category/:categoryID/delete
GET /item/:itemID/delete
GET /getAllCategories
GET /
GET /items
GET /categories
GET /login
```

This app uses POST for all modify and delete operations since each of these operations need authentication before being applied into the DB.
If somehow your session expires while you were working, server sends a special 444 code which will redirect you to login screen again.
POST requests supported are:
```
POST /loginUser/:provider -> Allowed values : 'google', 'userInput'
POST /profile/update -> To update Name and Password of user
POST /item/new
POST /category/new
POST /item/:itemID/edit
POST /category/:categoryID/edit
POST /item/:itemID/delete
POST /category/:categoryID/delete
```

Exposed API to get list of all Categories and their items in System: 
```
/getAllCategories
```

### DB Details
There are 3 tables in the Postgres DB

```
categories: [(id INTEGER PK), (name STRING 60 NOT_NULL), (description STRING 250)]
catalog_item : [(name STRING 80), (id INTEGER PK), (description STRING 250), (categoryId INTEGER ForeignKey[Categories.id])]
user: [(id INTEGER PK), (username STRING 32 INDEX), (picture STRING), (email STRING), (password_hash STRING 64)]
```

categories table holds all the categories created in the system
catalog_item holds all the items defined in the system with a Foreign Key relation to Category this item belongs to
user table holds list of recognized users

## Deployment Details

This app is using Amazon EC2 Ubuntu 16.04 based instance.

### Prepare to deploy Item Catalog Project
1. Install Apache and mod_wsgi
    * `$ sudo apt-get install apache2`
    * `$ sudo apt-get install libapache2-mod-wsgi-py3`
    * `$ sudo service apache2 restart`
2. Install Python and Git
    * `$ sudo apt-get install git`
    * `$ sudo apt-get install python3`
3. Clone Item Catalog App from Github
    * `$ sudo mkdir /var/www/itemcatalog`
    * Move into itemcatalog directory and clone the app repository:
        * `$ cd /var/www/itemcatalog`
        * `$ git clone https://github.com/sukhijaa/itemCatalog_p3_udacity.git`
4. Install and configure the virtual environment
    * Install pip: `$ sudo apt-get install python3-pip`
    * Install virtualenv: `$ sudo pip3 install virtualenv`
    * Rename virtualenv: `$ sudo virtualenv venv`
    * Activate virtual environment: `$ source venv/bin/activate`
    * Install all modules for this project,  `$ pip3 install -r requirements.txt`
    * Restart apache: `$ sudo service apache2 restart`
5. Install PostgreSQL and Initialize DB
    * Install PostgreSQL: `sudo apt-get install postrgresql postgresql-contrib`
    * Setup database: `$ python3 catalogDBSetup.py`
    * Initialize DB Tables with Data: `$ python3 itemCatalogFiller.py`
6. Configure and Enable a new virtual host
    * Move file itemCatalog.conf to /etc/apache2/sites-available
    * Enable this new virtual host: `$ sudo a2ensite itemcatalog.conf`
7. Restart Apache server
    * `$ sudo service apache2 restart`


## Authors

Abhishek Sukhija - abhisukhija@ymail.com

---

## References and Resources
* [SSH Essentials: Working with SSH Servers, Clients, and Keys](https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys)
* [README.md from MomokoXu](https://github.com/MomokoXu/Project-Linux-Server-Configuration/blob/master/README.md)
* [askubuntu](https://askubuntu.com/questions)
* [Stackoverflow](https://stackoverflow.com/)
* [Udacity Forum](https://discussions.udacity.com/)
## Copyright
This is a project for practicing skills in databses and backend courses not for any business use. Some templates and file description are used from [Udacity FSND program](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004). Please contact me if you think it violates your rights.


