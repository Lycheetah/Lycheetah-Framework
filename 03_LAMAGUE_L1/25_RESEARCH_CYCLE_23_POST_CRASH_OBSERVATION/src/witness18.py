"""Cycle 18 persistent Unix-domain witness. Research reference only.
Launch as a dedicated unprivileged OS identity, with private --state and --keys dirs.
"""
import os,sys,json,argparse,socket,struct,pathlib,stat,signal
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from witness17 import decide,send_obj,recv_obj,Denied


def read_secret(path, expected_length):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or (info.st_mode & 0o077):
            raise Denied('secret permissions invalid')
        if info.st_uid != os.geteuid():
            raise Denied('secret owner invalid')
        data=os.read(fd,expected_length+1)
        if len(data)!=expected_length:raise Denied('secret length invalid')
        return data
    finally:os.close(fd)

def peer_uid(sock):
    raw=sock.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12)
    return struct.unpack('3i',raw)[1]

def serve(socket_path,state_dir,keys_dir,allowed_uid,ready_fd=None):
    state=pathlib.Path(state_dir); keys=pathlib.Path(keys_dir)
    for p in (state,keys):
        info=p.stat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.geteuid() or (info.st_mode&0o077):
            raise Denied('private directory ownership/mode invalid')
    journal_key=read_secret(keys/'journal.key',32)
    witness_key=read_secret(keys/'witness.key',32)
    pub=Ed25519PublicKey.from_public_bytes(read_secret(keys/'signer.pub',32))
    path=pathlib.Path(socket_path)
    if path.exists():raise Denied('socket path already exists')
    listener=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
    listener.bind(str(path)); os.chmod(path,0o600);listener.listen(8)
    if ready_fd is not None:
        os.write(ready_fd,b'READY\n');os.close(ready_fd)
    try:
        while True:
            connection,_=listener.accept()
            with connection:
                connection.settimeout(3)
                try:
                    if peer_uid(connection)!=allowed_uid:raise Denied('peer uid not authorized')
                    request=recv_obj(connection)
                    result=decide(request,str(state),journal_key,witness_key,pub)
                except Exception as exc:
                    result={'state':'DENIED','authorized':False,'reason':str(exc)[:160]}
                try:send_obj(connection,result)
                except (BrokenPipeError,ConnectionError,OSError):pass
    finally:
        listener.close();path.unlink(missing_ok=True)

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--socket',required=True);a.add_argument('--state',required=True)
    a.add_argument('--keys',required=True);a.add_argument('--client-uid',type=int,required=True)
    x=a.parse_args();serve(x.socket,x.state,x.keys,x.client_uid)

if __name__=='__main__':main()
