# How to update on pypi / git

1. Change version in `setup.py`
2. Rebuild python dist
```
python setup.py sdist
```
3. Upload to pypi
```
twine upload dist/*
```
4. Create git tag
```
git tag X.Y(devZ)
```
5. Push to git
```
git push origin X.Y(devZ)
```
6. Optional: Create changelog at github web interface.
