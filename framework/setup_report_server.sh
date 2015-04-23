#!/bin/bash

if [[  $# -lt 1 ]];
then
   echo "The parameters didn't meet the requirements!"
   echo "Usage: ./setup_report_server.sh <proxyaddress> "
   exit 1
fi

proxy=$1

getwebpackage ()
{
    wget http://ocqa.sh.intel.com/oc/package/mtbf/server_0.60_rc3.tar.gz 
    tar xvf server_0.60_rc3.tar.gz
}

aptinstall ()
{
    sudo apt-get install -y libssl-dev python-dev libevent-dev python-pip mongodb unzip curl
}

insourcepacage ()
{
    for package in `curl http://ocqa.sh.intel.com/oc/package/mtbf/ | awk -F\" '/tar/{print $8}'`
    do
	    wget http://ocqa.sh.intel.com/oc/package/mtbf/$package
            tar xvf $package
            file=`echo $package | sed s/.tar.*//g`         
	    cd $file
            sudo python setup.py install
            cd ..
    done

}

pipinstall ()
{   
    sudo pip install -r server_0.60_rc3/requirements.txt --use-mirrors --proxy $proxy
    sudo service mongodb restart
    sudo pip install --upgrade celery --proxy $proxy
    sudo chmod 777 /usr/local/lib/python2.7/dist-packages/python_dateutil-2.2-py2.7.egg/EGG-INFO/top_level.txt
}

startserver ()
{    
    cd server_0.60_rc3/
    bash -x startservice.sh --start
}


aptinstall
getwebpackage
insourcepacage
pipinstall
startserver
if [ $? -eq 0 ];then
   echo "Install success"
else
   echo "Install fail"
fi

