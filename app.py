"""
=====================================================================
 FSM Automation - DFA Simulator
 Tugas Mata Kuliah Teori Bahasa Formal dan Otomata

 Bahasa yang dikenali:
 L = { x ∈ (0 + 1)+ | karakter terakhir dari x adalah 1
       DAN x tidak memiliki substring "00" }

 Author : Nabilah Bunga Sulistia
 NRP    : 5025241073
=====================================================================
"""

from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# ---------------------------------------------------------------
# DEFINISI DFA (Deterministic Finite Automaton)
# ---------------------------------------------------------------
# Q  = himpunan state           : {S, A, B, C}
# Σ  = alfabet input             : {0, 1}
# δ  = fungsi transisi           : lihat TRANSITIONS di bawah
# q0 = state awal                : S
# F  = himpunan state akhir      : {B}
#
# Penjelasan logika tiap state:
#   S : state awal, belum ada karakter yang dibaca
#   A : karakter terakhir yang dibaca adalah '0',
#       dan belum pernah muncul substring "00"
#   B : karakter terakhir yang dibaca adalah '1',
#       dan belum pernah muncul substring "00"  -> STATE AKHIR
#   C : "trap state" / dead state, dicapai begitu substring "00"
#       muncul. Begitu masuk C, string PASTI ditolak, dan DFA
#       tetap berada di C apapun input selanjutnya (self loop 0,1)
# ---------------------------------------------------------------

START_STATE = "S"
ACCEPT_STATES = {"B"}
TRAP_STATE = "C"

TRANSITIONS = {
    "S": {"0": "A", "1": "B"},
    "A": {"0": "C", "1": "B"},
    "B": {"0": "A", "1": "B"},
    "C": {"0": "C", "1": "C"},
}

STATE_DESC = {
    "S": "State awal, belum ada karakter dibaca.",
    "A": "Karakter terakhir '0', belum ada substring '00'.",
    "B": "Karakter terakhir '1', belum ada substring '00' (STATE AKHIR).",
    "C": "Trap state: substring '00' terdeteksi. String pasti ditolak.",
}


def validate_input_string(s: str):
    """Pastikan string hanya berisi karakter '0' dan '1'."""
    if s == "":
        return False, "String tidak boleh kosong."
    if not re.fullmatch(r"[01]+", s):
        return False, "String hanya boleh berisi karakter '0' dan '1'."
    return True, ""


def run_dfa(input_string: str):
    """
    Menjalankan DFA terhadap input_string.
    Mengembalikan dict berisi:
      - accepted (bool)
      - trace (list of step dict): state asal, simbol, state tujuan
      - final_state
      - reason (penjelasan textual hasil)
    """
    current_state = START_STATE
    trace = [{
        "step": 0,
        "from_state": None,
        "symbol": None,
        "to_state": current_state,
        "desc": STATE_DESC[current_state],
    }]

    for i, symbol in enumerate(input_string, start=1):
        next_state = TRANSITIONS[current_state][symbol]
        trace.append({
            "step": i,
            "from_state": current_state,
            "symbol": symbol,
            "to_state": next_state,
            "desc": STATE_DESC[next_state],
        })
        current_state = next_state

    accepted = current_state in ACCEPT_STATES

    if current_state == TRAP_STATE:
        reason = "Ditolak karena string mengandung substring '00'."
    elif current_state == "A":
        reason = "Ditolak karena karakter terakhir string adalah '0' (bukan '1')."
    elif accepted:
        reason = "Diterima: string diakhiri '1' dan tidak mengandung substring '00'."
    else:
        reason = "Ditolak."

    return {
        "input": input_string,
        "accepted": accepted,
        "final_state": current_state,
        "trace": trace,
        "reason": reason,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.get_json(silent=True) or {}
    input_string = str(data.get("input", "")).strip()

    valid, error_msg = validate_input_string(input_string)
    if not valid:
        return jsonify({"error": error_msg}), 400

    result = run_dfa(input_string)
    return jsonify(result)


@app.route("/api/batch", methods=["POST"])
def api_batch():
    """Cek banyak string sekaligus, dipisah newline."""
    data = request.get_json(silent=True) or {}
    raw = str(data.get("inputs", ""))
    lines = [line.strip() for line in raw.splitlines() if line.strip() != ""]

    if not lines:
        return jsonify({"error": "Tidak ada string untuk diperiksa."}), 400

    results = []
    for line in lines:
        valid, error_msg = validate_input_string(line)
        if not valid:
            results.append({
                "input": line,
                "accepted": False,
                "final_state": None,
                "trace": [],
                "reason": f"Invalid: {error_msg}",
                "invalid": True,
            })
        else:
            results.append(run_dfa(line))

    return jsonify({"results": results})


@app.route("/api/random", methods=["GET"])
def api_random():
    """Generate string acak (untuk fitur testing cepat)."""
    import random
    length = random.randint(1, 10)
    s = "".join(random.choice("01") for _ in range(length))
    return jsonify({"input": s})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
