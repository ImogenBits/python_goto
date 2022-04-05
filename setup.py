from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from os.path import join, dirname, exists
from os import symlink, remove

class build_with_pth(build_py):
    def run(self):
        super().run()
        out = join(self.build_lib, "control_flow.pth")
        self.copy_file("control_flow.pth", out, preserve_mode=0)
        

class develop_with_pth(develop):
    def run(self):
        super().run()
        out = join(self.install_dir, "control_flow.pth")
        if self.uninstall:
            remove(out)
        elif not exists(out):
            symlink(join(dirname(__file__), "control_flow.pth"), out)

setup(
    name = "control_flow",
    packages = ["control_flow"],
    python_requires = ">=3.7",
    cmdclass={"build_py": build_with_pth, "develop": develop_with_pth},
)
