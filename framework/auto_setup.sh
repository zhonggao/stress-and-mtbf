#!/bin/bash

function Installpy {
    zypper ref
    if [ $? -ne 0 ];then
       echo  "Please check zypper REPO or Network!"
    else
       zypper -n in python unzip
    fi
}

function Installdep {
    if ls nose-1.3.3.tar.gz;then
        tar xvf nose-1.3.3.tar.gz
        cd nose-1.3.3
        python setup.py install && cd ..
    else
        echo "Please download nose-1.3.3.tar.gz"
	exit 1
    fi
    if ls requests-master.zip;then
	unzip requests-master.zip
	cd requests-master
	python setup.py install && cd .. 
    else
	echo "Please download requests-master.zip"
	exit 1
    fi
}

function Done {
    echo "Setup done. Please dry run noserunner/runtest.py script"
}
Installpy
Installdep
Done
