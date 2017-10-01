# How to update on pypi / git

1. Test modifications locally in a clean conda environment. Example command:
```
rm -rf dist && rm -rf shiftsum.egg-info && python setup.py sdist && pip install --upgrade .
```
2. Change version in `setup.py`
3. Rebuild python dist
```
python setup.py sdist
```
4. Commit to python master/develop/... branch
```
git commit -a -m  "Fix XYZ"
```
5. Upload to pypi
```
twine upload dist/*
```
6. Create git tag
```
git tag X.Y(devZ)
```
7. Push to git
```
git push origin X.Y(devZ)
```
8. Optional: Create changelog at github web interface.
