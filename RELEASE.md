# For maintainers
The following steps describe how to make a release.

First update the CHANGES.rst with the changes the new release brings.
After that you'll want to run the following commands.
```bash
git add CHANGES.rst
poetry run invoke release
poetry publish --build
```
