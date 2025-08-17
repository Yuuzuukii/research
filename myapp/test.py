import os
import json
from autogen import AssistantAgent

# ==== 設定 ====
APIKEY = os.getenv("APIKEY")
llm_config = {"model": "gpt-4.1-nano", "api_key": APIKEY}

def run_debate(topic, agentA_sys, agentB_sys):
    agentA = AssistantAgent("AgentA", llm_config=llm_config)
    agentB = AssistantAgent("AgentB", llm_config=llm_config)

    dialogue_log = {}
    shared_history = []

    # === 論証構築（AgentA） ===
    shared_history.append({"role": "system", "name": "AgentA", "content": agentA_sys})
    prompt_A = f"議題: {topic}\n自分の論証を示せ。\n書式:\n論証:"
    shared_history.append({"role": "user", "content": prompt_A})
    arg_A = agentA.generate_reply(shared_history)
    shared_history.append({"role": "assistant", "name": "AgentA", "content": arg_A})
    dialogue_log["Thesis (AgentA)"] = arg_A

    # === アンチテーゼ構築（AgentB） ===
    shared_history.append({"role": "system", "name": "AgentB", "content": agentB_sys})
    prompt_B = f"議題: {topic}\n相手の論証：{arg_A}\n相手の論証と矛盾する自分の論証を示せ。\n書式:\n論証:"
    shared_history.append({"role": "user", "content": prompt_B})
    arg_B = agentB.generate_reply(shared_history)
    shared_history.append({"role": "assistant", "name": "AgentB", "content": arg_B})
    dialogue_log["Antithesis (AgentB)"] = arg_B

    argument = arg_A
    counter = arg_B
    turn = 1

    while True:
        if turn > 10:
            dialogue_log["結論"] = "反論が10回を超えたため議論を中断しました。"
            break

        agent = agentA if turn % 2 == 1 else agentB
        agent_name = agent.name
        opponent_name = "AgentB" if agent_name == "AgentA" else "AgentA"
        current_counter = counter if agent_name == "AgentA" else argument

        # === 反論可能か？
        shared_history.append({"role": "user", "name": opponent_name, "content": current_counter})
        prompt_refutability = {"role": "user", "content": "反論可能か？\nYES か NO で答えよ。\n反論可能?:"}
        shared_history.append(prompt_refutability)
        res = agent.generate_reply(shared_history).strip()
        shared_history.append({"role": "assistant", "name": agent_name, "content": res})
        dialogue_log[f"反論可能? ({agent_name}, Turn {turn})"] = res

        if res.upper() == "NO":
            # === 正当化されたか？
            prompt_justified = {"role": "user", "content": "相手の反論を正当化できてしまったか？YES/NO で答えよ。\n正当化されたか?:"}
            shared_history.append(prompt_justified)
            justified = agent.generate_reply(shared_history).strip()
            shared_history.append({"role": "assistant", "name": agent_name, "content": justified})
            dialogue_log[f"正当化 ({agent_name}, Turn {turn})"] = justified

            if justified.upper() == "YES":
                dialogue_log["結論"] = f"{agent_name} の主張は却下されました。"
                break
            else:
                # 止揚論証を提示
                summary_text = json.dumps(dialogue_log, ensure_ascii=False)
                sublate_prompt = {
                    "role": "user",
                    "content": f"これまでの対話:\n{summary_text}\n止揚論証を提案せよ。\n書式:\n止揚論証:"
                }
                shared_history.append(sublate_prompt)
                sublation = agent.generate_reply(shared_history)
                shared_history.append({"role": "assistant", "name": agent_name, "content": sublation})
                dialogue_log[f"止揚論証 ({agent_name})"] = sublation

                accept_prompt = {
                    "role": "user",
                    "name": agent_name,
                    "content": "止揚論証を受け入れるか？YES/NO で答えよ。\n受け入れるか?:"
                }
                shared_history.append(accept_prompt)
                accept = (agentB if agent_name == "AgentA" else agentA).generate_reply(shared_history).strip()
                shared_history.append({"role": "assistant", "name": opponent_name, "content": accept})
                dialogue_log[f"止揚論証受容 ({opponent_name})"] = accept

                dialogue_log["結論"] = "止揚論証は受容されました。" if accept.upper() == "YES" else "止揚論証は拒否されました。"
                break
        else:
            # === 新たな反論
            prompt_refute = {
                "role": "user",
                "content": f"相手の論証:\n{current_counter}\n反論せよ。ただし、以前と同じ主張を繰り返さないこと。\n書式:\n反論:"
            }
            shared_history.append(prompt_refute)
            new_argument = agent.generate_reply(shared_history)
            shared_history.append({"role": "assistant", "name": agent_name, "content": new_argument})
            dialogue_log[f"反論 ({agent_name} Turn {turn})"] = new_argument

            if agent_name == "AgentA":
                argument = new_argument
            else:
                counter = new_argument

            turn += 1

    with open("debate_log.json", "w", encoding="utf-8") as f:
        json.dump(dialogue_log, f, indent=2, ensure_ascii=False)

    return dialogue_log
