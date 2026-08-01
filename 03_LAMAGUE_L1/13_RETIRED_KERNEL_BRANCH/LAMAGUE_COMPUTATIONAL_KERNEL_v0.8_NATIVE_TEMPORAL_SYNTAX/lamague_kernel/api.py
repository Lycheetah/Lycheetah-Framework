from pathlib import Path
from .compiler import compile_program
from .parser import parse_file, parse_source
from .runtime import Runtime

def compile_source(source): return compile_program(parse_source(source))
def run_source(source):
    ir,ds=compile_source(source); return Runtime().execute(ir,ds)
def run_file(path):
    ir,ds=compile_program(parse_file(path)); return Runtime().execute(ir,ds)
