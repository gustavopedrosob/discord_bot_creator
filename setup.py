from cx_Freeze import setup, Executable

setup(
    name="Discord Bot Creator",
    version="2.0.0",
    description="Discord Bot Creator",
    options={
        "build_exe": {
            "include_files": [
                ("source/", "source"),
                ("translations/build", "translations/build"),
            ],
            "packages": ["audioop", "sqlalchemy.dialects.sqlite", "sqlite3"],
        }
    },
    executables=[
        Executable("main.py", target_name="Discord Bot Creator.exe", icon="logo.ico")
    ],
)
