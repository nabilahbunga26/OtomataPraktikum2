# FSM DFA Simulator — Tugas Otomata

Program simulasi **Deterministic Finite Automaton (DFA)** untuk mengecek keanggotaan string pada bahasa:

```
L = { x ∈ (0 + 1)+ | karakter terakhir pada x adalah 1
                      DAN x tidak memiliki substring "00" }
```

Dibangun dengan **Flask** (backend) dan UI **web pixel-art retro** (frontend), sesuai diagram DFA yang diberikan pada soal.

---

## 2. Diagram DFA (sesuai soal)

<img width="435" height="186" alt="image" src="https://github.com/user-attachments/assets/f3140af7-3a42-4924-9f38-8c45e3627ed9" />


- **Q (himpunan state)**: `{S, A, B, C}`
- **Σ (alfabet)**: `{0, 1}`
- **q0 (state awal)**: `S`
- **F (state akhir/diterima)**: `{B}`
- **δ (fungsi transisi)**:

| State | Input 0 | Input 1 |
|-------|---------|---------|
| **S** | A       | B       |
| **A** | C       | B       |
| **B** | A       | B       |
| **C** | C       | C       |

---

## 3. Logika Program

Setiap state merepresentasikan "ingatan" DFA terhadap apa yang sudah dibaca:

- **S** — state awal, belum ada karakter dibaca sama sekali.
- **A** — karakter terakhir yang dibaca adalah `0`, dan **belum pernah** muncul substring `00` sejauh ini. State ini "waspada": jika karakter berikutnya juga `0`, maka string pasti mengandung `00` dan harus ditolak.
- **B** — karakter terakhir yang dibaca adalah `1`, dan belum pernah muncul substring `00`. **Inilah satu-satunya state akhir (accepting state)**, karena jika string berhenti di sini berarti karakter terakhirnya `1` dan tidak ada `00` di dalamnya — persis sesuai definisi bahasa `L`.
- **C** — *trap state* / dead state. Begitu DFA masuk ke state ini (karena membaca `0` saat berada di state `A`, artinya muncul substring `00`), string **pasti ditolak**, apa pun input setelahnya (C punya self-loop untuk `0` dan `1`).

Proses pengecekan sebuah string:
1. DFA mulai dari state `S`.
2. Setiap karakter string dibaca satu per satu dari kiri ke kanan, dan state berpindah sesuai tabel transisi `δ`.
3. Setelah seluruh karakter habis dibaca, cek state akhir:
   - Jika berhenti di **B** → string **diterima**.
   - Jika berhenti di **A** atau **C** → string **ditolak**.
4. Program juga menampilkan jejak (*trace*) lengkap perpindahan state per langkah, sehingga pengguna bisa melihat persis di langkah mana string mulai gagal (misalnya tepat ketika masuk ke state `C`).

Validasi tambahan: string yang mengandung karakter selain `0` dan `1`, atau string kosong, langsung ditolak oleh validator sebelum masuk ke DFA (karena alfabet Σ = {0,1} dan L mensyaratkan x ∈ (0+1)⁺, minimal 1 karakter).

---

## 4. Fitur Program

1. **Cek satu string** — input satu string biner, langsung diproses dan ditampilkan hasil diterima/ditolak beserta alasannya.
2. **Trace table** — tabel step-by-step menampilkan perpindahan state (`from → symbol → to`) untuk setiap karakter, memudahkan debugging/pemahaman cara kerja DFA.
3. **Batch mode** — cek banyak string sekaligus (satu string per baris), cocok untuk testing cepat banyak kasus uji.
4. **Random string generator** — tombol untuk mengisi otomatis string acak (panjang 1–10 karakter) sebagai bahan uji coba cepat.
5. **Visualisasi diagram DFA** — diagram state DFA ditampilkan langsung di halaman web sebagai referensi visual.
6. **Validasi input** — menangani input kosong atau mengandung karakter selain 0/1 dengan pesan error yang jelas (tidak crash).
7. **REST API** — backend menyediakan endpoint JSON (`/api/check`, `/api/batch`, `/api/random`) sehingga logika DFA bisa dipakai ulang/diuji terpisah dari UI (mis. lewat `curl` atau Postman).
8. **UI pixel-art retro** — antarmuka web bergaya retro game (font Press Start 2P, neon, grid background) agar nyaman dan menarik digunakan.

---

## 5. Struktur File

```
fsm_project/
├── app.py                 # Backend Flask + implementasi DFA
├── templates/
│   └── index.html         # UI web (HTML+CSS+JS, pixel-art style)
├── requirements.txt        # Dependency Python
└── README.md               # Dokumentasi ini
```

---

## 6. Cara Menjalankan (Terminal)

### Prasyarat
- Python 3.8 atau lebih baru
- pip

### Langkah-langkah

1. Ekstrak file ZIP ini, lalu masuk ke folder project:
   ```bash
   cd fsm_project
   ```

2. (Opsional tapi disarankan) buat virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Linux/Mac
   venv\Scripts\activate           # Windows
   ```

3. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan program:
   ```bash
   python3 app.py
   ```

5. Buka browser, akses:
   ```
   http://localhost:5000
   ```

6. Masukkan string biner (misalnya `1011`) pada form **"Cek Satu String"**, lalu klik **PROSES**. Hasil diterima/ditolak beserta trace state akan langsung tampil.

7. Untuk uji banyak string sekaligus, gunakan form **"Batch Mode"** — masukkan beberapa string (satu per baris), lalu klik **PROSES BATCH**.

### Menjalankan via API langsung (opsional, tanpa browser)

```bash
curl -X POST http://localhost:5000/api/check \
  -H "Content-Type: application/json" \
  -d '{"input": "1011"}'
```

---

## 7. Contoh Hasil Uji

| String | Hasil      | Alasan                                      |
|--------|------------|----------------------------------------------|
| `1`    | DITERIMA   | Diakhiri 1, tanpa substring 00                |
| `1011` | DITERIMA   | Diakhiri 1, tanpa substring 00                |
| `101`  | DITERIMA   | Diakhiri 1, tanpa substring 00                |
| `0`    | DITOLAK    | Tidak diakhiri 1                              |
| `10`   | DITOLAK    | Tidak diakhiri 1                              |
| `00`   | DITOLAK    | Mengandung substring 00                       |
| `1100` | DITOLAK    | Mengandung substring 00                       |
| `0011` | DITOLAK    | Mengandung substring 00 (meski diakhiri 1)    |

---

## 8. Catatan

Program ini dibuat sebagai implementasi orisinal berdasarkan rancangan DFA pada soal tugas, ditulis dan didokumentasikan sendiri oleh penulis. Struktur kode (pemisahan logika DFA dari UI, sistem trace step-by-step, batch mode, dan gaya antarmuka) dirancang khusus untuk tugas ini.
