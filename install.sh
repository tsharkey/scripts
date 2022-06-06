#/bin/bash

# install pip on mac
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py

# cleanup pip
rm get-pip.py

# add this dir to path
if [ -d "$(pwd)" ] && [[ ":$PATH:" != *":$(pwd):"* ]]; then
    echo "Adding $(pwd) to PATH"
    export PATH=$PATH:$(pwd)
fi

pip install -r requirements.txt
