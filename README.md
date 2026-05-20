# 二段組PDF 4分割OCR前処理コードセット README

## 目的

このコードセットは、二段組・縦書きの文献PDFをOCRにかけやすくするために、各ページを次の4つに分割して、OCR前処理用のPDFまたはJPEG画像を作成するものです。

標準の分割順は、縦書き二段組を想定して、次の順番です。

```text
右上 → 右下 → 左上 → 左下
```

これにより、見開き・二段組のままOCRするよりも、1画面あたりの文字領域が整理され、OCRが読みやすくなることを狙います。

---

## ファイル構成

想定する保存場所は次のとおりです。

```text
/path/to/ocr-pdf-cut-to-four/
  split_pdf.py
  README_cut_to_four.md
```

`split_pdf.py` が実行用スクリプトです。

---

## 初回だけ必要な準備

PyMuPDF と Pillow をインストールします。

```bash
python3 -m pip install pymupdf pillow
```

すでに入っている場合は再インストール不要です。

---

## 基本の実行方法

ターミナルでコード保存フォルダへ移動します。

```bash
cd "/path/to/ocr-pdf-cut-to-four"
```

次に、入力PDFを指定して実行します。

```bash
python3 split_pdf.py "入力PDFのパス.pdf"
```

この場合、入力PDFと同じフォルダに、次のような名前で出力されます。

```text
入力PDF名_4split_180dpi.pdf
```

初期設定は次のとおりです。

```text
dpi: 180
JPEG品質: 70
色: グレースケール
出力形式: PDF
分割順: 右上 → 右下 → 左上 → 左下
```

---

## 実用上おすすめの基本コマンド

文献OCR前処理としては、まず次を推奨します。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70
```

実際のテストでは、元PDF 66.6MB に対して、`--dpi 180 --quality 70` で出力PDFが約120.6MBになりました。OCR前処理用としては現実的なサイズです。

---

## 出力先フォルダを指定する

入力PDFと別のフォルダに出力したい場合は、`--outdir` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --outdir "/path/to/ocr-pdf-cut-to-four/output" \
  --dpi 180 \
  --quality 70
```

この場合、指定した `output` フォルダ内に出力PDFが作成されます。

---

## 出力PDF名を直接指定する

出力ファイル名まで明示したい場合は、`--out` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --out "/path/to/ocr-pdf-cut-to-four/output/OCR用_4分割.pdf" \
  --dpi 180 \
  --quality 70
```

通常は `--out` なしで十分です。

---

## 分割線を上下左右にずらす

### 横の分割線を上に動かす

上下分割の境界線を少し上へ移動したい場合は、`--y-offset` にマイナス値を指定します。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --dpi 180 \
  --quality 70 \
  --y-offset -80
```

意味は次のとおりです。

```text
--y-offset -80  → 横の分割線を80px上へ移動
--y-offset  80  → 横の分割線を80px下へ移動
```

まずは `-50` から `-100` くらいで試すとよいです。

### 縦の分割線を左右に動かす

左右分割の境界線を動かしたい場合は、`--x-offset` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --dpi 180 \
  --quality 70 \
  --x-offset 50
```

意味は次のとおりです。

```text
--x-offset  50  → 縦の分割線を50px右へ移動
--x-offset -50  → 縦の分割線を50px左へ移動
```

---

## 分割線付近で文字が切れる場合

文字が分割線付近で切れる場合は、`--overlap` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --dpi 180 \
  --quality 70 \
  --overlap 30
```

これは、分割境界の周辺を30pxぶん重複させて切り出す設定です。

分割線を上にずらしつつ、文字切れも防ぎたい場合は次のようにします。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --dpi 180 \
  --quality 70 \
  --y-offset -80 \
  --overlap 30
```

---

## DPIと容量の目安

DPIは「1インチあたりの画素密度」です。4分割するからといってDPIを1/4にする必要はありません。

ページを4分割すると、各分割画像の面積は約1/4になりますが、文字の画素密度は元のDPIのまま維持されます。

目安は次のとおりです。

```text
250dpi → 高精度寄り。ただし容量が大きくなりやすい
200dpi → OCR精度重視と容量のバランス
180dpi → 実用上おすすめ。容量を抑えやすい
150dpi → 容量優先。文字が十分大きい資料向け
120dpi → かなり軽量。ただしOCR精度低下に注意
```

まずは次を標準にするのがおすすめです。

```bash
--dpi 180 --quality 70
```

精度が足りない場合は次を試します。

```bash
--dpi 200 --quality 70
```

容量をさらに下げたい場合は次を試します。

```bash
--dpi 150 --quality 65
```

---

## JPEG品質の目安

`--quality` はPDF内部に埋め込むJPEG画像の品質です。

```text
80〜85 → 高画質。ただし容量大
70     → 標準。おすすめ
60〜65 → 軽量。OCR精度に問題がなければ有効
50以下 → 劣化が目立つ可能性あり
```

通常は次で十分です。

```bash
--quality 70
```

---

## カラーで出力したい場合

初期設定では、容量削減のためグレースケールで出力します。

カラーを保持したい場合は、`--color` を付けます。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --dpi 180 \
  --quality 70 \
  --color
```

ただし、カラー出力は容量が大きくなりやすいです。OCR前処理だけが目的なら、通常はグレースケールで十分です。

---

## JPEG画像として出力する

PDFではなく、分割後の画像ファイルを出したい場合は `--mode images` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --mode images \
  --dpi 180 \
  --quality 70
```

この場合、次のようなフォルダが自動作成され、その中にJPEG画像が出力されます。

```text
入力PDF名_4split_images_180dpi_q70/
```

PDFとJPEG画像の両方を出したい場合は、`--mode both` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --mode both \
  --dpi 180 \
  --quality 70
```

---

## 分割順を変える

標準は縦書き二段組向けの `rtl_tb` です。

```text
rtl_tb = 右上 → 右下 → 左上 → 左下
```

横書き・左から読む資料の場合は `ltr_tb` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --order ltr_tb
```

Z順にしたい場合は `z` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --order z
```

分割順は次の3種類です。

```text
rtl_tb → 右上 → 右下 → 左上 → 左下
ltr_tb → 左上 → 左下 → 右上 → 右下
z      → 左上 → 右上 → 左下 → 右下
```

---

## よく使うコマンド集

### 標準実行

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70
```

### 上下の分割線を少し上へ移動

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70 --y-offset -80
```

### 文字切れ防止のため少し重複

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70 --overlap 30
```

### 分割線を上へ移動し、さらに重複を付ける

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70 --y-offset -80 --overlap 30
```

### 容量をさらに下げる

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 150 --quality 65
```

### 精度重視

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 200 --quality 75
```

### JPEG画像として出力

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --mode images --dpi 180 --quality 70
```

### PDFとJPEG画像を両方出力

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --mode both --dpi 180 --quality 70
```

---

## 長いパスを使うときの注意

PDFのパスに空白・日本語・記号が含まれる場合は、必ず `" "` で囲みます。

```bash
python3 split_pdf.py "/path/to/input/資料名.pdf" --dpi 180 --quality 70
```

複数行で書く場合は、行末に `\` を付けます。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --dpi 180 \
  --quality 70 \
  --y-offset -80
```

`\` の後ろには空白や文字を入れないでください。

---

## 出力サイズが大きすぎる場合

まず次を試します。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 150 --quality 65
```

それでも大きい場合は、さらに品質を下げます。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 150 --quality 60
```

ただし、容量を下げすぎるとOCR精度が落ちる可能性があります。最終判断は、数ページだけOCRテストして確認するのが安全です。

---

## OCR前処理としての推奨運用

1. まず数ページだけ、`--dpi 180 --quality 70` で試す。
2. 文字が切れる場合は、`--overlap 20〜40` を加える。
3. 上下の分割位置が合わない場合は、`--y-offset -50〜-100` で調整する。
4. OCR精度が足りない場合は、`--dpi 200` に上げる。
5. 容量が大きすぎる場合は、`--dpi 150 --quality 65` に下げる。
6. 条件が決まったら、全ページを処理する。

---

## トラブルシューティング

### `ModuleNotFoundError: No module named 'fitz'` が出る

PyMuPDF が入っていません。次を実行してください。

```bash
python3 -m pip install pymupdf pillow
```

### `入力PDFが見つかりません` と出る

パスが間違っている可能性があります。PDFをターミナルへドラッグ＆ドロップすると、正しいパスを入力しやすいです。

### 出力PDFが重い

DPIまたはJPEG品質を下げます。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 150 --quality 65
```

### 文字が分割線で切れる

`--overlap` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70 --overlap 30
```

### 分割位置が少しずれている

`--x-offset` または `--y-offset` を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70 --y-offset -80
```

---

## オプション一覧

| オプション | 意味 | 初期値 |
|---|---|---|
| `input_pdf` | 入力PDF | 必須 |
| `--out` | 出力PDFのフルパス | 自動生成 |
| `--outdir` | 出力先フォルダ | 入力PDFと同じフォルダ |
| `--images-dir` | JPEG画像出力先 | 自動生成 |
| `--dpi` | PDFを画像化する解像度 | `180` |
| `--quality` | JPEG品質。1〜95 | `70` |
| `--color` | グレースケール化せずカラー出力 | なし |
| `--overlap` | 分割境界の重複px | `0` |
| `--x-offset` | 縦分割線の左右移動px。+で右、-で左 | `0` |
| `--y-offset` | 横分割線の上下移動px。+で下、-で上 | `0` |
| `--order` | 分割順。`rtl_tb` / `ltr_tb` / `z` | `rtl_tb` |
| `--mode` | 出力形式。`pdf` / `images` / `both` | `pdf` |
| `--suffix` | 自動出力名の接尾辞 | `_4split` |

---

## 現在のおすすめ設定

現時点では、次を標準設定として使うのがよいです。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70
```

上下の分割線を少し上げたい資料では、次を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70 --y-offset -80
```

文字切れが心配な場合は、次を使います。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70 --y-offset -80 --overlap 30
```
