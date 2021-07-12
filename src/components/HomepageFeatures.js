import React from 'react';
import clsx from 'clsx';
import styles from './HomepageFeatures.module.css';

import CodeBlock from '@theme/CodeBlock';

import { indexCodes } from '../constants/indexCodes';

function Feature(props) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--left padding-horiz--md">
        <h3 className="text--center">{props.title}</h3>
        <div>{props.children}</div>
      </div>
    </div>
  );
}


export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          <Feature title='Installation'>
            <p>Run the following command for a basic installation:</p>
            <CodeBlock
              className='shell'
              children={indexCodes.installBasic}
            />
            <p>Or the command for a full installation:</p>
            <CodeBlock
              className='shell'
              children={indexCodes.installFull}
            />
          </Feature>
          <Feature title='Catch the stdout'>
            <p>The following codes provide an example of catching the python stdout:</p>
            <CodeBlock
              className='python'
              children={indexCodes.exPlain}
            />
          </Feature>
          <Feature title='Catch the stdout of a sub-process'>
            <p>The following codes provide an example of catching the python stdout:</p>
            <CodeBlock
              className='python'
              children={indexCodes.exProc}
            />
          </Feature>
        </div>
      </div>
    </section>
  );
}
