# DEVELOPMENT GUIDELINES

* workplace setup
* makefile targets
* release process

## WORKPLACE SETUP

Development can be done with a pure text editor and a terminal session.

### VSCode setup

Use python and mypy extensions for Visual Studio Code (from Microsoft).

* Control-P: "ext list"
  * look for "Python", "Pylance" (style checker), "Mypy Type Checker" (type checker)
  * optional "Makefile Tools"
* Control-P: "ext install ms-python.mypy-type-checker"
  * this one pulls the latest mypy from the visualstudio marketplace
  * https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker

The make targets are defaulting to tests with python3.6 but the mypy plugin
for vscode requires atleast python3.8. All current Linux distros provide an
additional package with a higher version number, e.g "zypper install python311".
Be sure to also install "python311-mypy" or compile "pip3 install mypy". 
Implant the paths to those tools into the workspace settings = `.vscode/settings.json`

    {
        "python.defaultInterpreterPath": "/usr/bin/python3.11",
        "mypy-type-checker.reportingScope": "file",
        "mypy-type-checker.path": [
                "/usr/bin/mypy-3.11"
        ],
        "mypy-type-checker.interpreter": [
                "/usr/bin/python3.11"
        ],
        "mypy-type-checker.args": [
                "--strict",
                "--show-error-codes",
                "--show-error-context",
                "--no-warn-unused-ignores",
                "--ignore-missing-imports",
                "--exclude=build"
        ]
    }

Hint: the mypy plugins likes the git workspace folder to be "docker_mirror_packages_repo"
(otherweise it says that "docker-mirror-packages-repo" is not a valid package name)

### Makefile setup

Make sure that you have `docker` installed and the service is running.
* `systemctl start docker`

Common distro packages are:
* `zypper install python3 python3-pip` # atleast python3.6
* `zypper install python3-wheel python3-twine`
* `zypper install python3-coverage python3-unittest-xml-reporting`
* `zypper install python3-mypy python3-mypy_extensions python3-typing_extensions`
* `zypper install python3-autopep8`

For ubuntu you can check the latest Github workflows under
* `grep apt-get .github/workflows/*.yml`

## Makefile targets

### static code checking

* `make type`
* `make style`

### testing targets

* `make check`
* `make install` and `make uninstall`

### release targets

* `make version`
* `make build`

## RELEASE PROCESS

### check distros

For each of the three realms, check for newer versions of distros.
* update the `*.mk` for each new distro version
* ensure that the `*-mirror.py` code can build correctly
* update "SUPPORTED.md" when ready

For each new distro version
* update the image sizes in "README.md"

For each new distro version
* extend the docker_mirror.tests.py by duplicate-changing the old distro version

### make release
* `make type`
* `make style`
*  check docker_mirror.tests.py if new distro versions were added
* `make check` # unittests for docker_mirror.py and dockerdir.py
* `make uninstall` # may fail as "not installed"
* `make install` 
* `make uninstall`
* `make version` # or `make version FOR=tomorrow`
* update long description in README.md
* update short description in setup.cfg
* `make build`
* `make install` 
* `make uninstall`
* `git commit v1.x` to the version in setup.cfg (or just uninstalled)
* `git push` # if necessary
* wait for github workflows to be okay
* prepare a tmp.changes.txt 
* `git tag -F tmp.changes.txt v1.x` to the version in setup.cfg
* `git push --tags`
* update the short description on github
* `make build` and following `twine upload` as shown
