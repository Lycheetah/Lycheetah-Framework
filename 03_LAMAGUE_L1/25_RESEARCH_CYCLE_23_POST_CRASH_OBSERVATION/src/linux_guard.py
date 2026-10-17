"""Experimental x86_64 Linux deny-list seccomp + no_new_privs.

NOT a complete system-call sandbox. A default-allow filter only refuses listed
network/process/privilege syscalls. Must be invoked in an already chrooted,
credential-dropped, trusted child; never use as a general untrusted code runner.
"""
import ctypes
import errno
import os
import platform
import sys

PR_SET_NO_NEW_PRIVS=38
PR_SET_SECCOMP=22
SECCOMP_MODE_FILTER=2
BPF_LD_W_ABS=0x20
BPF_JMP_JEQ_K=0x15
BPF_JMP_JGE_K=0x35
BPF_RET_K=0x06
SECCOMP_RET_ALLOW=0x7fff0000
SECCOMP_RET_ERRNO=0x00050000
SECCOMP_RET_KILL_PROCESS=0x80000000
AUDIT_ARCH_X86_64=0xc000003e
# Limited, documented deny list, not a syscall allow list.
DENIED = {
 'socket':41, 'connect':42, 'accept':43, 'sendto':44, 'recvfrom':45,
 'bind':49, 'listen':50, 'socketpair':53, 'clone':56, 'fork':57,
 'vfork':58, 'execve':59, 'ptrace':101, 'mount':165, 'umount2':166,
 'keyctl':250, 'unshare':272, 'accept4':288, 'perf_event_open':298,
 'setns':308, 'bpf':321, 'execveat':322, 'io_uring_setup':425,
 'clone3':435,
}
class Filter(ctypes.Structure):
    _fields_=[('code',ctypes.c_ushort),('jt',ctypes.c_ubyte),('jf',ctypes.c_ubyte),('k',ctypes.c_uint32)]
class FProg(ctypes.Structure):
    _fields_=[('len',ctypes.c_ushort),('filter',ctypes.POINTER(Filter))]
def supported():
    return sys.platform=='linux' and platform.machine()=='x86_64' and os.geteuid()==0

def install_after_drop():
    if sys.platform!='linux' or platform.machine()!='x86_64':
        raise RuntimeError('unsupported platform: fail closed')
    libc=ctypes.CDLL(None,use_errno=True)
    libc.prctl.restype=ctypes.c_int
    def ins(code,k,jt=0,jf=0):return Filter(code,jt,jf,k)
    rules=[ins(BPF_LD_W_ABS,4),ins(BPF_JMP_JEQ_K,AUDIT_ARCH_X86_64,1,0),
           ins(BPF_RET_K,SECCOMP_RET_KILL_PROCESS),ins(BPF_LD_W_ABS,0),
           # Disallow x32 ABI syscalls, even on an x86_64 process.
           ins(BPF_JMP_JGE_K,0x40000000,0,1),ins(BPF_RET_K,SECCOMP_RET_ERRNO|errno.EPERM)]
    for syscall in DENIED.values():
        rules += [ins(BPF_JMP_JEQ_K,syscall,0,1),ins(BPF_RET_K,SECCOMP_RET_ERRNO|errno.EPERM)]
    rules += [ins(BPF_RET_K,SECCOMP_RET_ALLOW)]
    array=(Filter*len(rules))(*rules)
    prog=FProg(len(rules),array)
    if libc.prctl(PR_SET_NO_NEW_PRIVS,1,0,0,0)!=0:
        raise OSError(ctypes.get_errno(),'PR_SET_NO_NEW_PRIVS failed')
    if libc.prctl(PR_SET_SECCOMP,SECCOMP_MODE_FILTER,ctypes.byref(prog),0,0)!=0:
        raise OSError(ctypes.get_errno(),'PR_SET_SECCOMP failed')
    return True

def install():
    if not supported():raise RuntimeError("requirements not met: fail closed")
    return install_after_drop()
