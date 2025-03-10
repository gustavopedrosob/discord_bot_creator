from cx_Freeze import setup, Executable

setup(
    name="Discord Bot Creator",
    version="1.0.1",
    description="Discord Bot Creator",
    options={
        "build_exe": {
            "include_files": [
                ("source/", "source"),
                ("translations/build", "translations/build"),
            ],
        }
    },
    executables=[Executable("main.py", base="Win32GUI", icon="logo.ico")],
)
