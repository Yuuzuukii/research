#streamlit run app.py

import streamlit as st
from test import run_debate

# === システムプロンプト生成テンプレート ===
def generate_system_prompt(role_desc: str, agent_name: str) -> str:
    return (
        f"あなたは {role_desc} の立場を持つする対話エージェントです。\n"
    )

# === UIレイアウト設定 ===
st.set_page_config(page_title="弁証法的対話システム", layout="centered")
st.title("🧠 弁証法的対話シミュレーター")

# === 入力項目 ===
topic = st.text_input("🎯 議題を入力してください", value="学校清掃は教育に必要か？")

with st.expander("🎭 各エージェントの立場を入力（例：日本人、保守的教育観）", expanded=True):
    agentA_role = st.text_input("🅰️ Agent A の立場", value="日本人")
    agentB_role = st.text_input("🅱️ Agent B の立場", value="アメリカ人")

# === 実行ボタン ===
if st.button("🚀 対話を開始する"):
    with st.spinner("対話中...お待ちください"):
        sysA = generate_system_prompt(agentA_role, "AgentA")
        sysB = generate_system_prompt(agentB_role, "AgentB")

        dialogue_log = run_debate(topic, sysA, sysB)

        if dialogue_log:
            st.success("✅ 対話完了")

            for key, val in dialogue_log.items():
                if key == "Topic":
                    st.subheader(f"🎯 議題: {val}")
                elif key.startswith("Thesis"):
                    st.subheader("🗣 論証（Agent A）")
                    st.markdown(val)
                elif key.startswith("Counter"):
                    st.subheader("🗣 反論（Agent B）")
                    st.markdown(val)
                elif key.startswith("Attackable"):
                    st.subheader("🧐 攻撃されたか（Agent A）")
                    st.markdown(f"**{val}**")
                elif key.startswith("Justification"):
                    st.subheader("🛡 正当化（Agent A）")
                    st.markdown(val)
                elif key.startswith("Justified"):
                    st.subheader("🧪 正当化の評価（Agent B）")
                    st.markdown(f"**{val}**")
                elif key.startswith("Synthesis"):
                    st.subheader("🔄 止揚論証（Agent A）")
                    st.markdown(val)
                elif key.startswith("Acceptance"):
                    st.subheader("🎯 最終評価（Agent B）")
                    st.markdown(f"**{val}**")
                elif key.startswith("Outcome"):
                    st.subheader("📌 結果")
                    st.markdown(f"**{val}**")
                else:
                    st.markdown(f"`{key}`: {val}")
        else:
            st.error("⚠️ 対話ログが生成されませんでした。")
