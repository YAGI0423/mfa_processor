import os
import subprocess

import hparams as hprm



def mfa_process() -> None:
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


    if process.returncode != 0:
        print(f"Error:\n{process.stderr}")


def file_remover() -> None:
    '''
    TextGrid가 존재하지 않은 audio 및 script 제거
    '''

    #1. TextGrid가 없는 `audio.txt`, `audio.wav` 제거
    for home, _, files in os.walk(hprm.RESULT_DIR):

        base_name = os.path.normpath(home)
        base_name = os.path.basename(base_name)

    
        if 'speaker' in base_name:
            #TextGrid가 없는 audio 목록 수집
            audios = list()
            textgrids = list()
            for f in files:
                f_name, ext = os.path.splitext(f)
                ext = ext[1:]
                if ext == 'wav':
                    audios.append(f_name)
                
                if ext == 'TextGrid':
                    textgrids.append(f_name)

            for tg in textgrids:
                audios.remove(tg)

            #Delete `audio` & `txt`
            del_list = tuple(audios)    #(audio120, audio60, ...)
            for del_f in del_list:
                del_dir = os.path.join(home, del_f)

                os.remove(f'{del_dir}.wav')
                os.remove(f'{del_dir}.txt')
            
                
def renaming() -> None:
    '''
    `file_remover`로 제거한 후
    audio0 ~ aduio00와 같은 순서대로 renaming
    '''
    for home, _, files in os.walk(hprm.RESULT_DIR):
        base_name = os.path.normpath(home)
        base_name = os.path.basename(base_name)

        if 'speaker' in base_name:
            audios = list()
            for f in files:
                f_name, _ = os.path.splitext(f)
                audios.append(f_name)
            

            #이미 존재하는 파일명으로 변경하는 것을 방지하기 위해 우선 idx로만 구성된 파일명으로 변경
            names = set(audios)
            for i, f_name in enumerate(names, 1):
                for ext in ('txt', 'wav', 'TextGrid'):
                    os.rename(
                        src=os.path.join(home, f'{f_name}.{ext}'), #old_name
                        dst=os.path.join(home, f'{i}.{ext}'), #new_name
                    )
            
            #올바르게 변경(50.txt -> audio50.txt)
            for i in range(len(names)):
                for ext in ('txt', 'wav', 'TextGrid'):
                    os.rename(
                        src=os.path.join(home, f'{i + 1}.{ext}'), #old_name
                        dst=os.path.join(home, f'audio{i + 1}.{ext}'), #new_name
                    )


def main() -> None:
    mfa_process()
    file_remover()
    renaming()
    print('MFA PROCESSOR IS DONE')


if __name__ == '__main__':
    main()
    