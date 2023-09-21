echo "creating layers with requirements.txt packages..."
cd ..
dir %cd%

RD /S /Q "env_layer/"
RD /S /Q "%1/"
mkdir %1

echo "Create and activate virtual environment..."
virtualenv -p %2 env_layer
call %cd%/env_layer/Scripts/activate

echo "Installing python dependencies..."
if exist requirements.txt echo "From: requirement.txt file exists..."  
if exist requirements.txt pip install -r requirements.txt -t %1/python
if exist requirements.txt RD /S /Q %cd%/%1/python/__pycache__/
if exist requirements.txt tar.exe -cf %5 "%cd%/%1/" else echo "Error: requirement.txt does not exist!"

echo "Deactivate virtual environment..."
deactivate

echo "deleting the python dist package modules"
RD /S /Q "%cd%/%1"