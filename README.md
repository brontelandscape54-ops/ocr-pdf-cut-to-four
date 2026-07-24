# 二段組PDF 4分割OCR前処理ツール

二段組・縦書きの文献PDFをOCRにかけやすくするため、各ページを4分割して、PDFまたはJPEG画像として出力するPythonツールです。

標準では、縦書き二段組を想定して次の順番で出力します。

```text
右上 → 右下 → 左上 → 左下
```

分割位置の調整、境界部分の重複、カラー／グレースケール、PDF／JPEG出力などを指定できます。

## 主な機能

- PDFの各ページを4分割
- 縦書き向け・横書き向け・Z順の出力順に対応
- 分割線の上下左右調整
- 分割境界の重複による文字切れ対策
- PDF、JPEG画像、または両方を出力
- DPI、JPEG品質、カラー／グレースケールを指定可能
- 入力PDFは外部へ送信せず、ローカル環境内で処理

## ファイル構成

```text
ocr-pdf-cut-to-four/
├── split_pdf.py
├── README.md
├── requirements.txt
├── LICENSE
├── input/
├── output/
└── logs/
```

`input`、`output`、`logs` フォルダ内の実データ、およびPDF・画像・ログ等は `.gitignore` によりGitの管理対象外です。

## 必要環境

- Python 3.9以降を推奨
- PyMuPDF
- Pillow

## インストール

リポジトリを取得し、フォルダへ移動します。

```bash
git clone https://github.com/brontelandscape54-ops/ocr-pdf-cut-to-four.git
cd ocr-pdf-cut-to-four
```

仮想環境を作る場合は次のようにします。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

依存ライブラリをインストールします。

```bash
python3 -m pip install -r requirements.txt
```

## 基本の使い方

```bash
python3 split_pdf.py "入力PDFのパス.pdf"
```

初期設定は次のとおりです。

```text
DPI: 180
JPEG品質: 70
色: グレースケール
出力形式: PDF
分割順: 右上 → 右下 → 左上 → 左下
```

入力PDFと同じフォルダに、次の形式で出力されます。

```text
入力PDF名_4split_180dpi.pdf
```

OCR前処理としては、まず次の設定を推奨します。

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --dpi 180 --quality 70
```

## 出力先を指定する

フォルダを指定する場合：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --outdir "output" \
  --dpi 180 \
  --quality 70
```

出力PDF名まで指定する場合：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --out "output/OCR用_4分割.pdf" \
  --dpi 180 \
  --quality 70
```

## 分割位置を調整する

横の分割線を上へ80px動かす場合：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --y-offset -80
```

縦の分割線を右へ50px動かす場合：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --x-offset 50
```

値の意味は次のとおりです。

```text
--x-offset  正の値で右、負の値で左
--y-offset  正の値で下、負の値で上
```

## 文字切れを防ぐ

分割線付近を30px重複させる場合：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --overlap 30
```

分割線を上へずらし、重複も付ける場合：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --y-offset -80 \
  --overlap 30
```

重複部分は隣接する分割画像の両方に含まれるため、OCR後に同じ文字が重複して認識される場合があります。

## 出力形式

JPEG画像として出力：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --mode images
```

PDFとJPEG画像を両方出力：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --mode both
```

JPEG出力先を指定する場合：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" \
  --mode images \
  --images-dir "output/images"
```

## 分割順

```text
rtl_tb  右上 → 右下 → 左上 → 左下（初期値・縦書き向け）
ltr_tb  左上 → 左下 → 右上 → 右下
z       左上 → 右上 → 左下 → 右下
```

例：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --order ltr_tb
```

## 画質と容量

目安は次のとおりです。

```text
200dpi  OCR精度を重視
180dpi  標準・推奨
150dpi  容量を抑えたい場合
```

JPEG品質の目安：

```text
75〜85  高画質・容量大
70      標準・推奨
60〜65  容量優先
```

カラーを保持する場合：

```bash
python3 split_pdf.py "入力PDFのパス.pdf" --color
```

OCR用途だけであれば、通常は初期値のグレースケールで十分です。

## オプション一覧

| オプション | 内容 | 初期値 |
|---|---|---|
| `input_pdf` | 入力PDF | 必須 |
| `--out` | 出力PDFのフルパス | 自動生成 |
| `--outdir` | 出力先フォルダ | 入力PDFと同じ場所 |
| `--images-dir` | JPEG画像の出力先 | 自動生成 |
| `--dpi` | レンダリング解像度 | `180` |
| `--quality` | JPEG品質（1〜95） | `70` |
| `--color` | カラーで出力 | なし |
| `--overlap` | 分割境界の重複px | `0` |
| `--x-offset` | 縦分割線の左右移動px | `0` |
| `--y-offset` | 横分割線の上下移動px | `0` |
| `--order` | `rtl_tb` / `ltr_tb` / `z` | `rtl_tb` |
| `--mode` | `pdf` / `images` / `both` | `pdf` |
| `--suffix` | 自動出力名の接尾辞 | `_4split` |

ヘルプは次のコマンドで確認できます。

```bash
python3 split_pdf.py --help
```

## 注意事項

- 元PDFは変更しません。
- 出力PDFは画像ベースであり、元PDFに含まれていたテキストレイヤーやしおり等は引き継ぎません。
- 4分割により出力ページ数は元PDFの4倍になります。
- PDFの内容や利用条件を確認し、著作権法その他の法令および資料提供元の規約に従って利用してください。
- 大量のページを処理する前に、数ページで分割位置とOCR精度を確認することを推奨します。

## ライセンス

このリポジトリの自作コードと文書は、GNU Affero General Public License v3.0 or later（AGPL-3.0-or-later）で公開します。詳しくは `LICENSE` を参照してください。

本ツールは次の外部ライブラリを利用します。各ライブラリには、それぞれのライセンス条件が適用されます。

- PyMuPDF：GNU AGPL v3または商用ライセンス
- Pillow：Pillow License（MIT-CMU系）

特に、非公開の商用製品への組込みなど、AGPLの条件に適合しない形でPyMuPDFを利用する場合は、PyMuPDF提供元の商用ライセンスが必要となる可能性があります。利用者自身で最新のライセンス条件を確認してください。

SPDX-License-Identifier: AGPL-3.0-or-later
