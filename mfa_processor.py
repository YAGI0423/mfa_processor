import os
import subprocess

import hparams as hprm



def main() -> None:
    os.makedirs(hprm.RESULT_DIR, exist_ok=True)

    cmd = (
        'mfa',
        'align',
        hprm.RESULT_DIR,
        hprm.DICT_NAME,
        hprm.MODEL_NAME,
        hprm.RESULT_DIR,
        '--clean',
        '--overwrite',
    )

    process = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True,
    )


    if process.returncode == 0:
        print("is Done")
    else:
        print(f"Error:\n{process.stderr}")


if __name__ == '__main__':
    main()