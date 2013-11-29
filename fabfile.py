from fabric.api import *

# the user to use for the remote commands
#env.user = 'appuser'
# the servers where the commands are executed
#env.hosts = ['server1.example.com', 'server2.example.com']
import time
import datetime
from fabric.colors import green, blue, red


def deploy(app, git):
	ts = int(time.time())
	curdir = '/var/www/%s/versions/%s' % (app, ts)
	run('mkdir -p %s' % (curdir))

	run('git clone %s %s' % (git, curdir))
	run('cp %s/app/config/parameters_prod.yml %s/app/config/parameters.yml' % (curdir, curdir))
	run('cd %s && composer install --optimize-autoloader' % (curdir))

	run('cd %s && app/console cache:clear' % (curdir))
	run('cd %s && app/console cache:clear --env=prod' % (curdir))
	run('cd %s && app/console cache:warmup' % (curdir))
	run('cd %s && app/console cache:warmup --env=prod' % (curdir))
	run('cd %s && app/console assetic:dump' % (curdir))
	run('cd %s && app/console doctrine:database:create || true' % (curdir))
	run('cd %s && app/console doctrine:schema:update --force' % (curdir))
	run('cd %s && app/console doctrine:fixtures:load --append' % (curdir))

	run('ln -s /var/www/%s/versions/%s /var/www/%s/_current' % (app,ts, app))
	run('mv -T /var/www/%s/_current /var/www/%s/current' % (app, app))


def ls(app):
		versions = run('ls /var/www/%s/versions/ | awk "{print $1}"' % (app))
		current = run('perl -le \'print readlink(\"/var/www/%s/current\")\'' % (app))
		curversion = int(current.split('/')[-1]);

		versionList = versions.split('\n');
		for version in versionList:
			dateAssociated = datetime.datetime.fromtimestamp(int(version)).strftime('%d-%m-%Y %H:%M:%S')
			v = int(version)
			if curversion == v:
				print ' > ', green(v), ' (', dateAssociated, ')', red("[current]")
			else:
				print ' > ', green(v), ' (', dateAssociated, ')'

def rollback(app, version):
	versions = run('ls /var/www/%s/versions/%s' % (app, version))
	run('ln -s /var/www/%s/versions/%s /var/www/%s/_current' % (app,version, app))
	run('mv -T /var/www/%s/_current /var/www/%s/current' % (app, app))
	print 'Version is now set to ', green(version)
