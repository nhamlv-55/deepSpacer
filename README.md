## Environment
python3

pip

## Setup
`pip install -r requirements.txt`
## Change the folder to where you have the .smt2 files
Change this line
https://github.com/nhamlv-55/deepSpacer/blob/de418a59708e0a1b3a302f85f6129aa3df89e01e/pobvis/app/main.py#L11
## Run
```
cd pobvis/app/
PYTHONPATH=z3/Release/python/:~/workspace/deepSpacer/ python main.py
(use your z3 and repo path)
```
a webpage will be served at http://localhost:8888/home/

## Default settings
By default the UI is running in `Iterative` mode: Each run, it will dump learnt lemmas into a file, and the next run will load that lemmas file and start from there (you will see that the `lemmas file` is updated to the newest lemmas file). That enables us to solve the file from level 0 to level k, pause, and solve from level k to k+1, and so on. However, it also leads to the __Known problem__

## Known problems and fix:
If you solve a different formula, please clear the `lemmas file` box. Otherwise, the UI will load lemmas file from the previous formula to solve the current formula.
