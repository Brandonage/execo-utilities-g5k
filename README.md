# execo-utilities-g5k

An easy way to script reproducible experiments on the g5k testbed.
It uses the utilities in https://github.com/Brandonage/execo-g5k-benchmarks
to launch benchmarks of different types of applications

To make it work we need to add in the in the .execo.conf.py file of our home directory the following key which will
be merged with the default execo.config.g5k_configuration

g5k_configuration = {
    'g5k_user' : 'abrandon'
}

It also needs the jsonpath_rw package

pip install --user jsonpath_rw
