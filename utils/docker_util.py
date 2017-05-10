from execo import Remote

from general_util import *
from general_util import wget_destination


def install_docker(nodes):
    docker_deb = "https://download.docker.com/linux/debian/dists/jessie/pool/stable/amd64/docker-ce_17.03.1~ce-0~debian-jessie_amd64.deb"
    Remote("wget {0} -O {1}/docker-ce.deb 2>1".format(docker_deb,wget_destination),hosts=nodes,
           connection_params={'user': 'root'}).run() ## download the debian package for docker
    Remote("dpkg -i {0}/docker-ce.deb".format(wget_destination),hosts=nodes,
           connection_params={'user': 'root'}).run() # install the package
    Remote("apt-get -fy install",hosts=nodes,
           connection_params={'user': 'root'}).run() # install the package
    Remote("docker run hello-world",hosts=nodes,
           connection_params={'user': 'root'}).run() # install the package