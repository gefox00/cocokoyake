import streamlit as st
import requests
import json


class ykch_converter:
    target = ''

    def __init__(self, url):
        self.target = url

    def cocoforia(self, dict_order: bool = False):
        # サーバーからデータを取得
        target_url = self.target + '.js'
        # データをJsonで確保
        res = requests.get(target_url).json()
        # データ組み立て用変数のセット
        memo = ''
        command = '＝＝＝＝＝ゆめ管理＝＝＝＝＝\n'
        param = []
        out_data = {"kind": "character"}
        status_data = []
        # パレット生成とパラメータ生成
        status_data.append({'label': f'おもい', 'value': 0, 'max': 0})
        status_data.append({'label': f'ふしぎ', 'value': 0, 'max': 0})
        status_data.append({'label': f'ゆめ', 'value': 0, 'max': 0})
        param.append({'label': 'しょうたい', 'value': res['shuzoku_name']})
        param.append({'label': 'へんげ', 'value': res['NC1']})
        param.append({'label': 'けもの', 'value': res['NC2']})
        param.append({'label': 'おとな', 'value': res['NC3']})
        param.append({'label': 'こども', 'value': res['NC4']})

        for i in res['tunagarid_dst']:
            status_data.append({'label': f'{i}へのゆめ', 'value': 0, 'max': 0})
            command += f':{i}へのゆめ+1\n'
            command += f'現在の{i}へのゆめ' + '{' + f'{i}へのゆめ' + '}\n'
            command += f':{i}へのゆめ=0\n'
            command += f':{i}へのつながり+1\n'
            param.append({'label': f'{i}への感情', 'value': '受容'})
        for i in res['tunagari_dst']:
            status_data.append({'label': f'{i}へのゆめ', 'value': 0, 'max': 0})
            command += f':{i}へのゆめ+1\n'
            command += f'現在の{i}へのゆめ' + '{' + f'{i}へのゆめ' + '}\n'
            command += f':{i}へのゆめ=0\n'

        for ch, emo in zip(res['tunagari_dst'], res['tunagarid_name'][1:]):
            param.append({'label': f'{ch}への感情', 'value': emo})
        command += '\n＝＝＝＝＝能力＝＝＝＝＝\n'
        for cat, flv, name, cost in zip(res['Powers_lv'], res['Powers_kouka'],
                                        res['Powers_name'], res['Powers_koukatime']):
            command += cat + ' ' + name + '：{' + name + '}\n'
            param.append({'label': name, 'value': f'コスト{cost}：{flv}'})
            memo += f'{cat}：{name}：{cost}\n{flv}\n\n'
            memo = memo[:-1]
        status_data.append({'label': '町へのつながり', 'value': 2, 'max': 5})

        for i in res['tunagari_dst']:
            match i:
                case _:
                    status_data.append({'label': f'{i}へのつながり', 'value': 2, 'max': 5})

        temp = {'name': res['pc_name'], 'initiative': 0,
                'externalUrl': str(self.target), 'memo': memo, 'commands': command,
                'status': status_data, 'params': param}
        out_data['data'] = temp
        if dict_order:
            str_out = out_data
        else:
            str_out = str(out_data).replace('\'', '"')
        return str_out


st.title('ココこやけフォーマット')

st.text_input(label='変換したいキャラシのURLを入力', key='-input-')
st.write('このツールはキャラクター保管所（下記URLのサイト）の')
st.write('ゆうやけこやけのキャラクターをココフォリアの駒に変換するためのツールです')
st.write('https://charasheet.vampire-blood.net/')
# セッションのコンポーネントのアクセスを簡略化
asset = st.session_state

get_button = st.button(label='変換', key='-convert-')
save_button = st.button(label='変換したデータをテキストで保存', key='-save_txt-')
# イベント処理
# 変換ボタン
if get_button and len(asset['-input-']) > 0:
    target = asset['-input-'] + '.js'
    target_json = requests.get(target).json()
    if 'https://charasheet.vampire-blood.net' in target and target_json['game'] == 'yukoya':
        convert = ykch_converter(asset['-input-']).cocoforia(True)
        st.write(
            '表示された変換データの右上に表示されているコピーボタンを押してデータをコピーして\nココフォリアに張り付けてください')
        st.code(json.dumps(convert), 'json')
        for ii in convert['data']:
            st.write(f'{ii} : {convert['data'][ii]}')

# テキストファイル保存ボタン
if save_button and len(asset['-input-']) > 0:
    target = asset['-input-'] + '.js'
    target_json = requests.get(target).json()
    convert = {}
    if 'https://charasheet.vampire-blood.net' in target and target_json['game'] == 'yukoya':
        convert = ykch_converter(asset['-input-']).cocoforia(True)
    text_data = json.dumps(convert, indent=4)

    # テキストデータをバイト形式に変換
    text_bytes = text_data.encode('utf-8')
    filename = ''
    print(convert)
    if len(convert["data"]["name"]) > 0:
        filename = convert["data"]["name"]
    else:
        filename = 'ななしのへんげ.txt'
    # ダウンロードボタンを作成
    st.download_button(
        label="テキストファイルをダウンロード",
        data=text_bytes,
        file_name=filename,
        mime="text/plain"
    )
