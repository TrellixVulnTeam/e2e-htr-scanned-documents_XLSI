import sys
import argparse
from executor import Executor


def batch_hook(epoch, batch, max_batches):
    percent = (float(batch) / max_batches) * 100
    out = 'epoch = {0} [ {2:100} ] {1:02.2f}% '.format(
        str(epoch).zfill(3), percent, "|" * int(percent))
    sys.stdout.write("\r" + out)
    sys.stdout.flush()


def epoch_hook(epoch, loss, time, val_stats):
    msg = 'epoch = {0} | loss = {1:.3f} | time {2:.3f} | ler {3:.3f}'.format(str(epoch).zfill(3),
                                                                             loss,
                                                                             time, val_stats['ler'])
    sys.stdout.write('\r{:130}\n'.format(msg))
    sys.stdout.flush()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--config')
    parser.add_argument(
        '--gpu', help='Runs scripts on gpu. Default is cpu.', default=-1, type=int)
    parser.add_argument('--softplacement', help='Allow Softplacement, default is True',
                        action='store_true', default=True)
    parser.add_argument('--logplacement', help='Log Device placement',
                        action='store_true', default=False)
    args = parser.parse_args()

    exc = Executor(args.config)
    exc.configure(args.gpu, args.softplacement, args.logplacement)
    exc.train({
        'batch': batch_hook,
        'epoch': epoch_hook
    })
