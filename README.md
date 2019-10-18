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

This project is actually the deployment of ItemCatalog App already created.
<br/>[ItemCatalog App](https://github.com/sukhijaa/itemCatalog_p2_udacity)

This includes a full fledged deployment of a running Python App.
From creating a Ubuntu Instance on a cloud, to configuring WSDL on it to serve the app to securing the Instance using Firewall.

## Deployment Details

This app is using Amazon EC2 Ubuntu 16.04 based instance.
<br/> To create a instance, register on EC2 and create a OS Only Linux Instance using Ubuntu 16.04

### Initializing

Its very important to stay updated with all the system libraries you have.
To update and upgrade all system libraries and installed softwares : 
<br/>    * `$ sudo apt-get update`
<br/>    * `$ sudo apt-get upgrade`

### User Management
1. Create user "grader"
    * `$ sudo adduser grader`
2. Give "grader" sudo permission
    * `$ sudo nano /etc/sudoers`
    * Paste **grader ALL=(ALL) NOPASSWD:ALL** into the file, save and exit.
3. Configure the key-based authentication for grader user
    * **In your local machine**
        * Generate encryption key: `$ ssh-keygen ~/.ssh/graderkey`
        * Get content and copy it: `$ cat ~/.ssh/graderkey.pub`
    * **In your instance server**
        * Make directory for your grader ssh: `$ sudo mkdir /home/grader/.ssh`
        * Paste the content you've copied from your local machine into authorized_keys: `$ touch /home/grader/.ssh/authorized_keys`
        * Change the permission and ownership of the key pair:
        `$ sudo chmod 700 /home/grader/.ssh`
        `$ sudo chmod 600 /home/grader/.ssh/authorized_keys`
        `$ sudo chown -R grader:grader /home/grader/.ssh`
    * **Now login the server as user grader** with grader's key in your local machine
    `$ ssh -i ~/.ssh/graderkey grader@18.219.184.137`
    
    
### Configure the Uncomplicated Firewall
1. `$ sudo ufw default deny incoming`
2. `$ sudo ufw default allow outgoing`
3. `$ sudo ufw allow ssh`
4. `$ sudo ufw allow 2222/tcp`
5. `$ sudo ufw allow 80/tcp`
6. `$ sudo ufw allow 123/udp`
7. `$ sudo ufw enable`

### Allow SSH Connection on port 2222
1. `$ sudo vi /etc/ssh/ssdh_config`
2. Add new line `PORT 2222` under existing line `PORT 22`. Save and Quit
3. `$ sudo service ssh restart`


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


