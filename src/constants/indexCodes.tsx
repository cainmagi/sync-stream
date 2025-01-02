export const indexCodes = {
  installBasic: `pip install syncstream`,
  installFull: `pip install syncstream[file,host]`,
  exPlain: `from contextlib import redirect_stdout
import syncstream

buffer = syncstream.LineBuffer(10)
with redirect_stdout(buffer):
  for i in range(20):
      print(f'Message "{i:02d}".')
  print('No line break.', end='')

messages = buffer.read()
for mitem in messages:
  print(mitem)`,
  exProc: `import multiprocessing
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
        print(mitem)`
}
