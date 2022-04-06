from __future__ import annotations
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from importlib.util import decode_source, spec_from_file_location
import re
import sys
import os
import types
from typing import Sequence

regex = re.compile(r"(?:^|\n)\s*(import control_flow| from control flow import label, goto)")

class Finder(MetaPathFinder):

    def __init__(self):
        self._finding = False

    def find_spec(self, fullname: str, path: Sequence[str] | None, target: types.ModuleType | None = ...) -> ModuleSpec | None:
        if self._finding:
            return None
        
        try:
            self._finding = True
            return self._find_spec(fullname, path, target)
        finally:
            self._finding = False
    
    def _find_spec(self, fullname: str, path: Sequence[str] | None, target: types.ModuleType | None) -> ModuleSpec | None:
        if not path:
            path = sys.path
        if "." in fullname:
            name = fullname.split(".")[-1]
        else:
            name = fullname
        
        for entry in path:
            if entry == "" or entry == ".":
                entry = os.getcwd()
            
            filename = os.path.join(entry, name + ".py")
            if os.path.exists(filename):
                with open(filename, "rb") as f:
                    source = decode_source(f.read())
                    if regex.search(source) is not None:
                        return spec_from_file_location(fullname, filename, loader=ControlFlowLoader(filename))
                return None
        return None


class ControlFlowLoader(Loader):
    def __init__(self, filename):
        self._filename = filename
    
    def create_module(self, spec: ModuleSpec) -> types.ModuleType | None:
        return None
    
    def exec_module(self, module: types.ModuleType) -> None:
        with open(self._filename, "rb") as f:
            source = decode_source(f.read())
            source = regex.sub("\nprint(123)", source)
            exec(compile(source, "test", "exec"), module.__dict__)

    @classmethod
    def get_code(cls, fullname):
        return None

    @classmethod
    def get_source(cls, fullname):
        return None



activated = False

def activate() -> None:
    global activated
    if not activated:
        sys.meta_path.insert(0, Finder())
        activated = True