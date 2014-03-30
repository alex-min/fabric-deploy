from fabric.api import *

# the user to use for the remote commands
#env.user = 'appuser'
# the servers where the commands are executed
#env.hosts = ['server1.example.com', 'server2.example.com']
import time
import datetime
from fabric.colors import green, blue, red
import json

def deploy(app, git):
	ts = int(time.time())

	curdir = '/var/www/%s/versions/%s' % (app, ts)
	run('mkdir -p %s' % (curdir))

	run('git clone %s %s' % (git, curdir))
	run('echo -n FAILED > /var/www/%s/versions/%s/.deploy-status' % (app, ts))
	#run('cp %s/app/config/parameters_prod.yml %s/app/config/parameters.yml' % (curdir, curdir))


	nodeploy = run('test -f /var/www/%s/versions/%s/deploy.sh || echo "nodeploy"' % (app, ts))
	if nodeploy != 'nodeploy':
		print blue('Executing the deploy.sh on the repository')
		run('chmod +x /var/www/%s/versions/%s/deploy.sh' % (app, ts))
		run('cd /var/www/%s/versions/%s && ./deploy.sh' % (app,ts))
	else:
		print red("No deploy.sh found in the repository, assuming that the application is deployed properly")
	run('ln -s /var/www/%s/versions/%s /var/www/%s/_current' % (app,ts, app))
	run('mv -T /var/www/%s/_current /var/www/%s/current' % (app, app))

	run('echo -n SUCCESS > /var/www/%s/versions/%s/.deploy-status' % (app, ts))
	print green('Application %s deployed properly' % (app))

def getStatusList (app, versions):
		statusList = []
		for version in versions:
			buildStatus = run('cat /var/www/%s/versions/%s/.deploy-status 2> /dev/null || true' % (app, int(version)))
			if buildStatus == '':
				buildStatus = 'UNKNOWN';
			buildStatus = buildStatus.replace("\n","").replace("\r", '').replace(' ', '')
			statusList.append(buildStatus)	
		return statusList;

def clean(app):
	versions = run('ls /var/www/%s/versions/ | awk "{print $1}"' % (app))

	current = run('perl -le \'print readlink(\"/var/www/%s/current\")\'' % (app))
	curversion = int(current.split('/')[-1]);
	
	versionList = versions.split('\n');

	statusList = getStatusList(app, versionList)
	
	deletedVersion = 0
	i = 0
	for version in versionList:
		v = int(version)
		if curversion != v:
			if statusList[i] == 'UNKNOWN' or statusList[i] == 'FAILED':
				run('rm -rf /var/www/%s/versions/%s' % (app, v))
				deletedVersion = deletedVersion + 1
		i = i + 1
	print green('%s version deleted' % deletedVersion)


def ls(app):
		versions = run('ls /var/www/%s/versions/ | awk "{print $1}"' % (app))
		current = run('perl -le \'print readlink(\"/var/www/%s/current\")\'' % (app))
		curversion = int(current.split('/')[-1]);


		i = 0
		versionList = versions.split('\n');
		statusList = getStatusList(app, versionList)

		print "\n\n";
		for version in versionList:
			
			dateAssociated = datetime.datetime.fromtimestamp(int(version)).strftime('%d-%m-%Y %H:%M:%S')
			v = int(version)
			buildString = ' > %s ( %s )  BuildStatus: %s' % (green(v), dateAssociated,  statusList[i])
			if curversion == v:
				print buildString, red("[current]")
			else:
				print buildString
			i = i + 1

def rollback(app, version):
	versions = run('ls /var/www/%s/versions/%s' % (app, version))
	run('ln -s /var/www/%s/versions/%s /var/www/%s/_current' % (app,version, app))
	run('mv -T /var/www/%s/_current /var/www/%s/current' % (app, app))
	print 'Version is now set to ', green(version)
