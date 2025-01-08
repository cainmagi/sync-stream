# Sync-stream

{:toc}

## CHANGELOG

### 1.2.2 @ 1/8/2025

#### :wrench: Fix

1. Fix: Correct a bug that `mprocs.LineProcMirror` does not response to the early stop signal.

### 1.2.1 @ 1/7/2025

#### :mega: New

1. Use the new `pyproject.toml` configuration style to replace the old style `setup.cfg`.
2. Add more information in the readme documents.

#### :wrench: Fix

1. Fix: Correct docstrings and bad definitions of some APIs.
2. Fix: Attempt to solve the lazy-load issue that only happens when using the workflow.
3. Fix: Fix an issue caused by the change of `importlib.utils._LazyModule`. Use a hacking technique to bypass this issue.

#### :floppy_disk: Change

1. Adjust the workflow configurations and use the new standard of PyPI publishing.
2. Remove unused `utils.cached_property`.
3. Adjust the package file list in `MANIFEST`.
4. Drop the legacy version `3.6` from the workflow because it is not supported in Ubuntu `22.04`.

### 1.2.0 @ 2/27/2024

#### :mega: New

1. Add some missing methods for completing the standard IO protocol: `closed`, `close()`, `fileno()`, `isatty()`, `readable()`, `writable()`, `seekable()`, `seek()`.
2. Add logics for mainatining the status when buffers are closed.
3. Enable `file.LineFileBuffer()` to capture warning/exception objects. But the captured objects will be stored as text items.
4. Expose the `maxlen` property and the `__len__` property for the buffers.

#### :wrench: Fix

1. Fix: A server bug causes the warning/exception objects are captured but not recorded by `host.LineHostBuffer()`. This problem has been fixed.
2. Fix: Fix an issue that the getting `__file__` attribute of a placeholder module will cause error.

#### :floppy_disk: Change

1. Make the `send_eof()`/`send_error()` methods automatically called by the context. Now the mirror/buffer objects will be closed once the context is closed.

### 1.1.2 @ 2/14/2024

#### :mega: New

1. Provide `.dockerignore` file for removing unexpected files in the built docker image.

#### :wrench: Fix

1. Fix: Remove an unexpected in-release package `version` which should only appear during the package building.
2. Find a way to include `tests.version` in `sdist` but exclude all `tests` codes in `wheel`.

#### :floppy_disk: Change

1. Improve the quality of codes.
2. Make the `flake8` warning validator omit the issues exempted by `black`.

### 1.1.1 @ 2/5/2024

#### :wrench: Fix

1. Fix: Fix an incompatibility issue when `urllib3` is used in `Python==3.6`.

#### :floppy_disk: Change

1. Improve the workflow versions.

### 1.1.0 @ 2/5/2024

#### :mega: New

1. Provide the user-friendly APIs `host.LineHostReader()`. This class reproduces all methods of `host.LineHostBuffer()` because the latter one will not be used once it is equipped as the services.
2. Add a `force_stop()` method for `mproc.LineProcBuffer`. This method should be used when the subprocesses will be terminated by `SIG_TERMIATE` or `SIG_KILL`.
3. Add tests for validating whether `Line*Buffer.read()` functionality is correct or not.

#### :wrench: Fix

1. Fix: If the `last_line` is not flushed by a new line (`\n`) symbol, the `read()` method may not read `size - 1` lines. This unexpected behavior may cause the buffer not to be fully read. Now it has been fixed.
2. Fix: `utils._LazyAttribute` may not initialize a type correctly in some cases. This issue has been fixed by adding a branch for treating the attribute types.
3. Fix: The `version` folder is missing in the docker scripts. Now the folder has been added.

#### :floppy_disk: Change

1. Replace the typehints `NoReturn` with `Never`.
2. Drop the testing dependency `requests` so that this package would be lighter.

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
