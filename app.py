import streamlit as st
import streamlit.components.v1 as components
import datetime
import json
import urllib.request
import urllib.parse

# ============================================================
# 設定
# ============================================================
st.set_page_config(
    page_title="富山旅タイプ診断",
    page_icon="🏔️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

GAS_URL = ""  # GASデプロイ後にURLを貼り付け

# ============================================================
# CSS（丸ボタン以外の要素用）
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&display=swap');
.stApp {
    font-family: 'Noto Sans JP', sans-serif;
    background: linear-gradient(180deg, #E8F4FD 0%, #FFFFFF 100%);
}
header[data-testid="stHeader"] { display: none; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.title-card {
    background: linear-gradient(135deg, #0091DA 0%, #00B4D8 100%);
    border-radius: 20px; padding: 2.5rem 2rem; text-align: center;
    color: white; margin-bottom: 1.5rem; box-shadow: 0 8px 32px rgba(0,145,218,0.3);
}
.title-card h1 { font-size: 2rem; font-weight: 900; margin: 0 0 0.5rem 0; color: white; }
.title-card p { font-size: 1rem; opacity: 0.9; margin: 0; color: white; }
.question-card {
    background: white; border-radius: 16px; padding: 2rem; margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.question-text { font-size: 1.15rem; font-weight: 700; color: #333; margin-bottom: 0; line-height: 1.6; }
.progress-container { background: #E0E0E0; border-radius: 10px; height: 8px; margin: 0.5rem 0 1.5rem 0; overflow: hidden; }
.progress-fill { background: linear-gradient(90deg, #0091DA, #00B4D8); height: 100%; border-radius: 10px; transition: width 0.4s ease; }
button[kind="primary"], button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #0091DA, #00B4D8) !important;
    border: none !important; color: white !important; border-radius: 30px !important;
    font-weight: 700 !important; padding: 0.8rem 2rem !important; font-size: 1rem !important;
}
button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #007BBD, #0091DA) !important;
}
.back-btn button {
    background: #DDD !important; color: #666 !important; border: none !important;
    border-radius: 30px !important; width: 100%; padding: 0.7rem 2rem !important; font-weight: 700 !important;
}
.back-btn button:hover { background: #CCC !important; color: #555 !important; }
.result-card {
    background: linear-gradient(135deg, #0091DA 0%, #00B4D8 100%);
    border-radius: 20px; padding: 2.5rem 2rem; text-align: center;
    color: #FFFFFF; margin: 1rem 0; box-shadow: 0 8px 32px rgba(0,145,218,0.3);
}
.result-card h2 { color: #FFFFFF; font-size: 1.5rem; font-weight: 900; margin-bottom: 0.3rem; text-shadow: 0 2px 8px rgba(0,0,0,0.15); }
.result-card .type-code { font-size: 2.5rem; font-weight: 900; color: #FFFFFF; letter-spacing: 0.15em; text-shadow: 0 2px 10px rgba(0,0,0,0.2); }
.result-card .type-name { font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin: 0.5rem 0; text-shadow: 0 1px 6px rgba(0,0,0,0.15); }
.result-card .type-tagline { font-size: 1rem; color: #FFFFFF; opacity: 0.95; font-style: italic; text-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.result-card .type-desc { font-size: 0.95rem; color: #FFFFFF; opacity: 0.9; margin-top: 1rem; line-height: 1.7; text-shadow: 0 1px 4px rgba(0,0,0,0.1); }
.spot-card {
    background: white; border-radius: 12px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); border-left: 4px solid #0091DA;
}
.spot-card h4 { color: #0091DA; margin: 0 0 0.3rem 0; font-size: 1rem; }
.spot-card p { color: #555; font-size: 0.85rem; margin: 0; line-height: 1.5; }
.axis-bar-container { margin: 0.8rem 0; }
.axis-bar-labels { display: flex; justify-content: space-between; font-size: 0.8rem; color: #555; margin-bottom: 4px; }
.axis-bar { background: #E0E0E0; border-radius: 6px; height: 12px; position: relative; overflow: visible; }
.axis-bar-marker {
    position: absolute; top: -4px; width: 20px; height: 20px;
    background: white; border: 3px solid #0091DA; border-radius: 50%;
    transform: translateX(-50%); box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 質問データ
# ============================================================
QUESTIONS = [
    {"axis": "SA", "text": "旅先での理想の朝の過ごし方は？", "left": "温泉や宿でゆっくり", "right": "早起きして絶景スポットへ"},
    {"axis": "SA", "text": "旅行の醍醐味は？", "left": "日常を忘れてリラックス", "right": "非日常のスリルや冒険"},
    {"axis": "SA", "text": "旅先で雨が降ったら？", "left": "宿や温泉でのんびり過ごす", "right": "雨でも外に出て探索する"},
    {"axis": "SA", "text": "旅行中に空き時間ができたら？", "left": "カフェでゆったりくつろぐ", "right": "予定外のスポットを探しに行く"},
    {"axis": "SA", "text": "宿を選ぶ基準は？", "left": "設備や温泉の質を最重視", "right": "アクティビティへのアクセス重視"},
    {"axis": "CN", "text": "旅先でカメラを向けるのは？", "left": "建築物や街並み・アート", "right": "山・海・花などの自然"},
    {"axis": "CN", "text": "「感動した！」と言いそうな場面は？", "left": "美術館で素晴らしい作品に出会う", "right": "展望台から絶景を見渡す"},
    {"axis": "CN", "text": "旅の思い出として残りやすいのは？", "left": "歴史ある建造物やお寺の雰囲気", "right": "雄大な山や美しい海岸線"},
    {"axis": "CN", "text": "ガイドブックで最初に開くページは？", "left": "博物館・美術館・文化財特集", "right": "絶景・自然・ハイキング特集"},
    {"axis": "CN", "text": "SNSでシェアしたくなる写真は？", "left": "おしゃれな建物やアート空間", "right": "大自然のダイナミックな風景"},
    {"axis": "GE", "text": "旅行の計画で最初に調べるのは？", "left": "その土地の名物料理やお店", "right": "体験できるアクティビティ"},
    {"axis": "GE", "text": "旅の満足度を最も左右するのは？", "left": "美味しい食事に出会えたかどうか", "right": "心に残る体験ができたかどうか"},
    {"axis": "GE", "text": "旅行のお土産は？", "left": "地元の食材やお菓子を買いたい", "right": "体験の記念品や写真が宝物"},
    {"axis": "GE", "text": "自由時間が2時間あったら？", "left": "地元で評判のお店を食べ歩き", "right": "気になるワークショップに参加"},
    {"axis": "GE", "text": "旅先で一番テンションが上がる瞬間は？", "left": "期待以上に美味しい料理が出てきた時", "right": "初めてのアクティビティに挑戦する時"},
    {"axis": "DW", "text": "旅行のスタイルは？", "left": "少ない場所をじっくり深く楽しむ", "right": "できるだけ多くの場所を回りたい"},
    {"axis": "DW", "text": "1つの観光地での滞在時間は？", "left": "たっぷり時間をかけて堪能する", "right": "サクッと見てどんどん次へ行く"},
    {"axis": "DW", "text": "理想の旅行計画は？", "left": "余白の多いゆとりあるスケジュール", "right": "分刻みで詰め込んだスケジュール"},
    {"axis": "DW", "text": "旅先の飲食店選びは？", "left": "1軒のお店でコースをじっくり", "right": "何軒もハシゴして色々味わう"},
    {"axis": "DW", "text": "帰宅後に旅を振り返ると？", "left": "1つの体験を深く語りたい", "right": "たくさんの場所の写真を見せたい"},
]

# ============================================================
# 16タイプ定義
# ============================================================
SPOT_DETAILS = {
    "雨晴海岸": "富山湾越しに望む立山連峰の絶景。万葉集にも詠まれた景勝地です。",
    "宇奈月温泉": "黒部峡谷の玄関口に位置する富山県随一の温泉郷。美肌の湯として有名です。",
    "富山市ガラス美術館": "隈研吾設計の美しい建築。現代ガラスアートの世界的コレクションを所蔵しています。",
    "富岩運河環水公園": "「世界一美しいスタバ」があることでも有名な、富山駅近くの水辺の公園です。",
    "国宝 高岡山瑞龍寺": "加賀前田家2代当主の菩提寺。国宝に指定された壮麗な伽藍が見どころです。",
    "新湊きっときと市場": "富山湾の新鮮な海の幸が勢揃い。白えびやホタルイカなど富山の味覚を堪能できます。",
    "五箇山": "世界遺産の合掌造り集落。日本の原風景が残る静かな山里です。",
    "立山黒部アルペンルート": "標高3,000m級の北アルプスを貫く山岳観光ルート。雪の大谷は圧巻です。",
    "黒部峡谷鉄道": "トロッコ電車で行く日本一深いV字峡谷。秘境の絶景が続きます。",
    "黒部ダム": "日本最大級のアーチ式ダム。186mからの放水は大迫力です。",
    "称名滝": "落差350m、日本一の滝。轟音と水しぶきの迫力は圧倒的です。",
    "岩瀬エリア": "北前船で栄えた港町。歴史的な町並みと日本酒の酒蔵が楽しめます。",
    "海王丸パーク": "美しい帆船「海王丸」が係留された港。新湊大橋の眺望も見事です。",
    "富山城": "富山市中心部のシンボル。郷土博物館として富山の歴史を伝えています。",
    "高岡大仏": "日本三大仏のひとつ。端正な顔立ちで「イケメン大仏」とも呼ばれます。",
    "砺波チューリップ公園": "300品種300万本のチューリップが咲き誇る日本最大級の花の公園です。",
    "ほたるいかミュージアム": "神秘的なホタルイカの生態を学べる体験型博物館。発光ショーは必見です。",
    "富山県美術館": "「アート＆デザイン」をテーマにした美術館。屋上のオノマトペ広場も人気です。",
    "庄川峡遊覧船": "エメラルドグリーンの庄川を遊覧。四季折々の渓谷美が楽しめます。",
    "新湊大橋": "富山新港に架かる日本海側最大級の斜張橋。ライトアップも美しいです。",
    "あさひ舟川「春の四重奏」": "桜並木・チューリップ・菜の花・残雪の北アルプスが織りなす絶景です。",
}

TYPES = {
    "SCGD": {"name": "富山じっくり美食の語り部", "tagline": "「老舗の寿司屋のカウンターで、時を忘れて語らう」", "desc": "歴史ある町並みを散策し、上質な食をじっくり堪能するのがあなたのスタイル。急がず焦らず、一つひとつの味と文化に深く向き合う旅を好みます。", "spots": ["岩瀬エリア", "国宝 高岡山瑞龍寺", "新湊きっときと市場"]},
    "SCGW": {"name": "富山カルチャー×食べ歩きマスター", "tagline": "「午前は美術館、午後は回転寿司、夜は地酒バー」", "desc": "文化もグルメも効率よく制覇するのがあなた流。限られた時間で最大限の「美味しい」と「美しい」を回収します。", "spots": ["富山市ガラス美術館", "富岩運河環水公園", "富山城", "高岡大仏"]},
    "SCED": {"name": "知的好奇心の温泉学者", "tagline": "「美術館で知を磨き、温泉で心を解き放つ」", "desc": "美術館や博物館で知的好奇心を満たした後は、温泉でゆっくりリフレッシュ。インプットとリラックスのバランスが絶妙な旅人です。", "spots": ["富山県美術館", "宇奈月温泉", "五箇山"]},
    "SCEW": {"name": "まちあるきカルチャー探検家", "tagline": "「路面電車に揺られて、未知の路地へ飛び込む」", "desc": "街歩きで偶然の出会いを楽しむタイプ。文化イベントや体験プログラムにも積極的に参加し、知らない世界を広く探ります。", "spots": ["富山城", "高岡大仏", "海王丸パーク", "岩瀬エリア"]},
    "SNGD": {"name": "富山の恵みに浸る至福の旅人", "tagline": "「雨晴海岸で絶景、温泉で極楽、白エビで至福」", "desc": "自然の美しさと温泉の癒し、そして海の幸を心ゆくまで堪能する三拍子の旅。一つの場所でじっくりと富山の恵みに浸ります。", "spots": ["雨晴海岸", "宇奈月温泉", "ほたるいかミュージアム"]},
    "SNGW": {"name": "絶景ハンターの美食家", "tagline": "「朝は立山の絶景、昼は港町の海の幸」", "desc": "自然の絶景ポイントを効率よく回りながら、行く先々でご当地グルメも欠かさない欲張りスタイル。テンポよく「映え×美味」を巡ります。", "spots": ["雨晴海岸", "新湊きっときと市場", "砺波チューリップ公園", "新湊大橋"]},
    "SNED": {"name": "大自然と温泉に癒される求道者", "tagline": "「称名滝の轟音を聴きながら、温泉で心を浄化する」", "desc": "壮大な自然と温泉だけがあればいい。人混みを避け、大自然の静寂の中でじっくり自分と向き合う、究極の癒し旅を求めます。", "spots": ["庄川峡遊覧船", "称名滝", "宇奈月温泉"]},
    "SNEW": {"name": "風まかせの自然派トラベラー", "tagline": "「風の向くまま、山から海へ」", "desc": "計画はほどほどに、自然が美しい場所を気の向くままに巡ります。花畑も海岸も山も、広く浅くではなく「広く美しく」がモットーです。", "spots": ["雨晴海岸", "海王丸パーク", "砺波チューリップ公園", "あさひ舟川「春の四重奏」"]},
    "ACGD": {"name": "こだわりの食と歴史を巡る冒険グルマン", "tagline": "「国宝の前で感動し、路地裏の名店で唸る」", "desc": "歴史深いスポットを探訪しつつ、地元の人しか知らない食の名店を発掘するのが生きがい。こだわりと冒険心が同居する旅人です。", "spots": ["国宝 高岡山瑞龍寺", "岩瀬エリア", "新湊きっときと市場"]},
    "ACGW": {"name": "富山フルコース完全制覇の達人", "tagline": "「朝は美術館、昼は寿司、夜は地酒、全部制覇！」", "desc": "文化施設もグルメスポットも余すところなく巡りたい完璧主義の冒険家。綿密な計画で「全部行く」を実現します。", "spots": ["富山市ガラス美術館", "富岩運河環水公園", "高岡大仏", "新湊きっときと市場"]},
    "ACED": {"name": "ディープな文化体験アドベンチャラー", "tagline": "「合掌造りの囲炉裏端で、地元のおばあちゃんの話に聴き入る」", "desc": "観光地の表面ではなく、文化の深層に触れたい探究者。工場見学や伝統体験にたっぷり時間をかけます。", "spots": ["五箇山", "富山県美術館", "庄川峡遊覧船"]},
    "ACEW": {"name": "好奇心全開！フルスロット探検家", "tagline": "「祭りで踊って、トロッコで駆け抜けて、次はどこ？」", "desc": "とにかく「やったことがないこと」に飛びつく好奇心の塊。文化体験もアクティビティも片っ端から挑戦します。", "spots": ["海王丸パーク", "富山城", "黒部峡谷鉄道", "ほたるいかミュージアム"]},
    "ANGD": {"name": "大自然とグルメの求道者", "tagline": "「雪の大谷を歩き、ます寿しに舌鼓」", "desc": "雄大な自然に挑み、その土地の食に深く向き合う。大自然の冒険と食のこだわりを両立する、贅沢な旅のスタイルです。", "spots": ["立山黒部アルペンルート", "黒部ダム", "新湊きっときと市場"]},
    "ANGW": {"name": "山も海も食も！弾丸グルメハンター", "tagline": "「黒部峡谷→雨晴海岸→寿司、全部今日中に！」", "desc": "大自然もグルメもスピード勝負で欲張りに回る弾丸トラベラー。体力と食欲が旅の武器です。", "spots": ["黒部峡谷鉄道", "雨晴海岸", "ほたるいかミュージアム", "立山黒部アルペンルート"]},
    "ANED": {"name": "秘境探訪の孤高の冒険家", "tagline": "「称名滝の水しぶきを浴び、黒部ダムの放水に立ち尽くす」", "desc": "人が少ない秘境や大自然の中で、時間をかけて深い体験をすることに至上の喜びを感じます。", "spots": ["称名滝", "黒部ダム", "立山黒部アルペンルート"]},
    "ANEW": {"name": "風と波に乗る自由な冒険旅人", "tagline": "「行き先は決めない。面白そうな方へ走る！」", "desc": "予定は未定。自然の中を自由に駆け巡り、たくさんの景色と出会いを集めるノープラン派の冒険家です。", "spots": ["雨晴海岸", "黒部峡谷鉄道", "あさひ舟川「春の四重奏」", "海王丸パーク"]},
}

# ============================================================
# ユーティリティ
# ============================================================
def calc_scores(answers):
    axes = {"SA": 0, "CN": 0, "GE": 0, "DW": 0}
    for i, q in enumerate(QUESTIONS):
        if i < len(answers) and answers[i] is not None:
            axes[q["axis"]] += answers[i] - 3
    return axes

def determine_type(scores):
    code = ""
    code += "S" if scores["SA"] <= 0 else "A"
    code += "C" if scores["CN"] <= 0 else "N"
    code += "G" if scores["GE"] <= 0 else "E"
    code += "D" if scores["DW"] <= 0 else "W"
    return code

def score_to_percent(score, num_questions=5):
    max_score = num_questions * 2
    return int((score + max_score) / (2 * max_score) * 100)

def save_to_gas(answers, scores, type_code):
    if not GAS_URL:
        return
    try:
        data = urllib.parse.urlencode({
            "timestamp": datetime.datetime.now().isoformat(),
            "answers": json.dumps(answers),
            "score_SA": scores["SA"],
            "score_CN": scores["CN"],
            "score_GE": scores["GE"],
            "score_DW": scores["DW"],
            "type_code": type_code,
        }).encode()
        req = urllib.request.Request(GAS_URL, data=data, method="POST")
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

def render_circle_buttons(idx, current_val, left_label, right_label):
    """丸ボタン5つをHTML/JSで描画。選択するとiframe親のURLパラメータを書き換える"""
    sizes = [44, 36, 28, 36, 44]
    circles = ""
    for i in range(5):
        val = i + 1
        s = sizes[i]
        if current_val == val:
            style = f"width:{s}px;height:{s}px;border-radius:50%;background:#0091DA;border:3px solid #0091DA;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,145,218,0.4);transition:all 0.2s;vertical-align:middle;"
            inner = f'<div style="width:{int(s*0.35)}px;height:{int(s*0.35)}px;border-radius:50%;background:white;"></div>'
        else:
            style = f"width:{s}px;height:{s}px;border-radius:50%;background:white;border:2.5px solid #CCC;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;transition:all 0.2s;vertical-align:middle;"
            inner = ""
        circles += f'<div onclick="selectVal({val})" style="{style}">{inner}</div>\n'

    html_code = f"""
    <div style="font-family:'Noto Sans JP',sans-serif;padding:0.5rem 0;">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span style="font-size:0.78rem;color:#888;">{left_label}</span>
            <span style="font-size:0.78rem;color:#888;">{right_label}</span>
        </div>
        <div style="display:flex;justify-content:center;align-items:center;gap:12px;">
            {circles}
        </div>
    </div>
    <script>
    function selectVal(v) {{
        // Streamlit の親ウィンドウのURLにパラメータを追加してリロード
        const url = new URL(window.parent.location.href);
        url.searchParams.set('ans_{idx}', v);
        window.parent.location.href = url.toString();
    }}
    </script>
    """
    components.html(html_code, height=100, scrolling=False)

# ============================================================
# セッション初期化 & URLパラメータ読み取り
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "top"
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = [None] * 20

# URLパラメータから回答を読み取り
params = st.query_params
for i in range(20):
    key = f"ans_{i}"
    if key in params:
        val = int(params[key])
        if st.session_state.answers[i] != val:
            st.session_state.answers[i] = val
            st.session_state.page = "quiz"
            st.session_state.q_index = i

# ============================================================
# ページ: トップ
# ============================================================
def page_top():
    st.markdown("""
    <div class="title-card">
        <h1>🏔️ 富山旅タイプ診断</h1>
        <p>20の質問に答えて、あなたにぴったりの<br>富山県の旅スタイルを見つけよう！</p>
        <p style="font-size:0.85rem; margin-top:1rem; opacity:0.8;">所要時間：約3分</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="background:white; border-radius:12px; padding:1.5rem; margin:1rem 0; box-shadow:0 2px 12px rgba(0,0,0,0.06);">
        <p style="color:#333; font-size:0.95rem; line-height:1.8; margin:0;">
            あなたの旅の好みを4つの軸で分析し、<strong>16タイプ</strong>の中からぴったりのスタイルを診断します。<br>
            結果に合わせて、おすすめの富山県観光スポットもご提案します。
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("診断をはじめる", type="primary", use_container_width=True):
        st.session_state.page = "quiz"
        st.session_state.q_index = 0
        st.session_state.answers = [None] * 20
        # URLパラメータをクリア
        st.query_params.clear()
        st.rerun()

# ============================================================
# ページ: 質問
# ============================================================
def page_quiz():
    idx = st.session_state.q_index
    q = QUESTIONS[idx]
    progress = idx / 20
    current_val = st.session_state.answers[idx]

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.2rem;">
        <span style="font-size:0.85rem; color:#0091DA; font-weight:700;">Q{idx+1} / 20</span>
        <span style="font-size:0.8rem; color:#999;">{int(progress*100)}%</span>
    </div>
    <div class="progress-container">
        <div class="progress-fill" style="width:{progress*100}%;"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="question-card">
        <div class="question-text">{q["text"]}</div>
    </div>
    """, unsafe_allow_html=True)

    # 丸ボタン（HTML/JS、スマホでも確実に横並び）
    render_circle_buttons(idx, current_val, q["left"], q["right"])

    # 「次へ」ボタン
    if current_val is not None:
        if idx < 19:
            if st.button("次へ →", key="next_btn", type="primary", use_container_width=True):
                st.session_state.q_index += 1
                st.rerun()
        else:
            if st.button("診断結果を見る 🎉", key="result_btn", type="primary", use_container_width=True):
                st.session_state.page = "result"
                st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center; color:#999; font-size:0.85rem; margin:0.5rem 0;">
            丸ボタンをタッチして回答してください
        </div>
        """, unsafe_allow_html=True)

    # 「戻る」ボタン
    if idx > 0:
        st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
        if st.button("← 戻る", key="back_btn", use_container_width=True):
            st.session_state.q_index -= 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# ページ: 結果
# ============================================================
def page_result():
    answers = st.session_state.answers
    scores = calc_scores(answers)
    type_code = determine_type(scores)
    t = TYPES.get(type_code, TYPES["SNGD"])
    save_to_gas(answers, scores, type_code)

    st.markdown(f"""
    <div class="result-card">
        <h2>あなたの富山旅タイプは…</h2>
        <div class="type-code">{type_code}</div>
        <div class="type-name">{t["name"]}</div>
        <div class="type-tagline">{t["tagline"]}</div>
        <div class="type-desc">{t["desc"]}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### あなたの旅スタイル")
    for axis_key, left_label, right_label in [("SA","🛁 癒し (S)","🏔️ 冒険 (A)"),("CN","🏛️ カルチャー (C)","🌿 ネイチャー (N)"),("GE","🍣 グルメ (G)","🎭 体験 (E)"),("DW","🔍 じっくり (D)","🗺️ 広く (W)")]:
        pct = score_to_percent(scores[axis_key])
        st.markdown(f"""
        <div class="axis-bar-container">
            <div class="axis-bar-labels"><span>{left_label}</span><span>{right_label}</span></div>
            <div class="axis-bar"><div class="axis-bar-marker" style="left:{pct}%;"></div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("### おすすめ観光スポット")
    for spot_name in t["spots"]:
        desc = SPOT_DETAILS.get(spot_name, "")
        st.markdown(f'<div class="spot-card"><h4>📍 {spot_name}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

    with st.expander("📈 このタイプの旅行者データ（参考）"):
        st.markdown('<div style="font-size:0.9rem;color:#555;line-height:1.8;">※ 富山県観光ウェブアンケート（2025年）の回答データに基づく参考値です。</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.metric("平均飲食消費額", "約15,000〜25,000円")
            st.metric("平均宿泊数", "1〜2泊")
        with c2:
            st.metric("旅行全体の満足度", "4.3 / 5.0")
            st.metric("再来訪意向", "高い傾向")

    with st.expander("📋 全16タイプ一覧"):
        for code, info in TYPES.items():
            hl = "border:2px solid #0091DA;background:#E8F4FD;" if code == type_code else ""
            st.markdown(f'<div style="padding:0.8rem;margin:0.4rem 0;border-radius:10px;background:white;box-shadow:0 1px 6px rgba(0,0,0,0.05);{hl}"><strong style="color:#0091DA;">{code}</strong> <span style="color:#333;font-weight:700;">{info["name"]}</span><br><span style="color:#777;font-size:0.85rem;">{info["tagline"]}</span></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    ca, cb = st.columns(2)
    with ca:
        if st.button("🔄 もう一度診断する", use_container_width=True):
            st.session_state.page = "top"
            st.session_state.q_index = 0
            st.session_state.answers = [None] * 20
            st.query_params.clear()
            st.rerun()
    with cb:
        share_text = urllib.parse.quote(f"私の富山旅タイプは【{type_code}】{t['name']}でした！ #富山旅タイプ診断")
        st.markdown(f'<a href="https://twitter.com/intent/tweet?text={share_text}" target="_blank"><button style="width:100%;padding:0.6rem;border-radius:30px;border:2px solid #1DA1F2;background:white;color:#1DA1F2;font-weight:700;cursor:pointer;">🐦 Xでシェア</button></a>', unsafe_allow_html=True)

# ============================================================
# ルーティング
# ============================================================
if st.session_state.page == "top":
    page_top()
elif st.session_state.page == "quiz":
    page_quiz()
elif st.session_state.page == "result":
    page_result()
