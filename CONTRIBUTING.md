# Contributing to syncstream

Thank you for your interest in contributing to `syncstream`! We are accepting pull
requests in any time.

As a reminder, all contributors are expected to follow our [Code of Conduct][coc].

[coc]: https://github.com/cainmagi/sync-stream/blob/main/CODE_OF_CONDUCT.md

## Contributing to the package

### Installation

Please [fork] this project as your own repository, and create a sub-branch based on any branch in this project. The new branch name could be a short description of the implemented new feature.

After that, clone your repository by

```shell
git clone -b <your-branch-name> --single-branch https://github.com/<your-name>/sync-stream.git syncstream
```

Then, install the dependencies for the development. We suggest to isolate your development environment as a virtual environment.

```shell
pip install -r requriements.txt
```

### Debugging

After that, you could debug and modify the codes by yourself. Each time you push your modification, the testing workflow would be triggered. If the testing fails, you should:

1. Modify your code, and fix the bug reported by the testing.
2. or firing a new issue about the testing codes.

You should **not** modify the testing codes in `./tests`. If you think there are any problems in these codes, please descript your problems in the issue.

You could also run the tests locally by

```shell
python -m pytest tests
```

### Sending pull requests

After you finish your works, please send a new request, and compare your branch with the target branch in `syncstream`. You could explain your works concisely in the pull request description. You are not required to add the updating reports in the repository, or add the documentation. I could take over these works based on your description.

## Contributing to docs

If you want to contribute to docs, please fork the [`docs`](https://github.com/cainmagi/sync-stream/tree/docs) branch, and clone it

```shell
git clone -b docs --single-branch https://github.com/<your-name>/sync-stream.git syncstream-docs
```

You need to install `nodejs` and `yarn` first. We suggest to create an isolated conda environment:

```shell
conda create -n docs -c conda-forge git python=3.9 nodejs
```

Then you could initialize the docs project by

```shell
cd syncstream-docs
npm install -g corepack
corepack enable
corepack prepare yarn --activate
yarn install
```

You could start the local debugging by

```shell
yarn start
```

After you finish your works, you could also send a pull request.
