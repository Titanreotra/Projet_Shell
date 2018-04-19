#!/usr/bin/env python3.4
#
# -*- encoding: utf-8 -*-
# Author: Olivier Dalle
# date: May 4th, 2014
#
# Notice: Python version above can safely be changed to any
# 3.x python version available.

""" This small program can be used to trace the signals received by
a process during execution. The traced signals are caught by a tracing
handler and then self-resent by the process after the default handler is
reinstalled in place of the tracing handler. The tracing handlers of the
signals that put the process to sleep (SIGTSTP, SIGTTIN, SIGTTOU) are
reinstalled after the process execution is resumed by a SIGCONT, such
that the job control effects can be observed.

Some interesting experiments:
- run a single instance, and watch: it should display the programm name
at regular interavals
- try Ctrl-Z: see SIGTSTP occuring. Notice process group, process id, and
terminal owner
- restart using fg (foreground), notice SIGCONT occuring
- while in foreground, try to type something at the keyboard and
see your text repeated after typing enter
- Try Ctrl-Z + restart with bg: notice the change in terminal owner. Even
though it is running in background, the process is still able to
output to the controlling terminal.
- try again to type something at the keyboard and observe the effect: the
process is stopped after the first character is typed. The shell prompt is
reprinted followed by the character that was just typed, which is the
demonstration of the system principle: all characters typed in are destined
exclusively to the foreground process, however the bg process can still
progress as long as it does not try to read something from the terminal and
no interaction with the fg process occurs.
"""


import sys,os,signal,time,select

"""32 standard POSIX signals"""
SIGNALS=('ZERO','HUP','INT','QUIT','ILL','TRAP','ABRT','EMT','FPE','KILL',
         'BUS','SEGV','SYS','PIPE','ALRM','TERM','URG','STOP','TSTP','CONT',
         'CHLD','TTIN','TTOU','IO','XCPU','XFSZ','VTALRM','PROF','WINCH','INFO',
         'USR1','USR2')

def process_infos(str="???"):
    """Show some useful data about the current process"""
    # stdin/stdout not always connected to a controlling terminal
    try:
        term_owner0 = os.tcgetpgrp(0)
    except OSError:
        term_owner0 = 0
    try:
        term_owner1 = os.tcgetpgrp(1)
    except OSError:
        term_owner1 = 0
    return "processus %s: pid=%d, pere=%d, groupe=%d, term owner:%d/%d, sid=%d"%(str,os.getpid(),os.getppid(),os.getpgid(0),term_owner0,term_owner1, os.getsid(0))

def sigtrace_handler(sig,ign):
    """Trace signal and resend with default handler to see what happens"""
    global SIGNALS
    print("received SIG%s: %s"%(SIGNALS[sig],process_infos("???")),file=sys.stderr)
    if sig == 2:
        # Python has a special handler for SIGINT that generates
        # a KeyboardInterrupt exception
        signal.signal(sig,signal.default_int_handler)
    elif sig == signal.SIGCONT:
        # When the process restarts after being stopped we re-install
        # tracing handler on Ctrl-Z and TTIN/TTOUT signals so it is
        # possible to play with job control
        signal.signal(signal.SIGTSTP,sigtrace_handler)
        signal.signal(signal.SIGTTOU,sigtrace_handler)
        signal.signal(signal.SIGTTIN,sigtrace_handler)
    else:
        # Once a signal has been received we reinstall the default
        # handler before self-resending the signal
        signal.signal(sig,signal.SIG_DFL)
    # All signal received but SIGCONT are self-resent after being received
    if sig != signal.SIGCONT:
        os.kill(os.getpid(),sig)

def main():
    """Main function. Even though this programm can be used as
a module it is meant to be started as a self-contained program."""
    os.write(2,bytes(process_infos(sys.argv[0])+"\n",'utf-8'))
    # Some signals of interest. Extend the list at will...
    signal.signal(signal.SIGALRM,sigtrace_handler)
    signal.signal(signal.SIGUSR1,sigtrace_handler)
    signal.signal(signal.SIGUSR2,sigtrace_handler)
    signal.signal(signal.SIGINT,sigtrace_handler)
    signal.signal(signal.SIGTERM,sigtrace_handler)
    signal.signal(signal.SIGCONT,sigtrace_handler)
    signal.signal(signal.SIGTSTP,sigtrace_handler)
    signal.signal(signal.SIGTTOU,sigtrace_handler)
    signal.signal(signal.SIGTTIN,sigtrace_handler)
    signal.signal(signal.SIGHUP,sigtrace_handler)


    while True:
        # Receiving a signal while in select will raise an exception
        try:
            # Wait for new input for at most one second
            rrdy,wrdy,erdy = select.select([sys.stdin],[],[],1.0)
            if len(rrdy) > 0:
                # select returns with stdin ready (before one second)
                buf = os.read(0,1024)
                os.write(1, bytes(sys.argv[0]+":",'utf-8')+buf)
            else:
                # select return with nothing to read on stdin
                os.write(1,bytes(sys.argv[0]+"\n","utf-8"))
        except InterruptedError:
            # select interrupted by signal: simply ignore and proceed
            pass
# Notice SIGINT is not included, it is a special case that
# generates a KeyboardInterrupt Exception that is not caught
# in this program (which results in program termination).


if __name__ == "__main__":
    main()