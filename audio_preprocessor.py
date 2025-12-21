import os
import torchaudio
from tqdm import tqdm
import questionary as quest

import hparams as hprm


def _split_path(path: str) -> tuple:
    '''
    입력된 경로(path)를 모두 분리하여 tuple로 반환
    
    :param path: 'E:/project/gitProject/translator/104_003_0019.flac'
    :type path: str
    :return: ('E:', 'project', 'gitProject', 'translator', '104_003_0019.flac')
    :rtype: tuple
    '''
    return path.replace('\\', '/').split('/')


def get_speaker_sep_idx(data_dir: str) -> int:
    '''
    경로(path)를 바탕으로 'speaker'를 구분하는 폴더의 위치(idx)를 반환합니다.

    ※※ 사용자 상황에 맞게 수정할 것 ※※


    :param data_dir: 음원 데이터셋의 경로(dir)
    :type data_dir: str
    :return: 'speaker' 구분 폴더 위치(idx)
    :rtype: int
    '''
    
    #깊은 경로를 탐색
    pre_home = ''
    for home, *_ in os.walk(data_dir):
        if len(home) >= len(pre_home):
            pre_home = home
        else:
            break

    choices = _split_path(pre_home)
    choices = tuple(quest.Choice(title=c, value=i) for i, c in enumerate(choices))

    answer = quest.select('`Speaker`를 결정하는 요소를 선택해주세요.', choices).ask()
    return answer


def get_scripts(path: str) -> dict:
    '''
    audio-script로 구성된 transcript 파일 해당 여부 판단 후,\n
    { audio: script, ... } 형식으로 반환\n

    ※※ 사용자 상황에 맞게 수정할 것 ※※
    
    :param path: 파일 경로
    :type path: str
    
    :return: { audio(str): script(str), ... }
    :rtype: dict
    '''
    scripts = dict()    #return value

    file_name, ext = os.path.splitext(os.path.basename(path))
    ext = ext[1:]   
    

    #< 조건 >---------
    EQ1 = 'trans' in file_name  #조건1, 파일명에 'trans'가 존재할 것
    EQ2 = ext in ('txt')        #조건2, txt 파일일 것
    #End--------------


    if EQ1 and EQ2:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.read().split('\n')


        for line in lines:
            
                #음원 파일명과 스크립트를 구분하는 ':' > ',' > ' ' 구분자(seperator)를 순차적으로 대입하여 자체적으로 분리

                #line = '199_003_0004 어쨌든 지난해 오십 구 승를 거뒀던 미네소타는 벌써 지난해 승수의 약 십 퍼센트가량을 만들어냈다'
                
                #audio = '199_003_0004'
                #script = '어쨌든 지난해 오십 구 승를 거뒀던 미네소타는 벌써 지난해 승수의 약 십 퍼센트가량을 만들어냈다'

            for sep in (':', ',', ' '):
                sep_idx = line.find(sep)

                if sep_idx > 0:
                    audio = line[:sep_idx]
                    script = line[sep_idx+1:]
                    break   #구분자 존재 여부 확인 후 반복문 종료
                    
            
            #Regist script
            try:
                    scripts[audio] = script
            except:
                Exception(
                    '''음원 파일명과 그에 해당하는 스크립트로 구성된 transcript 파일을 올바르게 읽을 수 없습니다.
                    `processor.py`의 `get_scripts` 함수를 사용자의 상황에 맞게 수정하여 주세요.'''
                )
    return scripts   #not script file


def get_audios(path: str, speaker_sep_idx: int) -> tuple[str, str]:
    '''
    음원 파일 해당 여부 판단 후,\n
    audio(str), speaker_sep(str) 반환\n
    * 해당하지 않을 경우, '', ''로 반환
    

    ※※ 사용자 상황에 맞게 수정할 것 ※※
    
    :param path: 파일 경로
    :type path: str
    
    :return: audio_name(str)    #확장자 명을 제외한 파일 이름
    :rtype: str
    '''
    #< 조건 >---------
    EQ1 = ('mp3', 'wav', 'flac')    #조건1 mp3, wav, flac 일 것
    #End--------------
    

    file_name, ext = os.path.splitext(os.path.basename(path))
    ext = ext[1:]

    if ext in EQ1:
        return file_name, _split_path(path)[speaker_sep_idx]
    return '', ''


def dir_align() -> None:
    '''
    MFA 실행 전, 데이터 구조 정렬

    mfa_result/
    |--- speaker1/
    |       |--- audio1.wav
    |       |--- audio1.txt
    |       |--- audio2.wav
    |       |--- audio2.txt
    |--- speaker2/
        ...

    1. 스크립트 수집:   scripts = { audio_path(str): script(str), ... }
    2. 음원 수집:       audios = { audio(str): path(str), ... }
    3. 구조 정렬
        3.1 음원 전처리: wav, sample rate
        3.2 음원 대응 스크립트 미존재 시 처리 방법(제외, SST 사용)
    '''
    os.makedirs(hprm.RESULT_DIR, exist_ok=True)   #Create mfa result dir

    speaker_sep_idx = get_speaker_sep_idx(hprm.DATA_DIR)


    scripts, audios = dict(), dict()
    for home, _, files in os.walk(hprm.DATA_DIR):
        for f in files:
            path = f'{home}/{f}'

            #1. collect script
            for audio, script in get_scripts(path).items():
                scripts[audio] = script

            
            #2. collect audios
            audio, sp_sep = get_audios(path, speaker_sep_idx)
            if audio:
                audios[path] = {
                    'audio': audio,
                    'speaker': sp_sep,
                }

    #speaker_sep(str) -> idx(int)로 변환
    #기존 폴더명 형식의 sp_sep(ex: 'jvs014')를
    #speaker의 총 수에 맞추어 0 ~ 00의 int로 변환
    sp_sep_by_idx = dict()
    i = 0
    for v in audios.values():
        sp_sep = v['speaker']
        if sp_sep not in sp_sep_by_idx:
            sp_sep_by_idx[sp_sep] = i
            i += 1

    
    for audio_path, value in audios.items():
        ori_sp_sep = value['speaker']
        new_sp_idx = sp_sep_by_idx[ori_sp_sep]
        audios[audio_path]['speaker'] = new_sp_idx


    #audios에 audio_idx 등록
    #speaker에 해당하는 audio idx
    sp_nums = dict()    #{ speaker_idx(int): audio_idx(int), ... }
    for audio_path, v in audios.items():
        sp_idx = v['speaker']   #앞서 sep -> idx로 변환하였으므로 sp_idx
        if sp_idx in sp_nums:
            sp_nums[sp_idx] += 1
        else:
            sp_nums[sp_idx] = 0
        
        audios[audio_path]['audio_idx'] = sp_nums[sp_idx]


    #3. 구조 재구성
    path_no_script = list()    #script가 존재하지 않는 audio path 리스트
    for audio_path, value in tqdm(audios.items()):
        audio_name, sp_idx, audio_idx = \
            value['audio'], value['speaker'], value['audio_idx']

        #load audio
        audio, ori_sr = torchaudio.load(audio_path)

        #Resampling
        if ori_sr != hprm.SAMPLE_RATE:
            audio = torchaudio.transforms.Resample(
                orig_freq=ori_sr,
                new_freq=hprm.SAMPLE_RATE,
            )(audio)

        
        #load script
        if audio_name in scripts:
            save_dir = os.path.join(hprm.RESULT_DIR, f'speaker{sp_idx+1}')
            os.makedirs(save_dir, exist_ok=True)

            common_dir = f'{save_dir}/audio{audio_idx+1}'

            #save to wav
            torchaudio.save(
                uri=f'{common_dir}.wav',
                src=audio,
                sample_rate=hprm.SAMPLE_RATE,
                format='wav',
            )

            #save scrip to txt
            with open(f'{common_dir}.txt', 'w', encoding='utf-8') as f:
                f.write(scripts[audio_name])

        else:   #when no script
            path_no_script.append(audio_path)
    

    #print skip path, script 미존재로 건너뛴 음원 목록 표시
    print('< List of audio without script >'.center(50, '-'))
    for i, p in enumerate(path_no_script):
        print(f'{i+1}\t{p}')
    print('-' * 50)

        

def main() -> None:
    dir_align()



if __name__ == '__main__':
    main()