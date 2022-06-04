#/bin/bash

# install pip on mac
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

# cleanup pip
rm get-pip.py

# add this dir to path
export PATH=$PATH:$(pwd)
