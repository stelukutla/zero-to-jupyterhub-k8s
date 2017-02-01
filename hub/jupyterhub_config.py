import os
import json
import sys

c.JupyterHub.spawner_class = 'kubespawner.KubeSpawner'

# Connect to a proxy running in a different pod
c.JupyterHub.proxy_api_ip = os.environ['PROXY_API_SERVICE_HOST']
c.JupyterHub.proxy_api_port = int(os.environ['PROXY_API_SERVICE_PORT'])

c.JupyterHub.ip = os.environ['PROXY_PUBLIC_SERVICE_HOST']
c.JupyterHub.port = int(os.environ['PROXY_PUBLIC_SERVICE_PORT'])

# the hub should listen on all interfaces, so the proxy can access it
c.JupyterHub.hub_ip = '0.0.0.0'

c.KubeSpawner.namespace = os.environ.get('POD_NAMESPACE', 'default')

# Upto 15 minutes, first pulls can be really slow because data8 user image is huge
c.KubeSpawner.start_timeout = 60 * 20

# Our simplest user image! Optimized to just... start, and be small!
c.KubeSpawner.singleuser_image_spec = os.environ['SINGLEUSER_IMAGE']
c.KubeSpawner.singleuser_image_pull_policy = 'Always'

# Configure dynamically provisioning pvc
c.KubeSpawner.pvc_name_template = 'claim-{username}-{userid}'
c.KubeSpawner.user_storage_class = os.environ['SINGLEUSER_STORAGE_CLASS']
c.KubeSpawner.user_storage_access_modes = ['ReadWriteOnce']
c.KubeSpawner.user_storage_capacity = os.environ['SINGLEUSER_STORAGE_CAPACITY']

c.KubeSpawner.singleuser_uid = 1000
c.KubeSpawner.singleuser_fs_gid = 1000

# Add volumes to singleuser pods
c.KubeSpawner.volumes = [
    {
        'name': 'volume-{username}-{userid}',
        'persistentVolumeClaim': {
            'claimName': 'claim-{username}-{userid}'
        }
    }
]
c.KubeSpawner.volume_mounts = [
    {
        'mountPath': '/home/jovyan',
        'name': 'volume-{username}-{userid}'
    }
]

# Shared data mounts - used to mount shared data (across all
# students) from pre-prepared PVCs to students.
# The env variable should be a JSON dictionary
# The key should be the subpath under /data/shared they should
# be mounted on, and the value should be name of PVC to mount
shared_data_mounts_str = os.environ.get('SHARED_DATA_MOUNTS', None)
if shared_data_mounts_str:
    shared_data_mounts = json.parse(shared_data_mounts_str)
    c.KubeSpawner.volumes += [{
        'name': 'shared-data-{name}'.format(name=name),
        'persistentVolumeClaim': {
            'claimName': claimName
        }
    } for name, claimName in shared_data_mounts.items()]
    c.KubeSpawner.volume_mounts += [{
        'mountPath': '/data/shared/{name}'.format(name=name),
        'name': 'shared-data-{name}'.format(name=name),
    }]

# Gives spawned containers access to the API of the hub
c.KubeSpawner.hub_connect_ip = os.environ['HUB_SERVICE_HOST']
c.KubeSpawner.hub_connect_port = int(os.environ['HUB_SERVICE_PORT'])

c.KubeSpawner.mem_limit = os.environ.get('SINGLEUSER_MEM_LIMIT', None)
c.KubeSpawner.mem_guarantee = os.environ.get('SINGLEUSER_MEM_GUARANTEE', None)
c.KubeSpawner.cpu_limit = os.environ.get('SINGLEUSER_CPU_LIMIT', None)
c.KubeSpawner.cpu_guarantee = os.environ.get('SINGLEUSER_CPU_GUARANTEE', None)

# Allow switching authenticators from environment variables
auth_type = os.environ['HUB_AUTH_TYPE']

if auth_type == 'google':
    c.JupyterHub.authenticator_class = 'oauthenticator.GoogleOAuthenticator'
    c.GoogleOAuthenticator.client_id = os.environ['GOOGLE_OAUTH_CLIENT_ID']
    c.GoogleOAuthenticator.client_secret = os.environ['GOOGLE_OAUTH_CLIENT_SECRET']
    c.GoogleOAuthenticator.oauth_callback_url = os.environ['GOOGLE_OAUTH_CALLBACK_URL']
    c.GoogleOAuthenticator.hosted_domain = os.environ['GOOGLE_OAUTH_HOSTED_DOMAIN']
    c.GoogleOAuthenticator.login_service = os.environ['GOOGLE_OAUTH_LOGIN_SERVICE']
    email_domain = os.environ['GOOGLE_OAUTH_HOSTED_DOMAIN']
elif auth_type == 'hmac':
    c.JupyterHub.authenticator_class = 'hmacauthenticator.HMACAuthenticator'
    c.HMACAuthenticator.secret_key = bytes.fromhex(os.environ['HMAC_SECRET_KEY'])
    email_domain = 'localdomain'

def generate_user_email(spawner):
    """
    Used as the EMAIL environment variable
    """
    return '{username}@{domain}'.format(
        username=spawner.user.name, domain=email_domain
    )

def generate_user_name(spawner):
    """
    Used as GIT_AUTHOR_NAME and GIT_COMMITTER_NAME environment variables
    """
    return spawner.user.name

c.KubeSpawner.environment = {
    'EMAIL': generate_user_email,
    # git requires these committer attributes
    'GIT_AUTHOR_NAME': generate_user_name,
    'GIT_COMMITTER_NAME': generate_user_name
}
 
c.JupyterHub.api_tokens = {
    os.environ['CULL_JHUB_TOKEN']: 'cull',
}

# Setup STATSD
if 'STATSD_SERVICE_HOST' in os.environ:
    c.JupyterHub.statsd_host = os.environ['STATSD_SERVICE_HOST']
    c.JupyterHub.statsd_port = int(os.environ['STATSD_SERVICE_PORT'])

# Enable admins to access user servers
c.JupyterHub.admin_access = True

c.Authenticator.admin_users = {
    'cull',
    # prob140
    'adhikari',
    'dibya.ghosh',
    'maxwelljweinstein',
    'zhang.j',
    # cogneuro
    'choldgraf',
    'fatma',
    'lwehbe',
    'mark.lescroart',
    #
    'arvindiyengar',
    'vinitra',
    'namushegian',
    'nskh',
    'alon.daks',
    'alon-daks',
    'jwhughes',
    'niraj.a.rao',
    'niraj-a-rao',
    'kellerstrass',
    'michelleyang',
    'priyanka.bhoj',
    'priyanka-bhoj',
    'tanaynathan18',
    'wumadeline',
    'marcus.lee',
    'marcus-lee',
    'delphine.ho',
    'j.hu',
    'j-hu',
    'huangjiayi0922',
    'swathugala',
    'supadhyay',
    'v.oikonomou',
    'v-oikonomou',
    'satish.vinay',
    'satish-vinay',
    'j_dong1021',
    'j-dong1021',
    'inan.husain',
    'inan-husain',
    'wiltonwu',
    'rjoshi',
    'stevenwuyinze',
    # all
    'denero',
    'samlau95',
    'yuvipanda',
    'rylo',
    'peterkangveerman'
}
