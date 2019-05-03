cd "$(dirname "$0")"
ln -s / .root
echo $@ > .paths
cat .paths
python -m buffed_run.py
rm .root
rm .paths
cd -
