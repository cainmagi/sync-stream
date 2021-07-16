---
id: sync-basic
title: Catch the stdout
sidebar_label: Catch the stdout
slug: /sync-basic
description: The basic usage of the package.
---

The following example catches the python stdout and stderr:

```python {5,15}
from contextlib import redirect_stdout, redirect_stderr
import syncstream

# Initialize the buffer.
buffer = syncstream.LineBuffer(10)

# Use contextlib to redirect stdout and stderr.
with redirect_stdout(buffer), redirect_stderr(buffer):
    for i in range(20):
        print('Message', f'"{i:02d}".')
    print('Line break\nin middle.', end='')
    print('No line break.', end='')

# Check the results
messages = buffer.read()
for mitem in messages:
    print(mitem)
```

In the definition of the buffer, we set the maximal number of catched lines as `10`:

```python
buffer = syncstream.LineBuffer(10)
```

The buffer could be passed to the redict context. Inside the context, the `print` function would be redirected to the buffer. Each time a new line is detected, a new record item would be created by the buffer. The rules for detecting the new lines are the same as those of [`str.splitlines`][py-str-splitlines] in the stdlib.

After catching all lines, the results could be returned by

```python
messages = buffer.read()
```

Each item of `messages` is a `str` representing a line catched inside the context.

[py-str-splitlines]:https://docs.python.org/3/library/stdtypes.html#str.splitlines