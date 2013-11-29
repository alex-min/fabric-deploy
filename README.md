fabric-deploy
=============

Deployment script built with python-fabric for symfony2

## Commands:
 
 - deploy:
    Deploy the application to the remote server
    - Arguments:
     - git : git repository url
     - app : application name

 - ls:
   List all the versions stored on the server
   - Arguments:
     - app : application name

 - rollback:
   Change the version in production
   - Arguments:
     - app : application name
     - version : version number (gathered with the ls command)
   