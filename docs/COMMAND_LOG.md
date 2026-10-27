Command Log
Day 1
python –version the version of python installed
git –version  the version of git installed
git clone https://github.com/davechow88/AIwithAbdullahLesson2_courseflow.git copy repository to local folder
cd AIwithAbdullahLesson2_courseflow go into folder
git status find out the status of git
git remote -v shows full address of fetch and push
git log --oneline -5 shows the five last logs of git
git branch it shows which branch you are in
git switch -c homework/venv-git-api create and go into a new branch
python -m venv .venv make a virtual environment called .venv
.\.venv\Scripts\Activate.ps1 enter venv
python -c "import sys; print(sys.executable)" import python system and install python.exe 
python -m pip –version version of python
python -m pip install requests installing requests dependency (package/library)
python -m pip show requests show details of requests package
python -m pip check check if packages are installed properly
python -m pip freeze | Set-Content -Encoding ascii requirements-dev.txt taking a snapshow and creating a requirements-dev.txt with the contents through piping
Get-Content requirements-dev.txt see the contents of requirements-dev.txt on terminal
python -m pip install -r requirements-dev.txt requirements already installed and is correct
 python -c "import requests; print(requests.__version__)" importing and checking the version of requests module
deactivate exit .venv
.\.venv\Scripts\python.exe -m pip show requests able to access requests module information without being inside .venv
git check-ignore .venv/  .venv/ is printed so the .gitignore file is working properly
git status --short shows that requirements-dev.txt is an untracked file
git status --short --ignored shows that .venv/ is ignored and requirements-dev.txt is untracked.
