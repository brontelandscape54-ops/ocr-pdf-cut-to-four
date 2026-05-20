#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from io import BytesIO
from pathlib import Path
from typing import Iterable

import fitz  # PyMuPDF
from PIL import Image


def make_default_output(input_pdf: Path, outdir: Path | None, dpi: int, suffix: str, ext: str) -> Path:
    base_dir = outdir if outdir is not None else input_pdf.parent
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"{input_pdf.stem}{suffix}_{dpi}dpi.{ext}"


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(max_value, value))


def crop_box(
    name: str,
    w: int,
    h: int,
    overlap: int,
    x_offset: int,
    y_offset: int,
) -> tuple[int, int, int, int]:
    """
    4分割の切り出し範囲を返す。

    x_offset: 縦の分割線を左右に動かす。+で右、-で左。単位は画像化後のpx。
    y_offset: 横の分割線を上下に動かす。+で下、-で上。単位は画像化後のpx。
    overlap : 分割線付近を上下左右に重複させる。単位は画像化後のpx。
    """
    split_x = clamp(w // 2 + x_offset, 1, w - 1)
    split_y = clamp(h // 2 + y_offset, 1, h - 1)

    if name == "right_top":
        return (max(0, split_x - overlap), 0, w, min(h, split_y + overlap))
    if name == "right_bottom":
        return (max(0, split_x - overlap), max(0, split_y - overlap), w, h)
    if name == "left_top":
        return (0, 0, min(w, split_x + overlap), min(h, split_y + overlap))
    if name == "left_bottom":
        return (0, max(0, split_y - overlap), min(w, split_x + overlap), h)
    raise ValueError(f"unknown crop name: {name}")


def order_names(order: str) -> list[str]:
    if order == "rtl_tb":
        # 縦書き二段組向け: 右上 → 右下 → 左上 → 左下
        return ["right_top", "right_bottom", "left_top", "left_bottom"]
    if order == "ltr_tb":
        # 横書き・左から読む資料向け: 左上 → 左下 → 右上 → 右下
        return ["left_top", "left_bottom", "right_top", "right_bottom"]
    if order == "z":
        # 一般的なZ順: 左上 → 右上 → 左下 → 右下
        return ["left_top", "right_top", "left_bottom", "right_bottom"]
    raise ValueError(f"unknown order: {order}")


def render_page_to_image(page: fitz.Page, dpi: int) -> Image.Image:
    zoom = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def prepare_image(img: Image.Image, grayscale: bool) -> Image.Image:
    if grayscale:
        return img.convert("L")
    return img.convert("RGB")


def image_to_jpeg_bytes(img: Image.Image, quality: int) -> bytes:
    bio = BytesIO()
    img.save(
        bio,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=False,
    )
    return bio.getvalue()


def add_jpeg_page(out_doc: fitz.Document, img: Image.Image, dpi: int, quality: int) -> None:
    jpeg_bytes = image_to_jpeg_bytes(img, quality)
    width_pt = img.width * 72.0 / dpi
    height_pt = img.height * 72.0 / dpi
    page = out_doc.new_page(width=width_pt, height=height_pt)
    page.insert_image(page.rect, stream=jpeg_bytes)


def split_pdf(
    input_pdf: Path,
    output_pdf: Path | None,
    images_dir: Path | None,
    dpi: int,
    quality: int,
    grayscale: bool,
    overlap: int,
    x_offset: int,
    y_offset: int,
    order: str,
    mode: str,
) -> None:
    doc = fitz.open(str(input_pdf))
    names = order_names(order)

    if mode in {"pdf", "both"}:
        if output_pdf is None:
            raise ValueError("output_pdf is required in pdf/both mode")
        out_doc = fitz.open()
    else:
        out_doc = None

    if mode in {"images", "both"}:
        if images_dir is None:
            raise ValueError("images_dir is required in images/both mode")
        images_dir.mkdir(parents=True, exist_ok=True)

    total = len(doc)
    split_count = 0

    for page_index, page in enumerate(doc, start=1):
        img = render_page_to_image(page, dpi)
        w, h = img.size

        for part_index, name in enumerate(names, start=1):
            box = crop_box(name, w, h, overlap, x_offset, y_offset)
            cropped = prepare_image(img.crop(box), grayscale)
            split_count += 1

            if out_doc is not None:
                add_jpeg_page(out_doc, cropped, dpi, quality)

            if mode in {"images", "both"} and images_dir is not None:
                out_name = f"{input_pdf.stem}_p{page_index:04d}_{part_index}_{name}_{dpi}dpi_q{quality}.jpg"
                cropped.save(
                    images_dir / out_name,
                    format="JPEG",
                    quality=quality,
                    optimize=True,
                    progressive=False,
                )

        print(f"[INFO] page {page_index}/{total} processed", file=sys.stderr)

    if out_doc is not None and output_pdf is not None:
        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        out_doc.save(str(output_pdf), garbage=4, deflate=True, clean=True)
        out_doc.close()
        print(f"[OK] PDF saved: {output_pdf}")

    if mode in {"images", "both"} and images_dir is not None:
        print(f"[OK] JPEG images saved: {images_dir}")

    print(f"[INFO] source pages: {total}")
    print(f"[INFO] split pages/images: {split_count}")
    print(f"[INFO] dpi={dpi}, jpeg_quality={quality}, grayscale={grayscale}, overlap={overlap}, x_offset={x_offset}, y_offset={y_offset}, order={order}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PDFの各ページを4分割し、OCR前処理用の軽量PDF/JPEGを作成する"
    )
    parser.add_argument("input_pdf", help="入力PDF")
    parser.add_argument("--out", default=None, help="出力PDFパス。省略時は入力PDFと同じフォルダに自動生成")
    parser.add_argument("--outdir", default=None, help="出力先フォルダ。--out未指定時に使用")
    parser.add_argument("--images-dir", default=None, help="JPEG画像出力先。省略時は outdir/input名_4split_images")
    parser.add_argument("--dpi", type=int, default=180, help="レンダリングDPI。初期値: 180")
    parser.add_argument("--quality", type=int, default=70, help="JPEG品質 1-95。初期値: 70")
    parser.add_argument("--color", action="store_true", help="グレースケール化せずカラーで出力する")
    parser.add_argument("--overlap", type=int, default=0, help="分割境界の重複ピクセル数。文字切れ対策。初期値: 0")
    parser.add_argument("--x-offset", type=int, default=0, help="縦の分割線を左右に移動するpx数。+で右、-で左。初期値: 0")
    parser.add_argument("--y-offset", type=int, default=0, help="横の分割線を上下に移動するpx数。+で下、-で上。初期値: 0")
    parser.add_argument(
        "--order",
        choices=["rtl_tb", "ltr_tb", "z"],
        default="rtl_tb",
        help="分割順。rtl_tb=右上→右下→左上→左下、ltr_tb=左上→左下→右上→右下、z=左上→右上→左下→右下",
    )
    parser.add_argument(
        "--mode",
        choices=["pdf", "images", "both"],
        default="pdf",
        help="出力形式。pdf/images/both。初期値: pdf",
    )
    parser.add_argument("--suffix", default="_4split", help="自動生成する出力名の接尾辞。初期値: _4split")

    args = parser.parse_args()

    input_pdf = Path(args.input_pdf).expanduser().resolve()
    if not input_pdf.exists() or not input_pdf.is_file():
        print(f"[ERROR] 入力PDFが見つかりません: {input_pdf}", file=sys.stderr)
        sys.exit(1)

    if args.dpi <= 0:
        print("[ERROR] --dpi は1以上にしてください", file=sys.stderr)
        sys.exit(1)
    if not (1 <= args.quality <= 95):
        print("[ERROR] --quality は1〜95で指定してください", file=sys.stderr)
        sys.exit(1)
    if args.overlap < 0:
        print("[ERROR] --overlap は0以上にしてください", file=sys.stderr)
        sys.exit(1)

    outdir = Path(args.outdir).expanduser().resolve() if args.outdir else None

    output_pdf = None
    if args.mode in {"pdf", "both"}:
        output_pdf = Path(args.out).expanduser().resolve() if args.out else make_default_output(
            input_pdf=input_pdf,
            outdir=outdir,
            dpi=args.dpi,
            suffix=args.suffix,
            ext="pdf",
        )

    images_dir = None
    if args.mode in {"images", "both"}:
        if args.images_dir:
            images_dir = Path(args.images_dir).expanduser().resolve()
        else:
            base = outdir if outdir is not None else input_pdf.parent
            images_dir = base / f"{input_pdf.stem}{args.suffix}_images_{args.dpi}dpi_q{args.quality}"

    split_pdf(
        input_pdf=input_pdf,
        output_pdf=output_pdf,
        images_dir=images_dir,
        dpi=args.dpi,
        quality=args.quality,
        grayscale=not args.color,
        overlap=args.overlap,
        x_offset=args.x_offset,
        y_offset=args.y_offset,
        order=args.order,
        mode=args.mode,
    )


if __name__ == "__main__":
    main()
