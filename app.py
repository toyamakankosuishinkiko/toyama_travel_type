import streamlit as st
import datetime
import json
import urllib.request
import urllib.parse

# ============================================================
# 基本設定
# ============================================================
st.set_page_config(
    page_title="富山旅タイプ診断 by きときと君",
    page_icon="🏔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

KITOKITO_IMG = "https://www.genspark.ai/api/files/s/IoU5naSJ"

# Google Apps Script Web App URL（蓄積用）
GAS_URL = "https://script.google.com/macros/s/AKfycbxBoJZRbciwDbi2OY4FhW1vM3To6edgaxEDkK-RaXPQrrCf8sEX_YjvDZKgNP_OuCx-/exec"  

# ============================================================
# カスタムCSS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap');

    .stApp {
        font-family: 'Noto Sans JP', sans-serif;
        background: linear-gradient(180deg, #E8F4FD 0%, #FFFFFF 100%);
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 720px;
    }
    .title-card {
        background: linear-gradient(135deg, #0091DA 0%, #00B4D8 100%);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,145,218,0.3);
        margin-bottom: 1.5rem;
    }
    .title-card h1 {
        font-size: 1.8rem;
        font-weight: 900;
        margin: 0.5rem 0;
        color: white;
    }
    .title-card p {
        font-size: 1rem;
        opacity: 0.95;
        margin: 0.3rem 0;
    }
    .question-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 5px solid #0091DA;
    }
    .question-number {
        color: #0091DA;
        font-weight: 900;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    .question-text {
        font-size: 1.15rem;
        font-weight: 700;
        color: #333;
        line-height: 1.6;
    }
    .scale-container {
        background: #F5F7FA;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-top: 0.8rem;
    }
    .scale-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        color: #555;
        margin-bottom: 0.4rem;
        font-weight: 700;
    }
    .scale-label-left {
        color: #0091DA;
        text-align: left;
        flex: 1;
    }
    .scale-label-center {
        color: #999;
        text-align: center;
        flex: 1;
        font-weight: 400;
    }
    .scale-label-right {
        color: #4CAF50;
        text-align: right;
        flex: 1;
    }
    .progress-container {
        background: #E0E0E0;
        border-radius: 10px;
        height: 8px;
        margin: 0.8rem 0 1.2rem 0;
        overflow: hidden;
    }
    .progress-bar {
        background: linear-gradient(90deg, #0091DA, #4CAF50);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    .result-card {
        background: linear-gradient(135deg, #0091DA 0%, #00B4D8 50%, #4CAF50 100%);
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(0,145,218,0.3);
        margin-bottom: 1.5rem;
    }
    .result-type-code {
        font-size: 2.5rem;
        font-weight: 900;
        letter-spacing: 0.3rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .result-type-name {
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 0.5rem;
    }
    .axis-container {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 0.6rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .axis-label-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    .axis-bar-bg {
        background: #E8F4FD;
        border-radius: 8px;
        height: 24px;
        position: relative;
        overflow: hidden;
    }
    .axis-bar-fill-left {
        position: absolute;
        right: 50%;
        height: 100%;
        background: linear-gradient(270deg, #0091DA, #0091DA);
        border-radius: 8px 0 0 8px;
        transition: width 0.8s ease;
    }
    .axis-bar-fill-right {
        position: absolute;
        left: 50%;
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #4CAF50);
        border-radius: 0 8px 8px 0;
        transition: width 0.8s ease;
    }
    .axis-bar-center {
        position: absolute;
        left: 50%;
        top: 0;
        width: 2px;
        height: 100%;
        background: #999;
        transform: translateX(-50%);
    }
    .axis-percentage {
        text-align: center;
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.3rem;
    }
    .speech-bubble {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 2px solid #0091DA;
        margin: 1rem 0;
    }
    .speech-bubble::before {
        content: '';
        position: absolute;
        top: -12px;
        left: 40px;
        width: 0;
        height: 0;
        border-left: 12px solid transparent;
        border-right: 12px solid transparent;
        border-bottom: 12px solid #0091DA;
    }
    .spot-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        text-align: center;
        border-top: 4px solid #0091DA;
        height: 100%;
    }
    .spot-name {
        font-weight: 900;
        font-size: 1rem;
        color: #0091DA;
        margin: 0.5rem 0 0.3rem 0;
    }
    .spot-desc {
        font-size: 0.82rem;
        color: #666;
        line-height: 1.5;
    }
    .stButton > button {
        background: linear-gradient(135deg, #0091DA 0%, #00B4D8 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 0.8rem 2.5rem;
        font-size: 1.1rem;
        font-weight: 700;
        font-family: 'Noto Sans JP', sans-serif;
        box-shadow: 0 4px 15px rgba(0,145,218,0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,145,218,0.4);
        background: linear-gradient(135deg, #007BC0 0%, #0091DA 100%);
        color: white;
    }
    div[role="radiogroup"] {
        display: flex;
        justify-content: space-between;
        gap: 0.3rem;
    }
    div[role="radiogroup"] label {
        flex: 1;
        text-align: center;
        background: white;
        border: 2px solid #DDD;
        border-radius: 10px;
        padding: 0.6rem 0.2rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.78rem;
        font-weight: 700;
        min-width: 0;
    }
    div[role="radiogroup"] label:hover {
        border-color: #0091DA;
        background: #E8F4FD;
    }
    footer {display: none;}
    .viewerBadge_container__r5tak {display: none;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# データ定義
# ============================================================
QUESTIONS = [
    {"id": "q1", "axis": "SA", "text": "旅先での理想の朝は？",
     "left": "温泉に浸かってからゆっくり朝食", "right": "早起きして絶景スポットへ出発"},
    {"id": "q2", "axis": "SA", "text": "旅行の一番の楽しみは？",
     "left": "宿でくつろぎ、日常を忘れること", "right": "知らない場所を自分の足で巡ること"},
    {"id": "q3", "axis": "SA", "text": "友人に旅行の感想を聞かれたら？",
     "left": "「とにかく癒された！」と答える", "right": "「めちゃくちゃ充実してた！」と答える"},
    {"id": "q4", "axis": "SA", "text": "旅先で自由な半日があったら？",
     "left": "露天風呂やスパでのんびり過ごす", "right": "レンタカーで少し遠くまでドライブ"},
    {"id": "q5", "axis": "SA", "text": "旅で重視するのは？",
     "left": "心と身体をリフレッシュすること", "right": "非日常のワクワク感を味わうこと"},
    {"id": "q6", "axis": "CN", "text": "旅先で写真を撮るなら？",
     "left": "美しい建築や歴史ある街並み", "right": "山・海・川など大自然の風景"},
    {"id": "q7", "axis": "CN", "text": "ガイドブックで最初に見るページは？",
     "left": "美術館・博物館・歴史スポット", "right": "自然景観・絶景・ハイキング"},
    {"id": "q8", "axis": "CN", "text": "休日の過ごし方に近いのは？",
     "left": "美術展や博物館に足を運ぶ", "right": "公園や自然の中を散策する"},
    {"id": "q9", "axis": "CN", "text": "旅先で感動するのは？",
     "left": "地域の歴史や文化に触れたとき", "right": "壮大な自然の景色を目にしたとき"},
    {"id": "q10", "axis": "CN", "text": "旅の思い出として残りやすいのは？",
     "left": "訪れた寺社仏閣や街の雰囲気", "right": "目にした山や海の絶景"},
    {"id": "q11", "axis": "GE", "text": "旅行の計画で最初に調べるのは？",
     "left": "その土地ならではの食べ物やお店", "right": "現地でできるアクティビティやイベント"},
    {"id": "q12", "axis": "GE", "text": "旅の予算を多めに使いたいのは？",
     "left": "美味しいものを食べること", "right": "ここでしかできない体験をすること"},
    {"id": "q13", "axis": "GE", "text": "お土産を選ぶなら？",
     "left": "地元の名産品やお菓子・食材", "right": "体験の記念品やご当地グッズ"},
    {"id": "q14", "axis": "GE", "text": "旅先の市場に来たら？",
     "left": "新鮮な食材や食べ歩きを楽しむ", "right": "市場の活気や文化的な雰囲気を楽しむ"},
    {"id": "q15", "axis": "GE", "text": "旅で「来てよかった！」と感じる瞬間は？",
     "left": "想像以上に美味しいものに出会えたとき", "right": "予想外の体験やイベントに遭遇したとき"},
    {"id": "q16", "axis": "DW", "text": "旅行のスタイルに近いのは？",
     "left": "少ないスポットをじっくり味わう", "right": "できるだけ多くの場所を巡る"},
    {"id": "q17", "axis": "DW", "text": "旅行の日数を選べるなら？",
     "left": "2泊以上でゆったりと過ごす", "right": "1泊か日帰りで効率よく回る"},
    {"id": "q18", "axis": "DW", "text": "同じ旅先を何度も訪れるのは？",
     "left": "好きな場所には何度でも行きたい", "right": "新しい場所をどんどん開拓したい"},
    {"id": "q19", "axis": "DW", "text": "旅先の飲食店を選ぶとき？",
     "left": "一軒を吟味して特別な体験にする", "right": "複数の店をハシゴして食べ比べる"},
    {"id": "q20", "axis": "DW", "text": "旅行後に振り返って嬉しいのは？",
     "left": "一つの場所を深く知れたこと", "right": "たくさんの場所を制覇できたこと"},
]

TYPES = {
    "SCGD": {
        "name": "富山じっくり美食の語り部",
        "emoji": "🍣",
        "quote": "老舗の寿司屋のカウンターで、職人と語らいながら富山湾の幸を味わう。それが最高の贅沢。",
        "description": "歴史ある町並みの中で上質な食を味わい、一つの土地に深く根ざすような旅を好むタイプ。富山の伝統文化と食文化の奥深さに惹かれ、何度訪れても新たな発見がある旅を楽しめます。宿での時間も大切にし、地元の食材を使った料理に感動を覚える人です。",
        "spots": [
            {"name": "岩瀬エリア", "desc": "北前船の歴史薫る町並みで地酒と食を堪能", "emoji": "🏘️"},
            {"name": "国宝 高岡山瑞龍寺", "desc": "加賀前田家の壮麗な国宝建築をじっくり鑑賞", "emoji": "⛩️"},
            {"name": "新湊きっときと市場", "desc": "富山湾の新鮮な海の幸を心ゆくまで", "emoji": "🦐"},
        ],
        "data": {"seafood": "白エビ、ブリ", "meal_budget": "15,000〜25,000円", "nights": "2泊以上", "satisfaction": "4.6", "repeat": "高い"}
    },
    "SCGW": {
        "name": "カルチャー×食べ歩きマスター",
        "emoji": "🎨",
        "quote": "午前はガラス美術館、午後は環水公園、夜は回転寿司。富山は1日で何度でも感動できる。",
        "description": "美術館も寺社も寿司屋もハシゴする、文化と食を両方制覇したい欲張りタイプ。短い日程でも効率よく「富山の本質」を掴む力があり、SNSで情報収集してから的確に動きます。一度の旅で多くの刺激を受けたい人です。",
        "spots": [
            {"name": "富山市ガラス美術館", "desc": "隈研吾建築×現代ガラスアートの融合", "emoji": "✨"},
            {"name": "富岩運河環水公園", "desc": "世界一美しいスタバと水辺の散策", "emoji": "☕"},
            {"name": "富山城", "desc": "富山の歴史を学べるコンパクトな城址公園", "emoji": "🏯"},
            {"name": "高岡大仏", "desc": "日本三大大仏のひとつをサクッと訪問", "emoji": "🙏"},
        ],
        "data": {"seafood": "白エビ、ホタルイカ", "meal_budget": "7,500〜15,000円", "nights": "1泊", "satisfaction": "4.4", "repeat": "やや高い"}
    },
    "SCED": {
        "name": "知的好奇心の温泉学者",
        "emoji": "♨️",
        "quote": "美術館で過ごす静かな午後と、温泉宿で味わう夜の静寂。富山には知と癒しが共存する。",
        "description": "美術館や博物館でじっくり時間を使い、宿に戻ったら温泉と読書。文化的な深い体験を求めつつ、心身のリラックスも忘れない知的探究型。ひとつの施設に何時間でもいられる集中力の持ち主です。",
        "spots": [
            {"name": "富山県美術館", "desc": "アート＆デザインと立山連峰の眺望", "emoji": "🖼️"},
            {"name": "宇奈月温泉", "desc": "峡谷に佇む温泉郷でゆったりと", "emoji": "♨️"},
            {"name": "五箇山", "desc": "世界遺産の合掌造り集落に日本の原風景を見る", "emoji": "🏡"},
        ],
        "data": {"seafood": "ブリ、紅ズワイガニ", "meal_budget": "15,000〜25,000円", "nights": "2泊以上", "satisfaction": "4.7", "repeat": "高い"}
    },
    "SCEW": {
        "name": "まちあるきカルチャー探検家",
        "emoji": "🚶",
        "quote": "路面電車に揺られて、知らない路地に迷い込む。富山の街には発見が転がっている。",
        "description": "街をぶらぶら歩きながら偶然の出会いやイベントを楽しむタイプ。歴史的な町並みの中に新しい発見を求め、祭りや地元のイベントにも積極的に参加します。フットワークの軽さが武器です。",
        "spots": [
            {"name": "富山城＆城址公園周辺", "desc": "まちなかの歴史散策の起点に", "emoji": "🏯"},
            {"name": "高岡大仏〜山町筋", "desc": "高岡の土蔵造りの町並みをまちあるき", "emoji": "🏘️"},
            {"name": "海王丸パーク", "desc": "帆船海王丸と新湊大橋の壮観な風景", "emoji": "⛵"},
        ],
        "data": {"seafood": "ホタルイカ、甘エビ", "meal_budget": "4,000〜7,500円", "nights": "日帰り〜1泊", "satisfaction": "4.2", "repeat": "中程度"}
    },
    "SNGD": {
        "name": "富山の恵みに浸る至福の旅人",
        "emoji": "🏔️",
        "quote": "雨晴海岸で立山連峰を眺め、温泉に浸かり、白エビにため息をつく。この幸せに名前はいらない。",
        "description": "温泉、自然の絶景、そして新鮮な海の幸——この三拍子を一つの宿泊エリアでじっくり堪能する、最も多くの富山旅行者に近い「王道」タイプ。何度でも富山を訪れたいと思わせる深い満足感を得る人です。",
        "spots": [
            {"name": "雨晴海岸", "desc": "海越しの立山連峰、日本屈指の絶景", "emoji": "🌊"},
            {"name": "宇奈月温泉", "desc": "黒部峡谷の入口に湧く名湯", "emoji": "♨️"},
            {"name": "ほたるいかミュージアム", "desc": "富山湾の神秘を体感＆味わう", "emoji": "🦑"},
        ],
        "data": {"seafood": "白エビ、ブリ、ホタルイカ", "meal_budget": "15,000〜25,000円", "nights": "2泊以上", "satisfaction": "4.6", "repeat": "非常に高い"}
    },
    "SNGW": {
        "name": "絶景ハンターの美食家",
        "emoji": "📸",
        "quote": "朝は立山を仰ぎ、昼は海辺で刺身定食、夕方は砺波の花畑。富山の全部が、ごちそう。",
        "description": "「あの景色も見たい、あの味も食べたい」——自然の美しさと美味しいものを求めて、テンポよく富山中を巡るタイプ。ドライブしながら絶景ポイントと漁港をハシゴする旅が得意です。",
        "spots": [
            {"name": "雨晴海岸", "desc": "海越しの立山、富山随一の絶景", "emoji": "🌊"},
            {"name": "新湊きっときと市場", "desc": "水揚げされたばかりの海の幸", "emoji": "🦐"},
            {"name": "砺波チューリップ公園", "desc": "春の色鮮やかな花の絨毯", "emoji": "🌷"},
            {"name": "新湊大橋", "desc": "富山湾を一望する美しい斜張橋", "emoji": "🌉"},
        ],
        "data": {"seafood": "白エビ、ブリ、甘エビ", "meal_budget": "7,500〜15,000円", "nights": "1泊", "satisfaction": "4.4", "repeat": "やや高い"}
    },
    "SNED": {
        "name": "大自然と温泉に癒される求道者",
        "emoji": "🧘",
        "quote": "称名滝の轟音と、庄川峡の静寂。自然は語りかけてくる。私はただ、耳を傾けるだけ。",
        "description": "自然の中で心を浄化し、静かな宿で体験を反芻する。自然を「眺め、浸り、感じる」ことに価値を置く瞑想的な旅人。一つの温泉地に連泊して、その土地の空気を吸い尽くします。",
        "spots": [
            {"name": "庄川峡遊覧船", "desc": "四季折々の峡谷美を船上から堪能", "emoji": "🚢"},
            {"name": "称名滝", "desc": "落差350m、日本一の大瀑布の迫力", "emoji": "💧"},
            {"name": "宇奈月温泉", "desc": "峡谷の自然に包まれる癒しの湯", "emoji": "♨️"},
        ],
        "data": {"seafood": "ゲンゲ、ブリ", "meal_budget": "15,000〜25,000円", "nights": "2泊以上", "satisfaction": "4.7", "repeat": "高い"}
    },
    "SNEW": {
        "name": "風まかせの自然派トラベラー",
        "emoji": "🍃",
        "quote": "あの山の向こうに何がある？ 行ってみよう。富山の自然は、いつも答えをくれる。",
        "description": "海も山も花畑も、その日の気分で訪れる先を決める。計画よりも偶然の出会いを楽しみ、イベントがあれば飛び入りで参加する自由な旅人です。",
        "spots": [
            {"name": "雨晴海岸", "desc": "思い立ったら立ち寄れる絶景スポット", "emoji": "🌊"},
            {"name": "海王丸パーク", "desc": "海風を感じながら港町を散策", "emoji": "⛵"},
            {"name": "砺波チューリップ公園", "desc": "季節のイベントに飛び込む", "emoji": "🌷"},
            {"name": "あさひ舟川「春の四重奏」", "desc": "桜・チューリップ・菜の花・残雪の競演", "emoji": "🌸"},
        ],
        "data": {"seafood": "ホタルイカ、甘エビ", "meal_budget": "4,000〜7,500円", "nights": "日帰り〜1泊", "satisfaction": "4.3", "repeat": "中程度"}
    },
    "ACGD": {
        "name": "こだわりの食と歴史を巡る冒険グルマン",
        "emoji": "🗺️",
        "quote": "瑞龍寺で加賀藩の歴史に思いを馳せた後、地元の回転寿司で本気のネタに感動する。それが富山。",
        "description": "積極的に動き回りつつも、食と文化にはとことんこだわる。地元の名店をリサーチし、歴史的背景まで理解した上で味わいます。食卓では誰よりもじっくり向き合うリピーター気質。",
        "spots": [
            {"name": "国宝 高岡山瑞龍寺", "desc": "加賀百二十万石の文化遺産をとことん堪能", "emoji": "⛩️"},
            {"name": "岩瀬エリア", "desc": "北前船の歴史と地元の酒蔵・食を巡る", "emoji": "🏘️"},
            {"name": "新湊きっときと市場", "desc": "プロも唸る鮮度の海の幸", "emoji": "🦐"},
        ],
        "data": {"seafood": "ブリ、白エビ、紅ズワイガニ", "meal_budget": "15,000〜25,000円", "nights": "2泊", "satisfaction": "4.5", "repeat": "高い"}
    },
    "ACGW": {
        "name": "富山フルコース完全制覇の達人",
        "emoji": "🏆",
        "quote": "朝イチで美術館、昼は寿司、午後はまちあるき、夜は地酒。富山は忙しい、でも最高に楽しい。",
        "description": "美術館も回転寿司も大仏も環水公園も全部行く、最も欲張りで行動力のあるタイプ。限られた時間でも計画性と機動力で富山の魅力をフルに味わい尽くします。",
        "spots": [
            {"name": "富山市ガラス美術館", "desc": "建築美とアートを効率よく堪能", "emoji": "✨"},
            {"name": "富岩運河環水公園", "desc": "散策と休憩を兼ねた都市のオアシス", "emoji": "☕"},
            {"name": "高岡大仏", "desc": "サクッと立ち寄れる歴史スポット", "emoji": "🙏"},
            {"name": "新湊きっときと市場", "desc": "ランチに最適な海の幸の宝庫", "emoji": "🦐"},
        ],
        "data": {"seafood": "白エビ、ホタルイカ、ブリ", "meal_budget": "7,500〜15,000円", "nights": "1泊", "satisfaction": "4.5", "repeat": "やや高い"}
    },
    "ACED": {
        "name": "ディープな文化体験アドベンチャラー",
        "emoji": "🔍",
        "quote": "合掌造りの囲炉裏端で地元の方の話を聞く。教科書には載っていない富山が、ここにある。",
        "description": "観光客が行かないような場所にも足を伸ばし、工場見学や伝統工芸体験など「ここでしかできないこと」にじっくり時間を使います。地元の人との交流も楽しむタイプ。",
        "spots": [
            {"name": "五箇山", "desc": "世界遺産の合掌造りで伝統文化を深く体験", "emoji": "🏡"},
            {"name": "富山県美術館", "desc": "デザインとアートの最前線に触れる", "emoji": "🖼️"},
            {"name": "庄川峡遊覧船", "desc": "峡谷の懐に入り込む特別な体験", "emoji": "🚢"},
        ],
        "data": {"seafood": "ゲンゲ、バイガイ", "meal_budget": "7,500〜15,000円", "nights": "2泊以上", "satisfaction": "4.6", "repeat": "高い"}
    },
    "ACEW": {
        "name": "好奇心全開！フルスロット探検家",
        "emoji": "🎪",
        "quote": "富山の祭りに飛び入り参加して、気づいたら地元の人と一緒に踊っていた。旅は、ハプニングが面白い。",
        "description": "文化施設もイベントもアクティビティも、興味があれば何でも飛びつく。行動範囲が広く、一つの旅で何倍もの体験を持ち帰ります。",
        "spots": [
            {"name": "海王丸パーク", "desc": "帆船×イベント、海辺の体験型スポット", "emoji": "⛵"},
            {"name": "富山城＆城址公園周辺", "desc": "まちなかイベントの拠点", "emoji": "🏯"},
            {"name": "黒部峡谷鉄道", "desc": "トロッコで峡谷を駆け抜ける冒険", "emoji": "🚂"},
            {"name": "ほたるいかミュージアム", "desc": "体験型ミュージアムで富山湾の神秘に触れる", "emoji": "🦑"},
        ],
        "data": {"seafood": "ホタルイカ、甘エビ", "meal_budget": "4,000〜7,500円", "nights": "1泊", "satisfaction": "4.3", "repeat": "中程度"}
    },
    "ANGD": {
        "name": "大自然とグルメの求道者",
        "emoji": "⛰️",
        "quote": "雪の大谷を歩いた後のます寿しの美味しさ。自然と食、どちらが主役かなんて決められない。",
        "description": "立山連峰の雄大さに感動し、その余韻とともに最高の一皿を味わう。自然と食のどちらにも妥協せず、一つの旅先に腰を据えてじっくり楽しみます。",
        "spots": [
            {"name": "立山黒部アルペンルート", "desc": "3,000m級の山岳ルートで大自然の絶景", "emoji": "🏔️"},
            {"name": "黒部ダム", "desc": "日本最大級のダムの圧倒的スケール", "emoji": "🌊"},
            {"name": "新湊きっときと市場", "desc": "冒険の後に味わう富山湾の幸", "emoji": "🦐"},
        ],
        "data": {"seafood": "白エビ、ブリ、紅ズワイガニ", "meal_budget": "15,000〜25,000円", "nights": "2泊", "satisfaction": "4.6", "repeat": "高い"}
    },
    "ANGW": {
        "name": "山も海も食も！弾丸グルメハンター",
        "emoji": "🚀",
        "quote": "黒部峡谷でトロッコに乗り、雨晴で絶景を拝み、夜は地元の回転寿司。富山の1日は36時間分。",
        "description": "朝は山、昼は海、夜は寿司。スピード感を持って富山の自然と食を制覇するタイプ。体力と計画力を武器に、短い旅でも密度の濃い体験をします。",
        "spots": [
            {"name": "黒部峡谷鉄道", "desc": "トロッコで秘境を駆け抜ける", "emoji": "🚂"},
            {"name": "雨晴海岸", "desc": "移動の合間にも立ち寄れる絶景", "emoji": "🌊"},
            {"name": "ほたるいかミュージアム", "desc": "食と学びのグルメスポット", "emoji": "🦑"},
            {"name": "立山黒部アルペンルート", "desc": "弾丸でも行く価値のある山岳絶景", "emoji": "🏔️"},
        ],
        "data": {"seafood": "白エビ、ホタルイカ", "meal_budget": "7,500〜15,000円", "nights": "1泊", "satisfaction": "4.4", "repeat": "やや高い"}
    },
    "ANED": {
        "name": "秘境探訪の孤高の冒険家",
        "emoji": "🧗",
        "quote": "称名滝の水しぶきを浴びた瞬間、生きている実感がした。富山の自然は、本気で向き合う人に応えてくれる。",
        "description": "人が少ない場所、まだ知られていない景色を求めて深く入り込む。一つのエリアに連泊してとことん自然と向き合う、最もストイックな旅人です。",
        "spots": [
            {"name": "称名滝", "desc": "日本一の落差を誇る瀑布、自然の圧倒的な力", "emoji": "💧"},
            {"name": "黒部ダム", "desc": "人間の技術と自然の迫力が交差する場所", "emoji": "🌊"},
            {"name": "立山黒部アルペンルート", "desc": "季節ごとに表情を変える山岳の世界", "emoji": "🏔️"},
        ],
        "data": {"seafood": "ゲンゲ、フクラギ", "meal_budget": "7,500〜15,000円", "nights": "2泊以上", "satisfaction": "4.5", "repeat": "高い"}
    },
    "ANEW": {
        "name": "風と波に乗る自由な冒険旅人",
        "emoji": "🌬️",
        "quote": "地図は持たない、予定も立てない。富山の風が連れて行ってくれる場所が、今日の目的地。",
        "description": "行き先も予定も決めずに、自然の中を気ままに巡る。その日の天気や気分で行き先を変える究極の自由旅タイプ。旅に「物語」が生まれます。",
        "spots": [
            {"name": "雨晴海岸", "desc": "ふらっと立ち寄って絶景に出会う", "emoji": "🌊"},
            {"name": "黒部峡谷鉄道", "desc": "気ままにトロッコで秘境へ", "emoji": "🚂"},
            {"name": "あさひ舟川「春の四重奏」", "desc": "季節限定の奇跡のような風景", "emoji": "🌸"},
            {"name": "海王丸パーク", "desc": "港の風を感じる自由な散策", "emoji": "⛵"},
        ],
        "data": {"seafood": "甘エビ、ホタルイカ", "meal_budget": "4,000〜7,500円", "nights": "日帰り〜1泊", "satisfaction": "4.2", "repeat": "中程度"}
    },
}

# ============================================================
# ユーティリティ関数
# ============================================================
def calculate_scores(answers):
    axis_scores = {"SA": 0, "CN": 0, "GE": 0, "DW": 0}
    for q in QUESTIONS:
        qid = q["id"]
        axis = q["axis"]
        if qid in answers:
            axis_scores[axis] += answers[qid]
    return axis_scores

def determine_type(scores):
    code = ""
    code += "S" if scores["SA"] <= 0 else "A"
    code += "C" if scores["CN"] <= 0 else "N"
    code += "G" if scores["GE"] <= 0 else "E"
    code += "D" if scores["DW"] <= 0 else "W"
    return code

def get_axis_percentage(score, max_score=10):
    pct = (score + max_score) / (2 * max_score) * 100
    return max(0, min(100, pct))

def render_axis_bar(label_left, label_right, score, emoji_left, emoji_right):
    pct = get_axis_percentage(score)
    if score <= 0:
        fill_width = abs(50 - pct)
        dominant = label_left
        dominant_pct = 100 - pct
    else:
        fill_width = pct - 50
        dominant = label_right
        dominant_pct = pct

    bar_html = f"""
    <div class="axis-container">
        <div class="axis-label-row">
            <span style="color:#0091DA;">{emoji_left} {label_left}</span>
            <span style="color:#4CAF50;">{label_right} {emoji_right}</span>
        </div>
        <div class="axis-bar-bg">
            <div class="axis-bar-center"></div>
            {"<div class='axis-bar-fill-left' style='width:" + str(fill_width) + "%;'></div>" if score <= 0 else ""}
            {"<div class='axis-bar-fill-right' style='width:" + str(fill_width) + "%;'></div>" if score > 0 else ""}
        </div>
        <div class="axis-percentage">{dominant} 寄り（{dominant_pct:.0f}%）</div>
    </div>
    """
    return bar_html

def save_to_gas(answers, scores, type_code):
    if not GAS_URL:
        return
    try:
        payload = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "answers": json.dumps(answers),
            "score_SA": scores["SA"],
            "score_CN": scores["CN"],
            "score_GE": scores["GE"],
            "score_DW": scores["DW"],
            "type_code": type_code,
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(GAS_URL, data=data, method="POST")
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass

# ============================================================
# Session State 初期化
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "top"
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}

# ============================================================
# トップ画面
# ============================================================
if st.session_state.page == "top":
    st.markdown("<div style='text-align:center; margin-top:1rem;'>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(KITOKITO_IMG, width=200)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="title-card">
        <h1>🏔️ 富山旅タイプ診断</h1>
        <p>あなたの「富山旅タイプ」は全16タイプのどれ？</p>
        <p>きときと君と一緒に20の質問に答えて</p>
        <p>ぴったりの富山旅を見つけよう！</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; color:#666; font-size:0.9rem; margin-bottom:1rem;">
        ⏱️ 所要時間：約3分 ｜ 📊 5,165人の旅行データに基づく診断
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚅 診断をはじめる", key="start_btn"):
            st.session_state.page = "quiz"
            st.session_state.current_q = 0
            st.session_state.answers = {}
            st.rerun()

# ============================================================
# 設問画面
# ============================================================
elif st.session_state.page == "quiz":
    idx = st.session_state.current_q
    q = QUESTIONS[idx]
    progress = idx / len(QUESTIONS)

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.2rem;">
        <span style="font-weight:700; color:#0091DA; font-size:0.9rem;">Q{idx+1} / {len(QUESTIONS)}</span>
        <span style="font-size:0.8rem; color:#999;">あと{len(QUESTIONS)-idx}問</span>
    </div>
    <div class="progress-container">
        <div class="progress-bar" style="width:{progress*100}%;"></div>
    </div>
    """, unsafe_allow_html=True)

    col_img, col_text = st.columns([1, 5])
    with col_img:
        st.image(KITOKITO_IMG, width=60)
    with col_text:
        st.markdown(f"""
        <div class="question-card">
            <div class="question-number">Question {idx+1}</div>
            <div class="question-text">{q["text"]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="scale-container">
        <div class="scale-labels">
            <span class="scale-label-left">👈 {q["left"]}</span>
        </div>
        <div class="scale-labels" style="margin-top:0.3rem;">
            <span class="scale-label-right">👉 {q["right"]}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    options = ["とても左寄り", "やや左寄り", "どちらともいえない", "やや右寄り", "とても右寄り"]
    score_values = [-2, -1, 0, 1, 2]

    default_idx = 2
    if q["id"] in st.session_state.answers:
        prev_val = st.session_state.answers[q["id"]]
        default_idx = score_values.index(prev_val)

    selected = st.radio(
        "選んでください",
        options=options,
        index=default_idx,
        horizontal=True,
        key=f"radio_{q['id']}",
        label_visibility="collapsed"
    )

    sel_idx = options.index(selected)
    st.session_state.answers[q["id"]] = score_values[sel_idx]

    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if idx > 0:
            if st.button("← 戻る", key="prev_btn"):
                st.session_state.current_q -= 1
                st.rerun()
    with col3:
        if idx < len(QUESTIONS) - 1:
            if st.button("次へ →", key="next_btn"):
                st.session_state.current_q += 1
                st.rerun()
        else:
            if st.button("🔍 結果を見る", key="result_btn"):
                st.session_state.page = "loading"
                st.rerun()

# ============================================================
# ローディング画面
# ============================================================
elif st.session_state.page == "loading":
    st.markdown("<div style='height:3rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(KITOKITO_IMG, width=150)
    st.markdown("""
    <div style="text-align:center; margin-top:1rem;">
        <h2 style="color:#0091DA;">🔍 きときと君が分析中...</h2>
        <p style="color:#666;">あなたの旅タイプを5,165人のデータから診断しています</p>
    </div>
    """, unsafe_allow_html=True)

    import time
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.02)
        progress_bar.progress(i + 1)

    scores = calculate_scores(st.session_state.answers)
    type_code = determine_type(scores)
    st.session_state.scores = scores
    st.session_state.type_code = type_code
    save_to_gas(st.session_state.answers, scores, type_code)
    st.session_state.page = "result"
    st.rerun()

# ============================================================
# 結果画面
# ============================================================
elif st.session_state.page == "result":
    scores = st.session_state.scores
    type_code = st.session_state.type_code
    type_info = TYPES[type_code]

    st.markdown(f"""
    <div class="result-card">
        <p style="font-size:1rem; opacity:0.9; margin-bottom:0.3rem;">あなたの富山旅タイプは...</p>
        <div class="result-type-code">{type_info["emoji"]} {type_code}</div>
        <div class="result-type-name">{type_info["name"]}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📊 あなたの4つの旅スタイル")
    st.markdown(render_axis_bar("癒し（S）", "冒険（A）", scores["SA"], "😌", "🤩"), unsafe_allow_html=True)
    st.markdown(render_axis_bar("文化（C）", "自然（N）", scores["CN"], "🏛️", "🏔️"), unsafe_allow_html=True)
    st.markdown(render_axis_bar("グルメ（G）", "体験（E）", scores["GE"], "🍣", "🎪"), unsafe_allow_html=True)
    st.markdown(render_axis_bar("じっくり（D）", "広く（W）", scores["DW"], "🔍", "🗺️"), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    col_img, col_bubble = st.columns([1, 5])
    with col_img:
        st.image(KITOKITO_IMG, width=70)
    with col_bubble:
        st.markdown(f"""
        <div class="speech-bubble">
            <p style="font-style:italic; color:#0091DA; font-weight:700; font-size:1.05rem; margin-bottom:0.8rem;">
                「{type_info["quote"]}」
            </p>
            <p style="color:#333; line-height:1.8; font-size:0.95rem;">
                {type_info["description"]}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🗺️ きときと君のおすすめスポット")
    spots = type_info["spots"]
    cols = st.columns(len(spots))
    for i, spot in enumerate(spots):
        with cols[i]:
            st.markdown(f"""
            <div class="spot-card">
                <div style="font-size:2rem;">{spot["emoji"]}</div>
                <div class="spot-name">{spot["name"]}</div>
                <div class="spot-desc">{spot["desc"]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    with st.expander("📈 このタイプの富山旅データを見る"):
        data = type_info["data"]
        st.markdown(f"""
        | 項目 | データ |
        |---|---|
        | 🍣 よく食べている海の幸 | {data["seafood"]} |
        | 💰 平均消費額（飲食） | {data["meal_budget"]} |
        | 🏨 平均宿泊数 | {data["nights"]} |
        | 😊 旅行全体の満足度 | {data["satisfaction"]} / 5.0 |
        | 🔄 リピート傾向 | {data["repeat"]} |
        """)

    with st.expander("📋 全16タイプを見る"):
        for code, info in TYPES.items():
            if code == type_code:
                st.markdown(f"**👉 {info['emoji']} {code} — {info['name']} 👈（あなた）**")
            else:
                st.markdown(f"{info['emoji']} **{code}** — {info['name']}")

    st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 もう一度診断する", key="retry_btn"):
            st.session_state.page = "top"
            st.session_state.current_q = 0
            st.session_state.answers = {}
            st.rerun()
    with col2:
        share_text = f"私の富山旅タイプは「{type_info['name']}」（{type_code}）でした！ #富山旅タイプ診断 #きときと君"
        share_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}"
        st.markdown(f'<a href="{share_url}" target="_blank" style="display:block; text-align:center; background:linear-gradient(135deg,#1DA1F2,#0091DA); color:white; padding:0.8rem; border-radius:30px; text-decoration:none; font-weight:700; font-size:1rem;">📤 Xでシェアする</a>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top:2rem; padding:1rem; color:#999; font-size:0.75rem;">
        <p>富山旅タイプ診断 by きときと君</p>
        <p>データ出典：富山県観光ウェブアンケート（n=5,165）</p>
        <p>© とやま観光推進機構</p>
    </div>
    """, unsafe_allow_html=True)
