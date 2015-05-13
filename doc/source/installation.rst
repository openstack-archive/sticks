#######################################
Sticks installation and configuration
#######################################


Install from source
===================

There is no release of Sticks as of now, the installation can be done from
the git repository.

Retrieve and install Sticks :

::

    git clone git://git.openstack.org/stackforge/sticks
    cd sticks
    python setup.py install

This procedure installs the ``sticks`` python library and a few
executables:

* ``sticks-api``: API service

Install a sample configuration file :

::

    mkdir /etc/sticks
    cp etc/sticks/sticks.conf.sample /etc/sticks/sticks.conf

Configure Sticks
==================

Edit :file:`/etc/sticks/sticks.conf` to configure Sticks.

The following shows the basic configuration items:

.. code-block:: ini

    [DEFAULT]
    verbose = True
    log_dir = /var/log/sticks

    rabbit_host = RABBIT_HOST
    rabbit_userid = openstack
    rabbit_password = RABBIT_PASSWORD

    # Class of tracking plugin, ie redmine, trac, etc.
    #tracking_plugin=

    # Name of sticks role (default: sticks)
    #sticks_role_name=sticks

    [auth]
    username = sticks
    password = STICKS_PASSWORD
    tenant = service
    region = RegionOne
    url = http://localhost:5000/v2.0

    [keystone_authtoken]
    username = sticks
    password = STICKS_PASSWORD
    project_name = service
    region = RegionOne
    auth_url = http://localhost:5000/v2.0
    auth_plugin = password

    [database]
    connection = mysql://sticks:STICKS_DBPASS@localhost/sticks

    DEFAULT]

Setup the database and storage backend
======================================

MySQL/MariaDB is the recommended database engine. To setup the database, use
the ``mysql`` client:

::

    mysql -uroot -p << EOF
    CREATE DATABASE sticks;
    GRANT ALL PRIVILEGES ON sticks.* TO 'sticks'@'localhost' IDENTIFIED BY 'STICKS_DBPASS';
    EOF

Run the database synchronisation scripts:

::

    sticks-dbsync upgrade

Init the storage backend:

::

    sticks-storage-init

Setup Keystone
==============

Sticks uses Keystone for authentication.

To integrate Sticks to Keystone, run the following commands (as OpenStack
administrator):

::

    keystone user-create --name sticks --pass STICKS_PASS
    keystone user-role-add --user sticks --role admin --tenant service

Create the ``Helpdesk`` service and its endpoints:

::

    keystone service-create --name Sticks --type helpdesk
    keystone endpoint-create --service-id SECURITY_SERVICE_ID \
        --publicurl http://localhost:8888 \
        --adminurl http://localhost:8888 \
        --internalurl http://localhost:8888

Start Sticks
==============

Start the API service :

::

    sticks-api --config-file /etc/sticks/sticks.conf
