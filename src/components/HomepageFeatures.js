import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';
import useThemeContext from '@theme/hooks/useThemeContext'; //docs: https://v2.docusaurus.io/docs/2.0.0-alpha.69/theme-classic#usethemecontext

import CodeBlock from "./CodeBlock";


function featureList(theme) {
  return [
    {
      title: 'Installation',
      description: (
        <>
          <p>Run the following command for a basic installation:</p>
          <CodeBlock
            theme={theme}
            language='shell'
            code={`pip install syncstream`}
          />
          <p>Or the command for a full installation:</p>
          <CodeBlock
            theme={theme}
            language='shell'
            code={`pip install syncstream[file,host]`}
          />
        </>
      ),
    },
    {
      title: 'Catch the stdout',
      description: (
        <>
          <p>The following codes provide an example of catching the python stdout:</p>
          <CodeBlock
            theme={theme}
            language='python'
            code={`from contextlib import redirect_stdout
import syncstream

buffer = syncstream.LineBuffer(10)
with redirect_stdout(buffer):
    for i in range(20):
        print(f'Message "{i:02d}".')
    print('No line break.', end='')

messages = buffer.read()
for mitem in messages:
    print(mitem)`}
          />
        </>
      ),
    },
    {
      title: 'Catch the stdout of a sub-process',
      description: (
        <>
          <p>The following codes provide an example of catching the python stdout:</p>
          <CodeBlock
            theme={theme}
            language='python'
            code={`import multiprocessing
from contextlib import redirect_stdout
import syncstream


def worker_process(buffer):
    '''Define the workder_process'''
    try:
        with redirect_stdout(buffer):
            print('Message', 'item')
    except Exception as err:
        buffer.send_error(err)
    else:
        buffer.send_eof()


if __name__ == '__main__':
    pbuf = syncstream.LineProcBuffer(10)
    with multiprocessing.Pool(4) as pool:
        pool.map_async(
            worker_process,
            tuple(pbuf.mirror for _ in range(4))
        )
        pbuf.wait()

    messages = pbuf.read()
    for mitem in messages:
        print(mitem)`}
          />
        </>
      ),
    },
  ];
}

function Feature({title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--left padding-horiz--md">
        <h3 className="text--center">{title}</h3>
        <div>{description}</div>
      </div>
    </div>
  );
}


export default function HomepageFeatures() {
  const { isDarkTheme } = useThemeContext();
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {featureList(isDarkTheme ? 'dark': 'light').map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
