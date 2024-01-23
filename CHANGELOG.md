# RESTful Dash (R-dash)

{:toc}

## CHANGELOG

### 1.0.0 @ 1/22/2024

#### :mega: New

1. Provide full typehints for all modules.
2. Make the optional packages `file` and `host` lazy-loaded. If their dependencies are missing, these modules will be marked as placeholder and their corresponding members will be replaced by `None`.
3. Provide context features to `LineBuffer` and `Line*Mirror`. Entering such contexts will redirect `stdout` and `stderr` to the correspnding buffer/mirror. Note that `Line*Buffer` does not support this feature.
4. Make the version lazy-loaded when buliding the pacakge.
5. Provide the docker scripts for fast-deployment of the testing environment.

#### :wrench: Fix

1. Fix: Previously, some typehints, for example, the out type of `LineProcBuffer.read()`, are not corrected. Now, these types got fixed.
2. Fix: Previously, `LineBuffer.write()` may return `None` in some cases. Now, such methods will always return `int`.
3. Fix: `LineBuffer` and `Line*Mirror` may not fit the type of `contextlib.redirect_stdout/stderr`. Now, we provide `syncstream.redirect_stdout/stderr` to solve this issue.
4. Fix: PyTest will raises errors if optional dependencies are absent. Now, this issue has been fixed. If any optional dependencies are missing, the corresponding tests will be skipped.
5. Fix: Move `version` as a pacakge because the module version is not compatible with Linux.

#### :floppy_disk: Change

1. Change the coding style to the Microsoft standards.
2. Make the whole package blackified.
3. Split the standard requirements, locked requirements, and developer's requirements.
4. Drop the dependency `flask-restful` for the optional `host` module. Since the service provider falls back to `flask`, there will be no error handler.
5. Refactor `conftest.py` and `setup` scripts to the modern style.
6. Refactor the GitHub templates for fixing some typos.
7. Update the GitHub Actions scripts to the newest versions.

### 0.3.3 @ 6/29/2021

1. Fix small typos.
2. Bump the dependencies to the newest versions.

### 0.3.2 @ 6/14/2021

1. Fix a bug caused by stopping the mirrors.
2. Format the meta-data defined in `setup.py`.
3. Add the documentation. Currently only the tutorial is finished.

### 0.3.0 @ 6/4/2021

1. Support the stop signal for `mproc` and `host` modules.
2. Fix some bugs in the testing script.
3. Fix typos.

### 0.2.2 @ 5/25/2021

1. Add `clear()` methods for all buffers and mirrors.
2. Fix typos in the package setup and info file.
3. Fix a bug caused by writing data to the host in the testing scripts for Linux.

### 0.2.1 @ 5/24/2021

1. Add the PyPI publish workflow.

### 0.2.0 @ 5/24/2021

1. Finish the synchronization based on the file lock package `fasteners`.
2. Finish the synchronization based on the web service packages `flask`, `flask-restful` and `urllib3`.
3. Fix the compatibility of the testing scripts for `py36`, `py37`.

### 0.1.0 @ 5/22/2021

1. Finish the synchronization based on the stdlib.
2. Create this project.
