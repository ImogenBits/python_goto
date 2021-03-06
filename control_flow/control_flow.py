from __future__ import annotations
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from importlib.util import decode_source, spec_from_file_location
import re
import sys
import os
import types
from typing import Sequence

find_pattern = re.compile(r"(?:^|\n)\s*(import control_flow|from __past__ import goto)($|\n)")

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
                    if find_pattern.search(source) is not None:
                        return spec_from_file_location(fullname, filename, loader=ControlFlowLoader(fullname, filename))
                return None
        return None


label_re = re.compile(r"^(\s*)label (\w+):$")
goto_re = re.compile(r"^(\s*)goto (\w+)$")

class ControlFlowLoader(Loader):
    fullnames = {}

    def __init__(self, fullname, filename):
        self._filename = filename
        self.fullnames[fullname] = self
    
    def create_module(self, spec: ModuleSpec) -> types.ModuleType | None:
        return None
    
    def _parse_module(self):
        with open(self._filename, "rb") as f:
            source = decode_source(f.read()).split("\n")

            if len(source) != 0 and not label_re.match(source[0]):
                for i, line in enumerate(source):
                    if label_re.match(line):
                        break
                    source[i] = "    " + line
                source.insert(0, "label __CONTROL_FLOW_START_LABEL__:")

            source = (["__CONTROL_FLOW_CURR_LABEL__: int = 0", "while True:"]
                    + ["    " + line for line in  source if not find_pattern.match(line)]
                    + ["    break"])
            labels = {}
            curr_label = 0
            for i, line in enumerate(source):
                m = label_re.match(line)
                if m is not None:
                    labels[m[2]] = curr_label
                    source[i] = f"{m[1]}if __CONTROL_FLOW_CURR_LABEL__ <= {curr_label}:"
                    curr_label += 1

            for i, line in enumerate(source):
                m = goto_re.match(line)
                if m is not None:
                    source[i] = f"{m[1]}__CONTROL_FLOW_CURR_LABEL__ = {labels[m[2]]}\n{m[1]}continue"
            
            out = "\n".join(source)
            #print(out)
            return compile(out, self._filename, "exec")

    def exec_module(self, module: types.ModuleType) -> None:
            code = self._parse_module()
            exec(code, module.__dict__)

    @classmethod
    def get_code(cls, fullname):
        if fullname in cls.fullnames:
            return cls.fullnames[fullname]._parse_module()
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
