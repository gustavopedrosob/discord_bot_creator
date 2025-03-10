from cx_Freeze import setup, Executable

setup(
    name="Bot Discord Easy Creator",
    version="1.0",
    description="Um software para o desenvolvimento de bot no Discord.",
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
